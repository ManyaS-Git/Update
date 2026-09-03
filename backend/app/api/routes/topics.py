from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.database import StoryRecord, TopicRecord, get_db
router=APIRouter(prefix="/api/topics",tags=["topics"])

def ensure(slug: str,db:Session)->TopicRecord:
    topic=db.get(TopicRecord,slug)
    if not topic: raise HTTPException(404,"Topic not found")
    return topic

@router.get("")
def topics(db:Session=Depends(get_db)):
    return [{"slug":item.slug,"title":item.title,"subtitle":item.subtitle,"total_conversations":item.total_conversations,"updated":item.updated,"demo":item.is_demo} for item in db.scalars(select(TopicRecord)).all()]
@router.get("/{slug}")
def topic(slug: str,db:Session=Depends(get_db)):
    item=ensure(slug,db);story=db.scalar(select(StoryRecord).where(StoryRecord.topic_slug==slug).order_by(StoryRecord.published_at.desc()));return {"slug":item.slug,"title":item.title,"subtitle":item.subtitle,"total_conversations":item.total_conversations,"updated":item.updated,"demo":item.is_demo,"image":story.image if story else "/images/real-data-check.jpg","category":story.category if story else "Analysis"}
@router.get("/{slug}/sentiment")
def sentiment(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["sentiment"]
@router.get("/{slug}/audience")
def audience(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["audience"]
@router.get("/{slug}/trends")
def trends(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["trends"]
@router.get("/{slug}/drivers")
def drivers(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["drivers"]
@router.get("/{slug}/voices")
def voices(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["voices"]
@router.get("/{slug}/network")
def network(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["network"]
@router.get("/{slug}/confidence")
def confidence(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["confidence"]
@router.get("/{slug}/brief")
def brief(slug: str,db:Session=Depends(get_db)): return ensure(slug,db).analytics["brief"]
