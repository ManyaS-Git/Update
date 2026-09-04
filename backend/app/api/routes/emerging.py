from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.emerging import emerging_snapshot

router = APIRouter(prefix="/api/emerging", tags=["emerging topics"])


@router.get("")
def emerging_topics(
    recent_hours: int = Query(12, ge=3, le=48),
    baseline_hours: int = Query(36, ge=12, le=168),
    limit: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
):
    return emerging_snapshot(db, recent_hours, baseline_hours, limit)
