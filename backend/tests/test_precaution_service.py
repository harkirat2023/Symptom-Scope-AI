from services.precaution_service import PrecautionService


class TestPrecautionService:
    def setup_method(self):
        self.service = PrecautionService()

    def test_known_disease_returns_precautions(self):
        precautions = self.service.get_precautions("Influenza")
        assert len(precautions) > 0
        assert any("Rest" in p for p in precautions)

    def test_unknown_disease_returns_fallback_by_severity(self):
        precautions = self.service.get_precautions("Unknown", severity="Severe")
        assert len(precautions) > 0
        assert any("immediate" in p.lower() for p in precautions)

    def test_unknown_disease_mild_fallback(self):
        precautions = self.service.get_precautions("Unknown", severity="Mild")
        assert any("Rest" in p for p in precautions)

    def test_unknown_disease_moderate_fallback(self):
        precautions = self.service.get_precautions("Unknown", severity="Moderate")
        assert any("appointment" in p.lower() for p in precautions)

    def test_allergic_reaction_precautions(self):
        precautions = self.service.get_precautions("Allergy")
        assert any("antihistamine" in p.lower() for p in precautions)

    def test_emergency_disease_has_emergency_advice(self):
        precautions = self.service.get_precautions("Heart Attack")
        assert any("emergency" in p.lower() for p in precautions)
