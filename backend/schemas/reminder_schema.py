from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal


class ReminderCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=50)
    frequency: Literal["daily", "specific_days", "every_x_hours", "as_needed"]
    schedule_details: dict = Field(default_factory=dict)
    duration_days: int = Field(default=7, ge=1, le=365)
    start_time: str = Field(default="08:00", pattern=r"^\d{2}:\d{2}$")
    linked_prediction_id: str | None = None
    email_reminder: bool = False


class ReminderUpdate(BaseModel):
    medicine_name: str | None = None
    dosage: str | None = None
    frequency: Literal["daily", "specific_days", "every_x_hours", "as_needed"] | None = None
    schedule_details: dict | None = None
    duration_days: int | None = Field(default=None, ge=1, le=365)
    start_time: str | None = None
    status: Literal["active", "paused", "completed"] | None = None
    email_reminder: bool | None = None


class ReminderResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    user_id: str
    medicine_name: str
    dosage: str
    frequency: str
    schedule_details: dict
    duration_days: int
    start_time: str
    status: str
    email_reminder: bool
    linked_prediction_id: str | None = None
    next_due_at: str | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(populate_by_name=True)


class ReminderLogCreate(BaseModel):
    status: Literal["taken", "missed", "skipped"]
    note: str | None = Field(default=None, max_length=200)


class ReminderLogResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    reminder_id: str
    status: str
    timestamp: str
    note: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ReminderListResponse(BaseModel):
    reminders: list[ReminderResponse]
    total: int


class UpcomingReminderResponse(BaseModel):
    reminder: ReminderResponse | None = None
    has_upcoming: bool
