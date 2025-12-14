"""Main menu keyboard."""

from telegram import ReplyKeyboardMarkup


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        ["🛒 ثبت سفارش", "📦 سفارشات من"],
        ["👤 پروفایل", "🔍 رهگیری سفارش"],
        ["📞 پشتیبانی", "ℹ️ راهنما"]
    ]
    
    # Add admin panel button for admins
    if is_admin:
        keyboard.append(["🔧 پنل مدیریت"])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
