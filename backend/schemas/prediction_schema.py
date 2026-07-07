from pydantic import BaseModel, Field
from datetime import datetime
from schemas.doctor_schema import DoctorResponse


class SymptomInput(BaseModel):
    symptoms: list[str] = Field(..., min_length=1, max_length=50)
    age: int | None = Field(None, ge=0, le=150)
    gender: str | None = Field(None, pattern=r"^(male|female|other)$", max_length=20)
    existing_conditions: list[str] = Field(default_factory=list, max_length=20)
    symptom_duration: str | None = Field(None, max_length=100)
    pain_level: int | None = Field(None, ge=0, le=10)


class TopContributingSymptom(BaseModel):
    symptom: str
    importance: float
    shap_value: float | None = None
    relative_contribution_pct: float | None = None


class ShapExplanation(BaseModel):
    base_value: float
    feature_values: list[TopContributingSymptom]


class ConfidenceInfo(BaseModel):
    label: str
    description: str


class EmergencyInfo(BaseModel):
    is_emergency: bool
    reasons: list[str]
    explanation: str = ""
    severity_triggered: bool = False
    confidence_triggered: bool = False
    escalation_triggered: bool = False


class PredictionRecord(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    symptoms: list[str]
    prediction: str
    confidence: float
    severity: str
    timestamp: str


class PredictionResponse(BaseModel):
    primary_prediction: str
    confidence: float = Field(..., ge=0, le=100)
    alternatives: list[str]
    severity: str
    top_contributing_symptoms: list[TopContributingSymptom]
    precautions: list[str]
    emergency: EmergencyInfo
    prediction_id: str
    recommended_specialist: str
    doctor_recommendations: list[DoctorResponse]
    explanation_summary: str
    confidence_info: ConfidenceInfo
    shap_explanation: ShapExplanation | None = None
    risk_score: float | None = None
    risk_category: str | None = None
