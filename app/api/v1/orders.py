import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.kds_ticket import KdsTicket
from app.models.user import User
from app.schemas.kds_ticket import KdsTicketResponse
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from app.services.order_service import OrderService
from app.websocket import create_event

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    sede_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    service = OrderService(db)
    user_id = None if current_user.role == "admin" else current_user.user_id
    return await service.get_orders(
        sede_id=sede_id,
        status=status_filter,
        user_id=user_id,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    service = OrderService(db)
    order = await service.get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    if current_user.role != "admin" and order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pedido",
        )
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    service = OrderService(db)
    order = await service.create_order(data, current_user.user_id)

    order_data = OrderResponse.model_validate(order).model_dump(mode="json")
    await create_event(db, order.sede_id, "order_created", order_data)

    result = await db.execute(
        select(KdsTicket).where(KdsTicket.order_id == order.order_id)
    )
    ticket = result.scalar_one_or_none()
    if ticket:
        ticket_data = KdsTicketResponse.model_validate(ticket).model_dump(mode="json")
        await create_event(db, order.sede_id, "kds_ticket_updated", ticket_data)

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    service = OrderService(db)
    order = await service.update_order_status(order_id, data.status)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    order_data = OrderResponse.model_validate(order).model_dump(mode="json")
    await create_event(db, order.sede_id, "order_status_changed", order_data)

    return order
