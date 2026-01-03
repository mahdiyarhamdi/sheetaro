"""Order Flow - Customer order management handlers.

This module handles order-related operations using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item,
    FLOW_ORDERS, ORDER_STEPS
)
from keyboards.manager import get_main_menu_keyboard, get_orders_menu_keyboard
from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def handle_orders_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for orders flow."""
    # Most order operations are callback-based, not text-based
    # This handles receipt uploads and similar
    
    if step == 'awaiting_receipt':
        # Check for photo
        if update.message.photo:
            await handle_receipt_upload(update, context)
        else:
            await update.message.reply_text("لطفا تصویر رسید را ارسال کنید.")
    else:
        logger.warning(f"Unknown orders step for text: {step}")
        await show_orders_menu(update, context)


async def show_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show orders menu."""
    set_flow(context, FLOW_ORDERS, 'orders_menu')
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("خطا در دریافت اطلاعات کاربر.")
        return
    
    result = await api_client.get_user_orders(user['id'], page=1, page_size=10)
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "شما هنوز سفارشی ثبت نکرده اید.\n\n"
            "برای ثبت سفارش جدید از منوی اصلی استفاده کنید."
        )
        clear_flow(context)
        return
    
    orders = result['items']
    update_flow_data(context, 'orders', orders)
    
    await update.message.reply_text(
        f"سفارشات شما ({result['total']} مورد):\n\n"
        "نوع سفارشات را انتخاب کنید:",
        reply_markup=get_orders_menu_keyboard()
    )


async def handle_receipt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle receipt image upload."""
    # TODO: Implement receipt upload handling
    pass

