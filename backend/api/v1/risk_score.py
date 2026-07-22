from fastapi import APIRouter, Depends, HTTPException, Query, Request
from schemas.risk_score_schema import (
    UserHealthProfile,
    UserHealthProfileResponse,
    RiskScoreResponse,
    RiskScoreHistoryResponse,
    RiskScoreHistoryItem,
    RiskTipsResponse,
    RiskFactorBreakdown,
)
from services.risk_score_service import RiskScoreService
from repositories.risk_score_repository import RiskScoreRepository
from repositories.prediction_repository import PredictionRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/risk-score", response_model=RiskScoreResponse)
@limiter.limit("10/minute")
async def get_risk_score(
    request: Request,
    user_id: str = Depends(get_current_user),
    risk_score_service: RiskScoreService = Depends(),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    latest = await risk_score_repository.get_latest_score(user_id)
    if not latest:
        raise HTTPException(
            status_code=404,
            detail="No risk score available. Use the Symptom Checker first.",
        )

    breakdown_data = latest.get("breakdown", {})
    breakdown = RiskFactorBreakdown(**breakdown_data)

    return RiskScoreResponse(
        current_score=latest["score"],
        category=latest["category"],
        breakdown=breakdown,
        last_prediction_id=latest.get("predictionId"),
        timestamp=latest["timestamp"],
    )


@router.get(
    "/risk-score/history", response_model=RiskScoreHistoryResponse
)
@limiter.limit("10/minute")
async def get_risk_score_history(
    request: Request,
    range: str = Query("6m", pattern="^(1m|3m|6m|1y)$"),
    user_id: str = Depends(get_current_user),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    history = await risk_score_repository.get_score_history(
        user_id, time_range=range
    )
    items = [
        RiskScoreHistoryItem(
            score=h["score"],
            category=h["category"],
            timestamp=h["timestamp"],
        )
        for h in history
    ]
    return RiskScoreHistoryResponse(history=items, total=len(items))


@router.get("/risk-score/tips", response_model=RiskTipsResponse)
@limiter.limit("10/minute")
async def get_risk_tips(
    request: Request,
    user_id: str = Depends(get_current_user),
    risk_score_service: RiskScoreService = Depends(),
):
    tips = await risk_score_service.get_tips(user_id)
    return RiskTipsResponse(tips=tips)


@router.put(
    "/risk-score/profile",
    response_model=UserHealthProfileResponse,
)
@limiter.limit("10/minute")
async def update_health_profile(
    request: Request,
    input_data: UserHealthProfile,
    user_id: str = Depends(get_current_user),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    profile = await risk_score_repository.upsert_profile(
        user_id, input_data.model_dump(exclude_none=True)
    )
    pid = str(profile.pop("_id"))
    return UserHealthProfileResponse(
        _id=pid,
        user_id=profile["userId"],
        bmi=profile.get("bmi"),
        exercise_frequency=profile.get("exercise_frequency"),
        diet_type=profile.get("diet_type"),
        smoking_status=profile.get("smoking_status"),
        sleep_hours=profile.get("sleep_hours"),
        existing_conditions=profile.get("existing_conditions", []),
        updated_at=profile.get("updatedAt", ""),
    )


@router.get(
    "/risk-score/profile",
    response_model=UserHealthProfileResponse | None,
)
@limiter.limit("10/minute")
async def get_health_profile(
    request: Request,
    user_id: str = Depends(get_current_user),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    profile = await risk_score_repository.get_profile(user_id)
    if not profile:
        return None
    pid = str(profile.pop("_id"))
    return UserHealthProfileResponse(
        _id=pid,
        user_id=profile["userId"],
        bmi=profile.get("bmi"),
        exercise_frequency=profile.get("exercise_frequency"),
        diet_type=profile.get("diet_type"),
        smoking_status=profile.get("smoking_status"),
        sleep_hours=profile.get("sleep_hours"),
        existing_conditions=profile.get("existing_conditions", []),
        updated_at=profile.get("updatedAt", ""),
    )
