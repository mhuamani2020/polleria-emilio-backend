import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    product_name: str = Field(..., min_length=1, max_length=150)
    qty: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    sede_id: uuid.UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(pendiente|en_preparacion|listo|entregado|cancelado)$")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    qty: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: uuid.UUID
    sede_id: uuid.UUID
    user_id: uuid.UUID
    order_date: datetime
    status: str
    total: float
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []
