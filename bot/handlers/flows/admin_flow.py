"""Admin Flow - Admin menu and payment management handlers.

This module handles admin-related operations using the unified flow manager.
All admin messages include breadcrumb navigation for better UX.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item,
    FLOW_ADMIN, FLOW_CATALOG, ADMIN_STEPS
)
from utils.breadcrumb import Breadcrumb, BreadcrumbPath, get_breadcrumb
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
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ADMIN_MENU)
    
    msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
    
    await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())


async def handle_admin_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin menu text selection."""
    text = update.message.text
    bc = get_breadcrumb(context)
    
    if "بازگشت" in text:
        clear_flow(context)
        bc.clear()
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
        bc.set_path(BreadcrumbPath.SETTINGS)
        msg = bc.format_message("برای تنظیمات کارت از دستور /settings استفاده کنید.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
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
    bc.set_path(BreadcrumbPath.ADMIN_MENU)
    msg = bc.format_message("گزینه نامعتبر. یکی را انتخاب کنید:")
    await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())


async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of pending payments."""
    set_step(context, 'pending_list')
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    if not result or not result.get('items'):
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("✅ هیچ پرداختی در انتظار تایید نیست.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        set_step(context, 'admin_menu')
        return
    
    payments = result['items']
    update_flow_data(context, 'pending_payments', payments)
    
    msg_text = (
        f"💳 پرداخت های در انتظار تایید ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(msg, reply_markup=get_pending_payments_keyboard(payments))


async def show_admin_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin management menu."""
    set_step(context, 'admin_management')
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ADMIN_MANAGEMENT)
    
    msg = bc.format_message(
        "👥 مدیریت مدیران:\n\n"
        "(در حال توسعه...)"
    )
    await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())


async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reject reason input."""
    # TODO: Implement
    pass


async def handle_add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new admin telegram ID input."""
    # TODO: Implement
    pass
