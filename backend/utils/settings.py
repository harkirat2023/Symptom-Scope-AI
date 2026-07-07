from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "SymptomScope AI"
    app_version: str = "1.0.0"
    debug: bool = False

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/symptomscope"
    mongodb_max_pool_size: int = 10
    mongodb_min_pool_size: int = 2

    # CORS
    cors_origins: str = "http://localhost:3000,https://symptomscope.vercel.app"

    # Clerk Authentication (at least one required)
    clerk_jwks_url: Optional[str] = None
    clerk_issuer: Optional[str] = None

    # Sentry
    sentry_dsn: Optional[str] = None
    sentry_env: str = "production"
    sentry_traces_sample_rate: float = 0.1

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Redis (for rate limiting / caching)
    redis_url: Optional[str] = None

    # LLM / AI Chat Assistant
    llm_api_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"

    # SMTP (for email reminders)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@symptomscope.ai"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()
