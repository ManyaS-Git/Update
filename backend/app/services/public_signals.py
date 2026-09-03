from __future__ import annotations

import json
import re
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database import StoryRecord, TopicRecord
from app.services.database import preview_analytics

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIMEDIA_PAGEVIEWS = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user"
USER_AGENT = "UPDATES-Intelligence/1.0 (public-signal research prototype)"
INDIAN_LOCATIONS = ("Mumbai", "Delhi", "New Delhi", "Maharashtra", "Uttar Pradesh", "Bihar", "Karnataka", "Kerala", "Tamil Nadu", "West Bengal", "Punjab", "Haryana", "Rajasthan", "Gujarat", "Hyderabad", "Bengaluru", "Chennai", "Kolkata", "Pune", "India")


def _get(client: httpx.Client, url: str, **kwargs) -> httpx.Response:
    for attempt in range(3):
        response = client.get(url, **kwargs)
        if response.status_code != 429:
            time.sleep(0.35)
            return response
        time.sleep(1.0 + attempt * 1.5)
    return response


def _search_terms(title: str) -> list[str]:
    clean = re.sub(r"\s+-\s+[^-]{2,40}$", "", title).strip()
    named = re.findall(r"(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,})){1,3}", clean)
    proper_words = re.findall(r"\b[A-Z][a-z]{2,}\b", clean)
    stop = {"Activist", "Latest", "Sets", "Reaches", "Out", "Protest", "Deadline", "News", "Live", "The"}
    name_pairs = [f"{left} {right}" for left, right in zip(proper_words, proper_words[1:]) if left not in stop and right not in stop]
    terms = name_pairs + named + [clean, " ".join(clean.split()[:6])]
    return list(dict.fromkeys(term for term in terms if len(term) >= 4))[:8]


def _wiki_pages(client: httpx.Client, title: str, limit: int = 3) -> list[str]:
    # One ranked search returns multiple candidates and avoids serially issuing
    # up to eight requests for every story in a large refresh backlog.
    clean = re.sub(r"\s+-\s+[^-]{2,40}$", "", title).strip()
    query = " ".join(clean.split()[:12])
    response = _get(client, WIKIPEDIA_API, params={"action": "query", "list": "search", "srsearch": query, "srlimit": limit, "format": "json"})
    response.raise_for_status()
    return list(dict.fromkeys(item["title"] for item in response.json().get("query", {}).get("search", [])))[:limit]


def _pageviews(client: httpx.Client, page: str, days: int = 30) -> tuple[int, list[dict]]:
    end = date.today() - timedelta(days=1); start = end - timedelta(days=days - 1)
    url = f"{WIKIMEDIA_PAGEVIEWS}/{quote(page.replace(' ', '_'), safe='')}/daily/{start:%Y%m%d}/{end:%Y%m%d}"
    response = _get(client, url)
    if response.status_code == 404:return 0, []
    response.raise_for_status();items = response.json().get("items", [])
    return sum(int(item.get("views", 0)) for item in items), items


def _geography(title: str) -> tuple[str, str]:
    matches = [place for place in INDIAN_LOCATIONS if re.search(rf"\b{re.escape(place)}\b", title, re.I)]
    return (matches[0], "High") if matches else ("India-wide / exact location not specified", "Low")


def enrich_public_signals(db: Session, topic_slug: str) -> dict:
    """Attach real attention signals without misrepresenting them as comments."""
    topic = db.get(TopicRecord, topic_slug)
    story = db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == topic_slug).order_by(StoryRecord.published_at.desc()))
    if not topic or not story:return {"status": "missing_topic", "signals": 0}
    with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        pages = _wiki_pages(client, story.title);page_rows = [];daily = Counter()
        for page in pages:
            views, items = _pageviews(client, page)
            if views:
                page_rows.append({"page": page, "views_30d": views})
                for item in items:daily[item.get("timestamp", "")[:8]] += int(item.get("views", 0))
    total = sum(item["views_30d"] for item in page_rows)
    analytics = preview_analytics(story.title, story.category, story.source_status.replace("news:", ""))
    geography, geo_confidence = _geography(story.title)
    analytics["audience"]["geography"] = {"value": geography, "confidence": geo_confidence, "coverage": 100 if geo_confidence == "High" else 0, "provenance": "Explicit place in headline" if geo_confidence == "High" else "Indian feed scope; exact audience location unavailable"}
    analytics["audience"]["age_bracket"] = {"value": "All ages · demographics not disclosed", "confidence": "Unavailable", "coverage": 0, "provenance": "Wikimedia aggregate pageviews do not expose age"}
    analytics["audience"]["leading_platform"] = "Wikipedia readership + indexed news coverage" if total else "Indexed news coverage"
    analytics["audience"]["confidence"]["platform"] = "High"
    analytics["audience"]["provenance"]["platform"] = "Wikimedia Pageviews API and indexed article metadata" if total else "Indexed article metadata"
    if daily:analytics["trends"] = [{"time": f"{day[6:8]}/{day[4:6]}", "volume": volume, "negative": analytics["sentiment"]["negative"]} for day, volume in sorted(daily.items())[-7:]]
    signal_total = total or 1
    sources = (["Wikimedia Pageviews API"] if total else []) + [story.source_status.replace("news:", "")]
    evidence = page_rows or [{"source": story.source_status.replace("news:", ""), "indexed_articles": 1}]
    analytics["confidence"] = {"level": "Medium" if total else "Low", "sources": sources, "qualified_conversations": 0, "qualified_public_signals": signal_total, "low_signal_excluded_or_downweighted": 0, "analysis_scope": "public_attention_signals", "metric_label": "public signals analysed", "disclaimer": "Counts are observed evidence signals. Wikimedia counts are pageviews—not unique people or social comments—and article records count as one indexed signal.", "evidence": evidence, "refreshed_at": datetime.now(timezone.utc).isoformat()}
    analytics["brief"]["insight"] = (f"Live public-attention analysis found {total:,} Wikimedia pageviews across {', '.join(item['page'] for item in page_rows)} in the last 30 days. " if total else "The news article is indexed, but no reliable matching Wikimedia readership series was found. ") + "Headline tone and themes are analysed separately; reader demographics and social stance are not claimed without evidence."
    analytics["brief"]["what_changed"] = "Public attention evidence collected from Wikimedia; social-comment collection remains credential-dependent."
    topic.total_conversations = signal_total;topic.subtitle = "Live public-attention & story-context analysis";topic.updated = "Live signals · 30-day evidence window";topic.is_demo = False;topic.analytics_json = json.dumps(analytics)
    db.commit();return {"status": "enriched", "signals": signal_total, "pages": page_rows}


def enrich_many_public_signals(db: Session, topic_slugs: list[str]) -> dict[str, dict]:
    results = {}
    for slug in topic_slugs:
        try:results[slug] = enrich_public_signals(db, slug)
        except (httpx.HTTPError, ValueError) as exc:results[slug] = {"status": "provider_unavailable", "signals": 0, "error": str(exc)}
    return results


def pending_public_signal_slugs(db: Session, limit: int = 12) -> list[str]:
    """Return newest story topics that have not yet completed public-signal enrichment."""
    rows = db.scalars(select(StoryRecord).order_by(StoryRecord.published_at.desc())).all()
    pending = [];seen = set()
    for story in rows:
        if story.topic_slug in seen:continue
        seen.add(story.topic_slug);topic = db.get(TopicRecord, story.topic_slug)
        if not topic:continue
        scope = topic.analytics.get("confidence", {}).get("analysis_scope")
        if scope not in {"public_attention_signals", "social_comments"}:
            pending.append(story.topic_slug)
        if len(pending) >= limit:break
    return pending


def due_public_signal_slugs(db: Session, refresh_minutes: int, limit: int = 100) -> list[str]:
    """Return every unseen or stale story topic, newest first."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(1, refresh_minutes))
    rows = db.scalars(select(StoryRecord).order_by(StoryRecord.published_at.desc())).all()
    due: list[str] = []; seen: set[str] = set()
    for story in rows:
        if story.topic_slug in seen:
            continue
        seen.add(story.topic_slug); topic = db.get(TopicRecord, story.topic_slug)
        if not topic:
            continue
        confidence = topic.analytics.get("confidence", {})
        refreshed_at = confidence.get("refreshed_at")
        try:
            refreshed = datetime.fromisoformat(refreshed_at.replace("Z", "+00:00")) if refreshed_at else None
            if refreshed and refreshed.tzinfo is None:
                refreshed = refreshed.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            refreshed = None
        if confidence.get("analysis_scope") not in {"public_attention_signals", "public_conversation"} or not refreshed or refreshed <= cutoff:
            due.append(story.topic_slug)
        if len(due) >= limit:
            break
    return due
