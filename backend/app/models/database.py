import json
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.core.config import get_settings

class Base(DeclarativeBase): pass

class TopicRecord(Base):
    __tablename__ = "topics"
    slug: Mapped[str] = mapped_column(String(120), primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    subtitle: Mapped[str] = mapped_column(String(300))
    total_conversations: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[str] = mapped_column(String(80), default="Not analysed")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    keywords_json: Mapped[str] = mapped_column(Text, default="[]")
    representation: Mapped[str] = mapped_column(String(300), default="")
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    velocity: Mapped[float] = mapped_column(Float, default=0.0)
    analytics_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def analytics(self) -> dict:
        return json.loads(self.analytics_json or "{}")

class NarrativeRecord(Base):
    __tablename__ = "narratives"
    slug: Mapped[str] = mapped_column(String(120), primary_key=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True, default="India")
    status: Mapped[str] = mapped_column(String(40), default="EMERGING")  # EMERGING, POPULAR_TREND, STABLE, DECLINING
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=True)
    momentum_score: Mapped[float] = mapped_column(Float, default=0.0)
    velocity: Mapped[float] = mapped_column(Float, default=0.0)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    cross_platform_score: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment_negative: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_neutral: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_positive: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_change_6h: Mapped[int] = mapped_column(Integer, default=0)
    ai_insight: Mapped[str] = mapped_column(Text, default="")
    confidence_level: Mapped[str] = mapped_column(String(40), default="Medium")
    total_conversations: Mapped[int] = mapped_column(Integer, default=0)
    qualified_count: Mapped[int] = mapped_column(Integer, default=0)
    low_signal_count: Mapped[int] = mapped_column(Integer, default=0)
    image: Mapped[str] = mapped_column(String(300), default="/images/real-protest.jpg")
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class StoryRecord(Base):
    __tablename__ = "stories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    relative_time: Mapped[str] = mapped_column(String(40), default="Just now")
    image: Mapped[str] = mapped_column(String(300))
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    topic_slug: Mapped[str] = mapped_column(ForeignKey("topics.slug"), default="live-narrative")
    summary: Mapped[str] = mapped_column(Text)
    source_status: Mapped[str] = mapped_column(String(80), default="live_stream")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PostRecord(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("platform", "post_id", name="uq_platform_post_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(40), index=True)
    post_id: Mapped[str] = mapped_column(String(180), index=True)
    author_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hashtags_json: Mapped[str] = mapped_column(Text, default="[]")
    mentions_json: Mapped[str] = mapped_column(Text, default="[]")
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    topic_slug: Mapped[str] = mapped_column(ForeignKey("topics.slug"), index=True)
    raw_metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserRecord(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("platform", "author_id", name="uq_platform_author_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[str] = mapped_column(String(180), index=True)
    platform: Mapped[str] = mapped_column(String(40), index=True)
    author_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    influence_score: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class SentimentRecord(Base):
    __tablename__ = "sentiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True, index=True)
    sentiment: Mapped[str] = mapped_column(String(30), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    stance: Mapped[str] = mapped_column(String(30), default="neutral")
    emotion: Mapped[str] = mapped_column(String(40), default="neutral")
    sarcasm_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    sarcasm_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    model_name: Mapped[str] = mapped_column(String(180), default="MuRIL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DemographicProfileRecord(Base):
    __tablename__ = "demographic_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_slug: Mapped[str] = mapped_column(ForeignKey("narratives.slug"), index=True)
    geography_observed: Mapped[str] = mapped_column(Text, default="{}")
    language_distribution: Mapped[str] = mapped_column(Text, default="{}")
    age_inferences: Mapped[str] = mapped_column(Text, default="{}")
    interests_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class NetworkNodeRecord(Base):
    __tablename__ = "network_nodes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_slug: Mapped[str] = mapped_column(ForeignKey("narratives.slug"), index=True)
    node_id: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(180))
    node_type: Mapped[str] = mapped_column(String(40), default="entity")
    centrality: Mapped[float] = mapped_column(Float, default=0.0)
    pagerank: Mapped[float] = mapped_column(Float, default=0.0)

class NetworkEdgeRecord(Base):
    __tablename__ = "network_edges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    narrative_slug: Mapped[str] = mapped_column(ForeignKey("narratives.slug"), index=True)
    source_id: Mapped[str] = mapped_column(String(120), index=True)
    target_id: Mapped[str] = mapped_column(String(120), index=True)
    relation_type: Mapped[str] = mapped_column(String(40), default="interaction")
    weight: Mapped[float] = mapped_column(Float, default=1.0)

class SourceCommentRecord(Base):
    __tablename__ = "source_comments"
    __table_args__ = (UniqueConstraint("platform", "external_id", name="uq_comment_platform_external"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_slug: Mapped[str] = mapped_column(ForeignKey("topics.slug"), index=True)
    platform: Mapped[str] = mapped_column(String(40), index=True)
    external_id: Mapped[str] = mapped_column(String(180), index=True)
    parent_external_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    author_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    engagement_json: Mapped[str] = mapped_column(Text, default="{}")
    public_signals_json: Mapped[str] = mapped_column(Text, default="{}")
    raw_metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class CommentAnalysisRecord(Base):
    __tablename__ = "comment_analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("source_comments.id"), unique=True, index=True)
    sentiment: Mapped[str] = mapped_column(String(30), index=True)
    sentiment_score: Mapped[float] = mapped_column(Float)
    stance: Mapped[str] = mapped_column(String(30), index=True)
    emotion: Mapped[str] = mapped_column(String(40))
    safety: Mapped[str] = mapped_column(String(30), index=True)
    language: Mapped[str] = mapped_column(String(30), index=True)
    interests_json: Mapped[str] = mapped_column(Text, default="[]")
    geography: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    age_bracket: Mapped[str | None] = mapped_column(String(60), nullable=True)
    inference_json: Mapped[str] = mapped_column(Text, default="{}")
    influence_score: Mapped[float] = mapped_column(Float, default=0)
    model_name: Mapped[str] = mapped_column(String(180))
    analysed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class IngestionJobRecord(Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    topic_slug: Mapped[str] = mapped_column(ForeignKey("topics.slug"), index=True)
    platforms_json: Mapped[str] = mapped_column(Text)
    query: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(40), index=True)
    results_json: Mapped[str] = mapped_column(Text, default="{}")
    error_json: Mapped[str] = mapped_column(Text, default="{}")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class BookmarkRecord(Base):
    __tablename__ = "bookmarks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PreferenceRecord(Base):
    __tablename__ = "preferences"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AnalysisRunRecord(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    topic_slug: Mapped[str] = mapped_column(ForeignKey("topics.slug"), index=True)
    status: Mapped[str] = mapped_column(String(40))
    mode: Mapped[str] = mapped_column(String(60))
    metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
