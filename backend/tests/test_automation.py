import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.models.database import SessionLocal, StoryRecord, TopicRecord
from app.services.public_signals import due_public_signal_slugs


def test_analysis_refresh_defaults_to_two_hours():
    settings = get_settings()
    assert settings.analysis_refresh_interval_minutes == 120
    assert settings.public_signal_batch_size >= settings.auto_news_refresh_max_items


def test_due_queue_includes_unanalysed_and_stale_topics():
    with SessionLocal() as db:
        story = db.scalar(select(StoryRecord).order_by(StoryRecord.published_at.desc()))
        assert story is not None
        topic = db.get(TopicRecord, story.topic_slug)
        original = topic.analytics_json
        analytics = topic.analytics
        analytics.setdefault("confidence", {})["analysis_scope"] = "public_attention_signals"
        analytics["confidence"]["refreshed_at"] = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        topic.analytics_json = json.dumps(analytics); db.commit()
        try:
            assert story.topic_slug in due_public_signal_slugs(db, 120, 100)
        finally:
            topic.analytics_json = original; db.commit()
