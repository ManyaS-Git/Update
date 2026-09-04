from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "UPDATES Intelligence API"
    demo_mode: bool = True
    pitch_showcase_mode: bool = False
    pitch_refresh_max_items: int = 3
    database_url: str = "sqlite:///./updates-demo.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:3001"
    llm_provider: str = "mock"
    sentiment_provider: str = "auto"
    hf_token: str | None = None
    hf_allow_model_download: bool = False
    hf_sentiment_model: str = "airzipm/sentiment-analysis-muril-v2"
    hf_inference_endpoint_url: str | None = None
    hf_safety_model: str = "Hate-speech-CNERG/indic-abusive-allInOne-MuRIL"
    safety_provider: str = "auto"
    sarcasm_inference_endpoint_url: str | None = None
    sarcasm_model_name: str = "not-configured"
    model_device: str = "cpu"
    hf_model_cache: str = "./.hf-cache"
    x_bearer_token: str | None = None
    youtube_api_key: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "UPDATES-Intelligence/1.0"
    facebook_page_access_token: str | None = None
    instagram_access_token: str | None = None
    facebook_post_ids: str = ""
    instagram_media_ids: str = ""
    meta_graph_version: str = "v25.0"
    collector_max_retries: int = 3
    admin_api_key: str | None = None
    allow_unauthenticated_local_mutations: bool = True
    privacy_hash_secret: str | None = None
    max_request_bytes: int = 1_000_000
    api_rate_limit_per_minute: int = 240
    expensive_rate_limit_per_minute: int = 30
    auto_ingestion_enabled: bool = False
    auto_ingestion_interval_minutes: int = 120
    auto_ingestion_platforms: str = "x,youtube,reddit,facebook,instagram"
    auto_ingestion_max_topics: int = 100
    auto_ingestion_max_items_per_platform: int = 100
    auto_news_refresh_enabled: bool = True
    auto_news_refresh_interval_minutes: int = 5
    auto_news_refresh_max_items: int = 12
    public_signal_batch_size: int = 100
    public_signal_workers: int = 2
    analysis_refresh_interval_minutes: int = 120
    trained_model_dir: str = "./data/artifacts"
    learning_min_labels: int = 60
    continuous_learning_enabled: bool = True
    continuous_learning_interval_minutes: int = 60
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = "PLAIN"
    kafka_sasl_username: str | None = None
    kafka_sasl_password: str | None = None
    kafka_client_id: str = "updates-intelligence"
    kafka_raw_topic: str = "social-media-raw"
    kafka_normalized_topic: str = "social-media-normalized"
    kafka_qualified_topic: str = "social-media-qualified"
    kafka_dead_letter_topic: str = "social-media-dead-letter"
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
