from collections import Counter
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.collectors.adapters import COLLECTORS, get_collector
from app.models.database import CommentAnalysisRecord, IngestionJobRecord, SourceCommentRecord, TopicRecord, get_db
from app.models.schemas import CommentInput, CommentIntelligence, IngestionRequest, KafkaStatus
from app.services.ingestion import run_ingestion
from app.services.auto_ingestion import automation_status, run_auto_ingestion
from app.services.intelligence import CommentIntelligenceService, model_status
from app.services.kafka_stream import get_kafka_service

router = APIRouter(prefix="/api", tags=["social intelligence"])

@router.get("/connectors")
def connectors():
    descriptions = {
        "x": "Recent public Posts and replies via X API v2",
        "twitter": "Recent public Posts and replies via X API v2",
        "youtube": "Video comments and replies via YouTube Data API v3",
        "reddit": "Posts and comments on discovered or supplied Reddit discussions",
        "telegram": "Public broadcast channels and Bot updates via Telegram API",
        "facebook": "Comments on authorised Facebook Page posts",
        "instagram": "Comments on authorised professional-account media",
    }
    # Filter unique platform names
    seen = set()
    result = []
    for name in ("x", "reddit", "telegram", "youtube", "facebook", "instagram"):
        if name in seen:
            continue
        seen.add(name)
        collector = get_collector(name)
        result.append({
            "platform": name,
            "configured": collector.configured,
            "description": descriptions.get(name, "Platform connector"),
            "credential_fields": list(collector.required_environment),
            "discovery_supported": name in {"x", "reddit", "telegram", "youtube"},
            "requires_targets": name in {"facebook", "instagram"},
        })
    return result

@router.get("/kafka/status", response_model=KafkaStatus)
def kafka_status():
    """Returns real Kafka streaming layer connectivity and active topics (Section 4)."""
    return get_kafka_service().get_status()

@router.get("/models/status")
def models():
    return model_status()

@router.post("/classify", response_model=CommentIntelligence)
def classify(payload: CommentInput):
    return CommentIntelligenceService().analyse(payload)

@router.post("/classify/batch", response_model=list[CommentIntelligence])
def classify_batch(payload: list[CommentInput]):
    if len(payload) > 500:
        raise HTTPException(422, "Batch limit is 500 comments")
    service = CommentIntelligenceService()
    return [service.analyse(item) for item in payload]

@router.post("/ingestion/run")
async def ingest(payload: IngestionRequest, db: Session = Depends(get_db)):
    try:
        return await run_ingestion(db, payload)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@router.get("/ingestion/jobs")
def jobs(db: Session = Depends(get_db)):
    rows = db.scalars(select(IngestionJobRecord).order_by(IngestionJobRecord.started_at.desc()).limit(50)).all()
    return [
        {
            "job_id": r.id,
            "topic_slug": r.topic_slug,
            "platforms": json.loads(r.platforms_json),
            "query": r.query,
            "status": r.status,
            "results": json.loads(r.results_json),
            "errors": json.loads(r.error_json),
            "started_at": r.started_at,
            "completed_at": r.completed_at,
        }
        for r in rows
    ]

@router.get("/ingestion/automation/status")
def auto_status():
    return automation_status()

@router.post("/ingestion/automation/run-now")
async def auto_run():
    return await run_auto_ingestion()

@router.get("/comments")
def comments(
    topic_slug: str | None = None,
    platform: str | None = None,
    sentiment: str | None = None,
    stance: str | None = None,
    language: str | None = None,
    safety: str | None = None,
    sort: str = Query("recent", pattern="^(recent|influence)$"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = select(SourceCommentRecord, CommentAnalysisRecord).join(
        CommentAnalysisRecord, CommentAnalysisRecord.comment_id == SourceCommentRecord.id
    )
    if topic_slug:
        query = query.where(SourceCommentRecord.topic_slug == topic_slug)
    if platform:
        query = query.where(SourceCommentRecord.platform == platform)
    if sentiment:
        query = query.where(CommentAnalysisRecord.sentiment == sentiment)
    if stance:
        query = query.where(CommentAnalysisRecord.stance == stance)
    if language:
        query = query.where(CommentAnalysisRecord.language == language)
    if safety:
        query = query.where(CommentAnalysisRecord.safety == safety)

    order = CommentAnalysisRecord.influence_score.desc() if sort == "influence" else SourceCommentRecord.published_at.desc()
    rows = db.execute(query.order_by(order).limit(limit)).all()
    return [
        {
            "id": c.id,
            "platform": c.platform,
            "text": c.text,
            "published_at": c.published_at,
            "engagement": json.loads(c.engagement_json),
            "sentiment": a.sentiment,
            "sentiment_score": a.sentiment_score,
            "stance": a.stance,
            "safety": a.safety,
            "language": a.language,
            "interests": json.loads(a.interests_json),
            "geography": a.geography,
            "age_bracket": a.age_bracket,
            "influence_score": a.influence_score,
            "model": a.model_name,
            "inference": json.loads(a.inference_json),
        }
        for c, a in rows
    ]

@router.get("/comments/summary")
def comment_summary(topic_slug: str | None = None, db: Session = Depends(get_db)):
    query = select(SourceCommentRecord, CommentAnalysisRecord).join(
        CommentAnalysisRecord, CommentAnalysisRecord.comment_id == SourceCommentRecord.id
    )
    if topic_slug:
        query = query.where(SourceCommentRecord.topic_slug == topic_slug)
    rows = db.execute(query).all()

    def counts(fn):
        return dict(Counter(fn(c, a) for c, a in rows if fn(c, a)))

    interest_counter = Counter(x for _, a in rows for x in json.loads(a.interests_json))
    geography_coverage = sum(bool(a.geography) for _, a in rows)
    age_coverage = sum(bool(a.age_bracket) for _, a in rows)
    signals = Counter(json.loads(a.inference_json).get("signal_classification", "UNKNOWN") for _, a in rows)
    return {
        "topic_slug": topic_slug or "all_topics",
        "total": len(rows),
        "platforms": counts(lambda c, a: c.platform),
        "sentiment": counts(lambda c, a: a.sentiment),
        "stance": counts(lambda c, a: a.stance),
        "safety": counts(lambda c, a: a.safety),
        "languages": counts(lambda c, a: a.language),
        "geography": counts(lambda c, a: a.geography),
        "age_brackets": counts(lambda c, a: a.age_bracket),
        "interests": dict(interest_counter.most_common(20)),
        "signal_quality": dict(signals),
        "average_influence": round(sum(a.influence_score for _, a in rows) / len(rows), 2) if rows else 0,
        "coverage": {
            "geography": round(geography_coverage / len(rows), 3) if rows else 0,
            "age": round(age_coverage / len(rows), 3) if rows else 0,
        },
        "disclosure": "Geography and age are only included when supported by explicit public metadata; missing values are not guessed. Interest labels describe conversation themes, not verified personal attributes.",
    }
