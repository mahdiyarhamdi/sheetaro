"""Admin Flow - Admin menu and payment management handlers.

This module handles admin-related operations using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item,
    FLOW_ADMIN, FLOW_CATALOG, ADMIN_STEPS
)
from keyboards.manager import (
    get_main_menu_keyboard, get_admin_menu_keyboard,
    get_pending_payments_keyboard, get_payment_review_keyboard,
    get_cancel_keyboard
)
from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for admin flow based on current step."""
    
    handlers = {
        'admin_menu': handle_admin_menu_text,
        'reject_reason': handle_reject_reason,
        'add_admin_id': handle_add_admin_id,
    }
    
    handler = handlers.get(step)
    if handler:
        await handler(update, context)
    else:
        logger.warning(f"Unknown admin step for text: {step}")
        await show_admin_menu(update, context)


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin menu."""
    set_flow(context, FLOW_ADMIN, 'admin_menu')
    
    await update.message.reply_text(
        "🔧 پنل مدیریت\n\nیکی را انتخاب کنید:",
        reply_markup=get_admin_menu_keyboard()
    )


async def handle_admin_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin menu text selection."""
    text = update.message.text
    
    if "بازگشت" in text:
        clear_flow(context)
        is_admin = context.user_data.get('is_admin', False)
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard(is_admin)
        )
        return
    
    if "پرداخت" in text:
        await show_pending_payments(update, context)
        return
    
    if "تنظیمات کارت" in text:
        await update.message.reply_text(
            "برای تنظیمات کارت از دستور /settings استفاده کنید.",
            reply_markup=get_admin_menu_keyboard()
        )
        return
    
    if "مدیریت مدیران" in text:
        await show_admin_management(update, context)
        return
    
    if "کاتالوگ" in text:
        # Switch to catalog flow
        from handlers.flows.catalog_flow import show_catalog_menu
        await show_catalog_menu(update, context)
        return
    
    # Unknown option
    await update.message.reply_text(
        "گزینه نامعتبر. یکی را انتخاب کنید:",
        reply_markup=get_admin_menu_keyboard()
    )


async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of pending payments."""
    set_step(context, 'pending_list')
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_admin_menu_keyboard()
        )
        return
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "هیچ پرداختی در انتظار تایید نیست.",
            reply_markup=get_admin_menu_keyboard()
        )
        set_step(context, 'admin_menu')
        return
    
    payments = result['items']
    update_flow_data(context, 'pending_payments', payments)
    
    await update.message.reply_text(
        f"پرداخت های در انتظار تایید ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:",
        reply_markup=get_pending_payments_keyboard(payments)
    )


async def show_admin_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin management menu."""
    set_step(context, 'admin_management')
    
    await update.message.reply_text(
        "مدیریت مدیران:\n\n"
        "(در حال توسعه...)",
        reply_markup=get_admin_menu_keyboard()
    )


async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reject reason input."""
    # TODO: Implement
    pass


async def handle_add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new admin telegram ID input."""
    # TODO: Implement
    pass

