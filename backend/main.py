import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.v1 import predict, doctors, reports, symptoms, hospitals, analytics, export, chat, reminders, risk_score
from utils.database import get_database, close_database, ensure_indexes
from utils.settings import settings
from utils.exceptions import global_exception_handler
from utils.rate_limit import limiter
from utils.security_headers import security_headers_middleware
from utils.logging_config import setup_logging
from utils.env_check import log_environment
from utils.request_logger import request_logging_middleware
from utils.monitoring import init_sentry
from services.reminder_service import scheduler as reminder_scheduler

setup_logging()
init_sentry()
logger = logging.getLogger("symptomscope")

MAX_REQUEST_SIZE = 1024 * 100  # 100 KB


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_environment()
    get_database()
    await ensure_indexes()
    await reminder_scheduler.start()
    logger.info("Application startup complete")
    yield
    await reminder_scheduler.stop()
    await close_database()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="SymptomScope AI API",
    description="AI-powered healthcare intelligence platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large"},
        )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_logging_middleware)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(doctors.router, prefix="/api/v1", tags=["Doctors"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(symptoms.router, prefix="/api/v1", tags=["Symptoms"])
app.include_router(hospitals.router, prefix="/api/v1", tags=["Hospitals"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(export.router, prefix="/api/v1", tags=["Export"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(reminders.router, prefix="/api/v1", tags=["Reminders"])
app.include_router(risk_score.router, prefix="/api/v1", tags=["Risk Score"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
