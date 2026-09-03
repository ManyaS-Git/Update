import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import case, delete, func, or_, select
from sqlalchemy.orm import Session
from app.models.database import (
    BookmarkRecord,
    CommentAnalysisRecord,
    PostRecord,
    PreferenceRecord,
    SentimentRecord,
    SourceCommentRecord,
    StoryRecord,
    TopicRecord,
    get_db,
)
from app.models.schemas import NotificationPreference, StoryCreate, TopicAnalysisRequest
from app.services.database import bookmarked_ids, relative_time, story_dict
from app.services.ingestion import analyze_topic_query
from app.services.news import DEFAULT_QUERY, refresh_latest_news

router = APIRouter(prefix="/api", tags=["content"])

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = db.execute(
        select(StoryRecord.category, func.count(StoryRecord.id))
        .group_by(StoryRecord.category)
        .order_by(StoryRecord.category)
    ).all()
    return [{"name": name, "count": count} for name, count in rows]

@router.get("/stories")
def stories(
    category: str | None = None,
    q: str | None = None,
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    # If no stories exist, bootstrap dynamically from live news
    existing_count = db.scalar(select(func.count(StoryRecord.id))) or 0
    if existing_count == 0:
        try:
            refresh_latest_news(db, limit=12)
        except Exception:
            pass

    live_source = case((or_(StoryRecord.source_status.like("gdelt:%"), StoryRecord.source_status.like("news:%"), StoryRecord.source_status == "live_stream"), 1), else_=0)
    query = select(StoryRecord).order_by(live_source.desc(), StoryRecord.published_at.desc(), StoryRecord.is_live.desc()).offset(offset).limit(limit)
    if category and category.lower() != "all":
        query = query.where(func.lower(StoryRecord.category) == category.lower())
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(StoryRecord.title.ilike(term), StoryRecord.summary.ilike(term), StoryRecord.category.ilike(term)))
    bookmarks = bookmarked_ids(db)
    return [story_dict(story, story.id in bookmarks) for story in db.scalars(query).all()]

@router.get("/posts")
def live_posts(
    topic_slug: str | None = None,
    platform: str | None = None,
    sentiment: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Real-time live social media post feed (Section 16)."""
    # 1. Query from posts table joined with sentiments
    q = select(PostRecord, SentimentRecord).outerjoin(SentimentRecord, SentimentRecord.post_id == PostRecord.id)
    if topic_slug:
        q = q.where(PostRecord.topic_slug == topic_slug)
    if platform:
        q = q.where(PostRecord.platform == platform)
    if sentiment:
        q = q.where(SentimentRecord.sentiment == sentiment)

    rows = db.execute(q.order_by(PostRecord.published_at.desc()).limit(limit)).all()
    if rows:
        results = []
        for post, sent in rows:
            results.append({
                "id": str(post.id),
                "platform": post.platform,
                "author": post.author_name or (f"@{post.author_id}" if post.author_id else f"{post.platform}_user"),
                "author_id": post.author_id,
                "content": post.content,
                "timestamp": relative_time(post.published_at, "Just now"),
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "views": post.views,
                "is_verified": post.is_verified,
                "topic_slug": post.topic_slug,
                "sentiment": sent.sentiment if sent else "neutral",
                "sentiment_confidence": sent.confidence if sent else 0.70,
                "url": post.url,
            })
        return results

    # 2. Fallback to source_comments if posts table is not yet populated
    c_q = select(SourceCommentRecord, CommentAnalysisRecord).outerjoin(
        CommentAnalysisRecord, CommentAnalysisRecord.comment_id == SourceCommentRecord.id
    )
    if topic_slug:
        c_q = c_q.where(SourceCommentRecord.topic_slug == topic_slug)
    if platform:
        c_q = c_q.where(SourceCommentRecord.platform == platform)

    c_rows = db.execute(c_q.order_by(SourceCommentRecord.published_at.desc()).limit(limit)).all()
    results = []
    for comment, analysis in c_rows:
        eng = json.loads(comment.engagement_json or "{}")
        results.append({
            "id": str(comment.id),
            "platform": comment.platform,
            "author": f"{comment.platform.capitalize()} User",
            "author_id": comment.author_hash,
            "content": comment.text,
            "timestamp": relative_time(comment.published_at, "Recently"),
            "published_at": comment.published_at.isoformat() if comment.published_at else None,
            "likes": eng.get("likes", 0),
            "comments": eng.get("replies", 0),
            "shares": eng.get("shares", 0),
            "views": eng.get("views"),
            "is_verified": False,
            "topic_slug": comment.topic_slug,
            "sentiment": analysis.sentiment if analysis else "neutral",
            "sentiment_confidence": analysis.sentiment_score if analysis else 0.70,
            "url": None,
        })
    return results

@router.post("/analyze/topic")
async def analyze_topic(payload: TopicAnalysisRequest, db: Session = Depends(get_db)):
    """Interactive topic analysis on user-entered topic (Section 17)."""
    try:
        return await analyze_topic_query(db, payload.query, payload.max_items)
    except Exception as exc:
        raise HTTPException(400, f"Analysis failed: {exc}") from exc

@router.post("/news/refresh")
def refresh_news(
    q: str = Query(DEFAULT_QUERY, min_length=2, max_length=300),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        result = refresh_latest_news(db, q, limit)
    except (ValueError, OSError) as exc:
        raise HTTPException(503, f"Latest-news provider unavailable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(502, "Latest-news provider did not return a usable response") from exc
    return {**result, "stories": stories(category=None, q=None, limit=limit, offset=0, db=db)}

@router.post("/stories", status_code=201)
def create_story(payload: StoryCreate, db: Session = Depends(get_db)):
    if not db.get(TopicRecord, payload.topic_slug):
        db.add(TopicRecord(
            slug=payload.topic_slug,
            title=payload.title,
            subtitle="Public sentiment & conversation analysis",
            total_conversations=0,
            updated="Live story",
            is_demo=False,
            analytics_json="{}",
        ))
        db.commit()

    story = StoryRecord(
        title=payload.title,
        category=payload.category,
        relative_time="Just now",
        image=payload.image,
        is_live=payload.is_live,
        topic_slug=payload.topic_slug,
        summary=payload.summary,
        source_status="user_created",
    )
    db.add(story)
    db.commit()
    db.refresh(story)
    return story_dict(story)

@router.get("/stories/{story_id}")
def story(story_id: int, db: Session = Depends(get_db)):
    record = db.get(StoryRecord, story_id)
    if not record:
        raise HTTPException(404, "Story not found")
    return story_dict(record, story_id in bookmarked_ids(db))

@router.get("/search")
def search(q: str = Query(min_length=1, max_length=150), db: Session = Depends(get_db)):
    term = f"%{q.strip()}%"
    bookmarks = bookmarked_ids(db)
    found_stories = db.scalars(
        select(StoryRecord)
        .where(or_(StoryRecord.title.ilike(term), StoryRecord.summary.ilike(term), StoryRecord.category.ilike(term)))
        .order_by(StoryRecord.published_at.desc())
        .limit(30)
    ).all()
    found_topics = db.scalars(
        select(TopicRecord).where(or_(TopicRecord.title.ilike(term), TopicRecord.subtitle.ilike(term))).limit(10)
    ).all()
    return {
        "query": q,
        "stories": [story_dict(item, item.id in bookmarks) for item in found_stories],
        "topics": [
            {"slug": item.slug, "title": item.title, "subtitle": item.subtitle, "updated": item.updated}
            for item in found_topics
        ],
    }

@router.get("/bookmarks")
def bookmarks(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(StoryRecord).join(BookmarkRecord, BookmarkRecord.story_id == StoryRecord.id).order_by(BookmarkRecord.created_at.desc())
    ).all()
    return [story_dict(item, True) for item in rows]

@router.post("/bookmarks/{story_id}", status_code=201)
def add_bookmark(story_id: int, db: Session = Depends(get_db)):
    if not db.get(StoryRecord, story_id):
        raise HTTPException(404, "Story not found")
    existing = db.scalar(select(BookmarkRecord).where(BookmarkRecord.story_id == story_id))
    if not existing:
        db.add(BookmarkRecord(story_id=story_id))
        db.commit()
    return {"story_id": str(story_id), "bookmarked": True}

@router.delete("/bookmarks/{story_id}")
def remove_bookmark(story_id: int, db: Session = Depends(get_db)):
    db.execute(delete(BookmarkRecord).where(BookmarkRecord.story_id == story_id))
    db.commit()
    return {"story_id": str(story_id), "bookmarked": False}

@router.get("/feed")
def feed(db: Session = Depends(get_db)):
    bookmarks = bookmarked_ids(db)
    live_source = case((or_(StoryRecord.source_status.like("gdelt:%"), StoryRecord.source_status.like("news:%"), StoryRecord.source_status == "live_stream"), 1), else_=0)
    rows = db.scalars(select(StoryRecord).order_by(live_source.desc(), StoryRecord.published_at.desc(), StoryRecord.is_live.desc()).limit(30)).all()
    return [story_dict(item, item.id in bookmarks) for item in rows]

@router.get("/preferences")
def preferences(db: Session = Depends(get_db)):
    record = db.get(PreferenceRecord, "notifications_enabled")
    return {"notifications_enabled": bool(record and record.value == "true")}

@router.put("/preferences/notifications")
def update_notifications(payload: NotificationPreference, db: Session = Depends(get_db)):
    record = db.get(PreferenceRecord, "notifications_enabled")
    if not record:
        record = PreferenceRecord(key="notifications_enabled", value="false")
        db.add(record)
    record.value = "true" if payload.enabled else "false"
    db.commit()
    return {"notifications_enabled": payload.enabled}

@router.get("/reports/{slug}", response_class=PlainTextResponse)
def report(slug: str, db: Session = Depends(get_db)):
    topic = db.get(TopicRecord, slug)
    if not topic:
        raise HTTPException(404, "Topic not found")
    analytics = topic.analytics
    sentiment = analytics.get("sentiment", {})
    drivers = analytics.get("drivers", [])
    body = "\n".join(
        [
            f"{topic.title} — Public Conversation Intelligence Brief",
            "=" * 56,
            f"{topic.subtitle}",
            f"Conversations analysed: {topic.total_conversations:,}",
            f"Last updated: {topic.updated}",
            "",
            "Sentiment Distribution",
            f"Negative: {sentiment.get('negative', 0)}% | Neutral: {sentiment.get('neutral', 0)}% | Positive: {sentiment.get('positive', 0)}%",
            "",
            "Conversation Drivers",
            *[f"- {item.get('title')}: {item.get('description')}" for item in drivers],
            "",
            "Methodology note: All metrics dynamically generated from real streaming social and news intelligence.",
        ]
    )
    headers = {"Content-Disposition": f'attachment; filename="{slug}-conversation-brief.txt"'}
    return PlainTextResponse(body, headers=headers)
