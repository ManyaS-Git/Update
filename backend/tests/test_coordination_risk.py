import pytest
from datetime import datetime, timezone, timedelta
from app.services.coordination_detection import get_coordination_service
from app.services.cross_platform_propagation import get_propagation_service
from app.services.risk_monitor import get_risk_monitor

def test_coordination_detection():
    coord_svc = get_coordination_service()

    # Create near-duplicate posts across different accounts
    posts = [
        {"author_name": "bot_a", "content": "The administration must cancel this decree right now #CancelDecreeNow #Strike"},
        {"author_name": "bot_b", "content": "The administration must cancel this decree right now #CancelDecreeNow #Strike"},
        {"author_name": "bot_c", "content": "The administration must cancel this decree right now #CancelDecreeNow #Strike"},
        {"author_name": "citizen_real", "content": "I am studying the decree details to understand its legal implications."},
    ]

    res = coord_svc.detect_coordination(posts)
    assert res.overall_coordination_risk >= 50.0
    assert len(res.clusters_detected) > 0
    assert res.clusters_detected[0].pattern_type in ("near_duplicate_text", "hashtag_coordination")

def test_cross_platform_propagation():
    prop_svc = get_propagation_service()
    base_time = datetime.now(timezone.utc)

    posts = [
        {"platform": "x", "published_at": base_time, "likes": 120, "shares": 45, "comments": 20},
        {"platform": "reddit", "published_at": base_time + timedelta(minutes=28), "likes": 80, "shares": 10, "comments": 65},
        {"platform": "youtube", "published_at": base_time + timedelta(minutes=72), "likes": 400, "shares": 30, "comments": 110},
    ]

    res = prop_svc.analyze_propagation(posts)
    assert res.origin_platform == "x"
    assert res.has_sufficient_timeline_evidence is True
    assert len(res.steps) == 3
    assert res.steps[1].delay_minutes == 28

def test_risk_monitor():
    risk_svc = get_risk_monitor()

    res = risk_svc.evaluate_risk(
        topic_slug="rail-derailment",
        topic_title="Railway Track Safety",
        negative_sentiment_pct=64.0,
        sentiment_shift_6h=18.0,
        momentum_score=82.0,
        coordination_risk=70.0,
        platforms=["x", "reddit", "telegram", "youtube"],
        volume=150,
    )

    assert res.level == "CRITICAL"
    assert res.risk_score >= 80.0
    assert len(res.evidence) >= 3
