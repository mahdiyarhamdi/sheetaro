"""Admin settings management handlers for the bot.

All admin messages include breadcrumb navigation for better UX.
"""

import logging
import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters,
)

from utils.api_client import api_client
from utils.helpers import get_user_menu_keyboard
from utils.breadcrumb import Breadcrumb, BreadcrumbPath, get_breadcrumb
from keyboards.admin import (
    get_settings_keyboard,
    get_cancel_settings_keyboard,
)

logger = logging.getLogger(__name__)

# Conversation states
SETTINGS_MENU, AWAITING_CARD_NUMBER, AWAITING_CARD_HOLDER = range(3)


async def is_admin(telegram_id: int) -> bool:
    """Check if user is an admin."""
    user = await api_client.get_user(telegram_id)
    if user and user.get('role') == 'ADMIN':
        return True
    return False


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show settings menu."""
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text(
            "⛔ شما دسترسی مدیر ندارید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.SETTINGS)
    
    # Get current card info
    card_info = await api_client.get_payment_card()
    
    if card_info:
        card_number = card_info.get('card_number', '')
        formatted_card = f"{card_number[:4]}-****-****-{card_number[12:]}" if len(card_number) >= 16 else card_number
        card_holder = card_info.get('card_holder', '-')
        
        text = (
            "⚙️ تنظیمات کارت بانکی\n\n"
            f"💳 شماره کارت فعلی: {formatted_card}\n"
            f"👤 به نام: {card_holder}\n\n"
            "برای تغییر یکی از گزینه‌ها را انتخاب کنید:"
        )
    else:
        text = (
            "⚙️ تنظیمات کارت بانکی\n\n"
            "⚠️ اطلاعات کارت تنظیم نشده است.\n\n"
            "برای تنظیم یکی از گزینه‌ها را انتخاب کنید:"
        )
    
    msg = bc.format_message(text)
    await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
    return SETTINGS_MENU


async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle settings menu callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_admin_menu":
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("🔧 بازگشت به منو...")
        await query.message.edit_text(msg)
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    if data == "change_card_number":
        bc.set_path(BreadcrumbPath.SETTINGS_CARD_NUMBER)
        msg = bc.format_message(
            "✏️ تغییر شماره کارت\n\n"
            "لطفاً شماره کارت جدید را وارد کنید (16 رقم):"
        )
        await query.message.edit_text(msg, reply_markup=get_cancel_settings_keyboard())
        return AWAITING_CARD_NUMBER
    
    if data == "change_card_holder":
        bc.set_path(BreadcrumbPath.SETTINGS_CARD_HOLDER)
        msg = bc.format_message(
            "✏️ تغییر نام صاحب کارت\n\n"
            "لطفاً نام صاحب کارت را وارد کنید:"
        )
        await query.message.edit_text(msg, reply_markup=get_cancel_settings_keyboard())
        return AWAITING_CARD_HOLDER
    
    if data == "back_to_settings":
        return await refresh_settings(query, context)
    
    return SETTINGS_MENU


async def handle_card_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle card number input from admin."""
    card_number = update.message.text.strip().replace("-", "").replace(" ", "")
    bc = get_breadcrumb(context)
    
    # Validate card number (16 digits)
    if not re.match(r'^\d{16}$', card_number):
        bc.set_path(BreadcrumbPath.SETTINGS_CARD_NUMBER)
        msg = bc.format_message(
            "❌ شماره کارت نامعتبر است.\n"
            "لطفاً یک شماره کارت 16 رقمی وارد کنید:"
        )
        await update.message.reply_text(msg, reply_markup=get_cancel_settings_keyboard())
        return AWAITING_CARD_NUMBER
    
    # Get user (admin)
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_user_menu_keyboard(context))
        return ConversationHandler.END
    
    # Get current card info to preserve card holder
    card_info = await api_client.get_payment_card()
    card_holder = card_info.get('card_holder', 'نامشخص') if card_info else 'نامشخص'
    
    # Update card number
    result = await api_client.update_payment_card(
        admin_id=user['id'],
        card_number=card_number,
        card_holder=card_holder,
    )
    
    bc.set_path(BreadcrumbPath.SETTINGS)
    
    if result:
        formatted_card = f"{card_number[:4]}-****-****-{card_number[12:]}"
        msg = bc.format_message(
            f"✅ شماره کارت با موفقیت تغییر کرد.\n\n"
            f"شماره جدید: {formatted_card}"
        )
        await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
        return SETTINGS_MENU
    else:
        msg = bc.format_message("❌ خطا در ذخیره شماره کارت.")
        await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
        return SETTINGS_MENU


async def handle_card_holder_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle card holder name input from admin."""
    card_holder = update.message.text.strip()
    bc = get_breadcrumb(context)
    
    # Validate name (at least 2 characters)
    if len(card_holder) < 2:
        bc.set_path(BreadcrumbPath.SETTINGS_CARD_HOLDER)
        msg = bc.format_message(
            "❌ نام نامعتبر است.\n"
            "لطفاً نام صاحب کارت را وارد کنید:"
        )
        await update.message.reply_text(msg, reply_markup=get_cancel_settings_keyboard())
        return AWAITING_CARD_HOLDER
    
    # Get user (admin)
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_user_menu_keyboard(context))
        return ConversationHandler.END
    
    # Get current card info to preserve card number
    card_info = await api_client.get_payment_card()
    if not card_info or not card_info.get('card_number'):
        bc.set_path(BreadcrumbPath.SETTINGS)
        msg = bc.format_message("⚠️ ابتدا باید شماره کارت را تنظیم کنید.")
        await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
        return SETTINGS_MENU
    
    card_number = card_info.get('card_number')
    
    # Update card holder
    result = await api_client.update_payment_card(
        admin_id=user['id'],
        card_number=card_number,
        card_holder=card_holder,
    )
    
    bc.set_path(BreadcrumbPath.SETTINGS)
    
    if result:
        msg = bc.format_message(
            f"✅ نام صاحب کارت با موفقیت تغییر کرد.\n\n"
            f"نام جدید: {card_holder}"
        )
        await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
        return SETTINGS_MENU
    else:
        msg = bc.format_message("❌ خطا در ذخیره نام صاحب کارت.")
        await update.message.reply_text(msg, reply_markup=get_settings_keyboard())
        return SETTINGS_MENU


async def handle_settings_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during settings input."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_settings":
        return await refresh_settings(query, context)
    
    return SETTINGS_MENU


async def refresh_settings(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the settings view."""
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.SETTINGS)
    
    # Get current card info
    card_info = await api_client.get_payment_card()
    
    if card_info:
        card_number = card_info.get('card_number', '')
        formatted_card = f"{card_number[:4]}-****-****-{card_number[12:]}" if len(card_number) >= 16 else card_number
        card_holder = card_info.get('card_holder', '-')
        
        text = (
            "⚙️ تنظیمات کارت بانکی\n\n"
            f"💳 شماره کارت فعلی: {formatted_card}\n"
            f"👤 به نام: {card_holder}\n\n"
            "برای تغییر یکی از گزینه‌ها را انتخاب کنید:"
        )
    else:
        text = (
            "⚙️ تنظیمات کارت بانکی\n\n"
            "⚠️ اطلاعات کارت تنظیم نشده است.\n\n"
            "برای تنظیم یکی از گزینه‌ها را انتخاب کنید:"
        )
    
    msg = bc.format_message(text)
    await query.message.edit_text(msg, reply_markup=get_settings_keyboard())
    return SETTINGS_MENU


# Create conversation handler
admin_settings_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("settings", show_settings),
        MessageHandler(filters.Regex("^(⚙️ تنظیمات|تنظیمات)$"), show_settings),
    ],
    states={
        SETTINGS_MENU: [
            CallbackQueryHandler(handle_settings_callback),
        ],
        AWAITING_CARD_NUMBER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_number_input),
            CallbackQueryHandler(handle_settings_cancel),
        ],
        AWAITING_CARD_HOLDER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_holder_input),
            CallbackQueryHandler(handle_settings_cancel),
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), lambda u, c: ConversationHandler.END),
    ],
)
