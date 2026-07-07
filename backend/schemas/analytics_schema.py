from pydantic import BaseModel, Field


class DiseaseFrequencyItem(BaseModel):
    disease: str
    count: int
    percentage: float


class SeverityBreakdownItem(BaseModel):
    severity: str
    count: int
    percentage: float


class DiseaseTrendBreakdown(BaseModel):
    disease: str
    count: int


class DiseaseTrend(BaseModel):
    month: str
    total: int
    breakdown: list[DiseaseTrendBreakdown]


class SeverityTrendBreakdown(BaseModel):
    severity: str
    count: int


class SeverityTrend(BaseModel):
    month: str
    breakdown: list[SeverityTrendBreakdown]


class TopSymptom(BaseModel):
    symptom: str
    count: int


class CommonPair(BaseModel):
    symptoms: list[str]
    count: int


class SymptomInsights(BaseModel):
    top_symptoms: list[TopSymptom]
    common_pairs: list[CommonPair]


class AnalyticsSummary(BaseModel):
    total_predictions: int
    most_common_disease: str
    average_confidence: float
    severe_count: int
    unique_conditions: int
    time_range_days: int


class SymptomTrend(BaseModel):
    symptom: str
    data: list[dict]  # [{month: str, count: int}]
    direction: str  # "increasing" | "decreasing" | "stable" | "insufficient_data"
    change_pct: float


class ConfidenceTrend(BaseModel):
    month: str
    average_confidence: float
    count: int


class RecurringCondition(BaseModel):
    disease: str
    occurrences: int
    last_detected: str
    frequency: str  # "frequent" | "occasional" | "rare"


class HealthSummary(BaseModel):
    period_label: str
    total_checks: int
    most_common_condition: str
    risk_level: str  # "low" | "moderate" | "high"
    recurring_issues: int
    improving: bool
    summary_text: str


class RiskScoreAnalytics(BaseModel):
    current_score: float | None = None
    category: str | None = None
    last_computed: str | None = None


class AnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    disease_frequency: list[DiseaseFrequencyItem]
    severity_breakdown: list[SeverityBreakdownItem]
    disease_trends: list[DiseaseTrend]
    severity_trends: list[SeverityTrend]
    symptom_insights: SymptomInsights
    symptom_trends: list[SymptomTrend]
    confidence_trends: list[ConfidenceTrend]
    recurring_conditions: list[RecurringCondition]
    health_summary: HealthSummary | None
    insights: list[str]
    risk_score: RiskScoreAnalytics | None = None
