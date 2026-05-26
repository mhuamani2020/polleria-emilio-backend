import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SedeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    address: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=20)
    manager: str = Field(..., min_length=1, max_length=150)
    status: str = Field(default="Activa", pattern=r"^(Activa|Inactiva)$")


class SedeCreate(SedeBase):
    pass


class SedeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    manager: str | None = Field(default=None, min_length=1, max_length=150)
    status: str | None = Field(default=None, pattern=r"^(Activa|Inactiva)$")


class SedeResponse(SedeBase):
    model_config = ConfigDict(from_attributes=True)

    sede_id: uuid.UUID
    sales: float
    created_at: datetime
    updated_at: datetime
