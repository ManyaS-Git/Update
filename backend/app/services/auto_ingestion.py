from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.collectors.adapters import COLLECTORS, get_collector
from app.core.config import get_settings
from app.models.database import SessionLocal, StoryRecord
from app.models.schemas import IngestionRequest
from app.services.ingestion import run_ingestion

_lock=asyncio.Lock()
_state={"status":"idle","last_started":None,"last_completed":None,"next_run":None,"topics_processed":0,"comments_stored":0,"errors":{}}


def configured_platforms()->list[str]:
    settings=get_settings();result=[]
    for name in settings.ingestion_platforms:
        if name not in COLLECTORS or not get_collector(name).configured:continue
        if name in {"facebook","instagram"} and not settings.target_ids(name):continue
        result.append(name)
    return result


def automation_status()->dict:
    settings=get_settings()
    return {**_state,"enabled":settings.auto_ingestion_enabled,"interval_minutes":settings.auto_ingestion_interval_minutes,"configured_platforms":configured_platforms(),"requested_platforms":settings.ingestion_platforms,"credential_setup_required":not bool(configured_platforms())}


async def run_auto_ingestion(max_topics:int|None=None)->dict:
    if _lock.locked():return {**automation_status(),"status":"already_running"}
    async with _lock:
        settings=get_settings();platforms=configured_platforms();_state.update(status="running",last_started=datetime.now(timezone.utc).isoformat(),topics_processed=0,comments_stored=0,errors={})
        if not platforms:
            with SessionLocal() as db:
                try:
                    from app.services.news import refresh_latest_news
                    res = refresh_latest_news(db, max_items=8)
                    _state.update(status="completed", last_completed=datetime.now(timezone.utc).isoformat(), topics_processed=res.get("added", 0))
                except Exception as e:
                    _state.update(status="blocked", last_completed=datetime.now(timezone.utc).isoformat(), errors={"credentials": f"No configured official social connectors; news refresh: {e}"})
            return automation_status()

        with SessionLocal() as db:
            limit=max_topics or settings.auto_ingestion_max_topics
            rows=db.scalars(select(StoryRecord).order_by(StoryRecord.published_at.desc()).limit(limit*3)).all();stories=[];seen=set()
            for row in rows:
                if row.topic_slug in seen:continue
                seen.add(row.topic_slug);stories.append(row)
                if len(stories)>=limit:break
            for story in stories:
                targets={platform:settings.target_ids(platform) for platform in platforms if settings.target_ids(platform)}
                payload=IngestionRequest(topic_slug=story.topic_slug,query=story.title,platforms=platforms,targets=targets,max_items=settings.auto_ingestion_max_items_per_platform)
                result=await run_ingestion(db,payload);stored=sum(item.get("stored",0) for item in result.get("results",{}).values());_state["comments_stored"]+=stored;_state["topics_processed"]+=1
                if result.get("errors"):_state["errors"][story.topic_slug]=result["errors"]
        _state.update(status="completed",last_completed=datetime.now(timezone.utc).isoformat())
        return automation_status()


async def auto_ingestion_loop() -> None:
    settings = get_settings()
    # Initial pause so startup and test initialization complete without blocking
    await asyncio.sleep(max(10, settings.auto_ingestion_interval_minutes * 60))
    while True:
        await run_auto_ingestion()
        await asyncio.sleep(max(60, settings.auto_ingestion_interval_minutes * 60))

