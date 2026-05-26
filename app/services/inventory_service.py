import uuid
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_status(self, current_stock: float, minimum_stock: float) -> str:
        if current_stock <= 0 or current_stock < minimum_stock * 0.5:
            return "Crítico"
        elif current_stock <= minimum_stock:
            return "Precaución"
        return "Óptimo"

    async def create(self, data: InventoryCreate) -> Inventory:
        status = await self.calculate_status(data.current_stock, data.minimum_stock)
        item = Inventory(
            product_id=data.product_id,
            sede_id=data.sede_id,
            current_stock=data.current_stock,
            minimum_stock=data.minimum_stock,
            unit=data.unit,
            status=status,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def get_all(
        self, sede_id: uuid.UUID | None = None, status: str | None = None
    ) -> list[Inventory]:
        query = select(Inventory)
        if sede_id:
            query = query.where(Inventory.sede_id == sede_id)
        if status:
            query = query.where(Inventory.status == status)
        query = query.order_by(Inventory.updated_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, inventory_id: uuid.UUID) -> Inventory | None:
        result = await self.db.execute(
            select(Inventory).where(Inventory.inventory_id == inventory_id)
        )
        return result.scalar_one_or_none()

    async def update_stock(
        self, inventory_id: uuid.UUID, data: InventoryUpdate
    ) -> Inventory | None:
        item = await self.get_by_id(inventory_id)
        if item is None:
            return None

        if data.current_stock is not None:
            item.current_stock = data.current_stock
        if data.minimum_stock is not None:
            item.minimum_stock = data.minimum_stock
        if data.unit is not None:
            item.unit = data.unit

        item.status = await self.calculate_status(
            float(item.current_stock), float(item.minimum_stock)
        )
        await self.db.flush()
        return item

    async def get_critical_count(self, sede_id: uuid.UUID | None = None) -> int:
        query = select(func.count(Inventory.inventory_id)).where(
            Inventory.status == "Crítico"
        )
        if sede_id:
            query = query.where(Inventory.sede_id == sede_id)
        result = await self.db.execute(query)
        return result.scalar()
