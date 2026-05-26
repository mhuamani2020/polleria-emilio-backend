import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):
    product_id: uuid.UUID
    sede_id: uuid.UUID
    current_stock: float = Field(..., ge=0)
    minimum_stock: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20)


class InventoryUpdate(BaseModel):
    current_stock: float | None = Field(default=None, ge=0)
    minimum_stock: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=20)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inventory_id: uuid.UUID
    product_id: uuid.UUID
    sede_id: uuid.UUID
    current_stock: float
    minimum_stock: float
    unit: str
    status: str
    updated_at: datetime
