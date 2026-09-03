from datetime import datetime, timezone
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.database import AnalysisRunRecord, TopicRecord, get_db
from app.models.schemas import AIQuestion, AIResponse, AnalysisRequest, AnalysisRunResponse
from app.services.rag_analyst import ask_rag_analyst
from app.services.ingestion import refresh_topic_analytics

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/ai/ask", response_model=AIResponse)
def ask(payload: AIQuestion, db: Session = Depends(get_db)):
    """Evidence-grounded RAG Chatbot (Section 18)."""
    return ask_rag_analyst(db, payload.topic_slug, payload.question)

@router.post("/analysis/run", response_model=AnalysisRunResponse)
def run(payload: AnalysisRequest, db: Session = Depends(get_db)):
    topic = db.get(TopicRecord, payload.topic_slug)
    if not topic:
        raise HTTPException(404, "Topic not found")

    refresh_topic_analytics(db, payload.topic_slug)
    db.refresh(topic)

    result = AnalysisRunRecord(
        id=str(uuid4()),
        topic_slug=payload.topic_slug,
        status="completed",
        mode="pipeline_executed",
        metrics_json=json.dumps({"records_processed": topic.total_conversations}),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(result)
    db.commit()
    return AnalysisRunResponse(run_id=result.id, topic_slug=result.topic_slug, status=result.status, mode=result.mode)

@router.get("/analysis/runs")
def runs(db: Session = Depends(get_db)):
    rows = db.scalars(select(AnalysisRunRecord).order_by(AnalysisRunRecord.started_at.desc()).limit(50)).all()
    return [
        {
            "run_id": r.id,
            "topic_slug": r.topic_slug,
            "status": r.status,
            "mode": r.mode,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "metrics": json.loads(r.metrics_json),
        }
        for r in rows
    ]

@router.get("/analysis/runs/{run_id}")
def run_status(run_id: str, db: Session = Depends(get_db)):
    r = db.get(AnalysisRunRecord, run_id)
    if not r:
        raise HTTPException(404, "Analysis run not found")
    return {
        "run_id": r.id,
        "topic_slug": r.topic_slug,
        "status": r.status,
        "mode": r.mode,
        "started_at": r.started_at,
        "completed_at": r.completed_at,
        "metrics": json.loads(r.metrics_json),
    }
