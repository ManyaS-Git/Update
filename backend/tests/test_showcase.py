from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_requested_stories_are_pinned_first():
    stories = client.get("/api/stories?limit=5").json()
    assert stories[0]["topic_slug"] == "maratha-reservation-protest-2026"
    assert stories[1]["topic_slug"] == "tukaram-mundhe-fda-testing-surge"
    assert "IAS Officer" in stories[1]["title"]


def test_normal_mode_never_serves_synthetic_showcase_analysis():
    for story in client.get("/api/stories?limit=100").json():
        slug = story["topic_slug"]
        confidence = client.get(f"/api/topics/{slug}/confidence").json()
        assert confidence.get("analysis_scope") != "pitch_demo"
        assert "pitch demo" not in confidence.get("metric_label", "")


def test_featured_stories_use_real_manual_public_samples():
    for slug in ("maratha-reservation-protest-2026", "tukaram-mundhe-fda-testing-surge"):
        topic = client.get(f"/api/topics/{slug}").json()
        audience = client.get(f"/api/topics/{slug}/audience").json()
        confidence = client.get(f"/api/topics/{slug}/confidence").json()
        voices = client.get(f"/api/topics/{slug}/voices").json()
        assert topic["total_conversations"] == 10
        assert confidence["analysis_scope"] == "public_conversation"
        assert confidence["sources"] == ["Reddit"]
        assert audience["age_bracket"]["confidence"] == "Unavailable"
        assert voices
