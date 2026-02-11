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
from keyboards.admin import (
    get_pending_validations_keyboard,
    get_validation_review_keyboard,
    get_validation_reject_keyboard,
)
from utils.api_client import api_client
from utils.notifications import (
    notify_customer_validation_approved,
    notify_customer_validation_rejected,
)

logger = logging.getLogger(__name__)


async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for admin flow based on current step."""
    
    handlers = {
        'admin_menu': handle_admin_menu_text,
        'reject_reason': handle_reject_reason,
        'add_admin_id': handle_add_admin_id,
        'validation_reject_comment': handle_validation_reject_comment,
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
    
    if "اعتبارسنجی" in text:
        await show_pending_validations(update, context)
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

    if "چاپخانه" in text:
        await show_printshop_management(update, context)
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


async def show_printshop_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show print shop management overview for admin."""
    set_step(context, 'printshop_management')

    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ADMIN_MENU)
    bc.push("🏭 چاپخانه‌ها")

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        msg = bc.format_message("❌ خطا در دریافت اطلاعات.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return

    # Get SLA report from API
    import httpx
    try:
        client = await api_client._get_client()
        response = await client.get(
            "/api/v1/admin/printshop-sla",
            params={"admin_id": user['id']},
        )
        response.raise_for_status()
        sla_data = response.json()
    except Exception as e:
        logger.error(f"Error getting SLA report: {e}")
        sla_data = {"queue_size": 0, "printshops": []}

    queue_size = sla_data.get("queue_size", 0)
    printshops = sla_data.get("printshops", [])

    msg_text = (
        f"🏭 مدیریت چاپخانه‌ها\n\n"
        f"📋 سفارش‌ها در صف: {queue_size}\n"
        f"🏭 تعداد چاپخانه‌ها: {len(printshops)}\n\n"
    )

    if printshops:
        msg_text += "📊 عملکرد چاپخانه‌ها:\n\n"
        for ps in printshops:
            name = ps.get('printshop_name', 'بدون نام')
            total = ps.get('total_orders', 0)
            sla = ps.get('sla_compliance_percent')
            sla_text = f"{sla}%" if sla is not None else "-"
            msg_text += f"• {name}: {total} سفارش | SLA: {sla_text}\n"
    else:
        msg_text += "هنوز چاپخانه‌ای ثبت نشده."

    msg = bc.format_message(msg_text)
    await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())


async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reject reason input."""
    # TODO: Implement
    pass


async def handle_add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new admin telegram ID input."""
    # TODO: Implement
    pass


# ==================== Validation Handlers ====================

async def show_pending_validations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of pending validations."""
    set_step(context, 'validations_list')
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return
    
    result = await api_client.get_pending_validations(
        admin_id=user['id'],
        status='PENDING',
        page=1,
        page_size=20,
    )
    
    if not result or not result.get('items'):
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("✅ هیچ اعتبارسنجی در انتظاری وجود ندارد.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        set_step(context, 'admin_menu')
        return
    
    validations = result['items']
    update_flow_data(context, 'pending_validations', validations)
    
    msg_text = (
        f"✅ اعتبارسنجی‌های در انتظار ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(msg, reply_markup=get_pending_validations_keyboard(validations))


async def show_validation_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """Show validation detail for review."""
    set_step(context, 'validation_review')
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.VALIDATION_REVIEW)
    
    # Find validation from cached list or fetch
    validations = get_flow_data_item(context, 'pending_validations') or []
    validation = next((v for v in validations if v['id'] == order_id), None)
    
    if not validation:
        # Try to fetch from API
        user = await api_client.get_user(update.effective_user.id)
        if user:
            result = await api_client.get_pending_validations(admin_id=user['id'])
            if result and result.get('items'):
                validation = next((v for v in result['items'] if v['id'] == order_id), None)
    
    if not validation:
        await update.callback_query.answer("❌ سفارش پیدا نشد", show_alert=True)
        return
    
    update_flow_data(context, 'current_validation', validation)
    
    # Format validation info
    user_name = validation.get('user_name', 'ناشناس')
    user_phone = validation.get('user_phone', '-')
    category = validation.get('category_name', '-')
    plan = validation.get('plan_name', '-')
    template = validation.get('template_name', '-')
    total_price = validation.get('total_price', 0)
    validation_price = validation.get('validation_price', 0)
    
    msg_text = (
        f"📋 جزئیات اعتبارسنجی\n\n"
        f"🆔 شماره سفارش: #{order_id[:8]}\n"
        f"👤 مشتری: {user_name}\n"
        f"📱 شماره تماس: {user_phone}\n"
        f"📁 دسته‌بندی: {category}\n"
        f"📝 پلن طراحی: {plan}\n"
        f"🎨 قالب: {template}\n"
        f"💰 قیمت کل: {int(total_price):,} تومان\n"
        f"💵 هزینه اعتبارسنجی: {int(validation_price):,} تومان\n"
    )
    
    if validation.get('design_preview_url'):
        msg_text += f"\n🖼 پیش‌نمایش طرح ارسال شده است."
    
    msg = bc.format_message(msg_text)
    
    # Edit message with validation details
    await update.callback_query.edit_message_text(
        msg,
        reply_markup=get_validation_review_keyboard(order_id)
    )
    
    # Send design preview if available
    if validation.get('design_preview_url'):
        try:
            preview_url = validation['design_preview_url']
            # Construct full URL if needed
            base_url = api_client.base_url.rstrip('/')
            if not preview_url.startswith('http'):
                if not preview_url.startswith('/api/v1'):
                    preview_url = f"/api/v1{preview_url}"
                preview_url = f"{base_url}{preview_url}"
            
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=preview_url,
                caption="🖼 پیش‌نمایش طرح"
            )
        except Exception as e:
            logger.error(f"Error sending design preview: {e}")


async def handle_validation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle validation-related callbacks. Returns True if handled."""
    query = update.callback_query
    data = query.data
    
    bc = get_breadcrumb(context)
    
    # Back to validations list
    if data == "back_to_validations_list":
        await query.answer()
        bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
        
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.edit_message_text("❌ خطا در دریافت اطلاعات")
            return True
        
        result = await api_client.get_pending_validations(
            admin_id=user['id'],
            status='PENDING',
        )
        
        if not result or not result.get('items'):
            msg = bc.format_message("✅ هیچ اعتبارسنجی در انتظاری وجود ندارد.")
            await query.edit_message_text(msg, reply_markup=get_pending_validations_keyboard([]))
            return True
        
        validations = result['items']
        update_flow_data(context, 'pending_validations', validations)
        
        msg_text = (
            f"✅ اعتبارسنجی‌های در انتظار ({result['total']} مورد):\n\n"
            "برای بررسی روی هر مورد کلیک کنید:"
        )
        msg = bc.format_message(msg_text)
        await query.edit_message_text(msg, reply_markup=get_pending_validations_keyboard(validations))
        return True
    
    # Review validation
    if data.startswith("review_validation_"):
        await query.answer()
        order_id = data.replace("review_validation_", "")
        await show_validation_detail(update, context, order_id)
        return True
    
    # Approve validation
    if data.startswith("approve_validation_"):
        order_id = data.replace("approve_validation_", "")
        
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.answer("❌ خطا در دریافت اطلاعات", show_alert=True)
            return True
        
        result = await api_client.approve_validation(order_id, user['id'])
        
        if result:
            await query.answer("✅ اعتبارسنجی تأیید شد", show_alert=True)
            
            # Notify customer
            validation = get_flow_data_item(context, 'current_validation')
            if validation:
                customer_telegram_id = validation.get('customer_telegram_id')
                if customer_telegram_id:
                    await notify_customer_validation_approved(
                        context.bot,
                        customer_telegram_id,
                        order_id,
                    )
            
            # Go back to list
            bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
            result = await api_client.get_pending_validations(admin_id=user['id'], status='PENDING')
            validations = result.get('items', []) if result else []
            
            if not validations:
                msg = bc.format_message("✅ هیچ اعتبارسنجی در انتظاری وجود ندارد.")
            else:
                msg = bc.format_message(f"✅ اعتبارسنجی‌های در انتظار ({len(validations)} مورد):")
            
            await query.edit_message_text(msg, reply_markup=get_pending_validations_keyboard(validations))
        else:
            await query.answer("❌ خطا در تأیید اعتبارسنجی", show_alert=True)
        return True
    
    # Start reject flow
    if data.startswith("reject_validation_"):
        await query.answer()
        order_id = data.replace("reject_validation_", "")
        set_step(context, 'validation_reject_comment')
        update_flow_data(context, 'rejecting_validation_id', order_id)
        
        bc.set_path(BreadcrumbPath.VALIDATION_REJECT)
        msg = bc.format_message(
            "📝 لطفاً موارد اصلاحی را وارد کنید:\n\n"
            "(این پیام به مشتری ارسال خواهد شد)"
        )
        await query.edit_message_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
        return True
    
    return False


async def handle_validation_reject_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle validation reject comment input."""
    comment = update.message.text.strip()
    order_id = get_flow_data_item(context, 'rejecting_validation_id')
    
    bc = get_breadcrumb(context)
    
    if not order_id:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا: سفارش پیدا نشد.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        set_step(context, 'admin_menu')
        return
    
    if len(comment) < 10:
        msg = bc.format_message("⚠️ لطفاً توضیحات کامل‌تری وارد کنید (حداقل ۱۰ کاراکتر):")
        await update.message.reply_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
        return
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return
    
    result = await api_client.reject_validation(order_id, user['id'], comment)
    
    if result:
        # Notify customer
        validation = get_flow_data_item(context, 'current_validation')
        if validation:
            customer_telegram_id = validation.get('customer_telegram_id')
            if customer_telegram_id:
                await notify_customer_validation_rejected(
                    context.bot,
                    customer_telegram_id,
                    order_id,
                    comment,
                )
        
        bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
        msg = bc.format_message("✅ اعتبارسنجی رد شد و پیام اصلاحیه برای مشتری ارسال شد.")
        
        # Get updated list
        result = await api_client.get_pending_validations(admin_id=user['id'], status='PENDING')
        validations = result.get('items', []) if result else []
        update_flow_data(context, 'pending_validations', validations)
        
        await update.message.reply_text(msg, reply_markup=get_pending_validations_keyboard(validations))
        set_step(context, 'validations_list')
    else:
        msg = bc.format_message("❌ خطا در ثبت رد اعتبارسنجی. لطفاً دوباره تلاش کنید.")
        await update.message.reply_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
