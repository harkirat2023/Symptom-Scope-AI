from services.emergency_service import EmergencyService


class TestEmergencyService:
    def setup_method(self):
        self.service = EmergencyService()

    def test_severe_severity_triggers_emergency(self):
        result = self.service.detect("Pneumonia", 80.0, "Severe")
        assert result["is_emergency"] is True
        assert any("Severe condition detected" in r for r in result["reasons"])

    def test_critical_disease_high_confidence_triggers_emergency(self):
        result = self.service.detect("Stroke", 95.0, "Moderate")
        assert result["is_emergency"] is True
        assert any("critical" in r.lower() for r in result["reasons"])

    def test_moderate_escalation_threshold(self):
        result = self.service.detect("Influenza", 96.0, "Moderate")
        assert result["is_emergency"] is True
        assert any("immediate" in r.lower() for r in result["reasons"])

    def test_no_emergency_normal_case(self):
        result = self.service.detect("Common Cold", 70.0, "Mild")
        assert result["is_emergency"] is False
        assert result["reasons"] == []

    def test_critical_disease_low_confidence_no_emergency(self):
        result = self.service.detect("Heart Attack", 50.0, "Mild")
        assert result["is_emergency"] is False

    def test_severe_overrides_moderate_logic(self):
        result = self.service.detect("Stroke", 50.0, "Severe")
        assert result["is_emergency"] is True
        assert any("Severe condition detected" in r for r in result["reasons"])
