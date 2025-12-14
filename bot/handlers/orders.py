"""Order management handlers for the bot."""

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
from utils.notifications import notify_admin_new_receipt
from keyboards.orders import (
    get_orders_menu_keyboard,
    get_orders_list_keyboard,
    get_order_detail_keyboard,
    get_status_text,
    get_cancel_confirm_keyboard,
    get_payment_card_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
ORDERS_MENU, ORDERS_LIST, ORDER_DETAIL, AWAITING_RECEIPT = range(4)


async def show_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show orders menu."""
    await update.message.reply_text(
        "📋 مدیریت سفارشات\n\nیکی را انتخاب کنید:",
        reply_markup=get_orders_menu_keyboard()
    )
    return ORDERS_MENU


async def handle_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle orders menu selection."""
    text = update.message.text
    
    if text == "🔙 بازگشت به منو":
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Get user
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    status_filter = None
    if "در حال انجام" in text:
        # Active orders
        context.user_data['order_filter'] = 'active'
    elif "تحویل شده" in text:
        status_filter = "DELIVERED"
        context.user_data['order_filter'] = 'delivered'
    
    # Get orders
    result = await api_client.get_user_orders(
        user_id=user['id'],
        status=status_filter,
    )
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "سفارشی یافت نشد.",
            reply_markup=get_orders_menu_keyboard()
        )
        return ORDERS_MENU
    
    orders = result['items']
    context.user_data['orders'] = orders
    
    await update.message.reply_text(
        f"📦 سفارشات شما ({result['total']} مورد):",
        reply_markup=get_orders_list_keyboard(orders)
    )
    return ORDERS_LIST


async def handle_orders_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle orders list callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_orders_menu":
        await query.message.reply_text(
            "📋 مدیریت سفارشات\n\nیکی را انتخاب کنید:",
            reply_markup=get_orders_menu_keyboard()
        )
        return ORDERS_MENU
    
    if data.startswith("order_"):
        order_id = data[6:]  # Remove "order_" prefix
        
        # Get user
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.message.edit_text("خطا در دریافت اطلاعات.")
            return ORDERS_LIST
        
        # Get order details
        order = await api_client.get_order(order_id, user['id'])
        
        if not order:
            await query.message.edit_text("سفارش یافت نشد.")
            return ORDERS_LIST
        
        context.user_data['current_order'] = order
        
        # Format order details
        status_text = get_status_text(order.get('status', ''))
        design_plan_names = {
            'PUBLIC': 'طرح آماده',
            'SEMI_PRIVATE': 'نیمه‌خصوصی',
            'PRIVATE': 'خصوصی',
            'OWN_DESIGN': 'طرح شخصی',
        }
        
        detail_text = (
            f"📋 جزئیات سفارش\n\n"
            f"شماره: #{order['id'][:8]}\n"
            f"وضعیت: {status_text}\n"
            f"پلن طراحی: {design_plan_names.get(order.get('design_plan', ''), '-')}\n"
            f"تعداد: {order.get('quantity', 0):,}\n"
            f"مبلغ کل: {int(order.get('total_price', 0)):,} تومان\n"
            f"تاریخ ثبت: {order.get('created_at', '')[:10]}\n"
        )
        
        if order.get('tracking_code'):
            detail_text += f"کد رهگیری: {order['tracking_code']}\n"
        
        await query.message.edit_text(
            detail_text,
            reply_markup=get_order_detail_keyboard(order)
        )
        return ORDER_DETAIL
    
    return ORDERS_LIST


async def handle_order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle order detail callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_orders_list":
        orders = context.user_data.get('orders', [])
        if orders:
            await query.message.edit_text(
                "📦 سفارشات شما:",
                reply_markup=get_orders_list_keyboard(orders)
            )
        return ORDERS_LIST
    
    if data.startswith("cancel_"):
        order_id = data[7:]  # Remove "cancel_" prefix
        await query.message.edit_text(
            "⚠️ آیا مطمئن هستید که می‌خواهید این سفارش را لغو کنید؟\n\n"
            "توجه: هزینه‌های انجام شده قابل استرداد نیستند.",
            reply_markup=get_cancel_confirm_keyboard(order_id)
        )
        return ORDER_DETAIL
    
    if data.startswith("confirm_cancel_"):
        order_id = data[15:]  # Remove "confirm_cancel_" prefix
        
        # Get user
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.message.edit_text("خطا در دریافت اطلاعات.")
            return ORDER_DETAIL
        
        # Cancel order
        result = await api_client.cancel_order(order_id, user['id'])
        
        if result:
            await query.message.edit_text("✅ سفارش با موفقیت لغو شد.")
        else:
            await query.message.edit_text("❌ خطا در لغو سفارش.")
        
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    if data.startswith("pay_"):
        order_id = data[4:]  # Remove "pay_" prefix
        
        # Get user
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.message.edit_text("خطا در دریافت اطلاعات.")
            return ORDER_DETAIL
        
        # Get payment card info
        card_info = await api_client.get_payment_card()
        if not card_info:
            await query.message.edit_text(
                "❌ اطلاعات کارت بانکی تنظیم نشده است.\n"
                "لطفاً با پشتیبانی تماس بگیرید."
            )
            return ORDER_DETAIL
        
        # Initiate payment to create payment record
        result = await api_client.initiate_payment(
            user_id=user['id'],
            order_id=order_id,
            payment_type="PRINT",
            callback_url="https://example.com/callback",  # Not used for card-to-card
        )
        
        if result:
            # Store payment info for receipt upload
            context.user_data['pending_payment_id'] = result.get('payment_id')
            context.user_data['pending_payment_amount'] = result.get('amount')
            
            # Format card number for display
            card_number = card_info.get('card_number', '')
            formatted_card = f"{card_number[:4]}-{card_number[4:8]}-{card_number[8:12]}-{card_number[12:]}"
            
            await query.message.edit_text(
                f"💳 پرداخت کارت به کارت\n\n"
                f"مبلغ: {int(result.get('amount', 0)):,} تومان\n\n"
                f"شماره کارت:\n`{formatted_card}`\n\n"
                f"به نام: {card_info.get('card_holder', '-')}\n\n"
                f"⚠️ پس از واریز، عکس رسید را ارسال کنید.",
                parse_mode='Markdown',
                reply_markup=get_payment_card_keyboard()
            )
            return AWAITING_RECEIPT
        else:
            await query.message.edit_text("❌ خطا در ایجاد درخواست پرداخت.")
        
        return ORDER_DETAIL
    
    if data.startswith("track_"):
        order_id = data[6:]  # Remove "track_" prefix
        order = context.user_data.get('current_order', {})
        tracking_code = order.get('tracking_code', '')
        
        if tracking_code:
            await query.message.edit_text(
                f"📍 کد رهگیری پستی: {tracking_code}\n\n"
                f"برای پیگیری به سایت پست مراجعه کنید:\n"
                f"https://tracking.post.ir/?id={tracking_code}"
            )
        else:
            await query.message.edit_text("کد رهگیری موجود نیست.")
        
        return ORDER_DETAIL
    
    return ORDER_DETAIL


async def handle_receipt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle receipt image upload from user."""
    payment_id = context.user_data.get('pending_payment_id')
    
    if not payment_id:
        await update.message.reply_text(
            "❌ خطا: اطلاعات پرداخت یافت نشد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Get user
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "❌ خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Get photo
    photo = update.message.photo[-1] if update.message.photo else None
    
    if not photo:
        await update.message.reply_text(
            "⚠️ لطفاً عکس رسید را ارسال کنید."
        )
        return AWAITING_RECEIPT
    
    # Get file info and construct URL
    file = await photo.get_file()
    receipt_image_url = file.file_path  # Telegram file URL
    
    # Upload receipt
    result = await api_client.upload_receipt(
        payment_id=payment_id,
        user_id=user['id'],
        receipt_image_url=receipt_image_url,
    )
    
    if result:
        # Get payment amount for notification
        payment_amount = context.user_data.get('pending_payment_amount', 0)
        
        # Clear pending payment data
        context.user_data.pop('pending_payment_id', None)
        context.user_data.pop('pending_payment_amount', None)
        
        await update.message.reply_text(
            "✅ رسید شما با موفقیت ثبت شد.\n\n"
            "⏳ در انتظار تأیید مدیر هستید.\n"
            "پس از بررسی رسید، نتیجه به شما اطلاع داده می‌شود.",
            reply_markup=get_main_menu_keyboard()
        )
        
        # Notify admin about new receipt
        customer_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        await notify_admin_new_receipt(
            bot=context.bot,
            payment_id=payment_id,
            amount=int(payment_amount),
            customer_name=customer_name,
            customer_telegram_id=update.effective_user.id,
        )
        
        logger.info(f"New receipt uploaded for payment {payment_id} by user {user['id']}")
        
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ خطا در ثبت رسید. لطفاً دوباره تلاش کنید."
        )
        return AWAITING_RECEIPT


async def handle_receipt_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel during receipt upload."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_payment":
        context.user_data.pop('pending_payment_id', None)
        context.user_data.pop('pending_payment_amount', None)
        
        await query.message.edit_text("پرداخت لغو شد.")
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    return AWAITING_RECEIPT


# Create conversation handler
orders_conversation = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^(📦 سفارشات من|سفارشات)$"), show_orders_menu),
    ],
    states={
        ORDERS_MENU: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_orders_menu),
        ],
        ORDERS_LIST: [
            CallbackQueryHandler(handle_orders_list_callback),
        ],
        ORDER_DETAIL: [
            CallbackQueryHandler(handle_order_detail_callback),
        ],
        AWAITING_RECEIPT: [
            MessageHandler(filters.PHOTO, handle_receipt_upload),
            CallbackQueryHandler(handle_receipt_cancel),
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), lambda u, c: ConversationHandler.END),
    ],
)

