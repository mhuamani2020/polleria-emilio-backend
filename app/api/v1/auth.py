import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user, get_current_session
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.user import UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshRequest, SessionResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    ip_address = request.client.host if request.client else None
    return await service.login(
        username=data.username,
        password=data.password,
        force=data.force,
        device_info=data.device_info,
        ip_address=ip_address,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post("/logout")
async def logout(
    session: UserSession | None = Depends(get_current_session),
    db: AsyncSession = Depends(get_db),
):
    if session:
        service = AuthService(db)
        await service.logout(session.id)
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/me/sessions", response_model=list[SessionResponse])
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.get_user_sessions(current_user.user_id)


@router.post("/me/sessions/{session_id}/revoke")
async def revoke_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    sessions = await service.get_user_sessions(current_user.user_id)
    if not any(s.id == session_id for s in sessions):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    await service.close_session_by_id(session_id)
    return {"message": "Sesión cerrada exitosamente"}
