from datetime import datetime, timezone, timedelta
from services.analytics_service import AnalyticsService
from schemas.prediction_schema import PredictionRecord


def make_record(
    prediction="Influenza",
    confidence=80.0,
    severity="Moderate",
    symptoms=None,
    days_ago=0,
):
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return PredictionRecord(
        _id=f"id-{days_ago}",
        user_id="user-1",
        symptoms=symptoms or ["fever", "cough"],
        prediction=prediction,
        confidence=confidence,
        severity=severity,
        timestamp=ts,
    )


class TestAnalyticsService:
    def setup_method(self):
        self.service = AnalyticsService()

    def test_empty_predictions_returns_empty_response(self):
        result = self.service.compute([])
        assert result["summary"]["total_predictions"] == 0
        assert result["summary"]["most_common_disease"] == ""
        assert result["health_summary"] is None

    def test_single_prediction(self):
        records = [make_record()]
        result = self.service.compute(records)
        assert result["summary"]["total_predictions"] == 1
        assert result["summary"]["most_common_disease"] == "Influenza"
        assert result["summary"]["average_confidence"] == 80.0
        assert result["disease_frequency"][0]["disease"] == "Influenza"

    def test_disease_frequency(self):
        records = [
            make_record(prediction="Influenza"),
            make_record(prediction="Influenza"),
            make_record(prediction="Common Cold"),
        ]
        result = self.service.compute(records)
        assert len(result["disease_frequency"]) == 2
        assert result["disease_frequency"][0]["disease"] == "Influenza"
        assert result["disease_frequency"][0]["count"] == 2

    def test_severity_breakdown(self):
        records = [
            make_record(severity="Mild"),
            make_record(severity="Moderate"),
            make_record(severity="Severe"),
        ]
        result = self.service.compute(records)
        severities = {s["severity"]: s["count"] for s in result["severity_breakdown"]}
        assert severities["Mild"] == 1
        assert severities["Moderate"] == 1
        assert severities["Severe"] == 1

    def test_time_range_filters_older_records(self):
        records = [
            make_record(days_ago=5),
            make_record(days_ago=200),
        ]
        result = self.service.compute(records, time_range="1m")
        assert result["summary"]["total_predictions"] == 1

    def test_symptom_insights(self):
        records = [
            make_record(symptoms=["fever", "cough"]),
            make_record(symptoms=["fever", "headache"]),
        ]
        result = self.service.compute(records)
        assert len(result["symptom_insights"]["top_symptoms"]) > 0

    def test_health_summary_returns_none_for_empty(self):
        result = self.service.compute([])
        assert result["health_summary"] is None

    def test_insights_generated_for_data(self):
        records = [make_record() for _ in range(5)]
        result = self.service.compute(records)
        assert len(result["insights"]) > 0

    def test_empty_insights_for_no_data(self):
        result = self.service.compute([])
        assert "No prediction data yet" in result["insights"][0]
