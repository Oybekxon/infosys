import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from handlers import start, menu, help_cmd, echo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL  = os.getenv("REDIS_URL", "redis://localhost:6379/1")


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN muhit o'zgaruvchisi ko'rsatilmagan!")

    redis = Redis.from_url(REDIS_URL)
    storage = RedisStorage(redis=redis)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(start)
    dp.include_router(menu)
    dp.include_router(help_cmd)
    dp.include_router(echo)

    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
