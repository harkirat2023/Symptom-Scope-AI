from datetime import datetime, timezone
from services.report_service import ReportService
from schemas.prediction_schema import PredictionRecord


def make_record(prediction="Flu", confidence=80.0, severity="Moderate"):
    return PredictionRecord(
        _id="test-id",
        user_id="user-1",
        symptoms=["fever", "cough"],
        prediction=prediction,
        confidence=confidence,
        severity=severity,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


class TestReportService:
    def setup_method(self):
        self.service = ReportService()

    def test_generate_empty_report(self):
        report = self.service.generate_report([])
        assert report.total_predictions == 0
        assert report.most_common_disease == ""
        assert report.avg_confidence == 0.0
        assert report.severe_count == 0
        assert report.severity_distribution == {}

    def test_generate_single_prediction(self):
        record = make_record()
        report = self.service.generate_report([record])
        assert report.total_predictions == 1
        assert report.most_common_disease == "Flu"
        assert report.avg_confidence == 80.0

    def test_most_common_disease(self):
        records = [
            make_record(prediction="Flu"),
            make_record(prediction="Flu"),
            make_record(prediction="Cold"),
        ]
        report = self.service.generate_report(records)
        assert report.most_common_disease == "Flu"

    def test_average_confidence(self):
        records = [
            make_record(confidence=90.0),
            make_record(confidence=70.0),
        ]
        report = self.service.generate_report(records)
        assert report.avg_confidence == 80.0

    def test_severity_distribution(self):
        records = [
            make_record(severity="Mild"),
            make_record(severity="Mild"),
            make_record(severity="Severe"),
        ]
        report = self.service.generate_report(records)
        assert report.severity_distribution == {"Mild": 2, "Severe": 1}
        assert report.severe_count == 1

    def test_generated_at_is_set(self):
        report = self.service.generate_report([])
        assert report.generated_at is not None
