from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.report_schema import ReportResponse
from services.report_service import ReportService
from repositories.prediction_repository import PredictionRepository
from repositories.risk_score_repository import RiskScoreRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.get("/reports/{user_id}", response_model=ReportResponse)
@limiter.limit("10/minute")
async def get_report(
    request: Request,
    user_id: str,
    auth_user_id: str = Depends(get_current_user),
    report_service: ReportService = Depends(),
    prediction_repository: PredictionRepository = Depends(),
    risk_score_repository: RiskScoreRepository = Depends(),
):
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Access denied"
        )
    prediction_records = await prediction_repository.find_by_user(user_id)
    if not prediction_records:
        raise HTTPException(
            status_code=404, detail="No predictions found for this user"
        )

    risk_score = None
    risk_category = None
    try:
        latest_risk = await risk_score_repository.get_latest_score(user_id)
        if latest_risk:
            risk_score = latest_risk["score"]
            risk_category = latest_risk["category"]
    except Exception:
        pass

    return report_service.generate_report(
        prediction_records,
        risk_score=risk_score,
        risk_category=risk_category,
    )
