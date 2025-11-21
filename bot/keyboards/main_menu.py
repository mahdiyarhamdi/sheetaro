from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard with excellent UX/CX."""
    keyboard = [
        [
            KeyboardButton("🏷️ سفارش لیبل"),
            KeyboardButton("💼 سفارش کارت ویزیت"),
        ],
        [
            KeyboardButton("📦 سفارشات من"),
            KeyboardButton("👤 پروفایل من"),
        ],
        [
            KeyboardButton("❓ راهنما"),
            KeyboardButton("📞 پشتیبانی"),
        ],
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="یکی از گزینه‌ها را انتخاب کنید..."
    )


# Button text constants for easy reference
class MenuButtons:
    """Menu button texts."""
    ORDER_LABEL = "🏷️ سفارش لیبل"
    ORDER_BUSINESS_CARD = "💼 سفارش کارت ویزیت"
    MY_ORDERS = "📦 سفارشات من"
    MY_PROFILE = "👤 پروفایل من"
    HELP = "❓ راهنما"
    SUPPORT = "📞 پشتیبانی"

