import uuid
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.inventory import Inventory
from app.models.sede import Sede
from app.schemas.dashboard import (
    KpiResponse,
    TopProduct,
    RecentTransaction,
    CategoryDistribution,
    DashboardResponse,
)


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpi(self, sede_id: uuid.UUID | None = None) -> KpiResponse:
        query_orders = select(
            func.count(Order.order_id),
            func.coalesce(func.sum(Order.total), 0),
        ).where(func.date(Order.order_date) == func.current_date())

        if sede_id:
            query_orders = query_orders.where(Order.sede_id == sede_id)

        result = await self.db.execute(query_orders)
        total_orders, total_sales = result.one()

        query_critical = select(func.count(Inventory.inventory_id)).where(
            Inventory.status == "Crítico"
        )
        if sede_id:
            query_critical = query_critical.where(Inventory.sede_id == sede_id)
        critical_count = (await self.db.execute(query_critical)).scalar()

        query_sedes = select(func.count(Sede.sede_id)).where(Sede.status == "Activa")
        if sede_id:
            query_sedes = query_sedes.where(Sede.sede_id == sede_id)
        active_sedes = (await self.db.execute(query_sedes)).scalar()

        return KpiResponse(
            total_sales_today=float(total_sales),
            total_orders_today=total_orders,
            critical_stock_count=critical_count,
            active_sedes=active_sedes,
        )

    async def get_top_products(
        self, sede_id: uuid.UUID | None = None, limit: int = 5
    ) -> list[TopProduct]:
        query = select(
            OrderItem.product_name,
            func.sum(OrderItem.qty).label("total_qty"),
            func.sum(OrderItem.subtotal).label("total_sales"),
        ).join(Order, OrderItem.order_id == Order.order_id)

        if sede_id:
            query = query.where(Order.sede_id == sede_id)

        query = query.group_by(OrderItem.product_name).order_by(
            desc("total_qty")
        ).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        total = sum(float(r.total_sales) for r in rows) if rows else 1

        return [
            TopProduct(
                name=row.product_name,
                qty=row.total_qty,
                total=float(row.total_sales),
                pct=round(float(row.total_sales) / total * 100, 1),
            )
            for row in rows
        ]

    async def get_recent_transactions(
        self, sede_id: uuid.UUID | None = None, limit: int = 10
    ) -> list[RecentTransaction]:
        query = select(
            Order.order_id,
            Order.sede_id,
            OrderItem.product_name,
            OrderItem.subtotal,
            Order.order_date,
        ).join(OrderItem, OrderItem.order_id == Order.order_id)

        if sede_id:
            query = query.where(Order.sede_id == sede_id)

        query = query.order_by(Order.order_date.desc()).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        sede_names: dict[str, str] = {}
        sede_result = await self.db.execute(select(Sede.sede_id, Sede.name))
        for sede in sede_result.all():
            sede_names[str(sede.sede_id)] = sede.name

        return [
            RecentTransaction(
                id=str(row.order_id),
                sede_name=sede_names.get(str(row.sede_id), "Unknown"),
                product=row.product_name,
                amount=float(row.subtotal),
                time=row.order_date.strftime("%H:%M"),
            )
            for row in rows
        ]

    async def get_category_distribution(
        self, sede_id: uuid.UUID | None = None
    ) -> list[CategoryDistribution]:
        from app.models.product import Product

        query = select(
            Product.category_id,
            func.sum(OrderItem.subtotal).label("total"),
        ).join(OrderItem, OrderItem.product_id == Product.product_id).join(
            Order, Order.order_id == OrderItem.order_id
        )

        if sede_id:
            query = query.where(Order.sede_id == sede_id)

        query = query.group_by(Product.category_id)

        result = await self.db.execute(query)
        rows = result.all()

        from app.models.category import Category

        cat_result = await self.db.execute(select(Category.category_id, Category.name))
        cat_map = {str(r.category_id): r.name for r in cat_result.all()}

        total = sum(float(r.total) for r in rows) or 1
        colors = ["#4F46E5", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6", "#EC4899"]

        return [
            CategoryDistribution(
                name=cat_map.get(str(row.category_id), "Unknown"),
                pct=round(float(row.total) / total * 100, 1),
                value=f"S/ {float(row.total):.2f}",
                color=colors[i % len(colors)],
            )
            for i, row in enumerate(rows)
        ]

    async def get_dashboard(
        self, sede_id: uuid.UUID | None = None
    ) -> DashboardResponse:
        kpi = await self.get_kpi(sede_id)
        top_products = await self.get_top_products(sede_id)
        transactions = await self.get_recent_transactions(sede_id)
        distribution = await self.get_category_distribution(sede_id)

        return DashboardResponse(
            kpi=kpi,
            top_products=top_products,
            recent_transactions=transactions,
            category_distribution=distribution,
        )
