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
    cors_origins: str = "http://localhost:3000,http://localhost:3001,https://symptomscope.vercel.app"

    # Development mode — when True, auth falls back to dev-user-id if Clerk is unreachable
    dev_mode: bool = True

    # Clerk Authentication (at least one required when not in dev mode)
    clerk_jwks_url: Optional[str] = None
    clerk_issuer: Optional[str] = None

    # Security
    secret_key: str = "default-insecure-secret-key-change-in-production"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Redis (for rate limiting / caching)
    redis_url: Optional[str] = None

    # LLM / AI Chat Assistant (Legacy — OpenAI-compatible)
    llm_api_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"

    # Gemini LLM (LangChain-based)
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash-latest"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 1024

    # Groq LLM (LangChain-based fallback)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 1024

    # RAG / ChromaDB
    chromadb_path: str = "./ml/rag/chromadb"
    # Default to a small, fast sentence-transformers model for local embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7

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
