from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.collectors.adapters import COLLECTORS, get_collector
from app.core.config import get_settings
from app.models.database import SessionLocal, StoryRecord
from app.models.schemas import IngestionRequest
from app.services.ingestion import run_ingestion

_lock=asyncio.Lock()
_state={"status":"idle","last_started":None,"last_completed":None,"next_run":None,"stories_discovered":0,"topics_queued":0,"topics_processed":0,"topics_failed":0,"comments_stored":0,"errors":{}}


def _schedule_next(minutes:int)->None:
    _state["next_run"]=(datetime.now(timezone.utc)+timedelta(minutes=max(1,minutes))).isoformat()


def configured_platforms()->list[str]:
    settings=get_settings();result=[]
    for name in settings.ingestion_platforms:
        if name not in COLLECTORS or not get_collector(name).configured:continue
        if name in {"facebook","instagram"} and not settings.target_ids(name):continue
        result.append(name)
    return result


def automation_status()->dict:
    settings=get_settings()
    return {**_state,"enabled":settings.auto_news_refresh_enabled,"interval_minutes":settings.analysis_refresh_interval_minutes,"news_refresh_interval_minutes":settings.auto_news_refresh_interval_minutes,"social_ingestion_enabled":settings.auto_ingestion_enabled,"configured_platforms":configured_platforms(),"requested_platforms":settings.ingestion_platforms,"credential_setup_required":not bool(configured_platforms())}


async def run_auto_ingestion(max_topics:int|None=None)->dict:
    if _lock.locked():return {**automation_status(),"status":"already_running"}
    async with _lock:
        settings=get_settings();platforms=configured_platforms();_state.update(status="running",last_started=datetime.now(timezone.utc).isoformat(),topics_processed=0,comments_stored=0,errors={})
        if not platforms:
            _state.update(status="blocked",last_completed=datetime.now(timezone.utc).isoformat(),errors={"credentials":"No configured official social connectors"})
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


async def enrich_topics(topic_slugs:list[str])->dict:
    """Immediately enrich newly indexed stories with every configured official connector."""
    if not topic_slugs:return {**automation_status(),"status":"nothing_new"}
    async with _lock:
        from app.services.public_signals import enrich_public_signals
        def collect_public_signals():
            def enrich_one(slug:str)->tuple[str,dict]:
                try:
                    with SessionLocal() as signal_db:return slug,enrich_public_signals(signal_db,slug)
                except Exception as exc:return slug,{"status":"provider_unavailable","signals":0,"error":str(exc)}
            results={}
            with ThreadPoolExecutor(max_workers=max(1,min(settings.public_signal_workers,len(topic_slugs)))) as pool:
                futures=[pool.submit(enrich_one,slug) for slug in topic_slugs]
                for future in as_completed(futures):
                    slug,value=future.result();results[slug]=value
            return results
        settings=get_settings()
        public_signal_results=await asyncio.to_thread(collect_public_signals)
        platforms=configured_platforms();_state.update(status="running",topics_processed=0,comments_stored=0)
        if not platforms:
            enriched=sum(1 for value in public_signal_results.values() if value.get("status")=="enriched")
            failed=len(public_signal_results)-enriched
            _state.update(status="partial" if failed else "completed",last_completed=datetime.now(timezone.utc).isoformat(),topics_processed=enriched,topics_failed=failed,errors={"social_credentials":"Public attention signals are live; social comments need at least one official connector"})
            return {**automation_status(),"public_signals":public_signal_results}
        with SessionLocal() as db:
            stories=db.scalars(select(StoryRecord).where(StoryRecord.topic_slug.in_(topic_slugs)).order_by(StoryRecord.published_at.desc())).all();seen=set()
            for story in stories:
                if story.topic_slug in seen:continue
                seen.add(story.topic_slug);targets={platform:settings.target_ids(platform) for platform in platforms if settings.target_ids(platform)};payload=IngestionRequest(topic_slug=story.topic_slug,query=story.title,platforms=platforms,targets=targets,max_items=settings.auto_ingestion_max_items_per_platform)
                result=await run_ingestion(db,payload);_state["comments_stored"]+=sum(item.get("stored",0) for item in result.get("results",{}).values());_state["topics_processed"]+=1
                if result.get("errors"):_state["errors"][story.topic_slug]=result["errors"]
        _state.update(status="completed",last_completed=datetime.now(timezone.utc).isoformat())
        return {**automation_status(),"public_signals":public_signal_results}


async def run_news_analysis_cycle()->dict:
    """Discover latest news, catch up stale stories, and enrich every queued topic."""
    from app.services.news import refresh_latest_news
    from app.services.public_signals import due_public_signal_slugs
    settings=get_settings();topic_slugs=[]
    _state.update(status="discovering",last_started=datetime.now(timezone.utc).isoformat(),stories_discovered=0,topics_queued=0,topics_processed=0,topics_failed=0,comments_stored=0,errors={})
    try:
        def refresh()->tuple[dict,list[str]]:
            with SessionLocal() as db:
                result=refresh_latest_news(db,max_items=settings.auto_news_refresh_max_items)
                due=due_public_signal_slugs(db,settings.analysis_refresh_interval_minutes,settings.public_signal_batch_size)
                return result,list(dict.fromkeys(result.get("added_topic_slugs",[])+due))
        result,topic_slugs=await asyncio.to_thread(refresh)
        _state.update(stories_discovered=result.get("added",0),topics_queued=len(topic_slugs))
        enrichment=await enrich_topics(topic_slugs)
        return {**automation_status(),"news":result,"enrichment":enrichment}
    except Exception as exc:
        _state["errors"]["news_refresh"]=str(exc);_state["status"]="partial" if topic_slugs else "failed"
        return automation_status()
    finally:
        _state["last_completed"]=datetime.now(timezone.utc).isoformat();_schedule_next(settings.analysis_refresh_interval_minutes)


async def auto_ingestion_loop()->None:
    settings=get_settings()
    while True:
        await run_auto_ingestion()
        await asyncio.sleep(max(60,settings.auto_ingestion_interval_minutes*60))


async def news_pipeline_loop()->None:
    """Discover news and refresh every due story without requiring a browser."""
    settings=get_settings();await asyncio.sleep(2)
    # Discover frequently; due_public_signal_slugs still limits full evidence
    # re-analysis to analysis_refresh_interval_minutes (two hours by default).
    interval=max(60,settings.auto_news_refresh_interval_minutes*60)
    while True:
        await run_news_analysis_cycle()
        await asyncio.sleep(interval)
