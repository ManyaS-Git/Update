import pytest
from app.services.sentimix_service import get_sentimix_service

def test_sentimix_classes_and_sarcasm():
    sentimix = get_sentimix_service()

    # 1. Positive social discourse
    pos_res = sentimix.predict("This infrastructure decision is excellent and truly beneficial for public transit.")
    assert pos_res.final_sentiment == "positive"
    assert pos_res.confidence >= 0.6
    assert not pos_res.is_sarcastic

    # 2. Negative social discourse
    neg_res = sentimix.predict("Total disaster and corruption in this contract, complete failure.")
    assert neg_res.final_sentiment == "negative"
    assert neg_res.confidence >= 0.6

    # 3. Sarcasm Polarity-Clash Augmentation (Praise + Negative Context Marker)
    sarcastic_res = sentimix.predict("Oh brilliant, amazing work ruining the whole transit grid again!")
    assert sarcastic_res.is_sarcastic is True
    # The Sarcasm layer should invert/correct final sentiment to negative
    assert sarcastic_res.final_sentiment == "negative"
    assert "Sarcasm detected" in sarcastic_res.sarcasm_explanation
