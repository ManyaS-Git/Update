import json
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.core.config import get_settings

class Base(DeclarativeBase): pass

class TopicRecord(Base):
    __tablename__="topics"
    slug:Mapped[str]=mapped_column(String(120),primary_key=True)
    title:Mapped[str]=mapped_column(String(240))
    subtitle:Mapped[str]=mapped_column(String(300))
    total_conversations:Mapped[int]=mapped_column(Integer,default=0)
    updated:Mapped[str]=mapped_column(String(80),default="Not analysed")
    is_demo:Mapped[bool]=mapped_column(Boolean,default=True)
    analytics_json:Mapped[str]=mapped_column(Text,default="{}")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

    @property
    def analytics(self)->dict: return json.loads(self.analytics_json or "{}")

class StoryRecord(Base):
    __tablename__="stories"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    title:Mapped[str]=mapped_column(String(300),index=True)
    category:Mapped[str]=mapped_column(String(80),index=True)
    relative_time:Mapped[str]=mapped_column(String(40))
    image:Mapped[str]=mapped_column(String(260))
    is_live:Mapped[bool]=mapped_column(Boolean,default=False)
    topic_slug:Mapped[str]=mapped_column(ForeignKey("topics.slug"),default="reservation-protest")
    summary:Mapped[str]=mapped_column(Text)
    source_status:Mapped[str]=mapped_column(String(80),default="seeded_demo")
    published_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class BookmarkRecord(Base):
    __tablename__="bookmarks"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    story_id:Mapped[int]=mapped_column(ForeignKey("stories.id"),unique=True,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class PreferenceRecord(Base):
    __tablename__="preferences"
    key:Mapped[str]=mapped_column(String(80),primary_key=True)
    value:Mapped[str]=mapped_column(Text)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))

class AnalysisRunRecord(Base):
    __tablename__="analysis_runs"
    id:Mapped[str]=mapped_column(String(80),primary_key=True)
    topic_slug:Mapped[str]=mapped_column(ForeignKey("topics.slug"),index=True)
    status:Mapped[str]=mapped_column(String(40))
    mode:Mapped[str]=mapped_column(String(60))
    metrics_json:Mapped[str]=mapped_column(Text,default="{}")
    started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)

class SourceCommentRecord(Base):
    __tablename__="source_comments"
    __table_args__=(UniqueConstraint("platform","external_id",name="uq_comment_platform_external"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    topic_slug:Mapped[str]=mapped_column(ForeignKey("topics.slug"),index=True)
    platform:Mapped[str]=mapped_column(String(40),index=True)
    external_id:Mapped[str]=mapped_column(String(180),index=True)
    parent_external_id:Mapped[str|None]=mapped_column(String(180),nullable=True)
    author_hash:Mapped[str|None]=mapped_column(String(80),nullable=True)
    text:Mapped[str]=mapped_column(Text)
    published_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True)
    engagement_json:Mapped[str]=mapped_column(Text,default="{}")
    public_signals_json:Mapped[str]=mapped_column(Text,default="{}")
    raw_metadata_json:Mapped[str]=mapped_column(Text,default="{}")
    ingested_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class CommentAnalysisRecord(Base):
    __tablename__="comment_analyses"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    comment_id:Mapped[int]=mapped_column(ForeignKey("source_comments.id"),unique=True,index=True)
    sentiment:Mapped[str]=mapped_column(String(30),index=True)
    sentiment_score:Mapped[float]=mapped_column(Float)
    stance:Mapped[str]=mapped_column(String(30),index=True)
    emotion:Mapped[str]=mapped_column(String(40))
    safety:Mapped[str]=mapped_column(String(30),index=True)
    language:Mapped[str]=mapped_column(String(30),index=True)
    interests_json:Mapped[str]=mapped_column(Text,default="[]")
    geography:Mapped[str|None]=mapped_column(String(120),nullable=True,index=True)
    age_bracket:Mapped[str|None]=mapped_column(String(60),nullable=True)
    inference_json:Mapped[str]=mapped_column(Text,default="{}")
    influence_score:Mapped[float]=mapped_column(Float,default=0)
    model_name:Mapped[str]=mapped_column(String(180))
    analysed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class IngestionJobRecord(Base):
    __tablename__="ingestion_jobs"
    id:Mapped[str]=mapped_column(String(80),primary_key=True)
    topic_slug:Mapped[str]=mapped_column(ForeignKey("topics.slug"),index=True)
    platforms_json:Mapped[str]=mapped_column(Text)
    query:Mapped[str]=mapped_column(String(300))
    status:Mapped[str]=mapped_column(String(40),index=True)
    results_json:Mapped[str]=mapped_column(Text,default="{}")
    error_json:Mapped[str]=mapped_column(Text,default="{}")
    started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)

class TrainingLabelRecord(Base):
    __tablename__="training_labels"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    text:Mapped[str]=mapped_column(Text)
    sentiment:Mapped[str|None]=mapped_column(String(30),nullable=True)
    safety:Mapped[str|None]=mapped_column(String(30),nullable=True)
    stance:Mapped[str|None]=mapped_column(String(30),nullable=True)
    language:Mapped[str|None]=mapped_column(String(30),nullable=True)
    source:Mapped[str]=mapped_column(String(60),default="human_review")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class FeedbackRecord(Base):
    __tablename__="learning_feedback"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    context:Mapped[str]=mapped_column(String(80))
    action:Mapped[str]=mapped_column(String(80))
    reward:Mapped[float]=mapped_column(Float)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

settings=get_settings()
connect_args={"check_same_thread":False} if settings.database_url.startswith("sqlite") else {}
engine=create_engine(settings.database_url,connect_args=connect_args,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=False)

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
