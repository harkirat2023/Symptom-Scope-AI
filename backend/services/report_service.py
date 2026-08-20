from datetime import UTC, datetime

from schemas.prediction_schema import PredictionRecord
from schemas.report_schema import ReportResponse


class ReportService:
    def generate_report(
        self,
        predictions: list[PredictionRecord],
        risk_score: float | None = None,
        risk_category: str | None = None,
    ) -> ReportResponse:
        severity_distribution = self._get_severity_distribution(predictions)
        return ReportResponse(
            generated_at=datetime.now(UTC).isoformat(),
            total_predictions=len(predictions),
            most_common_disease=self._get_most_common(predictions),
            avg_confidence=self._get_avg_confidence(predictions),
            severe_count=severity_distribution.get("Severe", 0),
            severity_distribution=severity_distribution,
            predictions=predictions,
            risk_score=risk_score,
            risk_category=risk_category,
        )

    def _get_most_common(self, predictions: list[PredictionRecord]) -> str:
        disease_counts: dict[str, int] = {}
        for p in predictions:
            disease_counts[p.prediction] = disease_counts.get(p.prediction, 0) + 1
        if not disease_counts:
            return ""
        return max(disease_counts, key=disease_counts.get)

    def _get_avg_confidence(self, predictions: list[PredictionRecord]) -> float:
        if not predictions:
            return 0.0
        total = sum(p.confidence for p in predictions)
        return round(total / len(predictions), 2)

    def _get_severity_distribution(
        self, predictions: list[PredictionRecord]
    ) -> dict[str, int]:
        distribution: dict[str, int] = {}
        for p in predictions:
            distribution[p.severity] = distribution.get(p.severity, 0) + 1
        return distribution
