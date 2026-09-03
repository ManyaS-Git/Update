from __future__ import annotations
import re
from datetime import datetime, timezone
import httpx
from app.collectors.base import BaseCollector
from app.core.config import Settings, get_settings
from app.models.schemas import NormalizedContent, SocialMediaPost

class TelegramCollector(BaseCollector):
    platform = "telegram"

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.telegram_bot_token) or bool(self.settings.telegram_channels)

    @property
    def required_environment(self) -> tuple[str, ...]:
        return ("telegram_bot_token",)

    async def fetch_posts(self, topic: str, limit: int = 50) -> list[dict]:
        """Fetch posts from Telegram Bot API if configured or public channels."""
        posts = []
        # 1. If Bot Token is configured, attempt Telegram Bot API getUpdates
        if self.settings.telegram_bot_token:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/getUpdates",
                        params={"limit": min(100, limit)},
                    )
                    if resp.status_code == 200:
                        data = resp.json().get("result", [])
                        for item in data:
                            msg = item.get("message") or item.get("channel_post") or {}
                            text = msg.get("text") or msg.get("caption") or ""
                            if not text:
                                continue
                            if topic.lower() in text.lower() or topic == "*":
                                posts.append({
                                    "id": str(msg.get("message_id", item.get("update_id"))),
                                    "text": text,
                                    "author_id": str((msg.get("from") or msg.get("chat") or {}).get("id", "telegram_user")),
                                    "author_name": (msg.get("from") or {}).get("first_name") or (msg.get("chat") or {}).get("title") or "Telegram Channel",
                                    "created_at": datetime.fromtimestamp(msg.get("date", datetime.now().timestamp()), tz=timezone.utc).isoformat(),
                                    "views": 0,
                                    "forwards": 0,
                                    "channel": (msg.get("chat") or {}).get("username") or "telegram_channel",
                                    "metadata": {"via": "bot_api", "chat_type": (msg.get("chat") or {}).get("type", "channel")},
                                })
            except Exception:
                pass

        # 2. Also check configured public broadcast channels via web preview
        channels = [c.strip() for c in self.settings.telegram_channels.split(",") if c.strip()]
        for channel in channels[:3]:
            if len(posts) >= limit:
                break
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    resp = await client.get(f"https://t.me/s/{channel}")
                    if resp.status_code == 200:
                        channel_posts = self._parse_telegram_web(resp.text, channel, topic)
                        posts.extend(channel_posts)
            except Exception:
                continue

        return posts[:limit]

    def _parse_telegram_web(self, html: str, channel: str, query: str) -> list[dict]:
        """Extract public channel posts from Telegram public web preview."""
        posts = []
        # Pattern for telegram messages
        msg_blocks = re.findall(
            r'class="tgme_widget_message_wrap[^"]*"[\s\S]*?(?=class="tgme_widget_message_wrap|$)',
            html,
        )
        for block in msg_blocks:
            text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)</div>', block)
            if not text_match:
                continue
            raw_text = re.sub(r"<[^>]+>", " ", text_match.group(1)).strip()
            raw_text = re.sub(r"\s+", " ", raw_text)
            if not raw_text:
                continue
            if query and query != "*" and query.lower() not in raw_text.lower():
                continue

            id_match = re.search(r'data-post="([^"]+)"', block)
            post_id = id_match.group(1) if id_match else f"{channel}_{len(posts)}"

            time_match = re.search(r'<time datetime="([^"]+)"', block)
            created_at = time_match.group(1) if time_match else datetime.now(timezone.utc).isoformat()

            views_match = re.search(r'<span class="tgme_widget_message_views">([^<]+)</span>', block)
            views_str = views_match.group(1) if views_match else "0"
            views = 0
            if "K" in views_str:
                views = int(float(views_str.replace("K", "").strip()) * 1000)
            elif "M" in views_str:
                views = int(float(views_str.replace("M", "").strip()) * 1000000)
            elif views_str.isdigit():
                views = int(views_str)

            posts.append({
                "id": post_id,
                "text": raw_text,
                "author_id": channel,
                "author_name": f"@{channel}",
                "created_at": created_at,
                "views": views,
                "forwards": 0,
                "channel": channel,
                "metadata": {"via": "public_web", "channel": channel, "url": f"https://t.me/{post_id.replace('/', '/')}"},
            })
        return posts

    async def fetch_comments(self, external_id: str, limit: int = 50) -> list[dict]:
        return []

    def normalize(self, raw: dict, topic_id: str) -> NormalizedContent:
        created_at = raw.get("created_at")
        ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if isinstance(created_at, str) else datetime.now(timezone.utc)
        return NormalizedContent(
            platform="telegram",
            external_id=str(raw["id"]),
            topic_id=topic_id,
            author_id=raw.get("author_id"),
            author_name=raw.get("author_name"),
            text=raw.get("text", "").strip(),
            timestamp=ts,
            parent_id=raw.get("parent_id"),
            engagement={"views": raw.get("views", 0), "shares": raw.get("forwards", 0), "likes": 0, "replies": 0},
            public_profile_signals={"channel": raw.get("channel", "")},
            raw_metadata=raw.get("metadata", {}),
        )

    def to_social_post(self, raw: dict) -> SocialMediaPost:
        created_at = raw.get("created_at")
        ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if isinstance(created_at, str) else datetime.now(timezone.utc)
        content = raw.get("text", "").strip()
        hashtags = re.findall(r"#(\w+)", content)
        mentions = re.findall(r"@(\w+)", content)
        return SocialMediaPost(
            platform="telegram",
            post_id=str(raw["id"]),
            author_id=raw.get("author_id"),
            author_name=raw.get("author_name") or f"@{raw.get('channel', 'telegram')}",
            content=content,
            timestamp=ts,
            likes=0,
            comments=0,
            shares=raw.get("forwards", 0),
            views=raw.get("views", 0),
            hashtags=hashtags,
            mentions=mentions,
            url=raw.get("metadata", {}).get("url") or f"https://t.me/{raw.get('id')}",
            is_verified=False,
            metadata=raw.get("metadata", {}),
        )
