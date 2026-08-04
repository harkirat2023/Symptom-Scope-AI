const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export interface RecoveryPlanResponse {
  id: string;
  user_id: string;
  prediction_id: string;
  disease: string;
  confidence: number;
  severity: string;
  symptoms: string[];
  recovery_timeline: string[];
  diet_recommendations: Record<string, unknown>;
  foods_to_eat: string[];
  foods_to_avoid: string[];
  hydration_advice: string;
  sleep_recommendation: string;
  exercise_recommendation: string;
  daily_physical_activity: string[];
  lifestyle_changes: string[];
  medicines_disclaimer: string;
  when_to_visit_doctor: string[];
  emergency_warning_signs: string[];
  mental_wellness_tips: string[];
  recovery_checklist: string[];
  progress_tracker: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface RecoveryPlanListResponse {
  plans: RecoveryPlanResponse[];
  total: number;
}

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export async function generateRecoveryPlan(
  predictionId: string,
  token?: string
): Promise<RecoveryPlanResponse> {
  const response = await fetch(`${API_URL}/api/v1/recovery-plan/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ prediction_id: predictionId }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Failed to generate recovery plan");
  }
  return response.json();
}

export async function getLatestRecoveryPlan(
  token?: string
): Promise<RecoveryPlanResponse | null> {
  const response = await fetch(`${API_URL}/api/v1/recovery-plan/latest`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error("Failed to fetch recovery plan");
  }
  return response.json();
}

export async function getRecoveryPlanHistory(
  token?: string
): Promise<RecoveryPlanListResponse> {
  const response = await fetch(`${API_URL}/api/v1/recovery-plan/history`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch recovery plan history");
  return response.json();
}

export async function regenerateRecoveryPlan(
  planId: string,
  token?: string
): Promise<RecoveryPlanResponse> {
  const response = await fetch(`${API_URL}/api/v1/recovery-plan/regenerate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ plan_id: planId }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Failed to regenerate recovery plan");
  }
  return response.json();
}

export async function getLatestPrediction(
  token?: string
): Promise<{
  primary_prediction: string;
  confidence: number;
  severity: string;
  prediction_id: string;
} | null> {
  const response = await fetch(`${API_URL}/api/v1/predictions/latest`, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error("Failed to fetch latest prediction");
  }
  return response.json();
}