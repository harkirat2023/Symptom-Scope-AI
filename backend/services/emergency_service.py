from services.disease_registry import is_emergency_risk, get_escalation, DISEASE_REGISTRY

CRITICAL_CONFIDENCE_THRESHOLD = 90
MODERATE_ESCALATION_THRESHOLD = 95


class EmergencyService:
    def detect(self, disease: str, confidence: float, severity: str) -> dict:
        is_emergency = False
        reasons: list[str] = []
        explanation_details: list[str] = []

        disease_meta = DISEASE_REGISTRY.get(disease)

        if severity == "Severe":
            is_emergency = True
            if disease_meta:
                reasons.append(f"Severe condition detected: {disease}")
                explanation_details.append(
                    f"The predicted condition '{disease}' is classified as Severe. "
                    f"{disease_meta.description} "
                    "Severe conditions require immediate medical evaluation."
                )
            else:
                reasons.append("Severe condition detected")
                explanation_details.append(
                    "The predicted condition is classified as Severe and requires immediate medical evaluation."
                )

        disease_risk = is_emergency_risk(disease)
        if disease_risk and confidence > CRITICAL_CONFIDENCE_THRESHOLD:
            is_emergency = True
            reasons.append(
                f"High confidence ({confidence:.1f}%) critical disease detection"
            )
            if disease_meta:
                explanation_details.append(
                    f"The system is highly confident ({confidence:.1f}%) in predicting '{disease}', "
                    f"which is classified as a critical condition. {disease_meta.description}"
                )
            else:
                explanation_details.append(
                    f"The system is highly confident ({confidence:.1f}%) in predicting a critical condition."
                )

        escalation_severity, escalation_threshold = get_escalation(disease)
        if escalation_severity == "Severe" and escalation_threshold is not None and confidence >= escalation_threshold:
            is_emergency = True
            reasons.append(
                f"Disease severity escalated to Severe at {confidence:.1f}% confidence (threshold: {escalation_threshold}%)"
            )
            if disease_meta:
                explanation_details.append(
                    f"'{disease}' severity has been escalated to Severe based on high confidence "
                    f"({confidence:.1f}%). {disease_meta.description}"
                )

        if severity == "Moderate" and confidence > MODERATE_ESCALATION_THRESHOLD:
            is_emergency = True
            reasons.append(
                f"Very high confidence ({confidence:.1f}%) warrants immediate medical evaluation"
            )
            explanation_details.append(
                f"Although '{disease}' is classified as Moderate severity, the very high confidence "
                f"({confidence:.1f}%) suggests this case may require urgent medical evaluation."
            )

        if not explanation_details and is_emergency:
            explanation_details.append(
                f"Emergency detected for '{disease}' (Severity: {severity}, Confidence: {confidence:.1f}%). "
                "Please seek immediate medical attention."
            )

        if not is_emergency:
            explanation_details.append(
                f"The predicted condition '{disease}' is classified as {severity} severity "
                f"with {confidence:.1f}% confidence. Emergency criteria are not met, "
                "but continue monitoring your symptoms."
            )

        return {
            "is_emergency": is_emergency,
            "reasons": reasons,
            "explanation": " ".join(explanation_details),
            "severity_triggered": severity == "Severe",
            "confidence_triggered": disease_risk and confidence > CRITICAL_CONFIDENCE_THRESHOLD,
            "escalation_triggered": escalation_severity == "Severe" and escalation_threshold is not None and confidence >= escalation_threshold,
        }
