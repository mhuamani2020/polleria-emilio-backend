import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import check_role
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    sede_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_role(current_user, ["admin"])
    service = StatsService(db)
    return await service.get_dashboard(sede_id=sede_id)
