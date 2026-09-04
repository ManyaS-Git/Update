from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database import StoryRecord, TopicRecord


STOP_WORDS = {
    "a", "about", "after", "against", "and", "are", "as", "at", "be", "before", "by", "for",
    "from", "has", "have", "how", "in", "india", "indian", "into", "is", "it", "its", "latest",
    "new", "news", "of", "on", "or", "over", "says", "the", "their", "this", "to", "under",
    "with", "amid", "report", "reports", "today", "live", "update", "updates",
}


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _tokens(title: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z][a-z'-]{2,}", title.lower())
        if token not in STOP_WORDS and not token.isdigit()
    }


def _source(story: StoryRecord) -> str:
    status = story.source_status or "unknown"
    return status.split(":", 1)[1].strip() if ":" in status else status.replace("_", " ")


def _similar(left: set[str], right: set[str]) -> bool:
    if not left or not right:
        return False
    shared = left & right
    return len(shared) >= 2 and len(shared) / min(len(left), len(right)) >= 0.28


@dataclass
class _Cluster:
    stories: list[StoryRecord]
    vocabulary: set[str]


def _cluster(stories: Iterable[StoryRecord]) -> list[_Cluster]:
    clusters: list[_Cluster] = []
    for story in stories:
        words = _tokens(story.title)
        match = next((item for item in clusters if _similar(words, item.vocabulary)), None)
        if match:
            match.stories.append(story)
            match.vocabulary.update(words)
        else:
            clusters.append(_Cluster([story], set(words)))
    return clusters


def _label(cluster: _Cluster) -> tuple[str, list[str]]:
    counts = Counter(token for story in cluster.stories for token in _tokens(story.title))
    keywords = [word for word, _ in counts.most_common(4)]
    if len(cluster.stories) == 1:
        return cluster.stories[0].title, keywords
    display = " · ".join(word.title() for word in keywords[:3])
    return display or cluster.stories[0].category, keywords


def detect_emerging_topics(
    stories: Iterable[StoryRecord],
    topics: dict[str, TopicRecord],
    *,
    now: datetime | None = None,
    recent_hours: int = 12,
    baseline_hours: int = 36,
    limit: int = 6,
) -> list[dict]:
    """Rank evidence clusters by acceleration, recency, source breadth and public attention.

    The score is deliberately deterministic and explainable. It never manufactures mention
    counts: article counts come from stored source records and attention signals come from the
    topic enrichment pipeline.
    """
    clock = _utc(now or datetime.now(timezone.utc))
    horizon = clock - timedelta(hours=recent_hours + baseline_hours)
    eligible = [story for story in stories if _utc(story.published_at) >= horizon]
    results: list[dict] = []
    for cluster in _cluster(sorted(eligible, key=lambda item: _utc(item.published_at), reverse=True)):
        recent = [item for item in cluster.stories if _utc(item.published_at) >= clock - timedelta(hours=recent_hours)]
        baseline = [item for item in cluster.stories if item not in recent]
        if not recent:
            continue
        recent_rate = len(recent) / recent_hours
        baseline_rate = len(baseline) / baseline_hours
        acceleration = recent_rate / max(baseline_rate, 1 / baseline_hours)
        sources = sorted({_source(item) for item in cluster.stories})
        attention = max((topics.get(item.topic_slug).total_conversations if topics.get(item.topic_slug) else 0) for item in cluster.stories)
        age_hours = max(0.0, (clock - max(_utc(item.published_at) for item in recent)).total_seconds() / 3600)
        recency = max(0.0, 1 - age_hours / recent_hours)
        acceleration_score = min(1.0, math.log1p(acceleration) / math.log(5))
        diversity_score = min(1.0, len(sources) / 4)
        attention_score = min(1.0, math.log1p(attention) / math.log(100_001))
        evidence_score = min(1.0, len(recent) / 4)
        score = round(100 * (0.34 * acceleration_score + 0.24 * recency + 0.20 * diversity_score + 0.14 * evidence_score + 0.08 * attention_score))
        is_emerging = len(recent) >= 2 and (acceleration >= 1.5 or len(baseline) == 0) and len(sources) >= 2
        status = "Emerging" if is_emerging else "Watching"
        confidence = "High" if len(recent) >= 4 and len(sources) >= 3 else "Medium" if len(recent) >= 2 else "Low"
        title, keywords = _label(cluster)
        lead = recent[0]
        results.append({
            "id": f"cluster-{lead.id}", "title": title, "keywords": keywords,
            "status": status, "confidence": confidence, "momentum_score": score,
            "recent_mentions": len(recent), "baseline_mentions": len(baseline),
            "growth_multiple": round(acceleration, 2), "velocity_per_hour": round(recent_rate, 3),
            "source_diversity": len(sources), "sources": sources,
            "public_attention_signals": attention, "topic_slug": lead.topic_slug,
            "latest_published_at": _utc(lead.published_at).isoformat(),
            "evidence": [{"story_id": str(item.id), "title": item.title, "source": _source(item), "published_at": _utc(item.published_at).isoformat()} for item in cluster.stories[:5]],
        })
    return sorted(results, key=lambda item: (item["status"] == "Emerging", item["momentum_score"], item["recent_mentions"]), reverse=True)[:limit]


def emerging_snapshot(db: Session, recent_hours: int = 12, baseline_hours: int = 36, limit: int = 6) -> dict:
    now = datetime.now(timezone.utc)
    horizon = now - timedelta(hours=recent_hours + baseline_hours)
    stories = db.scalars(select(StoryRecord).where(StoryRecord.published_at >= horizon).order_by(StoryRecord.published_at.desc())).all()
    topic_rows = db.scalars(select(TopicRecord)).all()
    narratives = detect_emerging_topics(stories, {item.slug: item for item in topic_rows}, now=now, recent_hours=recent_hours, baseline_hours=baseline_hours, limit=limit)
    return {
        "generated_at": now.isoformat(), "recent_window_hours": recent_hours,
        "baseline_window_hours": baseline_hours, "narratives": narratives,
        "methodology": "NLP-assisted headline clustering ranked by measured acceleration, recency, source diversity and available public-attention signals.",
        "disclaimer": "Emerging labels require at least two recent, independently sourced items. Watching labels are early signals, not verified trends.",
    }
