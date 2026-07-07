import re
import time
import logging
from fastapi import Request, Response

logger = logging.getLogger("symptomscope.request")


_USER_ID_PATTERN = re.compile(r"/[a-f0-9]{32,}|user_[a-zA-Z0-9]+")


def _sanitize_path(path: str) -> str:
    return _USER_ID_PATTERN.sub("/<user_id>", path)


async def request_logging_middleware(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed = time.perf_counter() - start

    logger.info(
        "%s %s %s %.0fms",
        request.method,
        _sanitize_path(request.url.path),
        response.status_code,
        elapsed * 1000,
    )
    return response
