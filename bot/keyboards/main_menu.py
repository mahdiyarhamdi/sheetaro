"""Main menu keyboard."""

from telegram import ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        ["🛒 ثبت سفارش", "📦 سفارشات من"],
        ["👤 پروفایل", "🔍 رهگیری سفارش"],
        ["📞 پشتیبانی", "ℹ️ راهنما"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
