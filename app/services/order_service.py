import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.kds_ticket import KdsTicket
from app.schemas.order import OrderCreate


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, data: OrderCreate, user_id: uuid.UUID) -> Order:
        total = sum(item.qty * item.unit_price for item in data.items)

        order = Order(
            sede_id=data.sede_id,
            user_id=user_id,
            total=total,
        )
        self.db.add(order)
        await self.db.flush()

        for item in data.items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                qty=item.qty,
                unit_price=item.unit_price,
                subtotal=item.qty * item.unit_price,
            )
            self.db.add(order_item)

        ticket = KdsTicket(
            order_id=order.order_id,
            label=f"Orden #{str(order.order_id)[:8]}",
            type="Normal",
        )
        self.db.add(ticket)

        await self.db.flush()
        return order

    async def get_orders(
        self,
        sede_id: uuid.UUID | None = None,
        status: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> list[Order]:
        query = select(Order)

        if sede_id:
            query = query.where(Order.sede_id == sede_id)
        if status:
            query = query.where(Order.status == status)
        if user_id:
            query = query.where(Order.user_id == user_id)

        query = query.order_by(Order.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_order_by_id(self, order_id: uuid.UUID) -> Order | None:
        result = await self.db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def update_order_status(self, order_id: uuid.UUID, status: str) -> Order | None:
        order = await self.get_order_by_id(order_id)
        if order is None:
            return None
        order.status = status

        if status in ("listo", "entregado", "cancelado"):
            ticket_result = await self.db.execute(
                select(KdsTicket).where(KdsTicket.order_id == order_id)
            )
            ticket = ticket_result.scalar_one_or_none()
            if ticket:
                ticket.status = "listo" if status == "listo" else status

        await self.db.flush()
        return order

    async def get_daily_stats(self, sede_id: uuid.UUID | None = None) -> dict:
        query = select(
            func.count(Order.order_id).label("total_orders"),
            func.coalesce(func.sum(Order.total), 0).label("total_sales"),
        ).where(func.date(Order.order_date) == func.current_date())

        if sede_id:
            query = query.where(Order.sede_id == sede_id)

        result = await self.db.execute(query)
        row = result.one()
        return {"total_orders": row.total_orders, "total_sales": float(row.total_sales)}
