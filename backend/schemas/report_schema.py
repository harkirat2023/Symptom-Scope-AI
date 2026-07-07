from pydantic import BaseModel
from schemas.prediction_schema import PredictionRecord


class ReportResponse(BaseModel):
    generated_at: str
    total_predictions: int
    most_common_disease: str
    avg_confidence: float
    severe_count: int
    severity_distribution: dict[str, int]
    predictions: list[PredictionRecord]
    risk_score: float | None = None
    risk_category: str | None = None
