from datetime import datetime, timezone
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.database import AnalysisRunRecord, TopicRecord, get_db
from app.models.schemas import AIQuestion, AIResponse, AnalysisRequest, AnalysisRunResponse
router=APIRouter(prefix="/api",tags=["analysis"])

@router.post("/ai/ask",response_model=AIResponse)
def ask(payload: AIQuestion,db:Session=Depends(get_db)):
    topic=db.get(TopicRecord,payload.topic_slug)
    if not topic: raise HTTPException(404,"Topic not found")
    if topic.total_conversations<=0:
        return AIResponse(answer=f"No qualified comments have been collected for {topic.title} yet. Run collection for this story before asking for sentiment, audience or trend conclusions.",evidence=["0 qualified comments for this topic","No cross-topic fallback was used"],confidence="Low",last_updated=topic.updated,provider="topic-scoped")
    analytics=topic.analytics;sentiment=analytics.get("sentiment",{});audience=analytics.get("audience",{});drivers=analytics.get("drivers",[]);negative=sentiment.get("negative",0);neutral=sentiment.get("neutral",0);positive=sentiment.get("positive",0);top_driver=drivers[0].get("title") if drivers else "No dominant narrative established";platform=audience.get("leading_platform") or "multiple collected sources"
    answer=f"For {topic.title}, {topic.total_conversations:,} qualified comments currently measure {negative}% opposing, {neutral}% neutral and {positive}% supportive. The leading observed source is {platform}; the strongest available narrative is {top_driver}."
    return AIResponse(answer=answer,evidence=[f"{topic.total_conversations:,} comments attached only to {topic.slug}",f"Topic analytics updated {topic.updated}"],confidence=analytics.get("confidence",{}).get("level","Medium") if analytics.get("confidence",{}).get("level") in {"Low","Medium","High"} else "Medium",last_updated=topic.updated,provider="topic-scoped")

@router.post("/analysis/run",response_model=AnalysisRunResponse)
def run(payload: AnalysisRequest,db:Session=Depends(get_db)):
    if not db.get(TopicRecord,payload.topic_slug): raise HTTPException(404,"Topic not found")
    settings=get_settings()
    result=AnalysisRunRecord(id=str(uuid4()),topic_slug=payload.topic_slug,status="completed" if settings.demo_mode else "queued",mode="demo" if settings.demo_mode else "configured_collectors",metrics_json=json.dumps({"records_processed":52480 if settings.demo_mode else 0}),completed_at=datetime.now(timezone.utc) if settings.demo_mode else None)
    db.add(result);db.commit()
    return AnalysisRunResponse(run_id=result.id,topic_slug=result.topic_slug,status=result.status,mode=result.mode)

@router.get("/analysis/runs")
def runs(db:Session=Depends(get_db)):
    rows=db.scalars(select(AnalysisRunRecord).order_by(AnalysisRunRecord.started_at.desc()).limit(50)).all()
    return [{"run_id":r.id,"topic_slug":r.topic_slug,"status":r.status,"mode":r.mode,"started_at":r.started_at,"completed_at":r.completed_at,"metrics":json.loads(r.metrics_json)} for r in rows]

@router.get("/analysis/runs/{run_id}")
def run_status(run_id:str,db:Session=Depends(get_db)):
    r=db.get(AnalysisRunRecord,run_id)
    if not r: raise HTTPException(404,"Analysis run not found")
    return {"run_id":r.id,"topic_slug":r.topic_slug,"status":r.status,"mode":r.mode,"started_at":r.started_at,"completed_at":r.completed_at,"metrics":json.loads(r.metrics_json)}
