from fastapi import APIRouter, Depends, Request
from schemas.prediction_schema import (
    SymptomInput,
    PredictionResponse,
    TopContributingSymptom,
    ShapExplanation,
    EmergencyInfo,
)
from schemas.doctor_schema import DoctorResponse
from services.prediction_service import PredictionService
from services.feature_engineering import FeatureEngineeringService
from services.severity_service import SeverityService
from services.precaution_service import PrecautionService
from services.emergency_service import EmergencyService
from services.doctor_service import DoctorService
from services.hospital_service import HospitalService
from services.explainability_service import ExplainabilityService
from services.risk_score_service import RiskScoreService
from repositories.prediction_repository import PredictionRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter
from services.analytics_service import invalidate_user_cache

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
@limiter.limit("10/minute")
async def predict_symptoms(
    request: Request,
    input_data: SymptomInput,
    user_id: str = Depends(get_current_user),
    prediction_service: PredictionService = Depends(),
    feature_service: FeatureEngineeringService = Depends(),
    severity_service: SeverityService = Depends(),
    precaution_service: PrecautionService = Depends(),
    emergency_service: EmergencyService = Depends(),
    doctor_service: DoctorService = Depends(),
    hospital_service: HospitalService = Depends(),
    explainability_service: ExplainabilityService = Depends(),
    prediction_repository: PredictionRepository = Depends(),
    risk_score_service: RiskScoreService = Depends(),
):
    encoded_features = feature_service.encode_symptoms(input_data.symptoms)
    prediction_result = prediction_service.predict(encoded_features)
    disease = prediction_result.primary_prediction
    confidence = prediction_result.confidence

    severity = severity_service.classify(disease, confidence)
    precautions = precaution_service.get_precautions(disease, severity)
    emergency = emergency_service.detect(disease, confidence, severity)
    recommended_specialist = await doctor_service.get_specialty_for_disease(disease)
    doctor_recommendations_raw = await doctor_service.get_recommendations(disease=disease, limit=3)
    doctor_recommendations = [DoctorResponse(**d) for d in doctor_recommendations_raw]
    confidence_info = prediction_service.get_confidence_info(confidence)
    explanation_summary = prediction_service.generate_explanation_summary(
        disease, confidence, prediction_result.alternatives, prediction_result.top_contributing_symptoms
    )

    shap_result = explainability_service.build_contributing_symptoms(
        encoded_features,
        prediction_result.predicted_class_idx,
        prediction_result.top_probability,
    )

    top_symptoms = [
        TopContributingSymptom(
            symptom=s["symptom"],
            importance=s["importance"],
            shap_value=s.get("shap_value"),
            relative_contribution_pct=s.get("relative_contribution_pct"),
        )
        for s in shap_result["top_contributing_symptoms"]
    ]

    shap_explanation = ShapExplanation(
        base_value=shap_result["base_value"],
        feature_values=top_symptoms,
    )

    prediction_record = await prediction_repository.create(
        user_id=user_id,
        symptoms=input_data.symptoms,
        prediction=disease,
        confidence=confidence,
        severity=severity,
        age=input_data.age,
        gender=input_data.gender,
        existing_conditions=input_data.existing_conditions,
        symptom_duration=input_data.symptom_duration,
        pain_level=input_data.pain_level,
    )

    invalidate_user_cache(user_id)

    try:
        history = await prediction_repository.find_by_user(user_id)
        predictions_for_risk = [
            {
                "severity": p.severity,
                "confidence": p.confidence,
                "prediction": p.prediction,
            }
            for p in history
        ]
        score, category, _ = await risk_score_service.compute_and_save(
            user_id=user_id,
            prediction_history=predictions_for_risk,
            most_recent_severity=severity,
            prediction_id=prediction_record.id,
        )
    except Exception:
        score, category = None, None

    return PredictionResponse(
        primary_prediction=disease,
        confidence=confidence,
        alternatives=prediction_result.alternatives,
        severity=severity,
        top_contributing_symptoms=top_symptoms,
        precautions=precautions,
        emergency=EmergencyInfo(
            is_emergency=emergency["is_emergency"],
            reasons=emergency["reasons"],
            explanation=emergency.get("explanation", ""),
            severity_triggered=emergency.get("severity_triggered", False),
            confidence_triggered=emergency.get("confidence_triggered", False),
            escalation_triggered=emergency.get("escalation_triggered", False),
        ),
        prediction_id=prediction_record.id,
        recommended_specialist=recommended_specialist,
        doctor_recommendations=doctor_recommendations,
        explanation_summary=explanation_summary,
        confidence_info=confidence_info,
        shap_explanation=shap_explanation,
        risk_score=score,
        risk_category=category,
    )
