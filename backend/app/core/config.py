from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "UPDATES Intelligence API"
    demo_mode: bool = False
    database_url: str = "sqlite:///./updates.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:3001"
    llm_provider: str = "rag"
    sentiment_provider: str = "auto"
    hf_token: str | None = None
    hf_sentiment_model: str = "airzipm/sentiment-analysis-muril-v2"
    hf_inference_endpoint_url: str | None = None
    hf_safety_model: str = "Hate-speech-CNERG/indic-abusive-allInOne-MuRIL"
    safety_provider: str = "auto"
    sarcasm_model: str = "helinivan/english-sarcasm-detector"
    model_device: str = "cpu"
    hf_model_cache: str = "./.hf-cache"
    twitter_api_key: str | None = None
    twitter_api_secret: str | None = None
    x_bearer_token: str | None = None
    youtube_api_key: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "UPDATES-Intelligence/1.0"
    telegram_bot_token: str | None = None
    telegram_channels: str = "news,worldnews,india"
    facebook_page_access_token: str | None = None
    instagram_access_token: str | None = None
    facebook_post_ids: str = ""
    instagram_media_ids: str = ""
    meta_graph_version: str = "v25.0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_enabled: bool = True
    csqe_min_threshold: float = 0.35
    collector_max_retries: int = 3
    auto_ingestion_enabled: bool = True
    auto_ingestion_interval_minutes: int = 15
    auto_ingestion_platforms: str = "x,reddit,telegram,youtube,facebook,instagram"
    auto_ingestion_max_topics: int = 8
    auto_ingestion_max_items_per_platform: int = 100
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ingestion_platforms(self) -> list[str]:
        return [item.strip().lower() for item in self.auto_ingestion_platforms.split(",") if item.strip()]

    def target_ids(self,platform:str) -> list[str]:
        value=self.facebook_post_ids if platform=="facebook" else self.instagram_media_ids if platform=="instagram" else ""
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
