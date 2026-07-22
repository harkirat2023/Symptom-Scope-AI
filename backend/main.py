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
from utils.logging_config import setup_logging
from utils.env_check import log_environment
from utils.request_logger import request_logging_middleware
from services.reminder_service import scheduler as reminder_scheduler

setup_logging()
logger = logging.getLogger("symptomscope")

MAX_REQUEST_SIZE = 1024 * 100  # 100 KB


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_environment()
    get_database()
    await ensure_indexes()

    # Auto-initialize RAG knowledge base if documents exist
    try:
        from services.rag_service import RAGService
        rag = RAGService()
        if not rag.has_documents():
            count = rag.initialize_knowledge_base()
            if count > 0:
                logger.info("RAG knowledge base initialized with %d chunks", count)
        else:
            logger.info("RAG knowledge base already initialized")
    except Exception as e:
        logger.warning("RAG initialization skipped: %s", e)

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
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    path = request.url.path

    if path.startswith(("/docs", "/redoc", "/openapi.json")):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "worker-src 'self' blob:; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.clerk.accounts.dev https://us-assets.i.posthog.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https://img.clerk.com; "
            "connect-src 'self' https://*.clerk.accounts.dev http://localhost:* https://us-assets.i.posthog.com https://us.i.posthog.com; "
            "worker-src 'self' blob:; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
    return response
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
    from services.rag_service import RAGService
    from utils.database import get_database
    from pathlib import Path

    db_ok = False
    try:
        db = get_database()
        db.command("ping")
        db_ok = True
    except Exception:
        pass

    ml_ok = all(
        (Path(__file__).parent / f"ml/models/{m}").exists()
        for m in ["decision_tree_v1.pkl", "random_forest_v1.pkl", "naive_bayes_v1.pkl"]
    )

    rag_stats = {"initialized": False}
    try:
        rag = RAGService()
        rag_stats = rag.get_knowledge_stats()
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "database": "connected" if db_ok else "unreachable",
            "ml_models": "loaded" if ml_ok else "missing",
            "gemini_api": "configured" if settings.gemini_api_key else "not configured",
            "rag_knowledge_base": "initialized" if rag_stats.get("initialized") else "empty",
        },
    }
