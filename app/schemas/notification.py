import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: uuid.UUID
    title: str
    message: str
    type: str
    is_read: bool
    user_id: uuid.UUID | None
    created_at: datetime


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: str = Field(default="info", pattern=r"^(info|warning|success|alert)$")
    user_id: uuid.UUID | None = None
