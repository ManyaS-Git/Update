from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

class SocialMediaPost(BaseModel):
    """Normalized common format for all social platforms."""
    platform: Literal["x", "twitter", "reddit", "telegram", "youtube", "instagram", "facebook"]
    post_id: str
    author_id: str | None = None
    author_name: str | None = None
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    language: str | None = None
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int | None = None
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    url: str | None = None
    is_verified: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

class SarcasmResult(BaseModel):
    sarcasm_detected: bool
    sarcasm_confidence: float = Field(ge=0.0, le=1.0)
    model_name: str
    evidence: list[str] = Field(default_factory=list)

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    sentiment_score: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    stance: Literal["supportive", "opposing", "neutral", "questioning"] = "neutral"
    emotion: str = "neutral"
    sarcasm: SarcasmResult | None = None
    language: str = "english"
    context_used: bool = False

class SignalQualification(BaseModel):
    text: str
    signal_quality: float = Field(ge=0.0, le=1.0)
    classification: Literal["HIGH_SIGNAL", "MEDIUM_SIGNAL", "LOW_SIGNAL"]
    reason: str

class NormalizedContent(BaseModel):
    platform: str
    external_id: str
    topic_id: str
    author_id: str | None = None
    author_name: str | None = None
    text: str
    timestamp: datetime
    parent_id: str | None = None
    engagement: dict[str, int] = Field(default_factory=dict)
    public_profile_signals: dict[str, str] = Field(default_factory=dict)
    raw_metadata: dict = Field(default_factory=dict)

class AIQuestion(BaseModel):
    topic_slug: str
    question: str = Field(min_length=2, max_length=500)

class AIResponse(BaseModel):
    answer: str
    evidence: list[str]
    confidence: Literal["Low", "Medium", "High"]
    last_updated: str
    provider: str

class AnalysisRequest(BaseModel):
    topic_slug: str

class AnalysisRunResponse(BaseModel):
    run_id: str
    topic_slug: str
    status: str
    mode: str

class NotificationPreference(BaseModel):
    enabled: bool

class StoryCreate(BaseModel):
    title: str = Field(min_length=4, max_length=300)
    category: str = Field(min_length=2, max_length=80)
    summary: str = Field(min_length=10, max_length=2000)
    image: str
    topic_slug: str = "live-narrative"
    is_live: bool = False

class TopicSummary(BaseModel):
    slug: str
    title: str
    subtitle: str
    total_conversations: int
    updated: str
    demo: bool

class CommentInput(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    context: str | None = Field(default=None, max_length=2000)
    platform: str = "manual"
    engagement: dict[str, int] = Field(default_factory=dict)
    public_signals: dict[str, str] = Field(default_factory=dict)

class CommentIntelligence(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    sentiment_score: float = Field(ge=0.0, le=1.0)
    stance: Literal["supportive", "opposing", "neutral", "questioning"]
    emotion: str
    safety: Literal["normal", "toxic", "hate"]
    language: Literal["english", "hindi", "hinglish", "other"]
    interests: list[str]
    geography: str | None
    age_bracket: str | None
    influence_score: float = Field(ge=0.0, le=100.0)
    sarcasm_detected: bool = False
    sarcasm_confidence: float = 0.0
    confidence: dict[str, float]
    evidence: dict[str, list[str]]
    model_name: str
    safety_model_name: str
    signal_quality: float = Field(ge=0.0, le=1.0)
    signal_classification: Literal["HIGH_SIGNAL", "MEDIUM_SIGNAL", "LOW_SIGNAL"]

class IngestionRequest(BaseModel):
    topic_slug: str
    query: str = Field(min_length=2, max_length=300)
    platforms: list[Literal["x", "twitter", "youtube", "reddit", "telegram", "facebook", "instagram"]]
    targets: dict[str, list[str]] = Field(default_factory=dict)
    max_items: int = Field(default=100, ge=1, le=1000)

class KafkaStatus(BaseModel):
    connected: bool
    bootstrap_servers: str
    topics: list[str]
    mode: str
    message: str

class TopicAnalysisRequest(BaseModel):
    query: str = Field(min_length=2, max_length=200)
    max_items: int = Field(default=50, ge=10, le=200)

class EmergingNarrative(BaseModel):
    slug: str
    title: str
    category: str
    status: Literal["EMERGING", "POPULAR_TREND", "STABLE", "DECLINING"]
    is_emerging: bool
    momentum_score: float
    velocity: float
    growth_rate: float
    cross_platform_score: float
    total_conversations: int
    sentiment: dict[str, int]
    topics: list[str]
    updated: str
