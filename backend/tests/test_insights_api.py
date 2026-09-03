import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, TopicRecord, NarrativeRecord, PostRecord

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def seed_test_data():
    with SessionLocal() as db:
        if not db.get(TopicRecord, "test-ai-narrative"):
            db.add(TopicRecord(
                slug="test-ai-narrative",
                title="AI & Semiconductor Policy",
                subtitle="Public debate regarding hardware manufacturing incentives",
                total_conversations=30,
            ))
            db.add(NarrativeRecord(
                slug="test-ai-narrative",
                title="AI & Semiconductor Policy",
                category="Science & Tech",
                status="EMERGING",
                momentum_score=72.0,
                velocity=18.5,
                sentiment_negative=42,
                sentiment_neutral=38,
                sentiment_positive=20,
                sentiment_change_6h=12,
                total_conversations=30,
            ))
            db.commit()

def test_insights_api_endpoints(client):
    # 1. Prioritized Insights
    res = client.get("/api/insights")
    assert res.status_code == 200
    cards = res.json()
    assert isinstance(cards, list)
    if cards:
        assert "priority_score" in cards[0]
        assert "confidence" in cards[0]
        assert "evidence" in cards[0]

    # 2. Executive Summary KPIs
    res = client.get("/api/insights/summary")
    assert res.status_code == 200
    summary = res.json()
    assert "total_posts" in summary
    assert "active_narratives" in summary

    # 3. Model Transparency
    res = client.get("/api/insights/models")
    assert res.status_code == 200
    models_data = res.json()
    assert "pipeline" in models_data
    model_names = [m["model"] for m in models_data["pipeline"]]
    assert "MuRIL" in model_names
    assert "SentiMix" in model_names
    assert "BERTopic" in model_names
    assert "c-TF-IDF" in model_names
    assert "NetworkX" in model_names
    assert "PageRank" in model_names
    assert "Node2Vec" in model_names
    assert "GraphSAGE" in model_names

    # 4. Intelligence Brief
    res = client.get("/api/intelligence-brief?topic_slug=test-ai-narrative")
    assert res.status_code == 200
    brief = res.json()
    assert "executive_summary" in brief
    assert "emerging_narratives" in brief
    assert "sentiment_overview" in brief
    assert "analyst_assessment" in brief

    # 5. RAG Analyst Query
    res = client.post("/api/analyst/query", json={
        "question": "What is the fastest-growing narrative right now?",
        "topic_slug": "global"
    })
    assert res.status_code == 200
    ans = res.json()
    assert "answer" in ans
    assert "evidence" in ans
