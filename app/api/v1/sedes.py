import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.sede import Sede
from app.models.user import User
from app.schemas.sede import SedeCreate, SedeUpdate, SedeResponse

router = APIRouter(prefix="/sedes", tags=["Sedes"])


@router.get("", response_model=list[SedeResponse])
async def list_sedes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(select(Sede).order_by(Sede.name))
    return list(result.scalars().all())


@router.get("/{sede_id}", response_model=SedeResponse)
async def get_sede(
    sede_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(select(Sede).where(Sede.sede_id == sede_id))
    sede = result.scalar_one_or_none()
    if sede is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    return sede


@router.post("", response_model=SedeResponse, status_code=status.HTTP_201_CREATED)
async def create_sede(
    data: SedeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    sede = Sede(**data.model_dump())
    db.add(sede)
    await db.flush()
    await db.refresh(sede)
    return sede


@router.put("/{sede_id}", response_model=SedeResponse)
async def update_sede(
    sede_id: uuid.UUID,
    data: SedeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(select(Sede).where(Sede.sede_id == sede_id))
    sede = result.scalar_one_or_none()
    if sede is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sede, key, value)

    await db.flush()
    await db.refresh(sede)
    return sede


@router.delete("/{sede_id}")
async def delete_sede(
    sede_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    result = await db.execute(select(Sede).where(Sede.sede_id == sede_id))
    sede = result.scalar_one_or_none()
    if sede is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")

    await db.delete(sede)
    return {"message": "Sede eliminada exitosamente"}
