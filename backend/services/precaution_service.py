from services.disease_registry import get_precautions, FALLBACK_PRECAUTIONS_BY_SEVERITY


class PrecautionService:
    def get_precautions(self, disease: str, severity: str = "Moderate") -> list[str]:
        precautions = get_precautions(disease)
        if precautions:
            sorted_precautions = sorted(precautions, key=lambda p: p.priority)
            return [p.text for p in sorted_precautions]
        fallback = FALLBACK_PRECAUTIONS_BY_SEVERITY.get(severity)
        if fallback:
            return [p.text for p in sorted(fallback, key=lambda p: p.priority)]
        return ["Consult a healthcare professional for guidance"]

    def get_precautions_with_priority(self, disease: str, severity: str = "Moderate") -> list[dict]:
        precautions = get_precautions(disease)
        if precautions:
            return [
                {"text": p.text, "priority": p.priority}
                for p in sorted(precautions, key=lambda x: x.priority)
            ]
        fallback = FALLBACK_PRECAUTIONS_BY_SEVERITY.get(severity, [])
        return [
            {"text": p.text, "priority": p.priority}
            for p in sorted(fallback, key=lambda x: x.priority)
        ]
