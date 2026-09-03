import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.database import (
    Base,
    BookmarkRecord,
    PreferenceRecord,
    StoryRecord,
    TopicRecord,
    NarrativeRecord,
    engine,
    SessionLocal,
)

logger = logging.getLogger("updates.database")

def empty_analytics(title: str = "Narrative") -> dict:
    """A clean contract with no invented measurements."""
    return {
        "sentiment": {"negative": 0, "neutral": 0, "positive": 0, "change_last_6h": 0, "qualified_conversations": 0},
        "audience": {
            "geography": {"value": "Awaiting collected location signals"},
            "language": {"distribution": {}},
            "age_bracket": {"value": "Not available from public source metadata", "confidence": "Unavailable"},
            "interest_groups": [],
            "key_topics": [],
            "leading_platform": "Awaiting streaming data",
        },
        "trends": [],
        "drivers": [],
        "voices": [],
        "network": {"nodes": [], "edges": []},
        "confidence": {"level": "Awaiting data", "sources": [], "qualified_conversations": 0, "low_signal_excluded_or_downweighted": 0},
        "brief": {"insight": f"Analysis for “{title}” will update as live signals enter the pipeline.", "what_changed": "Awaiting data.", "what_is_rising": "", "what_to_watch": ""},
    }

def preview_analytics(title: str, category: str = "Analysis") -> dict:
    return empty_analytics(title)

def init_database() -> None:

    """Initializes tables cleanly."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.get(PreferenceRecord, "notifications_enabled"):
            db.add(PreferenceRecord(key="notifications_enabled", value="false"))
            db.commit()

def bootstrap_live_data() -> None:
    """Bootstraps live news in background if database is empty."""
    with SessionLocal() as db:
        story_count = len(db.scalars(select(StoryRecord.id).limit(1)).all())
        if story_count == 0:
            try:
                from app.services.news import refresh_latest_news
                logger.info("Initializing database with live public news feed...")
                refresh_latest_news(db, max_items=12)
            except Exception as e:
                logger.warning(f"Could not bootstrap initial live news: {e}")


def relative_time(value: datetime | None, fallback: str) -> str:
    if not value:
        return fallback
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    seconds = max(0, int((datetime.now(timezone.utc) - value).total_seconds()))
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"

def story_dict(story: StoryRecord, bookmarked: bool = False) -> dict:
    return {
        "id": str(story.id),
        "title": story.title,
        "category": story.category,
        "time": relative_time(story.published_at, story.relative_time),
        "published_at": story.published_at.isoformat() if story.published_at else None,
        "image": story.image,
        "live": story.is_live,
        "topic_slug": story.topic_slug,
        "summary": story.summary,
        "source_status": story.source_status,
        "bookmarked": bookmarked,
    }

def bookmarked_ids(db: Session) -> set[int]:
    return set(db.scalars(select(BookmarkRecord.story_id)).all())
