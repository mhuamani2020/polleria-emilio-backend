import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.kds_ticket import KdsTicket
from app.models.user import User
from app.schemas.kds_ticket import KdsTicketStatusUpdate, KdsTicketResponse
from app.websocket import create_event

router = APIRouter(prefix="/kds", tags=["KDS"])


@router.get("", response_model=list[KdsTicketResponse])
async def list_kds_tickets(
    sede_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    from app.models.order import Order

    query = select(KdsTicket).join(Order, KdsTicket.order_id == Order.order_id)

    if sede_id:
        query = query.where(Order.sede_id == sede_id)
    if status_filter:
        query = query.where(KdsTicket.status == status_filter)

    query = query.order_by(KdsTicket.created_at.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.patch("/{ticket_id}/status", response_model=KdsTicketResponse)
async def update_ticket_status(
    ticket_id: uuid.UUID,
    data: KdsTicketStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    result = await db.execute(
        select(KdsTicket).where(KdsTicket.ticket_id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

    ticket.status = data.status
    if data.status == "listo":
        ticket.completed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(ticket)

    ticket_data = KdsTicketResponse.model_validate(ticket).model_dump(mode="json")
    try:
        sede_id = ticket.order.sede_id
        await create_event(db, sede_id, "kds_ticket_updated", ticket_data)
    except Exception:
        pass

    return ticket
