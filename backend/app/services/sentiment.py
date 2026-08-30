from typing import Protocol
from app.models.schemas import SentimentAnalysis

class SentimentProvider(Protocol):
    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis: ...

class HeuristicMultilingualProvider:
    supportive = {"support","important","equal opportunity","representation","zaroori","samarthan"}
    opposing = {"unfair","compromised","against","hurt","concern","galat","nuksan"}
    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis:
        lowered = f"{context or ''} {text}".lower()
        positive = sum(term in lowered for term in self.supportive)
        negative = sum(term in lowered for term in self.opposing)
        language = "hinglish" if any(term in lowered for term in ("hai","nahi","galat","zaroori")) else "english"
        if negative > positive: sentiment,stance,emotion="negative","opposing","concern"
        elif positive > negative: sentiment,stance,emotion="positive","supportive","support"
        elif "?" in text: sentiment,stance,emotion="neutral","questioning","questioning"
        else: sentiment,stance,emotion="neutral","neutral","uncertain"
        return SentimentAnalysis(sentiment=sentiment,stance=stance,emotion=emotion,confidence=.78 if positive != negative else .62,language=language,context_used=bool(context))

class SentimentService:
    """Replace provider with a fine-tuned MuRIL-compatible classifier later."""
    def __init__(self, provider: SentimentProvider | None = None): self.provider = provider or HeuristicMultilingualProvider()
    def analyse(self, text: str, context: str | None = None) -> SentimentAnalysis: return self.provider.analyse(text, context)
    def analyse_batch(self, texts: list[str]) -> list[SentimentAnalysis]: return [self.analyse(text) for text in texts]
