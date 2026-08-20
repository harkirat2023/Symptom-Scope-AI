from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserHealthProfile(BaseModel):
    bmi: float | None = Field(default=None, ge=10, le=60)
    exercise_frequency: int | None = Field(
        default=None, ge=0, le=7, description="Days per week"
    )
    diet_type: Literal["balanced", "unhealthy", "irregular"] | None = None
    smoking_status: Literal["never", "former", "current"] | None = None
    sleep_hours: float | None = Field(default=None, ge=1, le=24)
    existing_conditions: list[str] = Field(default_factory=list, max_length=20)


class UserHealthProfileResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    user_id: str
    bmi: float | None = None
    exercise_frequency: int | None = None
    diet_type: str | None = None
    smoking_status: str | None = None
    sleep_hours: float | None = None
    existing_conditions: list[str] = []
    updated_at: str

    model_config = ConfigDict(populate_by_name=True)


class RiskFactorBreakdown(BaseModel):
    age_score: float = 0
    bmi_score: float = 0
    lifestyle_score: float = 0
    smoking_score: float = 0
    sleep_score: float = 0
    existing_conditions_score: float = 0
    prediction_history_score: float = 0
    severity_trend_score: float = 0


class RiskScoreResponse(BaseModel):
    current_score: float = Field(..., ge=0, le=100)
    category: str
    breakdown: RiskFactorBreakdown
    last_prediction_id: str | None = None
    timestamp: str


class RiskScoreHistoryItem(BaseModel):
    score: float
    category: str
    timestamp: str


class RiskScoreHistoryResponse(BaseModel):
    history: list[RiskScoreHistoryItem]
    total: int


class RiskTipsResponse(BaseModel):
    tips: list[str]
