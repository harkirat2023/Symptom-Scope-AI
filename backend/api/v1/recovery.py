from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from typing import Any, Dict, List

from schemas.recovery_schema import (
    RecoveryPlanResponse,
    RecoveryPlanListResponse,
    RecoveryPlanRegenerateRequest,
)
from schemas.prediction_schema import PredictionRecord
from services.llm_service import LLMService
from repositories.recovery_repository import RecoveryPlanRepository
from repositories.prediction_repository import PredictionRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter
from bson.objectid import ObjectId
from bson.errors import InvalidId
import json
import logging

logger = logging.getLogger("symptomscope.api.recovery")

router = APIRouter()


class RecoveryPlanGenerateRequest(BaseModel):
    prediction_id: str


def _prediction_context(pred: PredictionRecord) -> Dict[str, Any]:
    """Build the LLM context from a PredictionRecord."""
    return {
        "disease": pred.prediction or "unknown",
        "confidence": pred.confidence or 0,
        "severity": pred.severity or "unknown",
        "symptoms": pred.symptoms or [],
        "age": pred.age,
        "gender": pred.gender,
        "existing_conditions": pred.existing_conditions or [],
        "symptom_duration": pred.symptom_duration,
        "pain_level": pred.pain_level,
    }


def _extract_json(text: str) -> dict:
    """Robustly extract a JSON object from an LLM response.

    Strips surrounding markdown code fences and locates the outermost
    JSON object so small formatting deviations do not break parsing.
    """
    if not text:
        raise ValueError("Empty LLM response")
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response")

    payload = stripped[start : end + 1]
    return json.loads(payload)


def _build_prompt(context: Dict[str, Any]) -> str:
    return f"""Generate a comprehensive, evidence-based, educational recovery plan for a patient predicted to have {context['disease']}.

Patient Context:
- Condition: {context['disease']}
- Confidence: {context['confidence']}%
- Severity: {context['severity']}
- Symptoms: {', '.join(context['symptoms']) or 'Not specified'}
- Age: {context['age'] or 'Not specified'}
- Gender: {context['gender'] or 'Not specified'}
- Existing Conditions: {', '.join(context['existing_conditions']) or 'None'}
- Symptom Duration: {context['symptom_duration'] or 'Not specified'}
- Pain Level: {context['pain_level'] or 'Not specified'}

Return a JSON object with EXACTLY these fields:
{{
  "what_it_means": "Plain-language explanation of what the predicted condition is and what it means for the patient",
  "what_to_do": ["Immediate action 1", "Immediate action 2", "Immediate action 3"],
  "recovery_timeline": ["Week 1: ...", "Week 2: ...", "Week 3-4: ...", "Month 2+: ..."],
  "diet_recommendations": {{"general_principles": "...", "specific_nutrients": "..."}},
  "foods_to_eat": ["Food 1 - reason", "Food 2 - reason", "Food 3 - reason"],
  "foods_to_avoid": ["Food 1 - reason", "Food 2 - reason", "Food 3 - reason"],
  "hydration_advice": "Specific hydration guidance",
  "sleep_recommendation": "Specific rest and sleep guidance",
  "exercise_recommendation": "Specific exercise and physical activity guidance",
  "daily_physical_activity": ["Activity 1", "Activity 2", "Activity 3"],
  "lifestyle_changes": ["Change 1", "Change 2", "Change 3"],
  "personalized_recommendations": ["Personalized recommendation 1", "Personalized recommendation 2", "Personalized recommendation 3"],
  "medicines_disclaimer": "Standard medical disclaimer",
  "when_to_visit_doctor": ["Sign 1", "Sign 2", "Sign 3"],
  "emergency_warning_signs": ["Sign 1", "Sign 2", "Sign 3"],
  "mental_wellness_tips": ["Tip 1", "Tip 2", "Tip 3"],
  "recovery_checklist": ["Item 1", "Item 2", "Item 3"],
  "progress_tracker": {{"week_1": "Goals", "week_2": "Goals", "week_3": "Goals", "week_4": "Goals"}}
}}

Rules:
- Be specific, evidence-based, and educational.
- Do NOT invent medications, dosages, doctor credentials, hospital names, or emergency numbers.
- Always include medical disclaimers and emphasize this is educational guidance, not a diagnosis or treatment plan."""


def _merge_plan_data(generated: dict, context: Dict[str, Any]) -> dict:
    """Merge the LLM output with the structured fallback so every section exists."""
    defaults = _get_default_plan(context)
    merged = dict(defaults)
    for key, value in generated.items():
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        if isinstance(value, dict) and not value:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        merged[key] = value
    return merged


async def _notify_recovery_plan_email(user_id: str, disease: str) -> None:
    """Config-gated notification email when a recovery plan is ready."""
    from services.email_service import EmailService
    from utils.database import get_database

    try:
        profile = await get_database()["user_health_profiles"].find_one(
            {"userId": user_id}
        )
    except Exception:
        profile = None
    email = profile.get("email") if profile else None
    if not email:
        return
    try:
        await EmailService().send_recovery_plan_email(email, disease)
    except Exception as e:
        logger.warning("Recovery plan email skipped: %s", e)


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
    except (InvalidId, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prediction ID format",
        )

    # Get the prediction
    pred = await prediction_repo.find_by_id(input_data.prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if pred.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    context = _prediction_context(pred)

    try:
        result = await llm_service.invoke(_build_prompt(context), "", json_mode=True)
        plan_data = _merge_plan_data(_extract_json(result), context)
    except Exception as e:
        logger.warning("Recovery plan LLM generation failed (%s); using fallback", e)
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

    await _notify_recovery_plan_email(user_id, context["disease"])

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
    except (InvalidId, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recovery plan ID format",
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

    context = _prediction_context(pred)

    prompt = (
        "Generate a NEW comprehensive, evidence-based recovery plan for a patient with "
        f"{context['disease']}.\n\n"
        "Patient Context:\n"
        f"- Condition: {context['disease']}\n"
        f"- Confidence: {context['confidence']}%\n"
        f"- Severity: {context['severity']}\n"
        f"- Symptoms: {', '.join(context['symptoms'])}\n"
        f"- Age: {context['age'] or 'Not specified'}\n"
        f"- Gender: {context['gender'] or 'Not specified'}\n"
        f"- Existing Conditions: {', '.join(context['existing_conditions']) or 'None'}\n\n"
        "Return a JSON object with the exact same structure as the original plan. "
        "Provide fresh, varied recommendations. Do not invent medications, dosages, "
        "doctor credentials, hospital names, or emergency numbers. Always include "
        "medical disclaimers."
    )

    try:
        result = await llm_service.invoke(prompt, "", json_mode=True)
        plan_data = _merge_plan_data(_extract_json(result), context)
    except Exception:
        plan_data = _get_default_plan(context)

    updated_plan = await recovery_repo.regenerate_plan(input_data.plan_id, plan_data)
    if not updated_plan:
        raise HTTPException(status_code=500, detail="Failed to regenerate plan")

    return _format_plan_response(updated_plan)


def _get_default_plan(context: Dict[str, Any]) -> dict:
    """Fallback plan if LLM fails. Educational, conservative, never fabricates facts."""
    disease = context.get("disease", "the predicted condition")
    return {
        "what_it_means": (
            f"Your assessment indicates a possible case of {disease}. "
            "This is an educational summary of what that condition generally involves "
            "and how to support your recovery while you consult a healthcare professional."
        ),
        "what_to_do": [
            "Follow the advice of your healthcare provider for any prescribed treatment.",
            "Monitor your symptoms daily and note any changes.",
            "Rest, hydrate, and eat nutritious meals to support recovery.",
        ],
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
        "sleep_recommendation": "Aim for 7-9 hours of quality sleep. Maintain a consistent sleep schedule and limit screens before bed.",
        "exercise_recommendation": "Start with gentle walking for 10-15 minutes daily and increase gradually as energy returns. Avoid strenuous activity until cleared by a professional.",
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
        "personalized_recommendations": [
            "Keep a daily symptom diary to share with your doctor.",
            "Re-run the symptom checker if new symptoms appear.",
            "Schedule a follow-up with your primary care provider for a clinical assessment.",
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
        "what_it_means": plan_data.get("what_it_means", ""),
        "what_to_do": plan_data.get("what_to_do", []),
        "recovery_timeline": plan_data.get("recovery_timeline", []),
        "diet_recommendations": plan_data.get("diet_recommendations", {}),
        "foods_to_eat": plan_data.get("foods_to_eat", []),
        "foods_to_avoid": plan_data.get("foods_to_avoid", []),
        "hydration_advice": plan_data.get("hydration_advice", ""),
        "sleep_recommendation": plan_data.get("sleep_recommendation", ""),
        "exercise_recommendation": plan_data.get("exercise_recommendation", ""),
        "daily_physical_activity": plan_data.get("daily_physical_activity", []),
        "lifestyle_changes": plan_data.get("lifestyle_changes", []),
        "personalized_recommendations": plan_data.get("personalized_recommendations", []),
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