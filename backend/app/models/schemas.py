from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    stance: Literal["supportive", "opposing", "neutral", "questioning"]
    emotion: str
    confidence: float = Field(ge=0, le=1)
    language: str
    context_used: bool

class SignalQualification(BaseModel):
    text: str
    signal_quality: float = Field(ge=0, le=1)
    classification: Literal["HIGH_SIGNAL", "MEDIUM_SIGNAL", "LOW_SIGNAL"]
    reason: str

class NormalizedContent(BaseModel):
    platform: str
    external_id: str
    topic_id: str
    author_id: str | None = None
    text: str
    timestamp: datetime
    parent_id: str | None = None
    engagement: dict[str, int] = Field(default_factory=dict)
    public_profile_signals: dict[str, str] = Field(default_factory=dict)
    raw_metadata: dict = Field(default_factory=dict)

class AIQuestion(BaseModel):
    topic_slug: str
    question: str = Field(min_length=2, max_length=500)

class ChatQuestion(BaseModel):
    message: str = Field(min_length=1,max_length=500)
    topic_slug: str | None = Field(default=None,max_length=120)
    page_path: str | None = Field(default=None,max_length=240)

class ChatResponse(BaseModel):
    answer: str
    actions: list[dict[str,str]] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)

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
    image: str = Field(max_length=500)
    topic_slug: str = "reservation-protest"
    is_live: bool = False

    @field_validator("image")
    @classmethod
    def safe_image(cls,value:str)->str:
        if value.startswith("/images/") or value.startswith(("https://","http://")):return value
        raise ValueError("image must be an http(s) URL or a local /images/ asset")

class TopicSummary(BaseModel):
    slug: str
    title: str
    subtitle: str
    total_conversations: int
    updated: str
    demo: bool

class CommentInput(BaseModel):
    text: str = Field(min_length=1,max_length=10000)
    context: str | None = Field(default=None,max_length=2000)
    platform: str = "manual"
    engagement: dict[str,int] = Field(default_factory=dict)
    public_signals: dict[str,str] = Field(default_factory=dict)

class CommentIntelligence(BaseModel):
    sentiment: Literal["positive","negative","neutral"]
    sentiment_score: float = Field(ge=0,le=1)
    stance: Literal["supportive","opposing","neutral","questioning"]
    emotion: str
    safety: Literal["normal","toxic","hate"]
    language: Literal["english","hindi","hinglish","other"]
    interests: list[str]
    geography: str | None
    age_bracket: str | None
    influence_score: float = Field(ge=0,le=100)
    confidence: dict[str,float]
    evidence: dict[str,list[str]]
    model_name: str
    safety_model_name: str
    signal_quality: float = Field(ge=0,le=1)
    signal_classification: Literal["HIGH_SIGNAL","MEDIUM_SIGNAL","LOW_SIGNAL"]

class IngestionRequest(BaseModel):
    topic_slug: str
    query: str = Field(min_length=2,max_length=300)
    platforms: list[Literal["x","youtube","reddit","facebook","instagram"]]
    targets: dict[str,list[str]] = Field(default_factory=dict)
    max_items: int = Field(default=100,ge=1,le=1000)

    @field_validator("platforms")
    @classmethod
    def unique_platforms(cls,value:list[str])->list[str]:
        if not value:raise ValueError("at least one platform is required")
        return list(dict.fromkeys(value))

    @field_validator("targets")
    @classmethod
    def safe_targets(cls,value:dict[str,list[str]])->dict[str,list[str]]:
        import re
        allowed={"x","youtube","reddit","facebook","instagram"}
        if any(key not in allowed for key in value):raise ValueError("unsupported target platform")
        for targets in value.values():
            if len(targets)>100 or any(not re.fullmatch(r"[A-Za-z0-9_.:-]{1,180}",target) for target in targets):raise ValueError("invalid external target identifier")
        return value

class TrainingLabelInput(BaseModel):
    text:str=Field(min_length=2,max_length=10000)
    sentiment:Literal["positive","negative","neutral"]|None=None
    safety:Literal["normal","toxic","hate"]|None=None
    stance:Literal["supportive","opposing","neutral","questioning"]|None=None
    language:Literal["english","hindi","hinglish","other"]|None=None

class LearningFeedbackInput(BaseModel):
    context:str=Field(min_length=2,max_length=80)
    action:str=Field(min_length=2,max_length=80)
    reward:float=Field(ge=-1,le=1)
