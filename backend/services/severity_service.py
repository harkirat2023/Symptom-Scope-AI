from services.disease_registry import (
    DISEASE_REGISTRY,
    SEVERITY_ORDER,
    get_severity,
    get_escalation,
)

SEVERITY_LEVELS = ("Mild", "Moderate", "Severe")

SEVERITY_DESCRIPTIONS: dict[str, str] = {
    "Mild": (
        "Mild conditions are typically self-limiting and can be managed "
        "with rest, hydration, and over-the-counter remedies. "
        "Medical attention is recommended if symptoms persist or worsen."
    ),
    "Moderate": (
        "Moderate conditions require medical evaluation and may need "
        "prescription treatment. Monitor symptoms closely and "
        "consult a healthcare provider if they do not improve."
    ),
    "Severe": (
        "Severe conditions require immediate medical attention. "
        "Do not delay — seek emergency care or contact a healthcare "
        "professional right away."
    ),
}


class SeverityService:
    def classify(self, disease: str, confidence: float = 0.0) -> str:
        base = get_severity(disease)
        escalation_severity, escalation_threshold = get_escalation(disease)
        if escalation_severity is not None and escalation_threshold is not None:
            if confidence >= escalation_threshold:
                return escalation_severity
        if base not in SEVERITY_LEVELS:
            return "Moderate"
        return base

    def is_more_severe(self, severity_a: str, severity_b: str) -> bool:
        return SEVERITY_ORDER.get(severity_a, 0) > SEVERITY_ORDER.get(severity_b, 0)

    def get_all_disease_severities(self) -> dict[str, str]:
        return {name: meta.severity for name, meta in DISEASE_REGISTRY.items()}

    def get_severity_description(self, severity: str) -> str:
        return SEVERITY_DESCRIPTIONS.get(severity, "")
