from __future__ import annotations
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.collectors.adapters import CollectorError, get_collector
from app.models.database import (
    CommentAnalysisRecord,
    IngestionJobRecord,
    NarrativeRecord,
    NetworkEdgeRecord,
    NetworkNodeRecord,
    PostRecord,
    SentimentRecord,
    SourceCommentRecord,
    StoryRecord,
    TopicRecord,
    UserRecord,
)
from app.models.schemas import CommentInput, IngestionRequest
from app.services.audience import AudienceIntelligenceService
from app.services.csqe import CSQEService
from app.services.intelligence import CommentIntelligenceService
from app.services.kafka_stream import get_kafka_service
from app.services.narrative_detection import detect_narratives
from app.services.network import analyze_network
from app.services.sentiment import SentimentService
from app.services.topic_modeling import extract_dynamic_topics

logger = logging.getLogger("updates.ingestion")
csqe_engine = CSQEService()
sentiment_service = SentimentService()
audience_service = AudienceIntelligenceService()

def _hash_author(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(f"updates-public-author:{value}".encode()).hexdigest()

def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

def _human_platform(name: str) -> str:
    return {"x": "X (Twitter)", "twitter": "X (Twitter)", "youtube": "YouTube", "reddit": "Reddit", "telegram": "Telegram", "facebook": "Facebook", "instagram": "Instagram"}.get(name.lower(), name.title())

def _percent(count: int, total: int) -> int:
    return round(100 * count / total) if total else 0

def _distribution(counts: Counter, total: int, keys: list[str] | None = None) -> dict[str, int]:
    names = keys or [name for name, _ in counts.most_common()]
    values = {name: _percent(counts[name], total) for name in names}
    if values:
        leader = max(names, key=lambda name: counts[name])
        values[leader] += 100 - sum(values.values())
    return values

async def _store(db: Session, topic_slug: str, platform: str, raw: dict, service: CommentIntelligenceService) -> bool:
    collector = get_collector(platform)
    item = collector.normalize(raw, topic_slug)
    social_post = collector.to_social_post(raw)

    if not item.text:
        return False

    # Check for duplicate in database
    existing_post = db.scalar(select(PostRecord).where(PostRecord.platform == platform, PostRecord.post_id == str(raw["id"])))
    existing_comment = db.scalar(select(SourceCommentRecord).where(SourceCommentRecord.platform == platform, SourceCommentRecord.external_id == item.external_id))
    if existing_post or existing_comment:
        return False

    # Publish raw to Kafka stream
    kafka = get_kafka_service()
    await kafka.publish_raw(platform, raw)

    # 1. CSQE Signal Qualification
    csqe_res = csqe_engine.qualify(social_post.content)

    # Publish normalized to Kafka
    await kafka.publish_normalized(social_post)

    # 2. Save into posts table
    post_record = PostRecord(
        platform=platform,
        post_id=social_post.post_id,
        author_id=social_post.author_id,
        author_name=social_post.author_name,
        content=social_post.content,
        published_at=social_post.timestamp,
        language=social_post.language,
        likes=social_post.likes,
        comments=social_post.comments,
        shares=social_post.shares,
        views=social_post.views,
        hashtags_json=json.dumps(social_post.hashtags),
        mentions_json=json.dumps(social_post.mentions),
        url=social_post.url,
        is_verified=social_post.is_verified,
        topic_slug=topic_slug,
        raw_metadata_json=json.dumps(raw.get("metadata", {})),
    )
    db.add(post_record)

    # 3. Save into users table if author exists
    if social_post.author_id:
        existing_user = db.scalar(select(UserRecord).where(UserRecord.platform == platform, UserRecord.author_id == social_post.author_id))
        if not existing_user:
            db.add(UserRecord(
                author_id=social_post.author_id,
                platform=platform,
                author_name=social_post.author_name,
                is_verified=social_post.is_verified,
                influence_score=float(min(100, (social_post.likes * 0.1) + (social_post.shares * 0.5))),
                location=item.public_profile_signals.get("location"),
                metadata_json=json.dumps(social_post.metadata),
            ))

    # 4. Save into legacy source_comments for backwards compatibility
    source_comment = SourceCommentRecord(
        topic_slug=topic_slug,
        platform=platform,
        external_id=item.external_id,
        parent_external_id=item.parent_id,
        author_hash=_hash_author(item.author_id),
        text=item.text,
        published_at=item.timestamp,
        engagement_json=json.dumps(item.engagement),
        public_signals_json=json.dumps(item.public_profile_signals),
        raw_metadata_json=json.dumps(item.raw_metadata),
    )
    db.add(source_comment)
    db.flush()

    # 5. NLP & Sentiment Analysis
    sent_res = sentiment_service.analyse(social_post.content, context=topic_slug)
    db.add(SentimentRecord(
        post_id=post_record.id,
        sentiment=sent_res.sentiment,
        confidence=sent_res.confidence,
        stance=sent_res.stance,
        emotion=sent_res.emotion,
        sarcasm_detected=sent_res.sarcasm.sarcasm_detected if sent_res.sarcasm else False,
        sarcasm_confidence=sent_res.sarcasm.sarcasm_confidence if sent_res.sarcasm else 0.0,
        model_name="MuRIL-Indic-Sentiment",
    ))

    result = service.analyse(CommentInput(
        text=item.text,
        context=topic_slug,
        platform=platform,
        engagement=item.engagement,
        public_signals=item.public_profile_signals,
    ))
    db.add(CommentAnalysisRecord(
        comment_id=source_comment.id,
        sentiment=sent_res.sentiment,
        sentiment_score=sent_res.sentiment_score,
        stance=sent_res.stance,
        emotion=sent_res.emotion,
        safety=result.safety,
        language=result.language,
        interests_json=json.dumps(result.interests),
        geography=result.geography,
        age_bracket=result.age_bracket,
        inference_json=json.dumps({
            "confidence": result.confidence,
            "evidence": result.evidence,
            "signal_quality": csqe_res.signal_quality,
            "signal_classification": csqe_res.classification,
            "safety_model": result.safety_model_name,
        }),
        influence_score=result.influence_score,
        model_name=result.model_name,
    ))

    # Publish qualified post to Kafka
    await kafka.publish_qualified({
        "post_id": social_post.post_id,
        "platform": social_post.platform,
        "content": social_post.content,
        "csqe": {"quality": csqe_res.signal_quality, "class": csqe_res.classification},
        "sentiment": sent_res.sentiment,
    })

    return True

def refresh_topic_analytics(db: Session, topic_slug: str) -> None:
    topic = db.get(TopicRecord, topic_slug)
    if not topic:
        return

    # Fetch all posts/comments for this topic
    rows = db.execute(
        select(SourceCommentRecord, CommentAnalysisRecord)
        .join(CommentAnalysisRecord, CommentAnalysisRecord.comment_id == SourceCommentRecord.id)
        .where(SourceCommentRecord.topic_slug == topic_slug)
    ).all()

    if not rows:
        return

    total = len(rows)
    posts_data = []
    for c, a in rows:
        posts_data.append({
            "id": str(c.id),
            "text": c.text,
            "author_id": c.author_hash or "anonymous",
            "author_name": c.platform.capitalize() + " User",
            "platform": c.platform,
            "timestamp": _utc(c.published_at),
            "likes": json.loads(c.engagement_json or "{}").get("likes", 0),
            "shares": json.loads(c.engagement_json or "{}").get("shares", 0),
            "comments": json.loads(c.engagement_json or "{}").get("replies", 0),
            "sentiment": a.sentiment,
            "public_signals": json.loads(c.public_signals_json or "{}"),
            "metadata": json.loads(c.raw_metadata_json or "{}"),
        })

    # 1. Dynamic Topic Modeling
    dynamic_topics = extract_dynamic_topics(posts_data)
    posts_by_topic = {}
    for dt in dynamic_topics:
        id_set = set(dt.post_ids)
        posts_by_topic[dt.topic_id] = [p for p in posts_data if p["id"] in id_set]

    # 2. Emerging Narrative Detection
    narratives = detect_narratives(dynamic_topics, posts_by_topic)

    # 3. Audience Profiling
    audience_metrics = audience_service.analyze_audience(posts_data)

    # 4. NetworkX & PageRank Analysis
    network_metrics = analyze_network(posts_data, narrative_title=topic.title)

    # 5. Temporal Volume & Trends
    bucket_rows: dict[str, list[dict]] = {}
    for p in posts_data:
        label = p["timestamp"].strftime("%Y-%m-%d %H:00")
        bucket_rows.setdefault(label, []).append(p)
    trends = [
        {"time": label, "volume": len(vals), "negative": _percent(sum(item["sentiment"] == "negative" for item in vals), len(vals))}
        for label, vals in sorted(bucket_rows.items())
    ]

    # 6. Sentiment Breakdown
    sentiments = Counter(p["sentiment"] for p in posts_data)
    now = datetime.now(timezone.utc)
    recent = [p for p in posts_data if p["timestamp"] >= now - timedelta(hours=6)]
    previous = [p for p in posts_data if now - timedelta(hours=12) <= p["timestamp"] < now - timedelta(hours=6)]
    recent_neg = _percent(sum(item["sentiment"] == "negative" for item in recent), len(recent))
    prev_neg = _percent(sum(item["sentiment"] == "negative" for item in previous), len(previous))
    change = recent_neg - prev_neg if previous else 0
    sentiment_dist = _distribution(sentiments, total, ["negative", "neutral", "positive"])

    # 7. Conversation Drivers (derived dynamically from topic modeling)
    drivers = []
    for idx, dt in enumerate(dynamic_topics[:4]):
        status = "TOP_CONCERN" if idx == 0 else "RISING" if idx < 3 else "STABLE"
        drivers.append({
            "title": dt.name,
            "description": f"Accounts for {dt.post_count} of {total} analysed conversations and is a leading discussion theme.",
            "status": status,
        })

    # 8. Representative Voices (real extracted quotes)
    voices = []
    used_quotes = set()
    for stance_type in ("opposing", "supportive", "questioning", "neutral"):
        candidates = [p for p in posts_data if p.get("sentiment") == ("negative" if stance_type == "opposing" else "positive" if stance_type == "supportive" else "neutral")]
        if candidates:
            best_post = max(candidates, key=lambda x: (x.get("likes", 0) + x.get("shares", 0), x["timestamp"]))
            clean_quote = " ".join(best_post["text"].split())[:280]
            if clean_quote not in used_quotes:
                label = "Concerned voice" if stance_type == "opposing" else "Supporting voice" if stance_type == "supportive" else "Questioning / neutral voice"
                voices.append({"quote": clean_quote, "label": f"{label} · {_human_platform(best_post['platform'])}", "tone": "concerned" if stance_type == "opposing" else "supporting" if stance_type == "supportive" else "neutral"})
                used_quotes.add(clean_quote)
                if len(voices) >= 3:
                    break

    # 9. Confidence
    signal_classes = Counter(json.loads(a.inference_json or "{}").get("signal_classification", "HIGH_SIGNAL") for _, a in rows)
    low_signal = signal_classes.get("LOW_SIGNAL", 0)
    qualified = max(0, total - low_signal)
    confidence_level = "High" if total >= 50 and qualified / total >= 0.75 else "Medium" if total >= 15 else "Low"
    sources_list = [_human_platform(name) for name in sorted(Counter(p["platform"] for p in posts_data))]

    # 10. AI Insight Brief
    top_driver_name = drivers[0]["title"] if drivers else topic.title
    dominant_sent = max(sentiments, key=sentiments.get) if sentiments else "neutral"
    insight_brief = (
        f"Public conversation regarding “{topic.title}” is currently leaning {dominant_sent} ({sentiment_dist.get(dominant_sent, 0)}%). "
        f"The primary emerging driver is {top_driver_name}. Analysis encompasses {total:,} verified public signals across {', '.join(sources_list)}."
    )

    analytics = {
        "sentiment": {**sentiment_dist, "change_last_6h": change, "qualified_conversations": total},
        "audience": audience_metrics,
        "trends": trends,
        "drivers": drivers,
        "voices": voices,
        "network": network_metrics,
        "confidence": {
            "level": confidence_level,
            "sources": sources_list,
            "qualified_conversations": qualified,
            "low_signal_excluded_or_downweighted": low_signal,
        },
        "brief": {
            "insight": insight_brief,
            "what_changed": f"Opposing sentiment shifted by {change:+d}% over the last 6 hours.",
            "what_is_rising": top_driver_name,
            "what_to_watch": drivers[1]["title"] if len(drivers) > 1 else top_driver_name,
        },
    }

    # Update TopicRecord
    topic.total_conversations = total
    topic.updated = "Just now"
    topic.is_demo = False
    topic.analytics_json = json.dumps(analytics)

    # Update or insert NarrativeRecord
    top_narrative = narratives[0] if narratives else None
    narrative_rec = db.get(NarrativeRecord, topic_slug)
    if not narrative_rec:
        narrative_rec = NarrativeRecord(
            slug=topic_slug,
            title=topic.title,
            category="India" if "protest" in topic_slug or "india" in topic_slug else "Analysis",
            status=top_narrative.status if top_narrative else "EMERGING",
            is_emerging=top_narrative.is_emerging if top_narrative else True,
            momentum_score=top_narrative.momentum_score if top_narrative else 0.5,
            velocity=top_narrative.velocity if top_narrative else 1.0,
            growth_rate=top_narrative.growth_rate if top_narrative else 0.2,
            cross_platform_score=top_narrative.cross_platform_score if top_narrative else 0.5,
            sentiment_negative=sentiment_dist.get("negative", 0),
            sentiment_neutral=sentiment_dist.get("neutral", 0),
            sentiment_positive=sentiment_dist.get("positive", 0),
            sentiment_change_6h=change,
            ai_insight=insight_brief,
            confidence_level=confidence_level,
            total_conversations=total,
            qualified_count=qualified,
            low_signal_count=low_signal,
            is_live=True,
            summary=insight_brief,
        )
        db.add(narrative_rec)
    else:
        narrative_rec.status = top_narrative.status if top_narrative else narrative_rec.status
        narrative_rec.is_emerging = top_narrative.is_emerging if top_narrative else narrative_rec.is_emerging
        narrative_rec.momentum_score = top_narrative.momentum_score if top_narrative else narrative_rec.momentum_score
        narrative_rec.velocity = top_narrative.velocity if top_narrative else narrative_rec.velocity
        narrative_rec.growth_rate = top_narrative.growth_rate if top_narrative else narrative_rec.growth_rate
        narrative_rec.sentiment_negative = sentiment_dist.get("negative", 0)
        narrative_rec.sentiment_neutral = sentiment_dist.get("neutral", 0)
        narrative_rec.sentiment_positive = sentiment_dist.get("positive", 0)
        narrative_rec.sentiment_change_6h = change
        narrative_rec.ai_insight = insight_brief
        narrative_rec.confidence_level = confidence_level
        narrative_rec.total_conversations = total
        narrative_rec.qualified_count = qualified
        narrative_rec.low_signal_count = low_signal
        narrative_rec.summary = insight_brief

    # Sync corresponding StoryRecord
    story = db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == topic_slug))
    if story:
        story.summary = insight_brief
        story.is_live = True

    db.commit()

async def run_ingestion(db: Session, payload: IngestionRequest) -> dict:
    if not db.get(TopicRecord, payload.topic_slug):
        # Create topic dynamically if it doesn't exist
        db.add(TopicRecord(
            slug=payload.topic_slug,
            title=payload.query.title(),
            subtitle="Public sentiment & conversation analysis",
            total_conversations=0,
            updated="Collecting live signals...",
            is_demo=False,
            analytics_json="{}",
        ))
        db.commit()

    job = IngestionJobRecord(
        id=str(uuid4()),
        topic_slug=payload.topic_slug,
        platforms_json=json.dumps(payload.platforms),
        query=payload.query,
        status="running",
    )
    db.add(job)
    db.commit()

    service = CommentIntelligenceService()
    results: dict[str, dict[str, int]] = {}
    errors: dict[str, str] = {}

    for platform in payload.platforms:
        try:
            collector = get_collector(platform)
            added = 0
            targets = payload.targets.get(platform, [])
            if targets:
                raw = []
                for target in targets:
                    raw.extend(await collector.fetch_comments(target, max(1, payload.max_items - len(raw))))
                    if len(raw) >= payload.max_items:
                        break
            elif platform == "x" or platform == "twitter":
                raw = await collector.fetch_posts(payload.query, payload.max_items)
            elif platform in {"youtube", "reddit"}:
                posts = await collector.fetch_posts(payload.query, min(10, payload.max_items))
                raw = []
                for post in posts:
                    raw.extend(await collector.fetch_comments(post["id"], max(1, payload.max_items - len(raw))))
                    if len(raw) >= payload.max_items:
                        break
            else:
                raw = await collector.fetch_posts(payload.query, payload.max_items)

            for item in raw[:payload.max_items]:
                success = await _store(db, payload.topic_slug, platform, item, service)
                if success:
                    added += 1

            db.commit()
            results[platform] = {"fetched": len(raw[:payload.max_items]), "stored": added}
        except Exception as exc:
            db.rollback()
            errors[platform] = str(exc)

    refresh_topic_analytics(db, payload.topic_slug)
    job = db.get(IngestionJobRecord, job.id)
    if job:
        job.results_json = json.dumps(results)
        job.error_json = json.dumps(errors)
        job.status = "completed" if any(v.get("stored", 0) > 0 for v in results.values()) else "failed" if errors else "completed"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

    return {"job_id": job.id if job else "completed", "status": job.status if job else "completed", "results": results, "errors": errors}

async def analyze_topic_query(db: Session, query: str, max_items: int = 50) -> dict:
    """Interactive topic analysis pipeline (Section 17)."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:80]
    topic = db.get(TopicRecord, slug)
    if not topic:
        topic = TopicRecord(
            slug=slug,
            title=query.title(),
            subtitle="Public sentiment & conversation analysis",
            total_conversations=0,
            updated="Awaiting collection",
            is_demo=False,
            analytics_json="{}",
        )
        db.add(topic)
        db.commit()

    # Determine active configured platforms
    from app.collectors.adapters import COLLECTORS
    configured_platforms = [p for p in COLLECTORS if get_collector(p).configured and p not in ("facebook", "instagram")]
    if not configured_platforms:
        # If no official credentials configured, utilize Telegram public web / GDELT / Reddit public
        configured_platforms = ["telegram", "reddit"]

    payload = IngestionRequest(
        topic_slug=slug,
        query=query,
        platforms=configured_platforms,
        max_items=max_items,
    )
    ingest_result = await run_ingestion(db, payload)
    refresh_topic_analytics(db, slug)

    db.refresh(topic)
    return {
        "slug": slug,
        "title": topic.title,
        "analytics": topic.analytics,
        "ingestion": ingest_result,
    }
