from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import Response
from auth.dependency import get_current_user
from repositories.prediction_repository import PredictionRepository
from repositories.risk_score_repository import RiskScoreRepository
from services.report_export_service import ReportExportService
from utils.rate_limit import limiter

router = APIRouter()


async def _get_risk_data(
    user_id: str,
    risk_score_repository: RiskScoreRepository,
) -> tuple[float | None, str | None]:
    try:
        latest = await risk_score_repository.get_latest_score(user_id)
        if latest:
            return latest["score"], latest["category"]
    except Exception:
        pass
    return None, None


@router.get("/export/csv/{user_id}")
@limiter.limit("10/minute")
async def export_csv(
    request: Request,
    user_id: str,
    summary: bool = Query(False, description="Include summary section"),
    auth_user_id: str = Depends(get_current_user),
    prediction_repository: PredictionRepository = Depends(),
    risk_score_repository: RiskScoreRepository = Depends(),
    export_service: ReportExportService = Depends(),
):
    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    predictions = await prediction_repository.find_by_user(user_id)
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this user")

    risk_score, risk_category = await _get_risk_data(user_id, risk_score_repository)

    if summary:
        csv_content = export_service.generate_csv_summary(
            predictions, risk_score=risk_score, risk_category=risk_category
        )
    else:
        csv_content = export_service.generate_csv(predictions)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=symptomscope_report_{user_id[:8]}.csv",
        },
    )


@router.get("/export/pdf/{user_id}")
@limiter.limit("10/minute")
async def export_pdf(
    request: Request,
    user_id: str,
    detailed: bool = Query(False, description="Generate detailed per-prediction report"),
    auth_user_id: str = Depends(get_current_user),
    prediction_repository: PredictionRepository = Depends(),
    risk_score_repository: RiskScoreRepository = Depends(),
    export_service: ReportExportService = Depends(),
):
    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    predictions = await prediction_repository.find_by_user(user_id)
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this user")

    risk_score, risk_category = await _get_risk_data(user_id, risk_score_repository)

    try:
        if detailed:
            pdf_bytes = export_service.generate_pdf_detailed(predictions)
        else:
            pdf_bytes = export_service.generate_pdf(
                predictions, risk_score=risk_score, risk_category=risk_category
            )
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=symptomscope_report_{user_id[:8]}.pdf",
        },
    )
