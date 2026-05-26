import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.merma import Merma
from app.models.user import User
from app.schemas.merma import MermaCreate, MermaResponse

router = APIRouter(prefix="/mermas", tags=["Mermas"])


@router.get("", response_model=list[MermaResponse])
async def list_mermas(
    sede_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero"])
    from app.models.inventory import Inventory

    query = select(Merma).join(Inventory, Merma.inventory_id == Inventory.inventory_id)

    if sede_id:
        query = query.where(Inventory.sede_id == sede_id)

    query = query.order_by(Merma.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=MermaResponse, status_code=status.HTTP_201_CREATED)
async def create_merma(
    data: MermaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    from app.services.inventory_service import InventoryService
    from app.schemas.inventory import InventoryUpdate

    inv_service = InventoryService(db)
    inventory = await inv_service.get_by_id(data.inventory_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de inventario no encontrado")

    new_stock = float(inventory.current_stock) - data.quantity
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad de merma supera el stock actual",
        )

    merma = Merma(
        inventory_id=data.inventory_id,
        quantity=data.quantity,
        unit=data.unit,
        reason=data.reason,
        notes=data.notes,
        registered_by=current_user.user_id,
    )
    db.add(merma)

    await inv_service.update_stock(
        data.inventory_id,
        InventoryUpdate(current_stock=new_stock),
    )

    await db.flush()
    await db.refresh(merma)
    return merma
