import pytest
from app.services.bertopic_service import get_bertopic_service

def test_bertopic_and_c_tfidf():
    bertopic = get_bertopic_service()

    posts = [
        {"id": "1", "content": "Railway track safety and signaling system upgrades are required immediately.", "platform": "x"},
        {"id": "2", "content": "Train derailment concerns and track maintenance problems reported by engineers.", "platform": "reddit"},
        {"id": "3", "content": "Locomotive signaling failure and railway safety standards audit underway.", "platform": "telegram"},
        {"id": "4", "content": "Renewable solar energy generation sets record output across western power grids.", "platform": "x"},
        {"id": "5", "content": "Solar panel efficiency and clean energy grid transmission expansion.", "platform": "reddit"},
        {"id": "6", "content": "Green energy storage batteries and solar farm installations booming.", "platform": "youtube"},
    ]

    clusters = bertopic.fit_transform(posts)
    assert len(clusters) >= 2
    for c in clusters:
        assert c.topic_id > 0
        assert len(c.topic_label) > 3
        assert len(c.keywords) > 0
        assert "c_tfidf" in c.keywords[0]
        assert c.volume > 0
        assert c.representation_method == "c-TF-IDF"
