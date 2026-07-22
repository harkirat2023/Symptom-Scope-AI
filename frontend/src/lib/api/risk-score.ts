const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export interface UserHealthProfile {
  bmi?: number;
  exercise_frequency?: number;
  diet_type?: "balanced" | "unhealthy" | "irregular";
  smoking_status?: "never" | "former" | "current";
  sleep_hours?: number;
  existing_conditions?: string[];
}

export interface UserHealthProfileResponse extends UserHealthProfile {
  id: string;
  user_id: string;
  updated_at: string;
}

export interface RiskFactorBreakdown {
  age_score: number;
  bmi_score: number;
  lifestyle_score: number;
  smoking_score: number;
  sleep_score: number;
  existing_conditions_score: number;
  prediction_history_score: number;
  severity_trend_score: number;
}

export interface RiskScoreResponse {
  current_score: number;
  category: "Low" | "Medium" | "High";
  breakdown: RiskFactorBreakdown;
  last_prediction_id: string | null;
  timestamp: string;
}

export interface RiskScoreHistoryItem {
  score: number;
  category: string;
  timestamp: string;
}

export interface RiskScoreHistoryResponse {
  history: RiskScoreHistoryItem[];
  total: number;
}

export interface RiskTipsResponse {
  tips: string[];
}

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export async function getRiskScore(
  token?: string
): Promise<RiskScoreResponse | null> {
  const res = await fetch(`${API_URL}/api/v1/risk-score`, {
    headers: authHeaders(token),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch risk score");
  return res.json();
}

export async function getRiskScoreHistory(
  range = "6m",
  token?: string
): Promise<RiskScoreHistoryResponse> {
  const res = await fetch(`${API_URL}/api/v1/risk-score/history?range=${range}`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch risk score history");
  return res.json();
}

export async function getRiskTips(
  token?: string
): Promise<RiskTipsResponse> {
  const res = await fetch(`${API_URL}/api/v1/risk-score/tips`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch risk tips");
  return res.json();
}

export async function updateHealthProfile(
  data: UserHealthProfile,
  token?: string
): Promise<UserHealthProfileResponse> {
  const res = await fetch(`${API_URL}/api/v1/risk-score/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update health profile");
  return res.json();
}

export async function getHealthProfile(
  token?: string
): Promise<UserHealthProfileResponse | null> {
  const res = await fetch(`${API_URL}/api/v1/risk-score/profile`, {
    headers: authHeaders(token),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch health profile");
  return res.json();
}
