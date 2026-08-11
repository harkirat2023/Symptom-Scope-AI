from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from typing import Optional, List
from schemas.recovery_schema import (
    RecoveryPlanResponse,
    RecoveryPlanListResponse,
    RecoveryPlanRegenerateRequest,
    RecoveryPlanCreate,
)
from services.llm_service import LLMService
from repositories.recovery_repository import RecoveryPlanRepository
from repositories.prediction_repository import PredictionRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter
from bson.objectid import ObjectId
from bson.errors import InvalidId
import json

router = APIRouter()


class RecoveryPlanGenerateRequest(BaseModel):
    prediction_id: str


@router.post("/recovery-plan/generate", response_model=RecoveryPlanResponse)
@limiter.limit("5/minute")
async def generate_recovery_plan(
    request: Request,
    input_data: RecoveryPlanGenerateRequest,
    user_id: str = Depends(get_current_user),
    llm_service: LLMService = Depends(),
    recovery_repo: RecoveryPlanRepository = Depends(),
    prediction_repo: PredictionRepository = Depends(),
):
    # Validate prediction_id is a valid ObjectId
    try:
        ObjectId(input_data.prediction_id)
    except (InvalidId, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prediction ID format"
        )

    # Get the prediction
    pred = await prediction_repo.find_by_id(input_data.prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if pred.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Build context for LLM
    context = {
        "disease": pred.get("prediction", "unknown"),
        "confidence": pred.get("confidence", 0),
        "severity": pred.get("severity", "unknown"),
        "symptoms": pred.get("symptoms", []),
        "age": pred.get("age"),
        "gender": pred.get("gender"),
        "existing_conditions": pred.get("existing_conditions", []),
        "symptom_duration": pred.get("symptom_duration", ""),
        "pain_level": pred.get("pain_level"),
    }

    # Generate recovery plan using LLM
    prompt = f"""Generate a comprehensive, evidence-based recovery plan for a patient with {context['disease']}.

Patient Context:
- Condition: {context['disease']}
- Confidence: {context['confidence']}%
- Severity: {context['severity']}
- Symptoms: {', '.join(context['symptoms'])}
- Age: {context['age'] or 'Not specified'}
- Gender: {context['gender'] or 'Not specified'}
- Existing Conditions: {', '.join(context['existing_conditions']) or 'None'}
- Symptom Duration: {context['symptom_duration'] or 'Not specified'}
- Pain Level: {context['pain_level'] or 'Not specified'}

Return a JSON object with these exact fields:
{{
  "recovery_timeline": ["Week 1: ...", "Week 2: ...", "Week 3-4: ...", "Month 2+: ..."],
  "diet_recommendations": {{"general_principles": "...", "specific_nutrients": "..."}},
  "foods_to_eat": ["Food 1 - reason", "Food 2 - reason", "Food 3 - reason"],
  "foods_to_avoid": ["Food 1 - reason", "Food 2 - reason", "Food 3 - reason"],
  "hydration_advice": "Specific hydration guidance",
  "sleep_recommendation": "Specific sleep guidance",
  "exercise_recommendation": "Specific exercise guidance",
  "daily_physical_activity": ["Activity 1", "Activity 2", "Activity 3"],
  "lifestyle_changes": ["Change 1", "Change 2", "Change 3"],
  "medicines_disclaimer": "Standard medical disclaimer",
  "when_to_visit_doctor": ["Sign 1", "Sign 2", "Sign 3"],
  "emergency_warning_signs": ["Sign 1", "Sign 2", "Sign 3"],
  "mental_wellness_tips": ["Tip 1", "Tip 2", "Tip 3"],
  "recovery_checklist": ["Item 1", "Item 2", "Item 3"],
  "progress_tracker": {{"week_1": "Goals", "week_2": "Goals", "week_3": "Goals", "week_4": "Goals"}}
}}

Be specific, evidence-based, and educational. Always include medical disclaimers."""

    try:
        result = await llm_service.invoke(prompt, "")
        plan_data = json.loads(result)
    except Exception as e:
        # Fallback to structured defaults
        plan_data = _get_default_plan(context)

    # Save to database
    plan = await recovery_repo.create(
        user_id=user_id,
        prediction_id=input_data.prediction_id,
        disease=context["disease"],
        confidence=context["confidence"],
        severity=context["severity"],
        symptoms=context["symptoms"],
        plan_data=plan_data,
    )

    return _format_plan_response(plan)


@router.get("/recovery-plan/latest", response_model=RecoveryPlanResponse)
@limiter.limit("10/minute")
async def get_latest_recovery_plan(
    request: Request,
    user_id: str = Depends(get_current_user),
    recovery_repo: RecoveryPlanRepository = Depends(),
):
    plan = await recovery_repo.find_latest_by_user(user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No recovery plan found")
    return _format_plan_response(plan)


@router.get("/recovery-plan/history", response_model=RecoveryPlanListResponse)
@limiter.limit("10/minute")
async def get_recovery_plan_history(
    request: Request,
    user_id: str = Depends(get_current_user),
    recovery_repo: RecoveryPlanRepository = Depends(),
):
    plans = await recovery_repo.find_by_user(user_id)
    return RecoveryPlanListResponse(
        plans=[_format_plan_response(p) for p in plans],
        total=len(plans),
    )


@router.post("/recovery-plan/regenerate", response_model=RecoveryPlanResponse)
@limiter.limit("3/minute")
async def regenerate_recovery_plan(
    request: Request,
    input_data: RecoveryPlanRegenerateRequest,
    user_id: str = Depends(get_current_user),
    llm_service: LLMService = Depends(),
    recovery_repo: RecoveryPlanRepository = Depends(),
    prediction_repo: PredictionRepository = Depends(),
):
    # Validate plan_id is a valid ObjectId
    try:
        ObjectId(input_data.plan_id)
    except (InvalidId, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recovery plan ID format"
        )

    plan = await recovery_repo.find_by_id(input_data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    if plan.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get original prediction for context
    pred = await prediction_repo.find_by_id(plan.get("predictionId"))
    if not pred:
        raise HTTPException(status_code=404, detail="Original prediction not found")

    context = {
        "disease": pred.get("prediction", "unknown"),
        "confidence": pred.get("confidence", 0),
        "severity": pred.get("severity", "unknown"),
        "symptoms": pred.get("symptoms", []),
        "age": pred.get("age"),
        "gender": pred.get("gender"),
        "existing_conditions": pred.get("existing_conditions", []),
        "symptom_duration": pred.get("symptom_duration", ""),
        "pain_level": pred.get("pain_level"),
    }

    prompt = f"""Generate a NEW comprehensive, evidence-based recovery plan for a patient with {context['disease']}.

Patient Context:
- Condition: {context['disease']}
- Confidence: {context['confidence']}%
- Severity: {context['severity']}
- Symptoms: {', '.join(context['symptoms'])}
- Age: {context['age'] or 'Not specified'}
- Gender: {context['gender'] or 'Not specified'}
- Existing Conditions: {', '.join(context['existing_conditions']) or 'None'}

Return a JSON object with the exact same structure as before. Provide fresh, varied recommendations."""

    try:
        result = await llm_service.invoke(prompt, "")
        plan_data = json.loads(result)
    except Exception:
        plan_data = _get_default_plan(context)

    updated_plan = await recovery_repo.regenerate_plan(input_data.plan_id, plan_data)
    if not updated_plan:
        raise HTTPException(status_code=500, detail="Failed to regenerate plan")

    return _format_plan_response(updated_plan)


def _get_default_plan(context: dict) -> dict:
    """Fallback plan if LLM fails."""
    return {
        "recovery_timeline": [
            "Week 1: Focus on rest, hydration, and symptom monitoring. Follow prescribed treatments.",
            "Week 2: Gradually increase activity as tolerated. Continue medication adherence.",
            "Week 3-4: Return to normal activities if symptoms have resolved. Maintain healthy habits.",
            "Month 2+: Focus on prevention and long-term wellness. Regular follow-ups as needed.",
        ],
        "diet_recommendations": {
            "general_principles": "Eat a balanced diet rich in fruits, vegetables, lean proteins, and whole grains.",
            "specific_nutrients": "Focus on vitamins C, D, zinc, and antioxidants for immune support.",
        },
        "foods_to_eat": [
            "Leafy greens (spinach, kale) - rich in vitamins and antioxidants",
            "Citrus fruits (oranges, lemons) - high in vitamin C",
            "Lean proteins (chicken, fish, legumes) - support tissue repair",
        ],
        "foods_to_avoid": [
            "Processed foods - may increase inflammation",
            "Excess sugar - can suppress immune function",
            "Alcohol - can interfere with recovery and medications",
        ],
        "hydration_advice": "Drink 8-10 glasses of water daily. Include herbal teas and broths. Monitor urine color.",
        "sleep_recommendation": "Aim for 7-9 hours of quality sleep. Maintain consistent sleep schedule. Limit screens before bed.",
        "exercise_recommendation": "Start with gentle walking 10-15 minutes daily. Increase gradually as energy returns. Avoid strenuous activity until cleared.",
        "daily_physical_activity": [
            "Morning: 10-minute gentle walk",
            "Afternoon: Light stretching or yoga",
            "Evening: Deep breathing exercises",
        ],
        "lifestyle_changes": [
            "Practice stress management (meditation, deep breathing)",
            "Maintain good hand hygiene",
            "Ensure adequate ventilation in living spaces",
        ],
        "medicines_disclaimer": "This plan is for educational purposes only. Always follow your healthcare provider's specific medication instructions. Never start, stop, or change medications without professional guidance.",
        "when_to_visit_doctor": [
            "Symptoms worsen or don't improve after 1 week",
            "New symptoms develop",
            "Side effects from medications occur",
        ],
        "emergency_warning_signs": [
            "Difficulty breathing or shortness of breath",
            "Chest pain or pressure",
            "Confusion or inability to stay awake",
        ],
        "mental_wellness_tips": [
            "Stay connected with supportive friends/family",
            "Practice mindfulness or meditation daily",
            "Limit exposure to stressful news",
        ],
        "recovery_checklist": [
            "Take medications as prescribed",
            "Stay hydrated throughout the day",
            "Get adequate rest and sleep",
            "Complete daily gentle movement",
        ],
        "progress_tracker": {
            "week_1": "Symptom monitoring, medication adherence, rest",
            "week_2": "Gradual activity increase, energy levels improving",
            "week_3": "Near-normal activity, residual symptoms minimal",
            "week_4": "Full recovery focus on prevention and wellness",
        },
    }


def _format_plan_response(plan: dict) -> dict:
    plan_data = plan.get("planData", {})
    return {
        "id": str(plan.get("_id", "")),
        "user_id": plan.get("userId", ""),
        "prediction_id": plan.get("predictionId", ""),
        "disease": plan.get("disease", ""),
        "confidence": plan.get("confidence", 0),
        "severity": plan.get("severity", ""),
        "symptoms": plan.get("symptoms", []),
        "recovery_timeline": plan_data.get("recovery_timeline", []),
        "diet_recommendations": plan_data.get("diet_recommendations", {}),
        "foods_to_eat": plan_data.get("foods_to_eat", []),
        "foods_to_avoid": plan_data.get("foods_to_avoid", []),
        "hydration_advice": plan_data.get("hydration_advice", ""),
        "sleep_recommendation": plan_data.get("sleep_recommendation", ""),
        "exercise_recommendation": plan_data.get("exercise_recommendation", ""),
        "daily_physical_activity": plan_data.get("daily_physical_activity", []),
        "lifestyle_changes": plan_data.get("lifestyle_changes", []),
        "medicines_disclaimer": plan_data.get("medicines_disclaimer", ""),
        "when_to_visit_doctor": plan_data.get("when_to_visit_doctor", []),
        "emergency_warning_signs": plan_data.get("emergency_warning_signs", []),
        "mental_wellness_tips": plan_data.get("mental_wellness_tips", []),
        "recovery_checklist": plan_data.get("recovery_checklist", []),
        "progress_tracker": plan_data.get("progress_tracker", {}),
        "created_at": plan.get("createdAt", ""),
        "updated_at": plan.get("updatedAt", ""),
        "version": plan.get("version", 1),
    }