from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.database import NarrativeRecord, StoryRecord, TopicRecord, get_db
from app.services.database import empty_analytics

router = APIRouter(prefix="/api/topics", tags=["topics"])

def ensure(slug: str, db: Session) -> TopicRecord:
    topic = db.get(TopicRecord, slug)
    if not topic:
        # Check if a narrative or story exists with this slug
        narrative = db.get(NarrativeRecord, slug)
        story = db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == slug))
        if narrative or story:
            title = narrative.title if narrative else story.title
            topic = TopicRecord(
                slug=slug,
                title=title,
                subtitle="Public sentiment & conversation analysis",
                total_conversations=narrative.total_conversations if narrative else 0,
                updated="Live",
                is_demo=False,
                analytics_json="{}",
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)
        else:
            raise HTTPException(404, "Topic not found")
    return topic

def get_topic_analytics(topic: TopicRecord) -> dict:
    analytics = topic.analytics
    if not analytics or not analytics.get("sentiment"):
        analytics = empty_analytics(topic.title)
    return analytics

@router.get("")
def topics(db: Session = Depends(get_db)):
    rows = db.scalars(select(TopicRecord).order_by(TopicRecord.total_conversations.desc(), TopicRecord.created_at.desc())).all()
    return [
        {
            "slug": item.slug,
            "title": item.title,
            "subtitle": item.subtitle,
            "total_conversations": item.total_conversations,
            "updated": item.updated,
            "demo": item.is_demo,
        }
        for item in rows
    ]

@router.get("/narratives")
def narratives(db: Session = Depends(get_db)):
    rows = db.scalars(select(NarrativeRecord).order_by(NarrativeRecord.is_emerging.desc(), NarrativeRecord.momentum_score.desc())).all()
    return [
        {
            "slug": n.slug,
            "title": n.title,
            "category": n.category,
            "status": n.status,
            "is_emerging": n.is_emerging,
            "momentum_score": n.momentum_score,
            "velocity": n.velocity,
            "growth_rate": n.growth_rate,
            "total_conversations": n.total_conversations,
            "sentiment": {
                "negative": n.sentiment_negative,
                "neutral": n.sentiment_neutral,
                "positive": n.sentiment_positive,
            },
            "sentiment_change_6h": n.sentiment_change_6h,
            "ai_insight": n.ai_insight,
            "confidence_level": n.confidence_level,
            "image": n.image,
            "is_live": n.is_live,
            "published_at": n.published_at.isoformat() if n.published_at else None,
        }
        for n in rows
    ]

@router.get("/{slug}")
def topic(slug: str, db: Session = Depends(get_db)):
    item = ensure(slug, db)
    story = db.scalar(select(StoryRecord).where(StoryRecord.topic_slug == slug).order_by(StoryRecord.published_at.desc()))
    narrative = db.get(NarrativeRecord, slug)
    image = (narrative.image if narrative else story.image) if (narrative or story) else "/images/real-data-check.jpg"
    category = (narrative.category if narrative else story.category) if (narrative or story) else "Analysis"
    return {
        "slug": item.slug,
        "title": item.title,
        "subtitle": item.subtitle,
        "total_conversations": item.total_conversations,
        "updated": item.updated,
        "demo": item.is_demo,
        "image": image,
        "category": category,
    }

@router.get("/{slug}/sentiment")
def sentiment(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["sentiment"]

@router.get("/{slug}/audience")
def audience(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["audience"]

@router.get("/{slug}/trends")
def trends(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["trends"]

@router.get("/{slug}/drivers")
def drivers(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["drivers"]

@router.get("/{slug}/voices")
def voices(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["voices"]

@router.get("/{slug}/network")
def network(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["network"]

@router.get("/{slug}/confidence")
def confidence(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["confidence"]

@router.get("/{slug}/brief")
def brief(slug: str, db: Session = Depends(get_db)):
    return get_topic_analytics(ensure(slug, db))["brief"]
