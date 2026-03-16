from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from pydantic import BaseModel
from typing import Optional

from models.database import get_db, TelegramUser, UserStatus
from routers.auth import get_current_admin

router = APIRouter()


class UserOut(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    language_code: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class UserUpsert(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    language_code: str = "uz"


# ─── Endpointlar ──────────────────────────────────────

@router.get("/")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    query = select(TelegramUser)

    if search:
        query = query.where(
            TelegramUser.username.ilike(f"%{search}%") |
            TelegramUser.first_name.ilike(f"%{search}%")
        )
    if status:
        query = query.where(TelegramUser.status == status)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar()

    query = query.offset(skip).limit(limit).order_by(TelegramUser.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "status": u.status,
                "language_code": u.language_code,
                "created_at": str(u.created_at),
            }
            for u in users
        ],
    }


@router.post("/upsert")
async def upsert_user(
    data: UserUpsert,
    db: AsyncSession = Depends(get_db),
):
    """Bot bu endpointni chaqiradi — foydalanuvchini yaratadi yoki yangilaydi"""
    result = await db.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == data.telegram_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.username = data.username
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.language_code = data.language_code
    else:
        user = TelegramUser(**data.model_dump())
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "telegram_id": user.telegram_id, "status": user.status}


@router.patch("/{user_id}/status")
async def change_status(
    user_id: int,
    status: UserStatus,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    result = await db.execute(select(TelegramUser).where(TelegramUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.status = status
    await db.commit()
    return {"message": f"Status '{status}' ga o'zgartirildi"}


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    result = await db.execute(select(TelegramUser).where(TelegramUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user
