from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for profile editing options."""
    keyboard = [
        [
            InlineKeyboardButton("📞 ویرایش شماره تماس", callback_data="edit_phone"),
        ],
        [
            InlineKeyboardButton("📍 ویرایش آدرس", callback_data="edit_address"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with cancel button."""
    keyboard = [
        [
            InlineKeyboardButton("❌ انصراف", callback_data="cancel"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)

