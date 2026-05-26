import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ComboItemCreate(BaseModel):
    product_id: uuid.UUID
    qty: int = Field(..., ge=1)


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    price: float = Field(..., gt=0)
    image_url: str | None = None
    icon: str | None = None
    category_id: uuid.UUID
    is_combo: bool = False
    combo_items: list[ComboItemCreate] | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    image_url: str | None = None
    icon: str | None = None
    category_id: uuid.UUID | None = None
    is_active: bool | None = None
    combo_items: list[ComboItemCreate] | None = None


class ComboItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    qty: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    name: str
    description: str | None
    price: float
    image_url: str | None
    icon: str | None
    category_id: uuid.UUID
    is_combo: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    combo_items: list[ComboItemResponse] = []
