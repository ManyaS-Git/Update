from app.services.sentiment import SentimentService
def test_sentiment_response_structure():
    result=SentimentService().analyse("This policy may hurt students",context="Reservation discussion")
    assert result.sentiment=="negative"
    assert result.context_used is True
    assert 0 <= result.confidence <= 1
