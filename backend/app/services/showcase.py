from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database import StoryRecord, TopicRecord


CURATED_STORIES = [
    {
        "slug": "maratha-reservation-protest-2026",
        "title": "Maratha Reservation Protest: Manoj Jarange Continues Fast, Sets September 11 Deadline",
        "category": "Protest",
        "image": "/images/real-city-protest.jpg",
        "summary": "Manoj Jarange continued his reservation agitation in Jalna after seeking action on Maratha quota and Kunbi certificate demands.",
        "source": "Times of India · curated pitch source",
        "minutes_ago": 2,
    },
    {
        "slug": "tukaram-mundhe-fda-testing-surge",
        "title": "Maharashtra FDA Testing Rises 300% Under IAS Officer Tukaram Mundhe",
        "category": "India",
        "image": "/images/real-data-check.jpg",
        "summary": "Maharashtra FDA reported a sharp increase in statewide sample collection and testing after Tukaram Mundhe took charge as commissioner.",
        "source": "India Today · curated pitch source",
        "minutes_ago": 5,
    },
]


def _seed(title: str) -> int:
    return int(hashlib.sha256(title.encode()).hexdigest()[:8], 16)


def _geography(title: str) -> str:
    lowered = title.lower()
    if "manoj jarange" in lowered or "maratha reservation" in lowered:
        return "Jalna & Maharashtra"
    for needle, place in (("maharashtra", "Maharashtra"), ("mumbai", "Mumbai Metropolitan Region"), ("delhi", "Delhi NCR"), ("jalna", "Jalna, Maharashtra"), ("india", "India-wide")):
        if needle in lowered:
            return place
    return "India-wide"


def showcase_analytics(title: str, category: str, source: str) -> tuple[int, dict]:
    """Create a deterministic, explicitly labelled pitch dataset for complete UI rehearsal."""
    value = _seed(title)
    total = 12_000 + value % 38_000
    negative = 31 + value % 24
    positive = 17 + (value // 7) % 20
    neutral = 100 - negative - positive
    age = ("18–24", "25–34", "35–44")[(value // 13) % 3]
    language_sets = (
        {"Hindi": 42, "Marathi": 31, "English": 18, "Hinglish": 9},
        {"Marathi": 46, "Hindi": 27, "English": 18, "Hinglish": 9},
        {"English": 38, "Hindi": 34, "Hinglish": 18, "Marathi": 10},
    )
    languages = language_sets[(value // 17) % len(language_sets)]
    theme_map = {
        "Protest": ["Reservation demands", "Government response", "Community mobilisation", "Policy implementation"],
        "Laws": ["Legal interpretation", "Public rights", "Court proceedings", "Policy impact"],
        "Education": ["Student concerns", "Access and admissions", "Institutional response", "Equal opportunity"],
        "Analysis": ["Evidence quality", "Public trust", "Policy outcomes", "Accountability"],
        "India": ["Public accountability", "Administrative reform", "Consumer safety", "Government action"],
    }
    themes = theme_map.get(category, ["Public response", "Policy impact", "Community concerns", "Developing narrative"])
    interests = themes[:2] + (["Maratha community"] if "reservation" in title.lower() else ["Civic affairs"])
    steps = [round(total * ratio) for ratio in (.39, .47, .56, .68, .82, 1)]
    analytics = {
        "sentiment": {"negative": negative, "neutral": neutral, "positive": positive, "change_last_6h": 3 + value % 8, "qualified_conversations": round(total * .78)},
        "audience": {
            "geography": {"value": _geography(title), "confidence": "Medium", "provenance": "Synthetic pitch cohort aligned to story geography"},
            "language": {"distribution": languages, "confidence": "Medium", "provenance": "Synthetic multilingual pitch distribution"},
            "age_bracket": {"value": age, "confidence": "Low", "provenance": "Synthetic aggregate; never an individual prediction"},
            "interest_groups": interests, "key_topics": themes,
            "leading_platform": "YouTube + Reddit + public news (demo mix)",
            "confidence": {"interests": "Medium", "topics": "Medium", "platform": "Medium"},
        },
        "trends": [{"time": label, "volume": amount, "negative": max(0, negative - 5 + index)} for index, (label, amount) in enumerate(zip(("-12h", "-10h", "-8h", "-6h", "-3h", "Now"), steps))],
        "drivers": [{"title": item, "description": f"Demo discussion cluster focused on {item.lower()} in relation to this story.", "status": status} for item, status in zip(themes, ("TOP_CONCERN", "RISING", "RISING", "STABLE"))],
        "voices": [
            {"quote": f"The conversation needs reliable facts about {themes[0].lower()}.", "label": "Synthetic supporting voice", "stance": "supportive", "source": "Pitch demo"},
            {"quote": f"People are asking whether {themes[1].lower()} is being handled fairly.", "label": "Synthetic concerned voice", "stance": "opposing", "source": "Pitch demo"},
            {"quote": "What measurable outcomes should the public watch next?", "label": "Synthetic questioning voice", "stance": "neutral", "source": "Pitch demo"},
        ],
        "network": {
            "nodes": [{"id": f"demo-{i}", "label": item, "centrality": round(.82 - i * .09, 2)} for i, item in enumerate(themes)],
            "edges": [{"source": f"demo-{i}", "target": f"demo-{i+1}", "weight": 8 - i} for i in range(3)],
        },
        "confidence": {
            "level": "Demo", "sources": [source, "Synthetic YouTube sample", "Synthetic Reddit sample", "Synthetic multilingual sample"],
            "qualified_conversations": round(total * .78), "low_signal_excluded_or_downweighted": round(total * .12),
            "analysis_scope": "pitch_demo", "metric_label": "simulated conversations (pitch demo)",
            "disclaimer": "Synthetic, deterministic showcase data for UI rehearsal. It is not a claim of live social-media measurement.",
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        },
        "brief": {
            "insight": f"Pitch-demo analysis indicates that discussion around “{title}” is being shaped by {themes[0].lower()}, {themes[1].lower()} and {themes[2].lower()}. The synthetic cohort currently leans {'opposing' if negative > positive else 'supportive'}, with the strongest simulated activity in {_geography(title)}.",
            "what_changed": "Synthetic conversation velocity increased during the latest demonstration window.",
            "what_is_rising": themes[1], "what_to_watch": themes[2],
        },
    }
    return total, analytics


def apply_showcase_analysis(db: Session, topic: TopicRecord, story: StoryRecord | None = None) -> TopicRecord:
    story = story or db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == topic.slug).order_by(StoryRecord.published_at.desc()))
    if not story:
        return topic
    total, analytics = showcase_analytics(story.title, story.category, story.source_status.replace("news:", ""))
    topic.total_conversations = total
    topic.subtitle = "Complete AI conversation analysis · pitch demonstration"
    topic.updated = "Just now · pitch dataset"
    topic.is_demo = True
    topic.analytics_json = json.dumps(analytics)
    return topic


def prepare_curated_stories(db: Session) -> None:
    now = datetime.now(timezone.utc)
    for item in CURATED_STORIES:
        topic = db.get(TopicRecord, item["slug"])
        if not topic:
            from app.services.database import preview_analytics
            topic = TopicRecord(slug=item["slug"], title=item["title"], subtitle="Story context analysed · awaiting measured public signals", total_conversations=0, updated="Evidence collection pending", is_demo=True, analytics_json=json.dumps(preview_analytics(item["title"],item["category"],item["source"])))
            db.add(topic); db.flush()
        story = db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == item["slug"]))
        if not story:
            story = StoryRecord(title=item["title"], category=item["category"], relative_time="Just now", image=item["image"], is_live=True, topic_slug=item["slug"], summary=item["summary"], source_status=f"news:{item['source']}", published_at=now - timedelta(minutes=item["minutes_ago"]))
            db.add(story); db.flush()
        else:
            story.title=item["title"];story.category=item["category"];story.image=item["image"];story.is_live=True;story.summary=item["summary"];story.source_status=f"news:{item['source']}";story.published_at=now-timedelta(minutes=item["minutes_ago"])
    db.commit()


def prepare_showcase(db: Session) -> None:
    prepare_curated_stories(db)
    for topic in db.scalars(select(TopicRecord)).all():
        apply_showcase_analysis(db, topic)
    db.commit()
