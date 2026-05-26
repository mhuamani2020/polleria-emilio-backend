import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.product import Product, ComboItem
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
async def list_products(
    category_id: uuid.UUID | None = None,
    search: str | None = None,
    is_combo: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    query = select(Product).where(Product.is_active == True)

    if category_id:
        query = query.where(Product.category_id == category_id)
    if is_combo is not None:
        query = query.where(Product.is_combo == is_combo)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    query = query.order_by(Product.name)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero", "mesero"])
    result = await db.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
        icon=data.icon,
        category_id=data.category_id,
        is_combo=data.is_combo,
    )
    db.add(product)
    await db.flush()

    if data.is_combo and data.combo_items:
        for item in data.combo_items:
            combo_item = ComboItem(
                combo_id=product.product_id,
                product_id=item.product_id,
                qty=item.qty,
            )
            db.add(combo_item)

    await db.flush()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True, exclude={"combo_items"})
    for key, value in update_data.items():
        setattr(product, key, value)

    if data.combo_items is not None:
        existing = await db.execute(
            select(ComboItem).where(ComboItem.combo_id == product_id)
        )
        for item in existing.scalars().all():
            await db.delete(item)

        for item in data.combo_items:
            combo_item = ComboItem(
                combo_id=product_id,
                product_id=item.product_id,
                qty=item.qty,
            )
            db.add(combo_item)

    await db.flush()
    await db.refresh(product)
    return product


@router.delete("/{product_id}")
async def deactivate_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    product.is_active = False
    await db.flush()
    return {"message": "Producto desactivado exitosamente"}
