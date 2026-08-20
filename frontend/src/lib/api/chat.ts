const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export interface ChatSession {
  id: string;
  user_id: string;
  started_at: string;
  last_activity_at: string;
  is_active: boolean;
  prediction_context?: {
    disease: string;
    confidence: number;
    severity: string;
    symptoms: string[];
    precautions: string[];
  } | null;
}

export interface PendingAction {
  id: string;
  session_id: string;
  tool: string;
  args: Record<string, unknown>;
  summary: string;
  status: string;
  created_at: string;
  expires_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  pending_action?: PendingAction | null;
}

export async function createChatSession(
  predictionId?: string,
  token?: string
): Promise<ChatSession> {
  const response = await fetch(`${API_URL}/api/v1/chat/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ prediction_id: predictionId ?? null }),
  });
  if (!response.ok) throw new Error("Failed to create chat session");
  return response.json();
}

export async function sendChatMessage(
  sessionId: string,
  content: string,
  token?: string
): Promise<ChatMessage> {
  const response = await fetch(`${API_URL}/api/v1/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ session_id: sessionId, content }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to send message");
  }
  return response.json();
}

export async function confirmChatAction(
  pendingActionId: string,
  decision: "approve" | "decline",
  token?: string
): Promise<ChatMessage> {
  const response = await fetch(`${API_URL}/api/v1/chat/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({
      pending_action_id: pendingActionId,
      decision,
    }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to process your decision");
  }
  return response.json();
}
