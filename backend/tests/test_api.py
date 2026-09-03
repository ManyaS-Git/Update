import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.main import app
from app.models.database import SessionLocal, TopicRecord, StoryRecord
from app.services.database import init_database

init_database()
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    with SessionLocal() as db:
        topic = db.get(TopicRecord, "test-narrative")
        if not topic:
            topic = TopicRecord(
                slug="test-narrative",
                title="Test Emerging Narrative",
                subtitle="Public sentiment & conversation analysis",
                total_conversations=150,
                updated="Just now",
                analytics_json="{}",
            )

            db.add(topic)
        
        story = db.get(StoryRecord, 1)
        if not story:
            story = StoryRecord(
                id=1,
                title="AI Innovations Accelerate Across Industry Sectors",
                category="Technology",
                relative_time="Just now",
                published_at=datetime.now(timezone.utc),
                image="/images/news/ai.jpg",
                is_live=True,
                topic_slug="test-narrative",
                summary="Global technological transformation is advancing rapidly.",
                source_status="verified",
            )
            db.add(story)
        db.commit()

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_topic():
    response = client.get("/api/topics/test-narrative")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Emerging Narrative"

def test_missing_topic():
    assert client.get("/api/topics/non-existent-topic-slug-xyz").status_code == 404

def test_story_search_and_detail():
    stories = client.get("/api/stories").json()
    assert len(stories) >= 1
    first_id = stories[0]["id"]
    detail = client.get(f"/api/stories/{first_id}")
    assert detail.status_code == 200
    search_res = client.get("/api/search?q=Innovations").json()
    assert len(search_res["stories"]) >= 1

def test_story_topics_dynamic_sentiment():
    topic = client.get("/api/topics/test-narrative").json()
    sentiment = client.get("/api/topics/test-narrative/sentiment").json()
    assert topic["title"] == "Test Emerging Narrative"
    assert "negative" in sentiment and "positive" in sentiment
    confidence = client.get("/api/topics/test-narrative/confidence").json()
    assert "level" in confidence

def test_bookmark_lifecycle():
    client.delete("/api/bookmarks/1")
    post_res = client.post("/api/bookmarks/1").json()
    assert post_res["bookmarked"] is True
    assert any(str(item["id"]) == "1" for item in client.get("/api/bookmarks").json())
    del_res = client.delete("/api/bookmarks/1").json()
    assert del_res["bookmarked"] is False

def test_preferences_persist():
    assert client.put("/api/preferences/notifications", json={"enabled": True}).json()["notifications_enabled"] is True
    assert client.get("/api/preferences").json()["notifications_enabled"] is True
    client.put("/api/preferences/notifications", json={"enabled": False})

def test_report_and_analysis_run():
    report = client.get("/api/reports/test-narrative")
    assert report.status_code == 200 and "Public Conversation" in report.text
    run = client.post("/api/analysis/run", json={"topic_slug": "test-narrative"}).json()
    assert client.get(f"/api/analysis/runs/{run['run_id']}").status_code == 200

