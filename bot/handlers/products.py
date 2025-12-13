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
from keyboards.products import (
    get_product_type_keyboard,
    get_products_inline_keyboard,
    get_design_plan_keyboard,
    get_validation_keyboard,
    get_quantity_keyboard,
    get_confirm_order_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_TYPE, SELECTING_PRODUCT, SELECTING_PLAN, SELECTING_VALIDATION, SELECTING_QUANTITY, CONFIRMING = range(6)


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
            reply_markup=get_main_menu_keyboard()
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
            reply_markup=get_main_menu_keyboard()
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
            reply_markup=get_main_menu_keyboard()
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
        
        if result:
            await query.message.edit_text(
                f"✅ سفارش شما با موفقیت ثبت شد!\n\n"
                f"شماره سفارش: #{result['id'][:8]}\n"
                f"مبلغ کل: {int(result['total_price']):,} تومان\n\n"
                "برای پرداخت و پیگیری سفارش از منوی سفارشات استفاده کنید."
            )
        else:
            await query.message.edit_text(
                "❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید."
            )
        
        await query.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    return CONFIRMING


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
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), lambda u, c: ConversationHandler.END),
    ],
)

