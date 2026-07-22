from utils.settings import settings
import logging

logger = logging.getLogger("symptomscope.env")


def validate_environment() -> list[str]:
    warnings: list[str] = []

    if not settings.clerk_jwks_url and not settings.clerk_issuer:
        warnings.append(
            "Clerk auth disabled: neither CLERK_JWKS_URL nor CLERK_ISSUER is set"
        )

    if not settings.gemini_api_key:
        warnings.append(
            "Gemini AI disabled: GEMINI_API_KEY not set — LLM features will fail"
        )

    if "localhost" in settings.mongodb_uri:
        warnings.append(
            "Using local MongoDB – ensure mongod is running or set MONGODB_URI"
        )

    if not settings.secret_key:
        warnings.append(
            "SECRET_KEY not set — using default (insecure for production)"
        )

    if settings.debug:
        warnings.append("DEBUG mode enabled – do not use in production")

    return warnings


def log_environment() -> None:
    mode = "DEBUG" if settings.debug else "PRODUCTION"
    logger.info("Starting %s v%s in %s mode", settings.app_name, settings.app_version, mode)
    logger.info("MongoDB: %s", _mask_uri(settings.mongodb_uri))
    logger.info("Gemini AI: %s", "configured" if settings.gemini_api_key else "NOT CONFIGURED")
    logger.info("Redis: %s", _mask_uri(settings.redis_url) if settings.redis_url else "not configured")
    logger.info("CORS origins: %s", settings.cors_origins)

    warnings = validate_environment()
    for w in warnings:
        logger.warning(w)


def _mask_uri(uri: str | None) -> str:
    if not uri:
        return "not configured"
    if "@" in uri:
        parts = uri.split("@")
        return f"***@{parts[-1]}"
    return uri
