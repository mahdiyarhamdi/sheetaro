"""Print shop keyboards for Telegram bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


STATUS_LABELS = {
    "PRINTING": "در حال چاپ",
    "PRINTED": "چاپ شده",
    "SHIPPED": "ارسال شده",
    "DELIVERED": "تحویل شده",
}


def get_printshop_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get the print shop main menu keyboard."""
    keyboard = [
        ["📋 صف سفارش‌ها"],
        ["📦 سفارش‌های من"],
        ["📊 آمار من", "💰 تسویه‌حساب"],
        ["🔙 بازگشت به منو"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_order_queue_keyboard(orders: list) -> InlineKeyboardMarkup:
    """Get inline keyboard for print shop order queue."""
    keyboard = []
    for order in orders:
        order_id = str(order.get("id", ""))[:8]
        quantity = order.get("quantity", 0)
        city = order.get("customer_city", "")
        label = f"#{order_id} - {quantity} عدد"
        if city:
            label += f" - {city}"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"ps_queue_{order['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔄 بروزرسانی", callback_data="ps_refresh_queue")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ps_back_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_queue_order_detail_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for order detail in queue (accept/back)."""
    keyboard = [
        [InlineKeyboardButton("✅ قبول سفارش", callback_data=f"ps_accept_{order_id}")],
        [InlineKeyboardButton("🔙 بازگشت به صف", callback_data="ps_refresh_queue")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_my_orders_filter_keyboard() -> InlineKeyboardMarkup:
    """Get filter keyboard for my orders."""
    keyboard = [
        [
            InlineKeyboardButton("همه", callback_data="ps_myorders_all"),
            InlineKeyboardButton("در حال چاپ", callback_data="ps_myorders_PRINTING"),
        ],
        [
            InlineKeyboardButton("چاپ شده", callback_data="ps_myorders_PRINTED"),
            InlineKeyboardButton("ارسال شده", callback_data="ps_myorders_SHIPPED"),
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="ps_back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_my_orders_keyboard(orders: list) -> InlineKeyboardMarkup:
    """Get inline keyboard for print shop's own orders."""
    keyboard = []
    for order in orders:
        order_id = str(order.get("id", ""))[:8]
        status = order.get("status", "")
        status_label = STATUS_LABELS.get(status, status)
        label = f"#{order_id} - {status_label}"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"ps_myorder_{order['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔄 بروزرسانی", callback_data="ps_myorders_all")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ps_back_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_my_order_actions_keyboard(order: dict) -> InlineKeyboardMarkup:
    """Get action keyboard for a specific assigned order."""
    order_id = order.get("id", "")
    status = order.get("status", "")
    keyboard = []

    if status == "PRINTING":
        keyboard.append([
            InlineKeyboardButton("✅ چاپ تکمیل شد", callback_data=f"ps_complete_{order_id}")
        ])
    elif status == "PRINTED":
        keyboard.append([
            InlineKeyboardButton("📮 ارسال سفارش", callback_data=f"ps_ship_{order_id}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="ps_myorders_all")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_tracking_confirm_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for tracking code entry cancellation."""
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data=f"ps_myorder_{order_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)
