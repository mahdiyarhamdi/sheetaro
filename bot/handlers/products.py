"""Product handlers for the bot."""

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
from utils.helpers import get_user_menu_keyboard
from keyboards.products import (
    get_product_type_keyboard,
    get_products_inline_keyboard,
    get_design_plan_keyboard,
    get_validation_keyboard,
    get_quantity_keyboard,
    get_confirm_order_keyboard,
)
from keyboards.orders import get_payment_card_keyboard

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_TYPE, SELECTING_PRODUCT, SELECTING_PLAN, SELECTING_VALIDATION, SELECTING_QUANTITY, CONFIRMING, AWAITING_RECEIPT = range(7)


async def show_product_types(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show product type selection."""
    await update.message.reply_text(
        "نوع محصول را انتخاب کنید:",
        reply_markup=get_product_type_keyboard()
    )
    return SELECTING_TYPE


async def handle_product_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle product type selection."""
    text = update.message.text
    
    if text == "🔙 بازگشت به منو":
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    product_type = None
    if "لیبل" in text:
        product_type = "LABEL"
        context.user_data['product_type'] = "LABEL"
    elif "فاکتور" in text:
        product_type = "INVOICE"
        context.user_data['product_type'] = "INVOICE"
    else:
        await update.message.reply_text("لطفاً یک گزینه معتبر انتخاب کنید.")
        return SELECTING_TYPE
    
    # Get products from API
    result = await api_client.get_products(product_type=product_type)
    
    if not result or not result.get('items'):
        await update.message.reply_text(
            "متأسفانه در حال حاضر محصولی موجود نیست.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    products = result['items']
    context.user_data['products'] = products
    
    await update.message.reply_text(
        f"📦 محصولات {'لیبل' if product_type == 'LABEL' else 'فاکتور'}:\n\nیکی را انتخاب کنید:",
        reply_markup=get_products_inline_keyboard(products)
    )
    return SELECTING_PRODUCT


async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle product selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_types":
        await query.message.reply_text(
            "نوع محصول را انتخاب کنید:",
            reply_markup=get_product_type_keyboard()
        )
        return SELECTING_TYPE
    
    if data.startswith("product_"):
        product_id = data[8:]  # Remove "product_" prefix
        context.user_data['selected_product_id'] = product_id
        
        # Find product details
        products = context.user_data.get('products', [])
        selected_product = next((p for p in products if p['id'] == product_id), None)
        
        if selected_product:
            context.user_data['selected_product'] = selected_product
            name = selected_product.get('name_fa') or selected_product.get('name')
            
            await query.message.edit_text(
                f"محصول انتخاب شده: {name}\n\n"
                "نوع طراحی را انتخاب کنید:",
                reply_markup=get_design_plan_keyboard()
            )
            return SELECTING_PLAN
    
    return SELECTING_PRODUCT


async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle design plan selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_products":
        products = context.user_data.get('products', [])
        await query.message.edit_text(
            "محصول را انتخاب کنید:",
            reply_markup=get_products_inline_keyboard(products)
        )
        return SELECTING_PRODUCT
    
    if data.startswith("plan_"):
        plan = data[5:]  # Remove "plan_" prefix
        context.user_data['design_plan'] = plan
        
        # For OWN_DESIGN, we would need to handle file upload
        # For now, show validation option
        plan_names = {
            'PUBLIC': 'طرح آماده',
            'SEMI_PRIVATE': 'نیمه‌خصوصی',
            'PRIVATE': 'خصوصی',
            'OWN_DESIGN': 'طرح شخصی',
        }
        
        await query.message.edit_text(
            f"پلن انتخاب شده: {plan_names.get(plan, plan)}\n\n"
            "آیا می‌خواهید طرح/فایل اعتبارسنجی شود؟\n"
            "(هزینه اعتبارسنجی: 50,000 تومان)",
            reply_markup=get_validation_keyboard()
        )
        return SELECTING_VALIDATION
    
    return SELECTING_PLAN


async def handle_validation_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle validation selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_plan":
        await query.message.edit_text(
            "نوع طراحی را انتخاب کنید:",
            reply_markup=get_design_plan_keyboard()
        )
        return SELECTING_PLAN
    
    if data in ["validation_yes", "validation_no"]:
        context.user_data['validation_requested'] = (data == "validation_yes")
        
        await query.message.edit_text(
            "تعداد/تیراژ را انتخاب کنید:",
            reply_markup=get_quantity_keyboard()
        )
        return SELECTING_QUANTITY
    
    return SELECTING_VALIDATION


async def handle_quantity_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle quantity selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_validation":
        await query.message.edit_text(
            "آیا می‌خواهید طرح/فایل اعتبارسنجی شود?",
            reply_markup=get_validation_keyboard()
        )
        return SELECTING_VALIDATION
    
    if data.startswith("qty_"):
        quantity = int(data[4:])  # Remove "qty_" prefix
        context.user_data['quantity'] = quantity
        
        # Show order summary
        product = context.user_data.get('selected_product', {})
        plan = context.user_data.get('design_plan', '')
        validation = context.user_data.get('validation_requested', False)
        
        product_name = product.get('name_fa') or product.get('name', 'نامشخص')
        base_price = int(product.get('base_price', 0))
        
        # Calculate prices
        design_prices = {
            'PUBLIC': 0,
            'SEMI_PRIVATE': 600000,
            'PRIVATE': 5000000,
            'OWN_DESIGN': 0,
        }
        design_price = design_prices.get(plan, 0)
        validation_price = 50000 if validation else 0
        print_price = base_price * quantity
        total = design_price + validation_price + print_price
        
        plan_names = {
            'PUBLIC': 'طرح آماده',
            'SEMI_PRIVATE': 'نیمه‌خصوصی',
            'PRIVATE': 'خصوصی',
            'OWN_DESIGN': 'طرح شخصی',
        }
        
        summary = (
            f"📋 خلاصه سفارش:\n\n"
            f"محصول: {product_name}\n"
            f"سایز: {product.get('size', '-')}\n"
            f"پلن طراحی: {plan_names.get(plan, plan)}\n"
            f"اعتبارسنجی: {'بله' if validation else 'خیر'}\n"
            f"تعداد: {quantity:,}\n\n"
            f"💰 قیمت‌ها:\n"
            f"طراحی: {design_price:,} تومان\n"
            f"اعتبارسنجی: {validation_price:,} تومان\n"
            f"چاپ: {print_price:,} تومان\n"
            f"───────────────\n"
            f"جمع کل: {total:,} تومان"
        )
        
        context.user_data['total_price'] = total
        
        await query.message.edit_text(
            summary,
            reply_markup=get_confirm_order_keyboard()
        )
        return CONFIRMING
    
    return SELECTING_QUANTITY


async def handle_order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle order confirmation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "cancel_order":
        await query.message.edit_text("سفارش لغو شد.")
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    if data == "confirm_order":
        # Get user info
        user = await api_client.get_user(update.effective_user.id)
        if not user:
            await query.message.edit_text(
                "خطا در دریافت اطلاعات کاربر. لطفاً دوباره تلاش کنید."
            )
            return ConversationHandler.END
        
        # Create order
        order_data = {
            "product_id": context.user_data.get('selected_product_id'),
            "design_plan": context.user_data.get('design_plan'),
            "quantity": context.user_data.get('quantity'),
            "validation_requested": context.user_data.get('validation_requested', False),
        }
        
        result = await api_client.create_order(user['id'], order_data)
        
        if not result:
            await query.message.edit_text(
                "❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید."
            )
            await query.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=get_user_menu_keyboard(context)
            )
            return ConversationHandler.END
        
        # Store order info
        context.user_data['current_order_id'] = result['id']
        total_price = int(float(result['total_price']))
        
        # Show success message
        await query.message.edit_text(
            f"✅ سفارش شما با موفقیت ثبت شد!\n\n"
            f"شماره سفارش: #{result['id'][:8]}\n"
            f"مبلغ کل: {total_price:,} تومان\n\n"
            "⏳ در حال آماده‌سازی پرداخت..."
        )
        
        # Get payment card info
        card_info = await api_client.get_payment_card()
        if not card_info:
            await query.message.reply_text(
                "❌ اطلاعات کارت بانکی تنظیم نشده است.\n"
                "لطفاً با پشتیبانی تماس بگیرید.",
                reply_markup=get_user_menu_keyboard(context)
            )
            return ConversationHandler.END
        
        # Initiate payment
        payment_result = await api_client.initiate_payment(
            user_id=user['id'],
            order_id=result['id'],
            payment_type="PRINT",
            callback_url="https://example.com/callback",
        )
        
        if not payment_result:
            await query.message.reply_text(
                "❌ خطا در ایجاد درخواست پرداخت.\n"
                "می‌توانید از منوی سفارشات، پرداخت را انجام دهید.",
                reply_markup=get_user_menu_keyboard(context)
            )
            return ConversationHandler.END
        
        # Store payment info
        context.user_data['pending_payment_id'] = payment_result.get('payment_id')
        context.user_data['pending_payment_amount'] = payment_result.get('amount')
        
        # Get card number (without formatting for easy copy)
        card_number = card_info.get('card_number', '')
        
        await query.message.reply_text(
            f"💳 پرداخت کارت به کارت\n\n"
            f"مبلغ: {int(float(payment_result.get('amount', 0))):,} تومان\n\n"
            f"شماره کارت (برای کپی کلیک کنید):\n`{card_number}`\n\n"
            f"به نام: {card_info.get('card_holder', '-')}\n\n"
            f"⚠️ پس از واریز، عکس رسید را ارسال کنید.",
            parse_mode='Markdown',
            reply_markup=get_payment_card_keyboard()
        )
        return AWAITING_RECEIPT
    
    return CONFIRMING


async def handle_receipt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle receipt image upload from user."""
    payment_id = context.user_data.get('pending_payment_id')
    
    if not payment_id:
        await update.message.reply_text(
            "❌ خطا: اطلاعات پرداخت یافت نشد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    # Get user
    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(
            "❌ خطا در دریافت اطلاعات کاربر.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    # Get photo
    photo = update.message.photo[-1] if update.message.photo else None
    
    if not photo:
        await update.message.reply_text(
            "⚠️ لطفاً عکس رسید را ارسال کنید."
        )
        return AWAITING_RECEIPT
    
    # Get file info and construct full URL
    file = await photo.get_file()
    # file.file_path might already be a full URL or just a path
    if file.file_path.startswith("https://"):
        receipt_image_url = file.file_path
    else:
        bot_token = context.bot.token
        receipt_image_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
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
        context.user_data.pop('current_order_id', None)
        
        await update.message.reply_text(
            "✅ رسید شما با موفقیت ثبت شد.\n\n"
            "⏳ در انتظار تأیید مدیر هستید.\n"
            "پس از بررسی رسید، نتیجه به شما اطلاع داده می‌شود.",
            reply_markup=get_user_menu_keyboard(context)
        )
        
        # Notify admin about new receipt
        customer_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        await notify_admin_new_receipt(
            bot=context.bot,
            payment_id=payment_id,
            amount=int(float(payment_amount)),
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
        context.user_data.pop('current_order_id', None)
        
        await query.message.edit_text(
            "⚠️ پرداخت لغو شد.\n\n"
            "می‌توانید از منوی سفارشات، پرداخت را انجام دهید."
        )
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_user_menu_keyboard(context)
        )
        return ConversationHandler.END
    
    return AWAITING_RECEIPT


# Create conversation handler
product_conversation = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^(🛒 ثبت سفارش|ثبت سفارش)$"), show_product_types),
    ],
    states={
        SELECTING_TYPE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_type),
        ],
        SELECTING_PRODUCT: [
            CallbackQueryHandler(handle_product_selection),
        ],
        SELECTING_PLAN: [
            CallbackQueryHandler(handle_plan_selection),
        ],
        SELECTING_VALIDATION: [
            CallbackQueryHandler(handle_validation_selection),
        ],
        SELECTING_QUANTITY: [
            CallbackQueryHandler(handle_quantity_selection),
        ],
        CONFIRMING: [
            CallbackQueryHandler(handle_order_confirmation),
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

