import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class KdsTicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(nuevo|en_preparacion|listo)$")


class KdsTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID
    order_id: uuid.UUID
    type: str
    status: str
    label: str
    created_at: datetime
    completed_at: datetime | None
