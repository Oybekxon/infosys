from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import httpx
import os

from models.database import get_db, Message, Broadcast, TelegramUser, BroadcastStatus, Activity
from routers.auth import get_current_admin, Admin

router = APIRouter()


# ─── Xabarlar ─────────────────────────────────────────

class MessageIn(BaseModel):
    user_id: int
    text: str
    direction: str = "in"
    telegram_msg_id: Optional[int] = None


@router.get("/")
async def list_messages(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    q = select(Message).order_by(desc(Message.created_at))
    if user_id:
        q = q.where(Message.user_id == user_id)
    result = await db.execute(q.offset(skip).limit(limit))
    msgs = result.scalars().all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "direction": m.direction,
            "text": m.text,
            "media_type": m.media_type,
            "is_read": m.is_read,
            "created_at": str(m.created_at),
        }
        for m in msgs
    ]


@router.post("/", status_code=201)
async def save_message(data: MessageIn, db: AsyncSession = Depends(get_db)):
    """Bot bu endpointni chaqiradi"""
    msg = Message(**data.model_dump())
    db.add(msg)
    await db.commit()
    return {"id": msg.id}
