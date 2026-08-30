from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database import StoryRecord, TopicRecord
from app.services.database import preview_analytics

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
DEFAULT_QUERY = '(protest OR policy OR education OR economy OR court) sourcecountry:india'


def _slug(title: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:94]
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
    return f"{stem}-{digest}"


def _published(value: str | None) -> datetime:
    if value:
        compact = re.sub(r"[^0-9]", "", value)
        for pattern, length in (("%Y%m%d%H%M%S", 14), ("%Y%m%d%H%M", 12)):
            try:
                return datetime.strptime(compact[:length], pattern).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return datetime.now(timezone.utc)


def _category(title: str) -> str:
    text = title.lower()
    if any(word in text for word in ("court", "law", "legal", "bill")): return "Laws"
    if any(word in text for word in ("school", "student", "university", "education")): return "Education"
    if any(word in text for word in ("climate", "environment", "pollution")): return "Environment"
    if any(word in text for word in ("economy", "market", "jobs", "employment")): return "Analysis"
    if any(word in text for word in ("protest", "rally", "demonstration", "strike")): return "Protest"
    return "India"


def _fallback_image(category: str) -> str:
    return {"Laws":"/images/real-supreme-court.jpg","Education":"/images/real-campus.jpg","Protest":"/images/real-city-protest.jpg","Analysis":"/images/real-data-check.jpg"}.get(category,"/images/real-protest.jpg")


def _fetch_gdelt(query: str, max_items: int) -> tuple[str,list[dict]]:
    with httpx.Client(timeout=12, follow_redirects=True) as client:
        response = client.get(GDELT_DOC_API, params={"query":query,"mode":"artlist","format":"json","sort":"datedesc","timespan":"48h","maxrecords":max_items})
        response.raise_for_status()
        return "GDELT DOC 2.0", response.json().get("articles", [])


def _fetch_rss(query: str, max_items: int) -> tuple[str,list[dict]]:
    # Availability fallback for the local prototype; GDELT remains the primary provider.
    with httpx.Client(timeout=12, follow_redirects=True) as client:
        response=client.get(GOOGLE_NEWS_RSS,params={"q":query.replace("sourcecountry:india","India"),"hl":"en-IN","gl":"IN","ceid":"IN:en"})
        response.raise_for_status()
    root=ElementTree.fromstring(response.content)
    articles=[]
    for item in root.findall("./channel/item")[:max_items]:
        title=(item.findtext("title") or "").strip();source=item.find("source")
        try: seen=parsedate_to_datetime(item.findtext("pubDate") or "").astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        except (TypeError,ValueError): seen=""
        articles.append({"title":title,"domain":source.text.strip() if source is not None and source.text else "Google News indexed source","seendate":seen,"socialimage":""})
    return "Google News RSS fallback",articles


def refresh_latest_news(db: Session, query: str = DEFAULT_QUERY, max_items: int = 12) -> dict:
    """Import recent article metadata. Analytics remain empty until comments are collected."""
    try: provider,articles=_fetch_gdelt(query,max_items)
    except (httpx.HTTPError,ValueError): provider,articles=_fetch_rss(query,max_items)

    existing_titles = set(db.scalars(select(StoryRecord.title)).all())
    added = 0
    for article in articles:
        title = (article.get("title") or "").strip()
        if len(title) < 8 or title in existing_titles:
            continue
        slug = _slug(title)
        if not db.get(TopicRecord, slug):
            db.add(TopicRecord(
                slug=slug, title=title, subtitle="Public sentiment & conversation analysis",
                total_conversations=0, updated="Preview · awaiting comments", is_demo=True,
                analytics_json=json.dumps(preview_analytics(title,_category(title))),
            ))
            db.flush()
        domain = (article.get("domain") or "GDELT indexed source").strip()
        category=_category(title);image = (article.get("socialimage") or _fallback_image(category)).strip()
        if not image.startswith(("https://", "http://", "/")):
            image = "/images/real-data-check.jpg"
        db.add(StoryRecord(
            title=title, category=category, relative_time="Just now", image=image,
            is_live=False, topic_slug=slug,
            summary=f"Recent coverage indexed from {domain}. Select this story to collect its comments and build story-specific intelligence.",
            source_status=f"news:{domain}"[:80], published_at=_published(article.get("seendate")),
        ))
        existing_titles.add(title)
        added += 1
    db.commit()
    return {"provider":provider,"received":len(articles),"added":added,"query":query}
