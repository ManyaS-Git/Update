from typing import Protocol
from app.models.schemas import AIResponse

class AIProvider(Protocol):
    def answer(self, question: str) -> AIResponse: ...

class MockAIProvider:
    def answer(self, question: str) -> AIResponse:
        lowered=question.lower()
        if "hour" in lowered or "changed" in lowered:
            answer="Conversation volume rose 18% and opposing sentiment increased by 8 percentage points in the last 6 hours. Education & Admissions is rising fastest."
        elif "platform" in lowered:
            answer="X is the largest observed source in the seeded dataset, with YouTube and Telegram contributing additional qualified discussion."
        elif "active" in lowered or "audience" in lowered:
            answer="Student communities and job aspirants are the most active inferred interest groups. The likely dominant age bracket is 18–24, with medium confidence."
        else:
            answer="The protest is gaining attention because fairness, access to education and employment implications are converging across student and policy-discussion communities."
        return AIResponse(answer=answer,evidence=["28,410 qualified conversations","6,281 low-signal items excluded or down-weighted","X, YouTube, Telegram and Reddit demo sources"],confidence="High",last_updated="2 min ago",provider="mock")

class AIAnalystService:
    def __init__(self, provider: AIProvider | None = None): self.provider=provider or MockAIProvider()
    def ask(self, question: str) -> AIResponse: return self.provider.answer(question)
