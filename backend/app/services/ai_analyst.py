from __future__ import annotations
from typing import Protocol
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.schemas import AIResponse
from app.services.rag_analyst import ask_rag_analyst

class AIProvider(Protocol):
    def answer(self, question: str, topic_slug: str = "general") -> AIResponse: ...

class GroundedRAGProvider:
    def answer(self, question: str, topic_slug: str = "general") -> AIResponse:
        with SessionLocal() as db:
            return ask_rag_analyst(db, topic_slug, question)

class AIAnalystService:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or GroundedRAGProvider()

    def ask(self, question: str, topic_slug: str = "general") -> AIResponse:
        return self.provider.answer(question, topic_slug=topic_slug)
