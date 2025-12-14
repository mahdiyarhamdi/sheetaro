"""Admin payment management handlers for the bot."""

import logging
from telegram import Update
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
)
from keyboards.admin import (
    get_admin_menu_keyboard,
    get_pending_payments_keyboard,
    get_payment_review_keyboard,
    get_reject_confirm_keyboard,
    get_admin_management_keyboard,
    get_admin_info_keyboard,
    get_confirm_remove_admin_keyboard,
    get_cancel_add_admin_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
(ADMIN_MENU, PENDING_LIST, PAYMENT_REVIEW, AWAITING_REJECT_REASON,
 ADMIN_MANAGEMENT, ADMIN_INFO, AWAITING_NEW_ADMIN_ID) = range(7)


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
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🔧 پنل مدیریت\n\nیکی را انتخاب کنید:",
        reply_markup=get_admin_menu_keyboard()
    )
    return ADMIN_MENU


async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin menu selection."""
    text = update.message.text
    
    if text == "🔙 بازگشت به منو":
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    if "پرداخت‌های در انتظار" in text:
        return await show_pending_payments(update, context)
    
    if "تنظیمات کارت" in text:
        # This will be handled by admin_settings handler
        await update.message.reply_text(
            "برای تنظیمات کارت از دستور /settings استفاده کنید.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    if "مدیریت مدیران" in text:
        return await show_admin_management(update, context)
    
    return ADMIN_MENU


async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of payments awaiting approval."""
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "✅ هیچ پرداختی در انتظار تأیید نیست.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    payments = result['items']
    context.user_data['pending_payments'] = payments
    
    await update.message.reply_text(
        f"💳 پرداخت‌های در انتظار تأیید ({result['total']} مورد):\n\n"
        "برای بررسی روی هر مورد کلیک کنید:",
        reply_markup=get_pending_payments_keyboard(payments)
    )
    return PENDING_LIST


async def handle_pending_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pending list callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_admin_menu":
        await query.message.edit_text("بازگشت به منوی مدیریت...")
        await query.message.reply_text(
            "🔧 پنل مدیریت\n\nیکی را انتخاب کنید:",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    if data.startswith("review_payment_"):
        payment_id = data[15:]  # Remove "review_payment_" prefix
        
        # Get payment details
        payment = await api_client.get_payment(payment_id)
        
        if not payment:
            await query.message.edit_text("پرداخت یافت نشد.")
            return PENDING_LIST
        
        context.user_data['current_payment'] = payment
        
        # Format payment details
        detail_text = (
            f"💳 بررسی پرداخت\n\n"
            f"شماره: #{payment['id'][:8]}\n"
            f"مبلغ: {int(payment.get('amount', 0)):,} تومان\n"
            f"نوع: {get_payment_type_text(payment.get('type', ''))}\n"
            f"تاریخ: {payment.get('created_at', '')[:10]}\n"
        )
        
        # Show receipt image if available
        if payment.get('receipt_image_url'):
            detail_text += f"\n📷 رسید: {payment['receipt_image_url']}\n"
            # Try to send the receipt image
            try:
                await query.message.reply_photo(
                    photo=payment['receipt_image_url'],
                    caption="عکس رسید پرداخت"
                )
            except Exception as e:
                logger.error(f"Error sending receipt image: {e}")
                detail_text += "(خطا در نمایش تصویر)\n"
        
        await query.message.edit_text(
            detail_text,
            reply_markup=get_payment_review_keyboard(payment_id)
        )
        return PAYMENT_REVIEW
    
    return PENDING_LIST


async def handle_payment_review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment review callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_pending_list":
        payments = context.user_data.get('pending_payments', [])
        if payments:
            await query.message.edit_text(
                "💳 پرداخت‌های در انتظار تأیید:",
                reply_markup=get_pending_payments_keyboard(payments)
            )
        return PENDING_LIST
    
    if data.startswith("approve_"):
        payment_id = data[8:]  # Remove "approve_" prefix
        
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.message.edit_text("خطا در دریافت اطلاعات.")
            return PAYMENT_REVIEW
        
        # Get current payment info for notification
        current_payment = context.user_data.get('current_payment', {})
        
        result = await api_client.approve_payment(
            payment_id=payment_id,
            admin_id=user['id'],
        )
        
        if result:
            await query.message.edit_text(
                "✅ پرداخت با موفقیت تأیید شد.\n\n"
                "به کاربر اطلاع داده می‌شود."
            )
            
            # Notify customer
            customer_telegram_id = current_payment.get('customer_telegram_id')
            if customer_telegram_id:
                await notify_customer_payment_approved(
                    bot=context.bot,
                    customer_telegram_id=customer_telegram_id,
                    payment_id=payment_id,
                    amount=int(result.get('amount', 0)),
                )
            
            # Refresh pending list
            return await refresh_pending_list(query, context)
        else:
            await query.message.edit_text("❌ خطا در تأیید پرداخت.")
            return PAYMENT_REVIEW
    
    if data.startswith("reject_"):
        payment_id = data[7:]  # Remove "reject_" prefix
        context.user_data['rejecting_payment_id'] = payment_id
        
        await query.message.edit_text(
            "❌ رد کردن پرداخت\n\n"
            "لطفاً علت رد کردن را بنویسید:",
            reply_markup=get_reject_confirm_keyboard(payment_id)
        )
        return AWAITING_REJECT_REASON
    
    return PAYMENT_REVIEW


async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle rejection reason from admin."""
    reason = update.message.text
    payment_id = context.user_data.get('rejecting_payment_id')
    
    if not payment_id:
        await update.message.reply_text(
            "خطا: اطلاعات پرداخت یافت نشد.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_admin_menu_keyboard()
        )
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
        
        await update.message.reply_text(
            f"❌ پرداخت رد شد.\n\n"
            f"علت: {reason}\n\n"
            "به کاربر اطلاع داده می‌شود.",
            reply_markup=get_admin_menu_keyboard()
        )
        
        # Notify customer
        customer_telegram_id = current_payment.get('customer_telegram_id')
        if customer_telegram_id:
            await notify_customer_payment_rejected(
                bot=context.bot,
                customer_telegram_id=customer_telegram_id,
                payment_id=payment_id,
                amount=int(result.get('amount', 0)),
                reason=reason,
            )
        
        return ADMIN_MENU
    else:
        await update.message.reply_text(
            "❌ خطا در رد کردن پرداخت.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU


async def handle_reject_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during reject reason input."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("review_payment_"):
        payment_id = query.data[15:]
        context.user_data.pop('rejecting_payment_id', None)
        
        # Return to payment review
        payment = context.user_data.get('current_payment')
        if payment:
            detail_text = (
                f"💳 بررسی پرداخت\n\n"
                f"شماره: #{payment['id'][:8]}\n"
                f"مبلغ: {int(payment.get('amount', 0)):,} تومان\n"
            )
            await query.message.edit_text(
                detail_text,
                reply_markup=get_payment_review_keyboard(payment_id)
            )
        return PAYMENT_REVIEW
    
    return AWAITING_REJECT_REASON


async def refresh_pending_list(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the pending payments list."""
    user = await api_client.get_user(query.from_user.id)
    if not user:
        return ADMIN_MENU
    
    result = await api_client.get_pending_approval_payments(
        admin_id=user['id'],
        page=1,
        page_size=20,
    )
    
    if not result or not result.get('items'):
        await query.message.reply_text(
            "✅ هیچ پرداختی در انتظار تأیید نیست.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    payments = result['items']
    context.user_data['pending_payments'] = payments
    
    await query.message.reply_text(
        f"💳 پرداخت‌های در انتظار تأیید ({result['total']} مورد):",
        reply_markup=get_pending_payments_keyboard(payments)
    )
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
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    result = await api_client.get_all_admins(admin_id=user['id'])
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "❌ خطا در دریافت لیست مدیران.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    admins = result['items']
    context.user_data['admins'] = admins
    
    await update.message.reply_text(
        f"👥 مدیریت مدیران ({result['total']} نفر)\n\n"
        "برای مشاهده جزئیات روی هر مدیر کلیک کنید:",
        reply_markup=get_admin_management_keyboard(admins)
    )
    return ADMIN_MANAGEMENT


async def handle_admin_management_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin management callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_admin_menu":
        await query.message.edit_text("بازگشت به منوی مدیریت...")
        await query.message.reply_text(
            "🔧 پنل مدیریت\n\nیکی را انتخاب کنید:",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    if data == "add_admin":
        await query.message.edit_text(
            "➕ افزودن مدیر جدید\n\n"
            "شناسه تلگرام (Telegram ID) کاربر جدید را وارد کنید:\n\n"
            "💡 نکته: کاربر باید قبلاً از ربات استفاده کرده باشد.",
            reply_markup=get_cancel_add_admin_keyboard()
        )
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
    
    if not admin_info:
        await query.message.edit_text("مدیر یافت نشد.")
        return ADMIN_MANAGEMENT
    
    context.user_data['selected_admin'] = admin_info
    
    admin_name = f"{admin_info.get('first_name', '')} {admin_info.get('last_name', '')}".strip()
    username = admin_info.get('username', '-')
    created_at = admin_info.get('created_at', '')[:10]
    
    is_self = telegram_id == query.from_user.id
    
    detail_text = (
        f"👤 اطلاعات مدیر\n\n"
        f"نام: {admin_name}\n"
        f"نام کاربری: @{username}\n"
        f"شناسه تلگرام: {telegram_id}\n"
        f"تاریخ عضویت: {created_at}\n"
    )
    
    if is_self:
        detail_text += "\n⚠️ این اکانت خودتان است."
    
    await query.message.edit_text(
        detail_text,
        reply_markup=get_admin_info_keyboard(telegram_id, is_self)
    )
    return ADMIN_INFO


async def handle_admin_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin info callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_admin_list":
        return await refresh_admin_list(query, context)
    
    if data.startswith("remove_admin_"):
        telegram_id = int(data[13:])  # Remove "remove_admin_" prefix
        admin_info = context.user_data.get('selected_admin', {})
        admin_name = f"{admin_info.get('first_name', '')} {admin_info.get('last_name', '')}".strip()
        
        await query.message.edit_text(
            f"⚠️ آیا مطمئن هستید که می‌خواهید {admin_name} را از مدیران حذف کنید؟",
            reply_markup=get_confirm_remove_admin_keyboard(telegram_id)
        )
        return ADMIN_INFO
    
    if data.startswith("confirm_remove_admin_"):
        telegram_id = int(data[21:])  # Remove "confirm_remove_admin_" prefix
        
        user = await api_client.get_user(query.from_user.id)
        if not user:
            await query.message.edit_text("خطا در دریافت اطلاعات.")
            return ADMIN_INFO
        
        result = await api_client.demote_from_admin(
            target_telegram_id=telegram_id,
            admin_id=user['id'],
        )
        
        if result:
            await query.message.edit_text("✅ مدیر با موفقیت حذف شد.")
            return await refresh_admin_list(query, context)
        else:
            await query.message.edit_text("❌ خطا در حذف مدیر.")
            return ADMIN_INFO
    
    if data.startswith("admin_info_"):
        telegram_id = int(data[11:])
        return await show_admin_info(query, context, telegram_id)
    
    return ADMIN_INFO


async def handle_new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new admin telegram ID input."""
    text = update.message.text.strip()
    
    # Validate telegram ID
    try:
        new_admin_telegram_id = int(text)
    except ValueError:
        await update.message.reply_text(
            "❌ شناسه نامعتبر است.\n"
            "لطفاً یک عدد وارد کنید:",
            reply_markup=get_cancel_add_admin_keyboard()
        )
        return AWAITING_NEW_ADMIN_ID
    
    # Get current user (admin)
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    
    # Check if user exists
    target_user = await api_client.get_user(new_admin_telegram_id)
    if not target_user:
        await update.message.reply_text(
            "❌ کاربری با این شناسه یافت نشد.\n"
            "کاربر باید قبلاً از ربات استفاده کرده باشد.\n\n"
            "شناسه دیگری وارد کنید:",
            reply_markup=get_cancel_add_admin_keyboard()
        )
        return AWAITING_NEW_ADMIN_ID
    
    # Promote to admin
    result = await api_client.promote_to_admin(
        target_telegram_id=new_admin_telegram_id,
        admin_id=user['id'],
    )
    
    if result:
        target_name = f"{target_user.get('first_name', '')} {target_user.get('last_name', '')}".strip()
        await update.message.reply_text(
            f"✅ {target_name} به مدیران اضافه شد.",
            reply_markup=get_admin_menu_keyboard()
        )
        return ADMIN_MENU
    else:
        await update.message.reply_text(
            "❌ خطا در افزودن مدیر.\n"
            "ممکن است کاربر از قبل مدیر باشد.",
            reply_markup=get_admin_menu_keyboard()
        )
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
    if not user:
        return ADMIN_MENU
    
    result = await api_client.get_all_admins(admin_id=user['id'])
    
    if not result or not result.get('items'):
        await query.message.edit_text(
            "❌ خطا در دریافت لیست مدیران."
        )
        return ADMIN_MENU
    
    admins = result['items']
    context.user_data['admins'] = admins
    
    await query.message.edit_text(
        f"👥 مدیریت مدیران ({result['total']} نفر)\n\n"
        "برای مشاهده جزئیات روی هر مدیر کلیک کنید:",
        reply_markup=get_admin_management_keyboard(admins)
    )
    return ADMIN_MANAGEMENT


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
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), lambda u, c: ConversationHandler.END),
    ],
)

