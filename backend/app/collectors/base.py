from abc import ABC, abstractmethod
from app.models.schemas import NormalizedContent

class BaseCollector(ABC):
    """Common contract for policy-compliant platform adapters."""
    platform: str
    @abstractmethod
    async def fetch_posts(self, topic: str, limit: int = 100) -> list[dict]: ...
    @abstractmethod
    async def fetch_comments(self, external_id: str, limit: int = 100) -> list[dict]: ...
    @abstractmethod
    def normalize(self, raw: dict, topic_id: str) -> NormalizedContent: ...
