import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationCreate
from app.websocket import create_event

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero"])
    query = select(Notification).where(
        or_(
            Notification.user_id == current_user.user_id,
            Notification.user_id.is_(None),
        )
    )

    if unread_only:
        query = query.where(Notification.is_read == False)

    query = query.order_by(Notification.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero"])
    notif = Notification(**data.model_dump())
    db.add(notif)
    await db.flush()
    await db.refresh(notif)

    notif_data = NotificationResponse.model_validate(notif).model_dump(mode="json")
    try:
        sede_id = current_user.sede_id
        await create_event(db, sede_id, "notification_new", notif_data)
    except Exception:
        pass

    return notif


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero"])
    result = await db.execute(
        select(Notification).where(Notification.notification_id == notification_id)
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")

    notif.is_read = True
    await db.flush()
    return {"message": "Notificación marcada como leída"}


@router.post("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin", "cajero"])
    await db.execute(
        update(Notification)
        .where(
            or_(
                Notification.user_id == current_user.user_id,
                Notification.user_id.is_(None),
            ),
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    await db.flush()
    return {"message": "Todas las notificaciones marcadas como leídas"}
