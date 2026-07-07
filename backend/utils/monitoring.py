import logging
import sentry_sdk
from utils.settings import settings

logger = logging.getLogger("symptomscope.monitoring")


def init_sentry() -> None:
    if not settings.sentry_dsn:
        logger.info("Sentry disabled: no DSN configured")
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        release=f"{settings.app_name}@{settings.app_version}",
        send_default_pii=False,
    )
    logger.info("Sentry initialized for environment: %s", settings.sentry_env)
