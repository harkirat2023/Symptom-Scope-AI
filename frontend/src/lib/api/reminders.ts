const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export type ReminderFrequency = "daily" | "specific_days" | "every_x_hours" | "as_needed";
export type ReminderStatus = "active" | "paused" | "completed";
export type ReminderLogStatus = "taken" | "missed" | "skipped";

export interface Reminder {
  id: string;
  user_id: string;
  medicine_name: string;
  dosage: string;
  frequency: ReminderFrequency;
  schedule_details: Record<string, unknown>;
  duration_days: number;
  start_time: string;
  status: ReminderStatus;
  email_reminder: boolean;
  linked_prediction_id?: string | null;
  next_due_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReminderLog {
  id: string;
  reminder_id: string;
  status: ReminderLogStatus;
  timestamp: string;
  note?: string | null;
}

export interface ReminderListResponse {
  reminders: Reminder[];
  total: number;
}

export interface UpcomingReminderResponse {
  reminder: Reminder | null;
  has_upcoming: boolean;
}

export async function createReminder(
  data: {
    medicine_name: string;
    dosage: string;
    frequency: ReminderFrequency;
    duration_days: number;
    start_time: string;
    linked_prediction_id?: string | null;
    email_reminder?: boolean;
  },
  token?: string
): Promise<Reminder> {
  const response = await fetch(`${API_URL}/api/v1/reminders`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to create reminder");
  }
  return response.json();
}

export async function fetchReminders(
  status?: ReminderStatus,
  token?: string
): Promise<ReminderListResponse> {
  const params = status ? `?status=${status}` : "";
  const response = await fetch(`${API_URL}/api/v1/reminders${params}`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch reminders");
  return response.json();
}

export async function updateReminder(
  id: string,
  data: Partial<{
    medicine_name: string;
    dosage: string;
    frequency: ReminderFrequency;
    duration_days: number;
    start_time: string;
    status: ReminderStatus;
    email_reminder: boolean;
  }>,
  token?: string
): Promise<Reminder> {
  const response = await fetch(`${API_URL}/api/v1/reminders/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to update reminder");
  }
  return response.json();
}

export async function deleteReminder(
  id: string,
  token?: string
): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/reminders/${id}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to delete reminder");
}

export async function logReminderStatus(
  id: string,
  status: ReminderLogStatus,
  note?: string,
  token?: string
): Promise<ReminderLog> {
  const response = await fetch(`${API_URL}/api/v1/reminders/${id}/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify({ status, note: note ?? null }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || "Failed to log status");
  }
  return response.json();
}

export async function fetchUpcomingReminder(
  token?: string
): Promise<UpcomingReminderResponse> {
  const response = await fetch(`${API_URL}/api/v1/reminders/upcoming`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch upcoming reminder");
  return response.json();
}
