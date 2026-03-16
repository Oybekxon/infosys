from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import httpx
import os

from models.database import get_db, Broadcast, TelegramUser, BroadcastStatus
from routers.auth import get_current_admin, Admin

router = APIRouter()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


class BroadcastCreate(BaseModel):
    title: str
    text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None


async def send_broadcast_task(broadcast_id: int, db: AsyncSession):
    """Background: barcha foydalanuvchilarga xabar yuborish"""
    result = await db.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        return

    # Faol foydalanuvchilarni olish
    users_result = await db.execute(
        select(TelegramUser).where(TelegramUser.status == "active")
    )
    users = users_result.scalars().all()

    sent = 0
    failed = 0

    async with httpx.AsyncClient() as client:
        for user in users:
            try:
                if broadcast.media_type == "photo" and broadcast.media_url:
                    resp = await client.post(
                        f"{TELEGRAM_API}/sendPhoto",
                        json={
                            "chat_id": user.telegram_id,
                            "photo": broadcast.media_url,
                            "caption": broadcast.text,
                            "parse_mode": "HTML",
                        },
                        timeout=10,
                    )
                else:
                    resp = await client.post(
                        f"{TELEGRAM_API}/sendMessage",
                        json={
                            "chat_id": user.telegram_id,
                            "text": broadcast.text,
                            "parse_mode": "HTML",
                        },
                        timeout=10,
                    )

                if resp.status_code == 200:
                    sent += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

    broadcast.status = BroadcastStatus.sent
    broadcast.sent_at = datetime.utcnow()
    broadcast.sent_count = sent
    broadcast.fail_count = failed
    await db.commit()


@router.get("/")
async def list_broadcasts(
    skip: int = 0, limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    result = await db.execute(
        select(Broadcast).order_by(desc(Broadcast.created_at)).offset(skip).limit(limit)
    )
    items = result.scalars().all()
    return [
        {
            "id": b.id,
            "title": b.title,
            "text": b.text[:100],
            "status": b.status,
            "sent_count": b.sent_count,
            "fail_count": b.fail_count,
            "created_at": str(b.created_at),
            "sent_at": str(b.sent_at) if b.sent_at else None,
        }
        for b in items
    ]


@router.post("/", status_code=201)
async def create_broadcast(
    data: BroadcastCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    broadcast = Broadcast(
        title=data.title,
        text=data.text,
        media_url=data.media_url,
        media_type=data.media_type,
        scheduled_at=data.scheduled_at,
        status=BroadcastStatus.draft,
        created_by=admin.id,
    )
    db.add(broadcast)
    await db.commit()
    await db.refresh(broadcast)

    # Agar scheduled_at yo'q bo'lsa — darhol yuborish
    if not data.scheduled_at:
        broadcast.status = BroadcastStatus.scheduled
        await db.commit()
        background_tasks.add_task(send_broadcast_task, broadcast.id, db)

    return {"id": broadcast.id, "status": broadcast.status}


@router.post("/{broadcast_id}/send")
async def send_now(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    result = await db.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast topilmadi")

    broadcast.status = BroadcastStatus.scheduled
    await db.commit()
    background_tasks.add_task(send_broadcast_task, broadcast_id, db)
    return {"message": "Yuborish boshlandi"}
