from pydantic import BaseModel, Field
from datetime import datetime


class ChatSessionCreate(BaseModel):
    prediction_id: str | None = None


class ChatSessionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    started_at: str
    last_activity_at: str
    is_active: bool
    prediction_context: dict | None = None

    class Config:
        populate_by_name = True


class MessageSend(BaseModel):
    session_id: str
    content: str = Field(..., min_length=1, max_length=500)


class ChatMessageResponse(BaseModel):
    id: str = Field(alias="_id")
    session_id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: str


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionResponse]
    total: int
