from services.severity_service import SeverityService


class TestSeverityService:
    def setup_method(self):
        self.service = SeverityService()

    def test_classify_mild(self):
        assert self.service.classify("Common Cold") == "Mild"
        assert self.service.classify("Allergy") == "Mild"
        assert self.service.classify("Urinary Tract Infection") == "Mild"

    def test_classify_moderate(self):
        assert self.service.classify("Influenza") == "Moderate"
        assert self.service.classify("Bronchitis") == "Moderate"
        assert self.service.classify("Gastroenteritis") == "Moderate"
        assert self.service.classify("Migraine") == "Moderate"

    def test_classify_severe(self):
        assert self.service.classify("Pneumonia") == "Severe"
        assert self.service.classify("Heart Attack") == "Severe"
        assert self.service.classify("Stroke") == "Severe"
        assert self.service.classify("Malaria") == "Severe"
        assert self.service.classify("Dengue") == "Severe"

    def test_unknown_disease_defaults_to_moderate(self):
        assert self.service.classify("Unknown Disease") == "Moderate"

    def test_covid_escalates_at_high_confidence(self):
        assert self.service.classify("COVID-19", confidence=50.0) == "Moderate"
        assert self.service.classify("COVID-19", confidence=85.0) == "Severe"
        assert self.service.classify("COVID-19", confidence=95.0) == "Severe"

    def test_covid_low_confidence_stays_moderate(self):
        assert self.service.classify("COVID-19", confidence=50.0) == "Moderate"
        assert self.service.classify("COVID-19", confidence=84.9) == "Moderate"
