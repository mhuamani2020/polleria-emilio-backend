import asyncio
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import AsyncSessionLocal
from app.models.realtime_event import RealtimeEvent

router = APIRouter()


async def create_event(db: AsyncSession, sede_id: uuid.UUID, type: str, payload: dict):
    event = RealtimeEvent(sede_id=sede_id, type=type, payload=payload)
    db.add(event)
    await db.flush()


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
):
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await ws.close(code=4001)
        return

    sede_id = uuid.UUID(payload.get("sede_id"))
    await ws.accept()

    last_id = 0
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.max(RealtimeEvent.id)).where(RealtimeEvent.sede_id == sede_id)
            )
            last_id = result.scalar() or 0

        while True:
            try:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(RealtimeEvent)
                        .where(RealtimeEvent.sede_id == sede_id, RealtimeEvent.id > last_id)
                        .order_by(RealtimeEvent.id.asc())
                    )
                    for event in result.scalars().all():
                        await ws.send_json({
                            "type": event.type,
                            "data": event.payload,
                            "event_id": event.id,
                        })
                        last_id = event.id
            except WebSocketDisconnect:
                raise
            except Exception:
                pass
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
