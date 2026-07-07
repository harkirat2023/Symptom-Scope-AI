import time
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from schemas.analytics_schema import AnalyticsResponse, RiskScoreAnalytics
from services.analytics_service import AnalyticsService, _ANALYTICS_CACHE, _ANALYTICS_CACHE_TTL, _ANALYTICS_LOCK
from repositories.prediction_repository import PredictionRepository
from repositories.risk_score_repository import RiskScoreRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/analytics/{user_id}", response_model=AnalyticsResponse)
@limiter.limit("10/minute")
async def get_analytics(
    request: Request,
    user_id: str,
    auth_user_id: str = Depends(get_current_user),
    range: str = Query("6m", description="Time range: 1m, 3m, 6m, 1y"),
    analytics_service: AnalyticsService = Depends(),
    prediction_repository: PredictionRepository = Depends(),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if range not in ("1m", "3m", "6m", "1y"):
        range = "6m"

    cache_key = f"{user_id}:{range}"
    now = time.time()
    with _ANALYTICS_LOCK:
        cached = _ANALYTICS_CACHE.get(cache_key)
        if cached and (now - cached[0]) < _ANALYTICS_CACHE_TTL:
            return cached[1]

    predictions = await prediction_repository.find_by_user(user_id, time_range=range)
    result = analytics_service.compute(predictions, time_range=range)

    try:
        latest_risk = await risk_score_repository.get_latest_score(user_id)
        if latest_risk:
            result["risk_score"] = RiskScoreAnalytics(
                current_score=latest_risk["score"],
                category=latest_risk["category"],
                last_computed=latest_risk["timestamp"],
            ).model_dump()
    except Exception:
        result["risk_score"] = None

    with _ANALYTICS_LOCK:
        _ANALYTICS_CACHE[cache_key] = (now, result)

    return result
