from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta

from models.database import get_db, TelegramUser, Message, Broadcast, Activity
from routers.auth import get_current_admin

router = APIRouter()


@router.get("/dashboard")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Jami foydalanuvchilar
    total_users = (await db.execute(select(func.count(TelegramUser.id)))).scalar()

    # Bu oy yangi foydalanuvchilar
    new_users_month = (await db.execute(
        select(func.count(TelegramUser.id)).where(TelegramUser.created_at >= month_ago)
    )).scalar()

    # Faol foydalanuvchilar
    active_users = (await db.execute(
        select(func.count(TelegramUser.id)).where(TelegramUser.status == "active")
    )).scalar()

    # Jami xabarlar
    total_messages = (await db.execute(select(func.count(Message.id)))).scalar()

    # Bugun yuborilgan xabarlar
    today_messages = (await db.execute(
        select(func.count(Message.id)).where(Message.created_at >= today_start)
    )).scalar()

    # Jami broadcastlar
    total_broadcasts = (await db.execute(select(func.count(Broadcast.id)))).scalar()

    # Oxirgi 7 kun xabarlar grafigi
    daily_messages = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = (await db.execute(
            select(func.count(Message.id)).where(
                Message.created_at >= day_start,
                Message.created_at < day_end
            )
        )).scalar()
        daily_messages.append({
            "date": day_start.strftime("%d.%m"),
            "count": count
        })

    # Oxirgi 7 kun foydalanuvchilar
    daily_users = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = (await db.execute(
            select(func.count(TelegramUser.id)).where(
                TelegramUser.created_at >= day_start,
                TelegramUser.created_at < day_end
            )
        )).scalar()
        daily_users.append({
            "date": day_start.strftime("%d.%m"),
            "count": count
        })

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "new_month": new_users_month,
        },
        "messages": {
            "total": total_messages,
            "today": today_messages,
        },
        "broadcasts": {
            "total": total_broadcasts,
        },
        "charts": {
            "daily_messages": daily_messages,
            "daily_users": daily_users,
        },
    }
