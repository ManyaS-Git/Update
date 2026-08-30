from app.services.trends import TrendService
def test_fast_rising_trend():
    result=TrendService().calculate([100,120,160])
    assert result["label"]=="FAST_RISING"
    assert result["growth"] > 0
