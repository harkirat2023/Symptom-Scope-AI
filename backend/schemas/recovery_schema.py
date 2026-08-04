from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class RecoveryPlanBase(BaseModel):
    disease: str
    confidence: float
    severity: str
    symptoms: List[str] = []


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
    symptoms: List[str]
    recovery_timeline: List[str] = []
    diet_recommendations: Dict[str, Any] = {}
    foods_to_eat: List[str] = []
    foods_to_avoid: List[str] = []
    hydration_advice: str = ""
    sleep_recommendation: str = ""
    exercise_recommendation: str = ""
    daily_physical_activity: List[str] = []
    lifestyle_changes: List[str] = []
    medicines_disclaimer: str = ""
    when_to_visit_doctor: List[str] = []
    emergency_warning_signs: List[str] = []
    mental_wellness_tips: List[str] = []
    recovery_checklist: List[str] = []
    progress_tracker: Dict[str, Any] = {}
    created_at: str
    updated_at: str
    version: int = 1

    model_config = ConfigDict(populate_by_name=True)


class RecoveryPlanListResponse(BaseModel):
    plans: List[RecoveryPlanResponse]
    total: int