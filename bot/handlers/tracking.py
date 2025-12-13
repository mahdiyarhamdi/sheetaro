"""Order tracking handlers for the bot."""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from utils.api_client import api_client
from keyboards.orders import get_status_text
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def track_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle quick order tracking."""
    await update.message.reply_text(
        "🔍 برای رهگیری سفارش، شماره سفارش یا کد رهگیری را وارد کنید:\n\n"
        "مثال: #abc12345"
    )
    context.user_data['awaiting_tracking'] = True


async def handle_tracking_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tracking input."""
    if not context.user_data.get('awaiting_tracking'):
        return
    
    text = update.message.text.strip()
    context.user_data['awaiting_tracking'] = False
    
    # Remove # if present
    if text.startswith('#'):
        text = text[1:]
    
    # Get user
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Try to find order
    result = await api_client.get_user_orders(user_id=user['id'])
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "سفارشی یافت نشد.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Search for matching order
    found_order = None
    for order in result['items']:
        if order['id'].startswith(text) or order.get('tracking_code') == text:
            found_order = order
            break
    
    if not found_order:
        await update.message.reply_text(
            "سفارش با این مشخصات یافت نشد.\n"
            "لطفاً شماره سفارش صحیح را وارد کنید.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Show order status
    status_text = get_status_text(found_order.get('status', ''))
    
    tracking_info = ""
    if found_order.get('tracking_code'):
        tracking_info = f"\n📍 کد رهگیری پستی: {found_order['tracking_code']}"
    
    await update.message.reply_text(
        f"📋 وضعیت سفارش #{found_order['id'][:8]}:\n\n"
        f"وضعیت: {status_text}\n"
        f"تاریخ ثبت: {found_order.get('created_at', '')[:10]}"
        f"{tracking_info}",
        reply_markup=get_main_menu_keyboard()
    )

