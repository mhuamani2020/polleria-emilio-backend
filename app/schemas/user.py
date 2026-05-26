import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    dni: str | None = Field(default=None, min_length=8, max_length=8, pattern=r"^\d{8}$")
    phone: str | None = Field(default=None, max_length=20)
    shift: str | None = Field(default=None, max_length=30)
    role: str = Field(..., pattern=r"^(admin|cajero|mesero)$")
    sede_id: uuid.UUID


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    password: str | None = Field(default=None, min_length=6, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    dni: str | None = Field(default=None, min_length=8, max_length=8, pattern=r"^\d{8}$")
    phone: str | None = Field(default=None, max_length=20)
    shift: str | None = Field(default=None, max_length=30)
    role: str | None = Field(default=None, pattern=r"^(admin|cajero|mesero)$")
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    username: str
    display_name: str | None
    dni: str | None
    phone: str | None
    shift: str | None
    role: str
    sede_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str
    force: bool = False
    device_info: str | None = None
