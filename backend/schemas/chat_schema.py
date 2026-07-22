from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


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


class ChatMessageResponse(BaseModel):
    id: str = Field(validation_alias="_id")
    session_id: str
    role: str
    content: str
    created_at: str


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionResponse]
    total: int
