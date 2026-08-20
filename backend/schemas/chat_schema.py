from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    prediction_id: str | None = None


class ChatSessionResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    user_id: str
    started_at: str
    last_activity_at: str
    is_active: bool
    prediction_context: dict | None = None

    model_config = ConfigDict(populate_by_name=True)


class MessageSend(BaseModel):
    session_id: str
    content: str = Field(..., min_length=1, max_length=500)


class PendingActionResponse(BaseModel):
    id: str
    session_id: str
    tool: str
    args: dict
    summary: str
    status: str
    created_at: str
    expires_at: str


class ChatMessageResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    session_id: str
    role: str
    content: str
    created_at: str
    pending_action: PendingActionResponse | None = None


class ConfirmActionRequest(BaseModel):
    pending_action_id: str
    decision: Literal["approve", "decline"]


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionResponse]
    total: int
