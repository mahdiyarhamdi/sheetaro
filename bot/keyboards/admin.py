"""Admin management keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for admin main menu."""
    keyboard = [
        ["💳 پرداخت‌های در انتظار تأیید"],
        ["⚙️ تنظیمات کارت بانکی"],
        ["👥 مدیریت مدیران"],
        ["🔙 بازگشت به منو"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_pending_payments_keyboard(payments: list) -> InlineKeyboardMarkup:
    """Get inline keyboard for pending payments list."""
    keyboard = []
    
    for payment in payments:
        payment_id = str(payment.get('id', ''))[:8]
        amount = int(payment.get('amount', 0))
        customer_name = payment.get('customer_name', 'ناشناس')
        
        button_text = f"#{payment_id} - {amount:,} تومان - {customer_name}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"review_payment_{payment['id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_payment_review_keyboard(payment_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for reviewing a payment."""
    keyboard = [
        [InlineKeyboardButton("✅ تأیید پرداخت", callback_data=f"approve_{payment_id}")],
        [InlineKeyboardButton("❌ رد کردن", callback_data=f"reject_{payment_id}")],
        [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_pending_list")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_reject_confirm_keyboard(payment_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for reject confirmation."""
    keyboard = [
        [InlineKeyboardButton("🔙 انصراف", callback_data=f"review_payment_{payment_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for settings menu."""
    keyboard = [
        [InlineKeyboardButton("✏️ تغییر شماره کارت", callback_data="change_card_number")],
        [InlineKeyboardButton("✏️ تغییر نام صاحب کارت", callback_data="change_card_holder")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_settings_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for cancelling settings change."""
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="back_to_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_management_keyboard(admins: list) -> InlineKeyboardMarkup:
    """Get keyboard for admin management."""
    keyboard = []
    
    for admin in admins:
        admin_name = f"{admin.get('first_name', '')} {admin.get('last_name', '')}".strip()
        telegram_id = admin.get('telegram_id', '')
        button_text = f"👤 {admin_name} (@{admin.get('username', telegram_id)})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"admin_info_{telegram_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("➕ افزودن مدیر جدید", callback_data="add_admin")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_admin_info_keyboard(telegram_id: int, is_self: bool = False) -> InlineKeyboardMarkup:
    """Get keyboard for admin info view."""
    keyboard = []
    
    if not is_self:
        keyboard.append([InlineKeyboardButton("❌ حذف از مدیران", callback_data=f"remove_admin_{telegram_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_admin_list")])
    
    return InlineKeyboardMarkup(keyboard)


def get_confirm_remove_admin_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for confirming admin removal."""
    keyboard = [
        [InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"confirm_remove_admin_{telegram_id}")],
        [InlineKeyboardButton("❌ خیر، برگرد", callback_data=f"admin_info_{telegram_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_add_admin_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for cancelling add admin."""
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="back_to_admin_list")],
    ]
    return InlineKeyboardMarkup(keyboard)

