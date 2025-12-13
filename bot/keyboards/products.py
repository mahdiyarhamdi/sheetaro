"""Product selection keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_product_type_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for selecting product type."""
    keyboard = [
        ["🏷️ لیبل"],
        ["🧾 فاکتور"],
        ["🔙 بازگشت به منو"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_products_inline_keyboard(products: list) -> InlineKeyboardMarkup:
    """Get inline keyboard for product list."""
    keyboard = []
    for product in products:
        name = product.get('name_fa') or product.get('name')
        price = int(product.get('base_price', 0))
        size = product.get('size', '')
        button_text = f"{name} - {size} - {price:,} تومان"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"product_{product['id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_types")])
    
    return InlineKeyboardMarkup(keyboard)


def get_design_plan_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting design plan."""
    keyboard = [
        [InlineKeyboardButton("🎨 طرح آماده (رایگان)", callback_data="plan_PUBLIC")],
        [InlineKeyboardButton("✏️ طراحی نیمه‌خصوصی (600,000 تومان)", callback_data="plan_SEMI_PRIVATE")],
        [InlineKeyboardButton("🖌️ طراحی خصوصی (5,000,000 تومان)", callback_data="plan_PRIVATE")],
        [InlineKeyboardButton("📤 آپلود طرح خودم", callback_data="plan_OWN_DESIGN")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_products")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_validation_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for validation option."""
    keyboard = [
        [InlineKeyboardButton("✅ بله، اعتبارسنجی شود (50,000 تومان)", callback_data="validation_yes")],
        [InlineKeyboardButton("❌ خیر، بدون اعتبارسنجی", callback_data="validation_no")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_plan")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_quantity_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting quantity."""
    keyboard = [
        [
            InlineKeyboardButton("100", callback_data="qty_100"),
            InlineKeyboardButton("250", callback_data="qty_250"),
            InlineKeyboardButton("500", callback_data="qty_500"),
        ],
        [
            InlineKeyboardButton("1000", callback_data="qty_1000"),
            InlineKeyboardButton("2500", callback_data="qty_2500"),
            InlineKeyboardButton("5000", callback_data="qty_5000"),
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_validation")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for order confirmation."""
    keyboard = [
        [InlineKeyboardButton("✅ تأیید و پرداخت", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)

