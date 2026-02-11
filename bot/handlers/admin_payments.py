"""Admin payment management handlers for the bot.

All admin messages include breadcrumb navigation for better UX.
"""

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from utils.api_client import api_client
from utils.notifications import (
    notify_customer_payment_approved,
    notify_customer_payment_rejected,
    notify_customer_validation_approved,
    notify_customer_validation_rejected,
)
from utils.breadcrumb import Breadcrumb, BreadcrumbPath, get_breadcrumb
from keyboards.manager import get_admin_menu_keyboard
from keyboards.admin import (
    get_pending_payments_keyboard,
    get_payment_review_keyboard,
    get_reject_confirm_keyboard,
    get_admin_management_keyboard,
    get_admin_info_keyboard,
    get_confirm_remove_admin_keyboard,
    get_cancel_add_admin_keyboard,
    get_pending_validations_keyboard,
    get_validation_review_keyboard,
    get_validation_reject_keyboard,
)
from utils.helpers import get_user_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
(ADMIN_MENU, PENDING_LIST, PAYMENT_REVIEW, AWAITING_REJECT_REASON,
 ADMIN_MANAGEMENT, ADMIN_INFO, AWAITING_NEW_ADMIN_ID,
 VALIDATIONS_LIST, VALIDATION_REVIEW, AWAITING_VALIDATION_REJECT_COMMENT) = range(10)


async def is_admin(telegram_id: int) -> bool:
    """Check if user is an admin."""
    user = await api_client.get_user(telegram_id)
    if user and user.get('role') == 'ADMIN':
        return True
    return False


async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show admin menu."""
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text(
            "⛔ شما دسترسی مدیر ندارید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ADMIN_MENU)
    
    msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
    
    await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
    return ADMIN_MENU


async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin menu selection."""
    text = update.message.text
    
    if text == "🔙 بازگشت به منو":
        # Clear breadcrumb
        bc = get_breadcrumb(context)
        bc.clear()
        
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    if "پرداخت‌های در انتظار" in text:
        return await show_pending_payments(update, context)
    
    if "اعتبارسنجی" in text:
        return await show_pending_validations(update, context)
    
    if "تنظیمات کارت" in text:
        # This will be handled by admin_settings handler
        bc = get_breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("برای تنظیمات کارت از دستور /settings استفاده کنید.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    if "مدیریت مدیران" in text:
        return await show_admin_management(update, context)
    
    if "کاتالوگ" in text:
        # Set catalog mode and show catalog menu directly
        context.user_data['in_catalog_mode'] = True
        from handlers.admin_catalog import show_catalog_menu
        await show_catalog_menu(update, context)
        return ConversationHandler.END
    
    return ADMIN_MENU


async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of payments awaiting approval."""
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
    
    if not result or not result.get('items'):
        msg = bc.format_message("✅ هیچ پرداختی در انتظار تأیید نیست.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    payments = result['items']
    context.user_data['pending_payments'] = payments
    
    msg_text = (
        f"💳 پرداخت‌های در انتظار تأیید ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(msg, reply_markup=get_pending_payments_keyboard(payments))
    return PENDING_LIST


async def handle_pending_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pending list callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_admin_menu":
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
        
        await query.message.edit_text("بازگشت به منوی مدیریت...")
        await query.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    if data.startswith("review_payment_"):
        payment_id = data[15:]  # Remove "review_payment_" prefix
        
        # Get payment details
        payment = await api_client.get_payment(payment_id)
        
        if not payment:
            bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
            msg = bc.format_message("❌ پرداخت یافت نشد.")
            await query.message.edit_text(msg)
            return PENDING_LIST
        
        context.user_data['current_payment'] = payment
        
        # Set breadcrumb
        bc.set_path(BreadcrumbPath.PAYMENT_REVIEW)
        
        # Format payment details
        detail_text = (
            f"💳 بررسی پرداخت\n\n"
            f"شماره: #{payment['id'][:8]}\n"
            f"مبلغ: {int(float(payment.get('amount', 0))):,} تومان\n"
            f"نوع: {get_payment_type_text(payment.get('type', ''))}\n"
            f"تاریخ: {payment.get('created_at', '')[:10]}\n"
        )
        msg = bc.format_message(detail_text)
        
        # Show receipt image if available
        receipt_url = payment.get('receipt_image_url')
        if receipt_url:
            # Send receipt as photo with full details and buttons in caption
            try:
                await query.message.reply_photo(
                    photo=receipt_url,
                    caption=msg,
                    reply_markup=get_payment_review_keyboard(payment_id)
                )
                # Delete the original message to avoid confusion
                await query.message.delete()
                return PAYMENT_REVIEW
            except Exception as e:
                logger.error(f"Error sending receipt image: {e}")
                msg = bc.format_message(detail_text + "\n📷 رسید موجود است (خطا در نمایش تصویر)\n")
        
        await query.message.edit_text(msg, reply_markup=get_payment_review_keyboard(payment_id))
        return PAYMENT_REVIEW
    
    return PENDING_LIST


async def handle_payment_review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment review callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_pending_list":
        payments = context.user_data.get('pending_payments', [])
        bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
        
        if payments:
            msg = bc.format_message("💳 پرداخت‌های در انتظار تأیید:")
            await query.message.edit_text(msg, reply_markup=get_pending_payments_keyboard(payments))
        return PENDING_LIST
    
    if data.startswith("approve_"):
        payment_id = data[8:]  # Remove "approve_" prefix
        
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            bc.set_path(BreadcrumbPath.PAYMENT_REVIEW)
            msg = bc.format_message("❌ خطا در دریافت اطلاعات.")
            await query.message.edit_text(msg)
            return PAYMENT_REVIEW
        
        # Get current payment info for notification
        current_payment = context.user_data.get('current_payment', {})
        
        result = await api_client.approve_payment(
            payment_id=payment_id,
            admin_id=user['id'],
        )
        
        if result:
            bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
            msg = bc.format_message(
                "✅ پرداخت با موفقیت تأیید شد.\n\n"
                "به کاربر اطلاع داده می‌شود."
            )
            await query.message.edit_text(msg)
            
            # Notify customer
            customer_telegram_id = current_payment.get('customer_telegram_id')
            if customer_telegram_id:
                await notify_customer_payment_approved(
                    bot=context.bot,
                    customer_telegram_id=customer_telegram_id,
                    payment_id=payment_id,
                    amount=int(float(result.get('amount', 0))),
                )
            
            # Refresh pending list
            return await refresh_pending_list(query, context)
        else:
            bc.set_path(BreadcrumbPath.PAYMENT_REVIEW)
            msg = bc.format_message("❌ خطا در تأیید پرداخت.")
            await query.message.edit_text(msg)
            return PAYMENT_REVIEW
    
    if data.startswith("reject_"):
        payment_id = data[7:]  # Remove "reject_" prefix
        context.user_data['rejecting_payment_id'] = payment_id
        
        bc.set_path(BreadcrumbPath.PAYMENT_REVIEW, "رد پرداخت")
        msg = bc.format_message(
            "❌ رد کردن پرداخت\n\n"
            "لطفاً علت رد کردن را بنویسید:"
        )
        await query.message.edit_text(msg, reply_markup=get_reject_confirm_keyboard(payment_id))
        return AWAITING_REJECT_REASON
    
    return PAYMENT_REVIEW


async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle rejection reason from admin."""
    reason = update.message.text
    payment_id = context.user_data.get('rejecting_payment_id')
    bc = get_breadcrumb(context)
    
    if not payment_id:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا: اطلاعات پرداخت یافت نشد.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    # Get current payment info for notification
    current_payment = context.user_data.get('current_payment', {})
    
    result = await api_client.reject_payment(
        payment_id=payment_id,
        admin_id=user['id'],
        reason=reason,
    )
    
    if result:
        context.user_data.pop('rejecting_payment_id', None)
        
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message(
            f"❌ پرداخت رد شد.\n\n"
            f"علت: {reason}\n\n"
            "به کاربر اطلاع داده می‌شود."
        )
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        
        # Notify customer
        customer_telegram_id = current_payment.get('customer_telegram_id')
        if customer_telegram_id:
            await notify_customer_payment_rejected(
                bot=context.bot,
                customer_telegram_id=customer_telegram_id,
                payment_id=payment_id,
                amount=int(float(result.get('amount', 0))),
                reason=reason,
            )
        
        return ADMIN_MENU
    else:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در رد کردن پرداخت.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU


async def handle_reject_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during reject reason input."""
    query = update.callback_query
    await query.answer()
    bc = get_breadcrumb(context)
    
    if query.data.startswith("review_payment_"):
        payment_id = query.data[15:]
        context.user_data.pop('rejecting_payment_id', None)
        
        # Return to payment review
        payment = context.user_data.get('current_payment')
        if payment:
            bc.set_path(BreadcrumbPath.PAYMENT_REVIEW)
            detail_text = (
                f"💳 بررسی پرداخت\n\n"
                f"شماره: #{payment['id'][:8]}\n"
                f"مبلغ: {int(float(payment.get('amount', 0))):,} تومان\n"
            )
            msg = bc.format_message(detail_text)
            await query.message.edit_text(msg, reply_markup=get_payment_review_keyboard(payment_id))
        return PAYMENT_REVIEW
    
    return AWAITING_REJECT_REASON


async def refresh_pending_list(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the pending payments list."""
    user = await api_client.get_user(query.from_user.id)
    bc = get_breadcrumb(context)
    
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        return ADMIN_MENU
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
    
    if not result or not result.get('items'):
        msg = bc.format_message("✅ هیچ پرداختی در انتظار تأیید نیست.")
        await query.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    payments = result['items']
    context.user_data['pending_payments'] = payments
    
    msg = bc.format_message(f"💳 پرداخت‌های در انتظار تأیید ({result['total']} مورد):")
    await query.message.reply_text(msg, reply_markup=get_pending_payments_keyboard(payments))
    return PENDING_LIST


def get_payment_type_text(payment_type: str) -> str:
    """Get Persian text for payment type."""
    type_map = {
        'VALIDATION': 'اعتبارسنجی',
        'DESIGN': 'طراحی',
        'FIX': 'اصلاح',
        'PRINT': 'چاپ',
        'SUBSCRIPTION': 'اشتراک',
    }
    return type_map.get(payment_type, payment_type)


# ==================== Admin Management Handlers ====================


async def show_admin_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show admin management menu."""
    user = await api_client.get_user(update.effective_user.id)
    bc = get_breadcrumb(context)
    
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_user_menu_keyboard(context))
        return ConversationHandler.END
    
    result = await api_client.get_all_admins(admin_id=user['id'])
    
    bc.set_path(BreadcrumbPath.ADMIN_MANAGEMENT)
    
    if not result or not result.get('items'):
        msg = bc.format_message("❌ خطا در دریافت لیست مدیران.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    admins = result['items']
    context.user_data['admins'] = admins
    
    msg_text = (
        f"👥 مدیریت مدیران ({result['total']} نفر)\n\n"
        "برای مشاهده جزئیات روی هر مدیر کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(msg, reply_markup=get_admin_management_keyboard(admins))
    return ADMIN_MANAGEMENT


async def handle_admin_management_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin management callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_admin_menu":
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
        
        await query.message.edit_text("بازگشت به منوی مدیریت...")
        await query.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    if data == "add_admin":
        bc.set_path(BreadcrumbPath.ADMIN_ADD)
        msg_text = (
            "➕ افزودن مدیر جدید\n\n"
            "شناسه تلگرام (Telegram ID) کاربر جدید را وارد کنید:\n\n"
            "💡 نکته: کاربر باید قبلاً از ربات استفاده کرده باشد."
        )
        msg = bc.format_message(msg_text)
        await query.message.edit_text(msg, reply_markup=get_cancel_add_admin_keyboard())
        return AWAITING_NEW_ADMIN_ID
    
    if data.startswith("admin_info_"):
        telegram_id = int(data[11:])  # Remove "admin_info_" prefix
        return await show_admin_info(query, context, telegram_id)
    
    if data == "back_to_admin_list":
        return await refresh_admin_list(query, context)
    
    return ADMIN_MANAGEMENT


async def show_admin_info(query, context: ContextTypes.DEFAULT_TYPE, telegram_id: int) -> int:
    """Show admin info."""
    admins = context.user_data.get('admins', [])
    admin_info = next((a for a in admins if a.get('telegram_id') == telegram_id), None)
    bc = get_breadcrumb(context)
    
    if not admin_info:
        bc.set_path(BreadcrumbPath.ADMIN_MANAGEMENT)
        msg = bc.format_message("❌ مدیر یافت نشد.")
        await query.message.edit_text(msg)
        return ADMIN_MANAGEMENT
    
    context.user_data['selected_admin'] = admin_info
    
    admin_name = f"{admin_info.get('first_name', '')} {admin_info.get('last_name', '')}".strip()
    username = admin_info.get('username', '-')
    created_at = admin_info.get('created_at', '')[:10]
    
    is_self = telegram_id == query.from_user.id
    
    bc.set_path(BreadcrumbPath.ADMIN_INFO, admin_name)
    
    detail_text = (
        f"👤 اطلاعات مدیر\n\n"
        f"نام: {admin_name}\n"
        f"نام کاربری: @{username}\n"
        f"شناسه تلگرام: {telegram_id}\n"
        f"تاریخ عضویت: {created_at}\n"
    )
    
    if is_self:
        detail_text += "\n⚠️ این اکانت خودتان است."
    
    msg = bc.format_message(detail_text)
    
    await query.message.edit_text(msg, reply_markup=get_admin_info_keyboard(telegram_id, is_self))
    return ADMIN_INFO


async def handle_admin_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin info callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_admin_list":
        return await refresh_admin_list(query, context)
    
    if data.startswith("remove_admin_"):
        telegram_id = int(data[13:])  # Remove "remove_admin_" prefix
        admin_info = context.user_data.get('selected_admin', {})
        admin_name = f"{admin_info.get('first_name', '')} {admin_info.get('last_name', '')}".strip()
        
        bc.set_path(BreadcrumbPath.ADMIN_INFO, admin_name, "حذف")
        msg = bc.format_message(f"⚠️ آیا مطمئن هستید که می‌خواهید {admin_name} را از مدیران حذف کنید؟")
        
        await query.message.edit_text(msg, reply_markup=get_confirm_remove_admin_keyboard(telegram_id))
        return ADMIN_INFO
    
    if data.startswith("confirm_remove_admin_"):
        telegram_id = int(data[21:])  # Remove "confirm_remove_admin_" prefix
        
        user = await api_client.get_user(query.from_user.id)
        if not user:
            bc.set_path(BreadcrumbPath.ADMIN_INFO)
            msg = bc.format_message("❌ خطا در دریافت اطلاعات.")
            await query.message.edit_text(msg)
            return ADMIN_INFO
        
        result = await api_client.demote_from_admin(
            target_telegram_id=telegram_id,
            admin_id=user['id'],
        )
        
        if result:
            bc.set_path(BreadcrumbPath.ADMIN_MANAGEMENT)
            msg = bc.format_message("✅ مدیر با موفقیت حذف شد.")
            await query.message.edit_text(msg)
            return await refresh_admin_list(query, context)
        else:
            bc.set_path(BreadcrumbPath.ADMIN_INFO)
            msg = bc.format_message("❌ خطا در حذف مدیر.")
            await query.message.edit_text(msg)
            return ADMIN_INFO
    
    if data.startswith("admin_info_"):
        telegram_id = int(data[11:])
        return await show_admin_info(query, context, telegram_id)
    
    return ADMIN_INFO


async def handle_new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new admin telegram ID input."""
    text = update.message.text.strip()
    bc = get_breadcrumb(context)
    
    # Validate telegram ID
    try:
        new_admin_telegram_id = int(text)
    except ValueError:
        bc.set_path(BreadcrumbPath.ADMIN_ADD)
        msg = bc.format_message(
            "❌ شناسه نامعتبر است.\n"
            "لطفاً یک عدد وارد کنید:"
        )
        await update.message.reply_text(msg, reply_markup=get_cancel_add_admin_keyboard())
        return AWAITING_NEW_ADMIN_ID
    
    # Get current user (admin)
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    # Check if user exists
    target_user = await api_client.get_user(new_admin_telegram_id)
    if not target_user:
        bc.set_path(BreadcrumbPath.ADMIN_ADD)
        msg = bc.format_message(
            "❌ کاربری با این شناسه یافت نشد.\n"
            "کاربر باید قبلاً از ربات استفاده کرده باشد.\n\n"
            "شناسه دیگری وارد کنید:"
        )
        await update.message.reply_text(msg, reply_markup=get_cancel_add_admin_keyboard())
        return AWAITING_NEW_ADMIN_ID
    
    # Promote to admin
    result = await api_client.promote_to_admin(
        target_telegram_id=new_admin_telegram_id,
        admin_id=user['id'],
    )
    
    if result:
        target_name = f"{target_user.get('first_name', '')} {target_user.get('last_name', '')}".strip()
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message(f"✅ {target_name} به مدیران اضافه شد.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    else:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message(
            "❌ خطا در افزودن مدیر.\n"
            "ممکن است کاربر از قبل مدیر باشد."
        )
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU


async def handle_add_admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during add admin."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_admin_list":
        return await refresh_admin_list(query, context)
    
    return AWAITING_NEW_ADMIN_ID


async def refresh_admin_list(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the admin list."""
    user = await api_client.get_user(query.from_user.id)
    bc = get_breadcrumb(context)
    
    if not user:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        return ADMIN_MENU
    
    result = await api_client.get_all_admins(admin_id=user['id'])
    
    bc.set_path(BreadcrumbPath.ADMIN_MANAGEMENT)
    
    if not result or not result.get('items'):
        msg = bc.format_message("❌ خطا در دریافت لیست مدیران.")
        await query.message.edit_text(msg)
        return ADMIN_MENU
    
    admins = result['items']
    context.user_data['admins'] = admins
    
    msg_text = (
        f"👥 مدیریت مدیران ({result['total']} نفر)\n\n"
        "برای مشاهده جزئیات روی هر مدیر کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await query.message.edit_text(msg, reply_markup=get_admin_management_keyboard(admins))
    return ADMIN_MANAGEMENT


# ==================== Validation Handlers ====================

async def show_pending_validations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of validations awaiting review."""
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    result = await api_client.get_pending_validations(
        admin_id=user['id'],
        status='PENDING',
        page=1,
        page_size=20,
    )
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
    
    if not result or not result.get('items'):
        msg = bc.format_message("✅ هیچ اعتبارسنجی در انتظار بررسی نیست.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    validations = result['items']
    context.user_data['pending_validations'] = validations
    
    msg_text = (
        f"✅ اعتبارسنجی‌های در انتظار ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(msg, reply_markup=get_pending_validations_keyboard(validations))
    return VALIDATIONS_LIST


async def handle_validations_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle validations list callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_admin_menu":
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
        
        await query.message.edit_text("بازگشت به منوی مدیریت...")
        await query.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    if data.startswith("review_validation_"):
        order_id = data[18:]  # Remove "review_validation_" prefix
        
        # Find validation from cached list
        validations = context.user_data.get('pending_validations', [])
        validation = next((v for v in validations if v['id'] == order_id), None)
        
        if not validation:
            bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
            msg = bc.format_message("❌ سفارش یافت نشد.")
            await query.message.edit_text(msg)
            return VALIDATIONS_LIST
        
        context.user_data['current_validation'] = validation
        
        # Set breadcrumb
        bc.set_path(BreadcrumbPath.VALIDATION_REVIEW)
        
        # Format validation details
        user_name = validation.get('user_name', 'ناشناس')
        user_phone = validation.get('user_phone', '-')
        category = validation.get('category_name', '-')
        plan = validation.get('plan_name', '-')
        template = validation.get('template_name', '-')
        total_price = validation.get('total_price', 0)
        validation_price = validation.get('validation_price', 0)
        
        detail_text = (
            f"📋 بررسی اعتبارسنجی\n\n"
            f"🆔 شماره سفارش: #{order_id[:8]}\n"
            f"👤 مشتری: {user_name}\n"
            f"📱 شماره تماس: {user_phone}\n"
            f"📁 دسته‌بندی: {category}\n"
            f"📝 پلن طراحی: {plan}\n"
            f"🎨 قالب: {template}\n"
            f"💰 قیمت کل: {int(total_price):,} تومان\n"
            f"💵 هزینه اعتبارسنجی: {int(validation_price):,} تومان\n"
        )
        msg = bc.format_message(detail_text)
        
        # Show design preview if available
        preview_url = validation.get('design_preview_url')
        if preview_url:
            try:
                base_url = api_client.base_url.rstrip('/')
                if not preview_url.startswith('http'):
                    if not preview_url.startswith('/api/v1'):
                        preview_url = f"/api/v1{preview_url}"
                    preview_url = f"{base_url}{preview_url}"
                
                await query.message.reply_photo(
                    photo=preview_url,
                    caption=msg,
                    reply_markup=get_validation_review_keyboard(order_id)
                )
                await query.message.delete()
                return VALIDATION_REVIEW
            except Exception as e:
                logger.error(f"Error sending design preview: {e}")
                msg = bc.format_message(detail_text + "\n🖼 پیش‌نمایش موجود است (خطا در نمایش)\n")
        
        await query.message.edit_text(msg, reply_markup=get_validation_review_keyboard(order_id))
        return VALIDATION_REVIEW
    
    return VALIDATIONS_LIST


async def handle_validation_review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle validation review callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data == "back_to_validations_list":
        validations = context.user_data.get('pending_validations', [])
        bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
        
        if validations:
            msg = bc.format_message("✅ اعتبارسنجی‌های در انتظار:")
            await query.message.edit_text(msg, reply_markup=get_pending_validations_keyboard(validations))
        else:
            msg = bc.format_message("✅ هیچ اعتبارسنجی در انتظار بررسی نیست.")
            await query.message.edit_text(msg, reply_markup=get_pending_validations_keyboard([]))
        return VALIDATIONS_LIST
    
    if data.startswith("approve_validation_"):
        order_id = data[19:]  # Remove "approve_validation_" prefix
        
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            bc.set_path(BreadcrumbPath.VALIDATION_REVIEW)
            msg = bc.format_message("❌ خطا در دریافت اطلاعات.")
            await query.message.edit_text(msg)
            return VALIDATION_REVIEW
        
        # Get current validation info for notification
        current_validation = context.user_data.get('current_validation', {})
        
        result = await api_client.approve_validation(
            order_id=order_id,
            admin_id=user['id'],
        )
        
        if result:
            bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
            msg = bc.format_message(
                "✅ اعتبارسنجی با موفقیت تأیید شد.\n\n"
                "پیام تأیید برای مشتری ارسال شد."
            )
            
            # Notify customer
            customer_telegram_id = current_validation.get('customer_telegram_id')
            if customer_telegram_id:
                await notify_customer_validation_approved(
                    query.message.get_bot(),
                    customer_telegram_id,
                    order_id,
                )
            
            # Refresh validations list
            refresh_result = await api_client.get_pending_validations(
                admin_id=user['id'],
                status='PENDING',
            )
            validations = refresh_result.get('items', []) if refresh_result else []
            context.user_data['pending_validations'] = validations
            
            await query.message.edit_text(msg, reply_markup=get_pending_validations_keyboard(validations))
            return VALIDATIONS_LIST
        else:
            msg = bc.format_message("❌ خطا در تأیید اعتبارسنجی.")
            await query.message.edit_text(msg, reply_markup=get_validation_review_keyboard(order_id))
            return VALIDATION_REVIEW
    
    if data.startswith("reject_validation_"):
        order_id = data[18:]  # Remove "reject_validation_" prefix
        context.user_data['rejecting_validation_id'] = order_id
        
        bc.set_path(BreadcrumbPath.VALIDATION_REJECT)
        msg = bc.format_message(
            "📝 لطفاً موارد اصلاحی را وارد کنید:\n\n"
            "(این پیام به مشتری ارسال خواهد شد)\n\n"
            "حداقل ۱۰ کاراکتر بنویسید."
        )
        await query.message.edit_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
        return AWAITING_VALIDATION_REJECT_COMMENT
    
    return VALIDATION_REVIEW


async def handle_validation_reject_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle validation reject comment input."""
    comment = update.message.text.strip()
    order_id = context.user_data.get('rejecting_validation_id')
    
    bc = get_breadcrumb(context)
    
    if not order_id:
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        msg = bc.format_message("❌ خطا: سفارش پیدا نشد.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    if len(comment) < 10:
        msg = bc.format_message("⚠️ لطفاً توضیحات کامل‌تری وارد کنید (حداقل ۱۰ کاراکتر):")
        await update.message.reply_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
        return AWAITING_VALIDATION_REJECT_COMMENT
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        msg = bc.format_message("❌ خطا در دریافت اطلاعات کاربر.")
        await update.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
        return ADMIN_MENU
    
    result = await api_client.reject_validation(order_id, user['id'], comment)
    
    if result:
        # Notify customer
        current_validation = context.user_data.get('current_validation', {})
        customer_telegram_id = current_validation.get('customer_telegram_id')
        if customer_telegram_id:
            await notify_customer_validation_rejected(
                update.get_bot(),
                customer_telegram_id,
                order_id,
                comment,
            )
        
        bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
        msg = bc.format_message("✅ اعتبارسنجی رد شد و پیام اصلاحیه برای مشتری ارسال شد.")
        
        # Get updated list
        refresh_result = await api_client.get_pending_validations(admin_id=user['id'], status='PENDING')
        validations = refresh_result.get('items', []) if refresh_result else []
        context.user_data['pending_validations'] = validations
        
        await update.message.reply_text(msg, reply_markup=get_pending_validations_keyboard(validations))
        return VALIDATIONS_LIST
    else:
        msg = bc.format_message("❌ خطا در ثبت رد اعتبارسنجی. لطفاً دوباره تلاش کنید.")
        await update.message.reply_text(msg, reply_markup=get_validation_reject_keyboard(order_id))
        return AWAITING_VALIDATION_REJECT_COMMENT


async def handle_validation_reject_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during validation rejection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    bc = get_breadcrumb(context)
    
    if data.startswith("review_validation_"):
        order_id = data[18:]
        
        # Find validation from cached list
        validations = context.user_data.get('pending_validations', [])
        validation = next((v for v in validations if v['id'] == order_id), None)
        
        if validation:
            context.user_data['current_validation'] = validation
            bc.set_path(BreadcrumbPath.VALIDATION_REVIEW)
            
            # Format validation details
            user_name = validation.get('user_name', 'ناشناس')
            category = validation.get('category_name', '-')
            plan = validation.get('plan_name', '-')
            total_price = validation.get('total_price', 0)
            
            detail_text = (
                f"📋 بررسی اعتبارسنجی\n\n"
                f"🆔 شماره سفارش: #{order_id[:8]}\n"
                f"👤 مشتری: {user_name}\n"
                f"📁 دسته‌بندی: {category}\n"
                f"📝 پلن: {plan}\n"
                f"💰 قیمت کل: {int(total_price):,} تومان\n"
            )
            msg = bc.format_message(detail_text)
            
            await query.message.edit_text(msg, reply_markup=get_validation_review_keyboard(order_id))
            return VALIDATION_REVIEW
    
    # Fallback to validations list
    validations = context.user_data.get('pending_validations', [])
    bc.set_path(BreadcrumbPath.VALIDATIONS_PENDING)
    msg = bc.format_message("✅ اعتبارسنجی‌های در انتظار:")
    await query.message.edit_text(msg, reply_markup=get_pending_validations_keyboard(validations))
    return VALIDATIONS_LIST


# Create conversation handler
admin_payments_conversation = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^(🔧 پنل مدیریت|پنل مدیریت|مدیریت)$"), show_admin_menu),
    ],
    states={
        ADMIN_MENU: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_menu),
        ],
        PENDING_LIST: [
            CallbackQueryHandler(handle_pending_list_callback),
        ],
        PAYMENT_REVIEW: [
            CallbackQueryHandler(handle_payment_review_callback),
        ],
        AWAITING_REJECT_REASON: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reject_reason),
            CallbackQueryHandler(handle_reject_cancel),
        ],
        ADMIN_MANAGEMENT: [
            CallbackQueryHandler(handle_admin_management_callback),
        ],
        ADMIN_INFO: [
            CallbackQueryHandler(handle_admin_info_callback),
        ],
        AWAITING_NEW_ADMIN_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_admin_id),
            CallbackQueryHandler(handle_add_admin_cancel),
        ],
        # Validation states
        VALIDATIONS_LIST: [
            CallbackQueryHandler(handle_validations_list_callback),
        ],
        VALIDATION_REVIEW: [
            CallbackQueryHandler(handle_validation_review_callback),
        ],
        AWAITING_VALIDATION_REJECT_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_validation_reject_comment),
            CallbackQueryHandler(handle_validation_reject_cancel),
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), lambda u, c: ConversationHandler.END),
    ],
)
