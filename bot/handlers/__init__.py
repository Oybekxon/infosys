"""Bot handlerlari — start, menu, yordam, echo"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import logging

import api_client
from keyboards.menu import main_menu_kb, contact_kb

logger = logging.getLogger(__name__)

# ─── /start ───────────────────────────────────────────
start = Router()

@start.message(CommandStart())
async def cmd_start(msg: Message):
    user = msg.from_user
    try:
        db_user = await api_client.upsert_user(
            telegram_id   = user.id,
            username      = user.username,
            first_name    = user.first_name,
            last_name     = user.last_name,
            language_code = user.language_code or "uz",
        )
        await api_client.save_message(
            user_id       = db_user["id"],
            text          = msg.text or "/start",
            direction     = "in",
            telegram_msg_id = msg.message_id,
        )
    except Exception as e:
        logger.warning(f"API xatosi: {e}")

    await msg.answer(
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        "InfoSys axborot tizimiga xush kelibsiz.\n"
        "Quyidagi menyudan foydalaning:",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ─── Menyu handlerlari ────────────────────────────────
menu = Router()

@menu.message(F.text == "📰 Yangiliklar")
async def news_section(msg: Message):
    await msg.answer(
        "📰 <b>So'nggi yangiliklar</b>\n\n"
        "• Tizim muvaffaqiyatli yangilandi ✅\n"
        "• Yangi funksiyalar qo'shildi 🚀\n"
        "• Texnik xizmat ko'rsatish tugallandi 🔧",
        parse_mode="HTML",
    )

@menu.message(F.text == "ℹ️ Ma'lumot")
async def info_section(msg: Message):
    await msg.answer(
        "ℹ️ <b>Tizim haqida</b>\n\n"
        "InfoSys — Telegram bot va veb-panel yordamida "
        "qurilgan zamonaviy axborot tizimi.\n\n"
        "Versiya: 1.0.0\nYaratuvchi: InfoSys Team",
        parse_mode="HTML",
    )

@menu.message(F.text == "📞 Aloqa")
async def contact_section(msg: Message):
    await msg.answer(
        "📞 <b>Biz bilan bog'laning</b>",
        parse_mode="HTML",
        reply_markup=contact_kb(),
    )


# ─── /help ────────────────────────────────────────────
help_cmd = Router()

@help_cmd.message(Command("help"))
@help_cmd.message(F.text == "❓ Yordam")
async def cmd_help(msg: Message):
    await msg.answer(
        "❓ <b>Yordam</b>\n\n"
        "/start — Boshiga qaytish\n"
        "/help  — Ushbu yordam xabari\n\n"
        "📰 Yangiliklar — So'nggi xabarlar\n"
        "ℹ️ Ma'lumot   — Tizim haqida\n"
        "📞 Aloqa      — Bog'lanish yo'llari",
        parse_mode="HTML",
    )


# ─── Catch-all echo ───────────────────────────────────
echo = Router()

@echo.message()
async def echo_handler(msg: Message):
    await msg.answer(
        "❓ Tushunmadim. /help buyrug'ini ishlating yoki menyu tugmalaridan foydalaning.",
        reply_markup=main_menu_kb(),
    )
