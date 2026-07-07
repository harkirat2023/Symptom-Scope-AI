import numpy as np
from datetime import datetime, timezone, timedelta
from schemas.risk_score_schema import RiskFactorBreakdown


def compute_risk_score(
    age: int | None = None,
    bmi: float | None = None,
    exercise_frequency: int | None = None,
    diet_type: str | None = None,
    smoking_status: str | None = None,
    sleep_hours: float | None = None,
    existing_conditions: list[str] | None = None,
    prediction_history: list[dict] | None = None,
    most_recent_severity: str | None = None,
) -> tuple[float, str, RiskFactorBreakdown]:
    score = 0.0
    breakdown = RiskFactorBreakdown()

    # Age factor (0–15 points)
    if age is not None:
        if age >= 60:
            age_score = 15
        elif age >= 45:
            age_score = 10
        elif age >= 30:
            age_score = 5
        else:
            age_score = 0
        breakdown.age_score = age_score
        score += age_score

    # BMI factor (0–10 points)
    if bmi is not None:
        if bmi >= 30:
            bmi_score = 10
        elif bmi >= 25:
            bmi_score = 5
        else:
            bmi_score = 0
        breakdown.bmi_score = bmi_score
        score += bmi_score

    # Lifestyle factor (0–10 points)
    lifestyle_score = 0
    if exercise_frequency is not None and exercise_frequency < 2:
        lifestyle_score += 5
    if diet_type in ("unhealthy", "irregular"):
        lifestyle_score += 5
    breakdown.lifestyle_score = lifestyle_score
    score += lifestyle_score

    # Smoking factor (0–15 points)
    if smoking_status == "current":
        smoking_score = 15
    elif smoking_status == "former":
        smoking_score = 8
    else:
        smoking_score = 0
    breakdown.smoking_score = smoking_score
    score += smoking_score

    # Sleep factor (0–10 points)
    if sleep_hours is not None:
        if sleep_hours < 5 or sleep_hours > 9:
            sleep_score = 10
        elif sleep_hours < 6 or sleep_hours > 8:
            sleep_score = 5
        else:
            sleep_score = 0
        breakdown.sleep_score = sleep_score
        score += sleep_score

    # Existing conditions (0–20 points)
    conditions = existing_conditions or []
    conditions_score = min(len(conditions) * 5, 20)
    breakdown.existing_conditions_score = conditions_score
    score += conditions_score

    # Prediction history factor (0–20 points)
    history_score = 0
    if prediction_history:
        severe_count = sum(
            1
            for p in prediction_history
            if p.get("severity") == "Severe"
        )
        moderate_count = sum(
            1
            for p in prediction_history
            if p.get("severity") == "Moderate"
        )
        mild_count = sum(
            1
            for p in prediction_history
            if p.get("severity") == "Mild"
        )
        history_score = max(0, min(
            severe_count * 5 + moderate_count * 3 - mild_count * 1,
            20,
        ))
    breakdown.prediction_history_score = history_score
    score += history_score

    # Severity trend (0–10 points)
    severity_score = 0
    if most_recent_severity == "Severe":
        severity_score = 10
    elif most_recent_severity == "Moderate":
        severity_score = 5
    breakdown.severity_trend_score = severity_score
    score += severity_score

    final_score = min(round(score, 1), 100)

    if final_score >= 67:
        category = "High"
    elif final_score >= 34:
        category = "Medium"
    else:
        category = "Low"

    return final_score, category, breakdown


def generate_risk_tips(
    breakdown: RiskFactorBreakdown,
    smoking_status: str | None = None,
    exercise_frequency: int | None = None,
    diet_type: str | None = None,
    sleep_hours: float | None = None,
    bmi: float | None = None,
) -> list[str]:
    tips = []

    if breakdown.smoking_score >= 8:
        tips.append(
            "Consider a smoking cessation program — it's the single best "
            "thing you can do for your health."
        )

    if breakdown.bmi_score >= 5:
        tips.append(
            "A balanced diet and regular exercise can help manage your "
            "BMI and reduce associated health risks."
        )

    if breakdown.lifestyle_score >= 5:
        if exercise_frequency is not None and exercise_frequency < 2:
            tips.append(
                "Aim for at least 150 minutes of moderate exercise per "
                "week to improve cardiovascular health."
            )
        if diet_type in ("unhealthy", "irregular"):
            tips.append(
                "Try incorporating more fruits, vegetables, and whole "
                "grains into your diet."
            )

    if breakdown.sleep_score >= 5:
        tips.append(
            "Adults should aim for 7–9 hours of quality sleep per night "
            "for optimal health."
        )

    if breakdown.existing_conditions_score > 0:
        tips.append(
            "Regular check-ups with your healthcare provider are important "
            "for managing existing conditions."
        )

    tips.append(
        "Use the Symptom Checker regularly to track changes in your "
        "health and detect issues early."
    )

    return tips


class RiskScoreService:
    def __init__(self):
        pass

    async def compute_and_save(
        self,
        user_id: str,
        age: int | None = None,
        prediction_history: list[dict] | None = None,
        most_recent_severity: str | None = None,
        prediction_id: str | None = None,
    ) -> tuple[float, str, RiskFactorBreakdown]:
        from repositories.risk_score_repository import RiskScoreRepository

        repo = RiskScoreRepository()
        profile = await repo.get_profile(user_id)

        bmi = profile.get("bmi") if profile else None
        exercise_frequency = (
            profile.get("exercise_frequency") if profile else None
        )
        diet_type = profile.get("diet_type") if profile else None
        smoking_status = profile.get("smoking_status") if profile else None
        sleep_hours = profile.get("sleep_hours") if profile else None
        existing_conditions = (
            profile.get("existing_conditions") if profile else []
        )

        score, category, breakdown = compute_risk_score(
            age=age,
            bmi=bmi,
            exercise_frequency=exercise_frequency,
            diet_type=diet_type,
            smoking_status=smoking_status,
            sleep_hours=sleep_hours,
            existing_conditions=existing_conditions,
            prediction_history=prediction_history,
            most_recent_severity=most_recent_severity,
        )

        await repo.save_score(
            user_id, score, category, breakdown.model_dump(), prediction_id
        )

        return score, category, breakdown

    async def get_tips(
        self, user_id: str
    ) -> list[str]:
        from repositories.risk_score_repository import RiskScoreRepository

        repo = RiskScoreRepository()
        profile = await repo.get_profile(user_id) or {}
        latest = await repo.get_latest_score(user_id)

        if not latest:
            return [
                "Complete your health profile and use the Symptom Checker "
                "to receive personalized risk reduction tips."
            ]

        breakdown_data = latest.get("breakdown", {})
        breakdown = RiskFactorBreakdown(**breakdown_data)

        return generate_risk_tips(
            breakdown=breakdown,
            smoking_status=profile.get("smoking_status"),
            exercise_frequency=profile.get("exercise_frequency"),
            diet_type=profile.get("diet_type"),
            sleep_hours=profile.get("sleep_hours"),
            bmi=profile.get("bmi"),
        )
