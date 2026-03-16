from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📰 Yangiliklar"), KeyboardButton(text="ℹ️ Ma'lumot")],
            [KeyboardButton(text="📞 Aloqa"),       KeyboardButton(text="❓ Yordam")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyu tugmasini tanlang..."
    )


def contact_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Email yuborish", url="mailto:info@example.com")],
        [InlineKeyboardButton(text="🌐 Veb-sayt",       url="https://example.com")],
    ])
