import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RealtimeEvent(Base):
    __tablename__ = "realtime_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sede_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_realtime_events_sede_id", "sede_id", "id"),
    )
