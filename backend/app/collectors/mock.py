from datetime import datetime, timezone
from app.collectors.base import BaseCollector
from app.models.schemas import NormalizedContent

class MockCollector(BaseCollector):
    platform = "mock"
    async def fetch_posts(self, topic: str, limit: int = 100) -> list[dict]:
        return [{"id":"demo-1","text":"The policy needs a fair and transparent implementation.","created_at":datetime.now(timezone.utc).isoformat()}]
    async def fetch_comments(self, external_id: str, limit: int = 100) -> list[dict]:
        return []
    def normalize(self, raw: dict, topic_id: str) -> NormalizedContent:
        return NormalizedContent(platform=self.platform,external_id=raw["id"],topic_id=topic_id,text=raw["text"],timestamp=raw["created_at"])
