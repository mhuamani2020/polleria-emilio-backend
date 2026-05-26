import uuid
from datetime import datetime
from pydantic import BaseModel


class ActiveSessionInfo(BaseModel):
    device_info: str | None
    ip_address: str | None
    created_at: datetime


class LoginConflictResponse(BaseModel):
    detail: str = "Ya tienes una sesión activa en otro dispositivo"
    session: ActiveSessionInfo


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class SessionResponse(BaseModel):
    id: uuid.UUID
    device_info: str | None
    ip_address: str | None
    is_active: bool
    created_at: datetime
    expires_at: datetime
