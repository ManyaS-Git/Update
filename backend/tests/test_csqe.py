from app.services.csqe import CSQEService

def test_contextless_phrase_is_low_signal():
    result=CSQEService().qualify("BINOD")
    assert result.classification=="LOW_SIGNAL"
    assert result.signal_quality < .2

def test_relevant_policy_opinion_is_high_signal():
    result=CSQEService().qualify("The reservation policy may hurt students and education opportunities.")
    assert result.classification=="HIGH_SIGNAL"
    assert result.signal_quality >= .7
