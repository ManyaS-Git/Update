from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get("/health").json()["status"]=="ok"
def test_topic():
    response=client.get("/api/topics/reservation-protest")
    assert response.status_code==200
    assert response.json()["total_conversations"]==52480
def test_missing_topic(): assert client.get("/api/topics/missing").status_code==404

def test_story_search_and_detail():
    stories=client.get("/api/stories").json()
    assert len(stories)>=12
    assert len({item["topic_slug"] for item in stories[:12]})>1
    assert client.get(f"/api/stories/{stories[0]['id']}").status_code==200
    assert client.get("/api/search?q=Supreme%20Court").json()["stories"]

def test_story_topics_do_not_reuse_reservation_metrics():
    story=next(item for item in client.get("/api/stories").json() if item["topic_slug"]=="student-community-food-drives")
    topic=client.get(f"/api/topics/{story['topic_slug']}").json()
    sentiment=client.get(f"/api/topics/{story['topic_slug']}/sentiment").json()
    assert topic["title"]==story["title"]
    assert topic["total_conversations"]==0
    assert sentiment["negative"]+sentiment["neutral"]+sentiment["positive"]==100
    assert sentiment!={"negative":55,"neutral":27,"positive":18,"change_last_6h":8,"qualified_conversations":28410}
    confidence=client.get(f"/api/topics/{story['topic_slug']}/confidence").json()
    assert confidence["sources"]==["Story metadata preview"]
    analyst=client.post("/api/ai/ask",json={"topic_slug":story["topic_slug"],"question":"Why is sentiment negative?"}).json()
    assert analyst["confidence"]=="Low"
    assert "No qualified comments" in analyst["answer"]

def test_bookmark_lifecycle():
    client.delete("/api/bookmarks/1")
    assert client.post("/api/bookmarks/1").json()["bookmarked"] is True
    assert any(item["id"]=="1" for item in client.get("/api/bookmarks").json())
    assert client.delete("/api/bookmarks/1").json()["bookmarked"] is False

def test_preferences_persist():
    assert client.put("/api/preferences/notifications",json={"enabled":True}).json()["notifications_enabled"] is True
    assert client.get("/api/preferences").json()["notifications_enabled"] is True
    client.put("/api/preferences/notifications",json={"enabled":False})

def test_report_and_analysis_run():
    report=client.get("/api/reports/reservation-protest")
    assert report.status_code==200 and "Public Conversation Brief" in report.text
    run=client.post("/api/analysis/run",json={"topic_slug":"reservation-protest"}).json()
    assert client.get(f"/api/analysis/runs/{run['run_id']}").status_code==200
