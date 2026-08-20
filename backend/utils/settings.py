
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SymptomScope AI"
    app_version: str = "1.0.0"
    debug: bool = False

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/symptomscope"
    mongodb_db_name: str = "symptomscope"
    mongodb_max_pool_size: int = 10
    mongodb_min_pool_size: int = 2

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001,https://symptomscope.vercel.app"

    # Development mode — when True, auth falls back to dev-user-id if Clerk is unreachable
    dev_mode: bool = True

    # Clerk Authentication (at least one required when not in dev mode)
    clerk_jwks_url: str | None = None
    clerk_issuer: str | None = None

    # Security
    secret_key: str = "default-insecure-secret-key-change-in-production"

    # Public base URL used in email links (e.g. https://symptomscope.vercel.app)
    public_base_url: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Redis (for rate limiting / caching)
    redis_url: str | None = None

    # Groq LLM (LangChain-based; the only LLM provider used by the app)
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 2048

    # RAG / ChromaDB
    chromadb_path: str = "./ml/rag/chromadb"
    # Default to a small, fast sentence-transformers model for local embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7

    # SMTP (for email reminders)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
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
