"""Order management keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_orders_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for orders menu."""
    keyboard = [
        ["📋 سفارشات در حال انجام"],
        ["📦 سفارشات تحویل شده"],
        ["🔙 بازگشت به منو"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_orders_list_keyboard(orders: list) -> InlineKeyboardMarkup:
    """Get inline keyboard for orders list."""
    keyboard = []
    
    for order in orders:
        order_id = order['id'][:8]  # Show first 8 chars of UUID
        status_text = get_status_text(order.get('status', ''))
        date_str = order.get('created_at', '')[:10]  # Just the date
        
        button_text = f"#{order_id} - {status_text} - {date_str}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"order_{order['id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_orders_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_order_detail_keyboard(order: dict) -> InlineKeyboardMarkup:
    """Get keyboard for order detail view."""
    keyboard = []
    status = order.get('status', '')
    
    # Cancel button (only for cancellable orders)
    if status in ['PENDING', 'AWAITING_VALIDATION', 'NEEDS_ACTION', 'DESIGNING', 'READY_FOR_PRINT']:
        keyboard.append([InlineKeyboardButton("❌ لغو سفارش", callback_data=f"cancel_{order['id']}")])
    
    # Tracking info
    if status in ['SHIPPED', 'DELIVERED'] and order.get('tracking_code'):
        keyboard.append([InlineKeyboardButton("📍 رهگیری مرسوله", callback_data=f"track_{order['id']}")])
    
    # Payment button (if payment needed)
    if status == 'PENDING':
        keyboard.append([InlineKeyboardButton("💳 پرداخت", callback_data=f"pay_{order['id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_orders_list")])
    
    return InlineKeyboardMarkup(keyboard)


def get_status_text(status: str) -> str:
    """Get Persian text for order status."""
    status_map = {
        'PENDING': '⏳ در انتظار',
        'AWAITING_VALIDATION': '🔍 اعتبارسنجی',
        'NEEDS_ACTION': '⚠️ نیاز به اقدام',
        'DESIGNING': '🎨 در حال طراحی',
        'READY_FOR_PRINT': '📄 آماده چاپ',
        'PRINTING': '🖨️ در حال چاپ',
        'SHIPPED': '📦 ارسال شده',
        'DELIVERED': '✅ تحویل شده',
        'CANCELLED': '❌ لغو شده',
    }
    return status_map.get(status, status)


def get_cancel_confirm_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for cancel confirmation."""
    keyboard = [
        [InlineKeyboardButton("✅ بله، لغو شود", callback_data=f"confirm_cancel_{order_id}")],
        [InlineKeyboardButton("❌ خیر، برگرد", callback_data=f"order_{order_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)

