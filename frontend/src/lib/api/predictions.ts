import { API_BASE_URL as API_URL } from "./config";

export interface TopContributingSymptom {
  symptom: string;
  importance: number;
  shap_value?: number | null;
  relative_contribution_pct?: number | null;
}

export interface ConfidenceInfo {
  label: string;
  description: string;
}

export interface EmergencyInfo {
  is_emergency: boolean;
  reasons: string[];
  explanation: string;
  severity_triggered: boolean;
  confidence_triggered: boolean;
  escalation_triggered: boolean;
}

export interface ShapExplanation {
  base_value: number;
  feature_values: TopContributingSymptom[];
}

export interface PredictionResponse {
  primary_prediction: string;
  confidence: number;
  alternatives: string[];
  severity: string;
  top_contributing_symptoms: TopContributingSymptom[];
  precautions: string[];
  emergency: EmergencyInfo;
  prediction_id: string;
  recommended_specialist: string;
  doctor_recommendations: DoctorResponse[];
  explanation_summary: string;
  confidence_info: ConfidenceInfo;
  shap_explanation?: ShapExplanation | null;
  risk_score?: number | null;
  risk_category?: string | null;
}

export interface PredictionRecord {
  id: string;
  user_id: string;
  symptoms: string[];
  prediction: string;
  confidence: number;
  severity: string;
  timestamp: string;
}

export interface ReportResponse {
  generated_at: string;
  total_predictions: number;
  most_common_disease: string;
  avg_confidence: number;
  severe_count: number;
  severity_distribution: Record<string, number>;
  predictions: PredictionRecord[];
}

export interface DoctorResponse {
  id?: string | null;
  name: string;
  specialty: string;
  location: string;
  rating: number;
  distance_km?: number;
  availability: string[];
  phone?: string;
  hospital?: string;
  experience_years?: number;
  available?: boolean;
  consultation_fee?: number;
  image_url?: string;
  bio?: string;
}

export interface HospitalResponse {
  id?: string | null;
  name: string;
  address: string;
  location?: string;
  specialties: string[];
  rating: number;
  distance_km?: number | null;
  phone?: string;
  emergency: boolean;
  has_ambulance: boolean;
  has_emergency_room?: boolean;
  latitude?: number;
  longitude?: number;
  image_url?: string;
}

export interface HospitalSearchResponse {
  hospitals: HospitalResponse[];
  total: number;
  locations: string[];
}

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export async function predictSymptoms(
  input: {
    symptoms: string[];
    age?: number | null;
    gender?: string | null;
    existing_conditions?: string[];
    symptom_duration?: string;
    pain_level?: number | null;
  },
  token?: string
): Promise<PredictionResponse> {
  const response = await fetch(`${API_URL}/api/v1/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Prediction request failed");
  }
  return response.json();
}

export async function fetchUserReports(
  userId: string,
  token?: string
): Promise<ReportResponse | null> {
  const response = await fetch(`${API_URL}/api/v1/reports/${userId}`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error("Failed to fetch reports");
  }
  return response.json();
}

export async function fetchHospitals(
  params?: {
    q?: string;
    location?: string;
    specialty?: string;
    emergency_only?: boolean;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
  },
  token?: string
): Promise<HospitalSearchResponse> {
  const searchParams = new URLSearchParams();
  if (params?.q) searchParams.set("q", params.q);
  if (params?.location) searchParams.set("location", params.location);
  if (params?.specialty) searchParams.set("specialty", params.specialty);
  if (params?.emergency_only) searchParams.set("emergency_only", "true");
  if (params?.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params?.sort_order) searchParams.set("sort_order", params.sort_order);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  const response = await fetch(
    `${API_URL}/api/v1/hospitals?${searchParams.toString()}`,
    { headers: authHeaders(token) }
  );
  if (!response.ok) throw new Error("Failed to fetch hospitals");
  return response.json();
}

export interface AnalyticsSummary {
  total_predictions: number;
  most_common_disease: string;
  average_confidence: number;
  severe_count: number;
  unique_conditions: number;
  time_range_days: number;
}

export interface DiseaseFrequencyItem {
  disease: string;
  count: number;
  percentage: number;
}

export interface SeverityBreakdownItem {
  severity: string;
  count: number;
  percentage: number;
}

export interface DiseaseTrend {
  month: string;
  total: number;
  breakdown: { disease: string; count: number }[];
}

export interface SeverityTrend {
  month: string;
  breakdown: { severity: string; count: number }[];
}

export interface TopSymptom {
  symptom: string;
  count: number;
}

export interface CommonPair {
  symptoms: string[];
  count: number;
}

export interface SymptomTrend {
  symptom: string;
  data: { month: string; count: number }[];
  direction: "increasing" | "decreasing" | "stable" | "insufficient_data";
  change_pct: number;
}

export interface ConfidenceTrend {
  month: string;
  average_confidence: number;
  count: number;
}

export interface RecurringCondition {
  disease: string;
  occurrences: number;
  last_detected: string;
  frequency: "frequent" | "occasional" | "rare";
}

export interface HealthSummary {
  period_label: string;
  total_checks: number;
  most_common_condition: string;
  risk_level: "low" | "moderate" | "high";
  recurring_issues: number;
  improving: boolean;
  summary_text: string;
}

export interface RiskScoreAnalytics {
  current_score: number | null;
  category: string | null;
  last_computed: string | null;
}

export interface AnalyticsResponse {
  summary: AnalyticsSummary;
  disease_frequency: DiseaseFrequencyItem[];
  severity_breakdown: SeverityBreakdownItem[];
  disease_trends: DiseaseTrend[];
  severity_trends: SeverityTrend[];
  symptom_insights: {
    top_symptoms: TopSymptom[];
    common_pairs: CommonPair[];
  };
  symptom_trends: SymptomTrend[];
  confidence_trends: ConfidenceTrend[];
  recurring_conditions: RecurringCondition[];
  health_summary: HealthSummary | null;
  insights: string[];
  risk_score?: RiskScoreAnalytics | null;
}

export async function fetchAnalytics(
  userId: string,
  range: "1m" | "3m" | "6m" | "1y" = "6m",
  token?: string
): Promise<AnalyticsResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/analytics/${userId}?range=${range}`,
    { headers: authHeaders(token) }
  );
  if (!response.ok) throw new Error("Failed to fetch analytics");
  return response.json();
}
