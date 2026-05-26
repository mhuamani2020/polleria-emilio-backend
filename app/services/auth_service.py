import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth import ActiveSessionInfo, TokenResponse, LoginConflictResponse
from app.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(
        self,
        username: str,
        password: str,
        force: bool = False,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
            )

        active_session = await self._get_active_session(user.user_id)

        if active_session and not force:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=LoginConflictResponse(
                    detail="Ya tienes una sesión activa en otro dispositivo",
                    session=ActiveSessionInfo(
                        device_info=active_session.device_info,
                        ip_address=active_session.ip_address,
                        created_at=active_session.created_at,
                    ),
                ).model_dump(),
            )

        if active_session and force:
            await self._close_session(active_session.id)

        session = await self._create_session(
            user_id=user.user_id,
            device_info=device_info,
            ip_address=ip_address,
        )

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role,
            sede_id=user.sede_id,
        )
        refresh_token = create_refresh_token(
            user_id=user.user_id,
            session_id=session.id,
        )

        logger.info(
            "Login exitoso",
            extra={"user": user.username, "role": user.role, "session": str(session.id)},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        from app.core.security import decode_token

        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
            )

        session_id = uuid.UUID(payload.get("session_id"))
        user_id = uuid.UUID(payload.get("sub"))

        result = await self.db.execute(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.is_active == True,
            )
        )
        session = result.scalar_one_or_none()

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión no encontrada o cerrada",
            )

        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo",
            )

        new_access_token = create_access_token(
            user_id=user.user_id,
            role=user.role,
            sede_id=user.sede_id,
        )
        new_refresh_token = create_refresh_token(
            user_id=user.user_id,
            session_id=session.id,
        )

        session.refresh_token = new_refresh_token

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, session_id: uuid.UUID) -> None:
        await self._close_session(session_id)
        logger.info("Logout exitoso", extra={"session": str(session_id)})

    async def get_user_sessions(self, user_id: uuid.UUID) -> list[UserSession]:
        result = await self.db.execute(
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .order_by(UserSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def close_session_by_id(self, session_id: uuid.UUID) -> None:
        await self._close_session(session_id)

    async def _get_active_session(self, user_id: uuid.UUID) -> UserSession | None:
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def _create_session(
        self,
        user_id: uuid.UUID,
        device_info: str | None,
        ip_address: str | None,
    ) -> UserSession:
        session_id = uuid.uuid4()
        refresh_token = create_refresh_token(
            user_id=user_id,
            session_id=session_id,
        )

        session = UserSession(
            id=session_id,
            user_id=user_id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            is_active=True,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def _close_session(self, session_id: uuid.UUID) -> None:
        await self.db.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(is_active=False, closed_at=datetime.now(timezone.utc))
        )
