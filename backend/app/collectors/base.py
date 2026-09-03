from abc import ABC, abstractmethod
from app.models.schemas import NormalizedContent, SocialMediaPost

class BaseCollector(ABC):
    """Common contract for policy-compliant platform adapters."""
    platform: str

    @abstractmethod
    async def fetch_posts(self, topic: str, limit: int = 100) -> list[dict]:
        """Fetch posts matching topic."""
        ...

    @abstractmethod
    async def fetch_comments(self, external_id: str, limit: int = 100) -> list[dict]:
        """Fetch comments for a given post/media external id."""
        ...

    @abstractmethod
    def normalize(self, raw: dict, topic_id: str) -> NormalizedContent:
        """Legacy normalization helper."""
        ...

    @abstractmethod
    def to_social_post(self, raw: dict) -> SocialMediaPost:
        """Normalize raw platform payload into common SocialMediaPost format."""
        ...
