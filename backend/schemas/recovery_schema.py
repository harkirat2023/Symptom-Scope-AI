from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecoveryPlanBase(BaseModel):
    disease: str
    confidence: float
    severity: str
    symptoms: list[str] = []


class RecoveryPlanCreate(RecoveryPlanBase):
    prediction_id: str


class RecoveryPlanRegenerateRequest(BaseModel):
    plan_id: str


class RecoveryPlanResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    user_id: str
    prediction_id: str
    disease: str
    confidence: float
    severity: str
    symptoms: list[str]
    what_it_means: str = ""
    what_to_do: list[str] = []
    recovery_timeline: list[str] = []
    diet_recommendations: dict[str, Any] = {}
    foods_to_eat: list[str] = []
    foods_to_avoid: list[str] = []
    hydration_advice: str = ""
    sleep_recommendation: str = ""
    exercise_recommendation: str = ""
    daily_physical_activity: list[str] = []
    lifestyle_changes: list[str] = []
    personalized_recommendations: list[str] = []
    medicines_disclaimer: str = ""
    when_to_visit_doctor: list[str] = []
    emergency_warning_signs: list[str] = []
    mental_wellness_tips: list[str] = []
    recovery_checklist: list[str] = []
    progress_tracker: dict[str, Any] = {}
    created_at: str
    updated_at: str
    version: int = 1

    model_config = ConfigDict(populate_by_name=True)


class RecoveryPlanListResponse(BaseModel):
    plans: list[RecoveryPlanResponse]
    total: int