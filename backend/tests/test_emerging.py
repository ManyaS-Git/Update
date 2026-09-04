from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models.database import StoryRecord, TopicRecord
from app.services.emerging import detect_emerging_topics


client = TestClient(app)


def _story(identifier: int, title: str, hours_ago: int, source: str) -> StoryRecord:
    return StoryRecord(
        id=identifier, title=title, category="Laws", relative_time="recent", image="/test.jpg",
        topic_slug="court-policy", summary="test", source_status=f"news:{source}",
        published_at=NOW - timedelta(hours=hours_ago),
    )


NOW = datetime(2026, 9, 4, 12, tzinfo=timezone.utc)


def test_multi_source_accelerating_cluster_is_emerging():
    topic = TopicRecord(slug="court-policy", title="Court policy", subtitle="test", total_conversations=4200)
    stories = [
        _story(1, "Supreme Court reviews student admission policy", 1, "Source A"),
        _story(2, "Student admission policy reaches Supreme Court", 4, "Source B"),
        _story(3, "Supreme Court hearing on student admission policy", 8, "Source C"),
        _story(4, "Earlier report on Supreme Court student admission policy", 30, "Source A"),
    ]
    result = detect_emerging_topics(stories, {topic.slug: topic}, now=NOW)
    assert result[0]["status"] == "Emerging"
    assert result[0]["recent_mentions"] == 3
    assert result[0]["source_diversity"] == 3
    assert result[0]["evidence"][0]["title"]


def test_single_source_item_is_only_watching():
    result = detect_emerging_topics([_story(1, "Unique climate policy announcement", 1, "Source A")], {}, now=NOW)
    assert result[0]["status"] == "Watching"
    assert result[0]["confidence"] == "Low"


def test_emerging_endpoint_exposes_methodology_and_evidence():
    response = client.get("/api/emerging")
    assert response.status_code == 200
    body = response.json()
    assert "methodology" in body
    assert "disclaimer" in body
    assert isinstance(body["narratives"], list)
    if body["narratives"]:
        assert "evidence" in body["narratives"][0]
