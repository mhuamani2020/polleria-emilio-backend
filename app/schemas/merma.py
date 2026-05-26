import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MermaCreate(BaseModel):
    inventory_id: uuid.UUID
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    reason: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None


class MermaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merma_id: uuid.UUID
    inventory_id: uuid.UUID
    quantity: float
    unit: str
    reason: str
    notes: str | None
    registered_by: uuid.UUID
    created_at: datetime
