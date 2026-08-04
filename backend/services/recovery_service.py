"""
Recovery Plan Service - Generates evidence-based recovery recommendations
using the centralized LLMService.
"""

from services.llm_service import LLMService
from repositories.recovery_repository import RecoveryPlanRepository
from repositories.prediction_repository import PredictionRepository
from bson.objectid import ObjectId


RECOVERY_PLAN_PROMPT = """You are a medical recovery advisor for SymptomScope AI. Generate a comprehensive, evidence-based recovery plan for a patient with the following condition.

Patient Context:
- Predicted Condition: {disease}
- Confidence: {confidence}%
- Severity: {severity}
- Reported Symptoms: {symptoms}
- Patient Age: {age}
- Patient Gender: {gender}
- Existing Conditions: {existing_conditions}
- Symptom Duration: {symptom_duration}
- Pain Level: {pain_level}

Generate a detailed recovery plan in JSON format with the following structure. Be specific, actionable, and evidence-based. Include medical disclaimers.

{{
  "recovery_timeline": [
    "Week 1: Expected milestones and focus areas",
    "Week 2: Expected milestones and focus areas",
    "Week 3-4: Expected milestones and focus areas",
    "Month 2+: Long-term recovery expectations"
  ],
  "diet_recommendations": {{
    "general_principles": "Overall dietary approach for this condition",
    "specific_nutrients": "Key nutrients to focus on and why"
  }},
  "foods_to_eat": [
    "Specific food 1 with reason",
    "Specific food 2 with reason",
    "Specific food 3 with reason"
  ],
  "foods_to_avoid": [
    "Specific food 1 with reason",
    "Specific food 2 with reason",
    "Specific food 3 with reason"
  ],
  "hydration_advice": "Specific hydration recommendations (amount, types of fluids, timing)",
  "sleep_recommendation": "Sleep duration, positioning, and hygiene tips specific to this condition",
  "exercise_recommendation": "Safe exercise types, intensity, frequency, and progression for this condition",
  "daily_physical_activity": [
    "Specific daily activity 1",
    "Specific daily activity 2",
    "Specific daily activity 3"
  ],
  "lifestyle_changes": [
    "Lifestyle modification 1 with rationale",
    "Lifestyle modification 2 with rationale",
    "Lifestyle modification 3 with rationale"
  ],
  "medicines_disclaimer": "IMPORTANT: This information is for educational purposes only. No medication recommendations are provided. All medication decisions must be made by a qualified healthcare provider based on individual assessment.",
  "when_to_visit_doctor": [
    "Specific sign/symptom 1 that warrants medical follow-up",
    "Specific sign/symptom 2 that warrants medical follow-up",
    "Specific sign/symptom 3 that warrants medical follow-up"
  ],
  "emergency_warning_signs": [
    "Emergency sign 1 - call emergency services immediately",
    "Emergency sign 2 - call emergency services immediately",
    "Emergency sign 3 - call emergency services immediately"
  ],
  "mental_wellness_tips": [
    "Mental health strategy 1 for this condition",
    "Mental health strategy 2 for this condition",
    "Mental health strategy 3 for this condition"
  ],
  "recovery_checklist": [
    "Daily/weekly action item 1",
    "Daily/weekly action item 2",
    "Daily/weekly action item 3",
    "Daily/weekly action item 4",
    "Daily/weekly action item 5"
  ],
  "progress_tracker": {{
    "symptoms_to_monitor": ["symptom 1", "symptom 2", "symptom 3"],
    "frequency": "daily/weekly",
    "improvement_indicators": ["indicator 1", "indicator 2"],
    "red_flags": ["red flag 1", "red flag 2"]
  }}
}}

Rules:
1. Return ONLY valid JSON - no markdown, no explanations
2. Be specific to the diagnosed condition
3. Include evidence-based recommendations
4. Always include appropriate medical disclaimers
5. Tailor to severity level (mild/moderate/severe)
6. Consider patient age and comorbidities
7. If mental wellness tips aren't applicable, include general stress management
"""


class RecoveryPlanService:
    def __init__(self):
        self.llm_service = LLMService()
        self.repo = RecoveryPlanRepository()
        self.pred_repo = PredictionRepository()

    async def generate_recovery_plan(
        self,
        user_id: str,
        prediction_id: str,
    ) -> dict:
        """Generate a new recovery plan for a prediction."""
        # Get prediction details
        pred = await self.pred_repo.find_by_id(prediction_id)
        if not pred:
            raise ValueError("Prediction not found")
        if pred.user_id != user_id:
            raise ValueError("Access denied")

        # Get latest plan if exists (for context)
        existing = await self.repo.find_by_prediction(prediction_id)
        
        # Build context for LLM
        context = {
            "disease": pred.prediction,
            "confidence": pred.confidence,
            "severity": pred.severity,
            "symptoms": pred.symptoms,
            "age": pred.age,
            "gender": pred.gender,
            "existing_conditions": pred.existing_conditions or [],
            "symptom_duration": pred.symptom_duration,
            "pain_level": pred.pain_level,
        }

        # Generate plan using LLM
        prompt = RECOVERY_PLAN_PROMPT.format(**{
            k: v if v is not None else "Not specified" 
            for k, v in context.items()
        })
        
        import json
        result = await self.llm_service.invoke(prompt, "Generate the recovery plan JSON.")
        
        # Parse JSON response
        try:
            plan_data = json.loads(result)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                plan_data = json.loads(result[start:end])
            else:
                raise ValueError("Failed to parse LLM response as JSON")

        # Save to database
        plan = await self.repo.create(
            user_id=user_id,
            prediction_id=prediction_id,
            disease=pred.prediction,
            confidence=pred.confidence,
            severity=pred.severity,
            symptoms=pred.symptoms,
            plan_data=plan_data,
        )
        return plan

    async def get_latest_plan(self, user_id: str) -> dict | None:
        """Get the latest recovery plan for a user."""
        return await self.repo.find_latest_by_user(user_id)

    async def get_plan_by_id(self, user_id: str, plan_id: str) -> dict | None:
        """Get a specific recovery plan."""
        plan = await self.repo.find_by_id(plan_id)
        if plan and plan.get("userId") == user_id:
            return plan
        return None

    async def get_user_plans(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get all recovery plans for a user."""
        return await self.repo.find_by_user(user_id, limit)

    async def regenerate_plan(self, user_id: str, plan_id: str) -> dict:
        """Regenerate an existing recovery plan."""
        plan = await self.repo.find_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        if plan.get("userId") != user_id:
            raise ValueError("Access denied")

        # Get original prediction for context
        pred = await self.pred_repo.find_by_id(plan["predictionId"])
        if not pred:
            raise ValueError("Original prediction not found")

        context = {
            "disease": pred.prediction,
            "confidence": pred.confidence,
            "severity": pred.severity,
            "symptoms": pred.symptoms,
            "age": pred.age,
            "gender": pred.gender,
            "existing_conditions": pred.existing_conditions or [],
            "symptom_duration": pred.symptom_duration,
            "pain_level": pred.pain_level,
        }

        prompt = RECOVERY_PLAN_PROMPT.format(**{
            k: v if v is not None else "Not specified" 
            for k, v in context.items()
        })

        import json
        result = await self.llm_service.invoke(prompt, "Generate the recovery plan JSON.")
        
        try:
            plan_data = json.loads(result)
        except json.JSONDecodeError:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                plan_data = json.loads(result[start:end])
            else:
                raise ValueError("Failed to parse LLM response as JSON")

        updated = await self.repo.regenerate_plan(plan_id, plan_data)
        return updated