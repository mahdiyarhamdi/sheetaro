"""Print Shop Flow - Print shop menu and order management handlers.

This module handles print-shop-related operations using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item,
    FLOW_PRINT_SHOP, PRINT_SHOP_STEPS,
)
from utils.breadcrumb import get_breadcrumb
from keyboards.manager import get_main_menu_keyboard
from keyboards.printshop import (
    get_printshop_menu_keyboard,
    get_order_queue_keyboard,
    get_queue_order_detail_keyboard,
    get_my_orders_filter_keyboard,
    get_my_orders_keyboard,
    get_my_order_actions_keyboard,
    get_tracking_confirm_keyboard,
    STATUS_LABELS,
)
from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def handle_printshop_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for print shop flow based on current step."""
    handlers = {
        'printshop_menu': handle_printshop_menu_text,
        'printshop_enter_tracking': handle_tracking_code_input,
    }
    handler = handlers.get(step)
    if handler:
        await handler(update, context)
    else:
        logger.warning(f"Unknown printshop step for text: {step}")
        await show_printshop_menu(update, context)


async def show_printshop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show print shop main menu."""
    set_flow(context, FLOW_PRINT_SHOP, 'printshop_menu')
    msg = "🏭 پنل چاپخانه\n\nیکی را انتخاب کنید:"
    await update.message.reply_text(msg, reply_markup=get_printshop_menu_keyboard())


async def handle_printshop_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle print shop menu text selection."""
    text = update.message.text

    if "بازگشت" in text:
        clear_flow(context)
        is_admin = context.user_data.get('is_admin', False)
        is_printshop = context.user_data.get('is_printshop', False)
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard(is_admin)
        )
        return

    if "صف سفارش" in text:
        await show_order_queue(update, context)
        return

    if "سفارش‌های من" in text or "سفارشات من" in text or "سفارش های من" in text:
        await show_my_orders_menu(update, context)
        return

    if "آمار" in text:
        await show_stats(update, context)
        return

    if "تسویه" in text:
        await show_settlements(update, context)
        return

    # Unknown option
    msg = "گزینه نامعتبر. یکی را انتخاب کنید:"
    await update.message.reply_text(msg, reply_markup=get_printshop_menu_keyboard())


# ==================== Order Queue ====================

async def show_order_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show orders ready for printing."""
    set_step(context, 'printshop_order_queue')

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات کاربر.")
        return

    result = await api_client.get_printshop_queue(
        printshop_id=user['id'],
        page=1,
        page_size=20,
    )

    if not result or not result.get('items'):
        await update.message.reply_text(
            "📋 صف سفارش‌ها خالی است.\n\nهیچ سفارشی آماده چاپ نیست.",
            reply_markup=get_printshop_menu_keyboard(),
        )
        set_step(context, 'printshop_menu')
        return

    orders = result['items']
    update_flow_data(context, 'queue_orders', orders)

    msg = f"📋 سفارش‌های آماده چاپ ({result['total']} مورد):\n\nبرای مشاهده جزئیات روی هر مورد کلیک کنید:"
    await update.message.reply_text(msg, reply_markup=get_order_queue_keyboard(orders))


async def show_queue_order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """Show detail of a queue order."""
    set_step(context, 'printshop_order_detail')

    orders = get_flow_data_item(context, 'queue_orders') or []
    order = next((o for o in orders if o['id'] == order_id), None)

    if not order:
        await update.callback_query.answer("❌ سفارش پیدا نشد", show_alert=True)
        return

    update_flow_data(context, 'current_queue_order', order)

    customer = order.get('customer_name', 'ناشناس')
    city = order.get('customer_city', '-')
    phone = order.get('customer_phone', '-')
    quantity = order.get('quantity', 0)
    total_price = int(float(order.get('total_price', 0)))
    created = order.get('created_at', '')[:10]

    msg = (
        f"📋 جزئیات سفارش\n\n"
        f"🆔 شماره: #{order_id[:8]}\n"
        f"👤 مشتری: {customer}\n"
        f"📱 تلفن: {phone}\n"
        f"🏙 شهر: {city}\n"
        f"📦 تعداد: {quantity}\n"
        f"💰 مبلغ کل: {total_price:,} تومان\n"
        f"📅 تاریخ ثبت: {created}\n"
    )

    await update.callback_query.edit_message_text(
        msg,
        reply_markup=get_queue_order_detail_keyboard(order_id),
    )


# ==================== My Orders ====================

async def show_my_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show my orders filter menu."""
    set_step(context, 'printshop_my_orders')
    msg = "📦 سفارش‌های من\n\nفیلتر مورد نظر را انتخاب کنید:"
    await update.message.reply_text(msg, reply_markup=get_my_orders_filter_keyboard())


async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE, status_filter: str = None) -> None:
    """Show assigned orders with optional filter."""
    set_step(context, 'printshop_my_orders')

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.callback_query.answer("❌ خطا", show_alert=True)
        return

    result = await api_client.get_printshop_my_orders(
        printshop_id=user['id'],
        status=status_filter,
        page=1,
        page_size=20,
    )

    if not result or not result.get('items'):
        filter_label = STATUS_LABELS.get(status_filter, "همه") if status_filter else "همه"
        msg = f"📦 سفارش‌های من ({filter_label})\n\nسفارشی یافت نشد."
        await update.callback_query.edit_message_text(
            msg,
            reply_markup=get_my_orders_filter_keyboard(),
        )
        return

    orders = result['items']
    update_flow_data(context, 'my_orders', orders)

    msg = f"📦 سفارش‌های من ({result['total']} مورد):"
    await update.callback_query.edit_message_text(
        msg,
        reply_markup=get_my_orders_keyboard(orders),
    )


async def show_my_order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """Show detail of an assigned order."""
    set_step(context, 'printshop_my_order_detail')

    orders = get_flow_data_item(context, 'my_orders') or []
    order = next((o for o in orders if o['id'] == order_id), None)

    if not order:
        # Try to fetch from API
        user = await api_client.get_user(update.effective_user.id)
        if user:
            order = await api_client.get_printshop_order_detail(user['id'], order_id)

    if not order:
        await update.callback_query.answer("❌ سفارش پیدا نشد", show_alert=True)
        return

    update_flow_data(context, 'current_my_order', order)

    customer = order.get('customer_name', 'ناشناس')
    city = order.get('customer_city', '-')
    phone = order.get('customer_phone', '-')
    address = order.get('customer_address') or order.get('shipping_address', '-')
    quantity = order.get('quantity', 0)
    total_price = int(float(order.get('total_price', 0)))
    status = order.get('status', '')
    status_label = STATUS_LABELS.get(status, status)
    tracking = order.get('tracking_code', '')

    msg = (
        f"📦 جزئیات سفارش من\n\n"
        f"🆔 شماره: #{order_id[:8]}\n"
        f"📊 وضعیت: {status_label}\n"
        f"👤 مشتری: {customer}\n"
        f"📱 تلفن: {phone}\n"
        f"🏙 شهر: {city}\n"
        f"📍 آدرس: {address}\n"
        f"📦 تعداد: {quantity}\n"
        f"💰 مبلغ کل: {total_price:,} تومان\n"
    )

    if tracking:
        msg += f"🔍 کد رهگیری: {tracking}\n"

    await update.callback_query.edit_message_text(
        msg,
        reply_markup=get_my_order_actions_keyboard(order),
    )


# ==================== Stats ====================

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show print shop statistics."""
    set_step(context, 'printshop_stats')

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات.")
        return

    stats = await api_client.get_printshop_stats(user['id'])
    if not stats:
        await update.message.reply_text(
            "❌ خطا در دریافت آمار.",
            reply_markup=get_printshop_menu_keyboard(),
        )
        return

    sla = stats.get('sla_compliance_percent')
    sla_text = f"{sla}%" if sla is not None else "بدون داده"
    avg_print = stats.get('avg_print_time_hours')
    avg_print_text = f"{avg_print} ساعت" if avg_print is not None else "بدون داده"
    avg_ship = stats.get('avg_ship_time_hours')
    avg_ship_text = f"{avg_ship} ساعت" if avg_ship is not None else "بدون داده"

    msg = (
        "📊 آمار چاپخانه\n\n"
        f"📋 صف انتظار: {stats.get('pending_orders', 0)} سفارش\n"
        f"🖨 در حال چاپ: {stats.get('in_progress_orders', 0)}\n"
        f"✅ چاپ شده: {stats.get('printed_orders', 0)}\n"
        f"📮 ارسال شده: {stats.get('shipped_orders', 0)}\n"
        f"📬 تحویل شده: {stats.get('delivered_orders', 0)}\n"
        f"📦 کل سفارش‌ها: {stats.get('total_orders', 0)}\n\n"
        f"⏱ میانگین زمان چاپ: {avg_print_text}\n"
        f"⏱ میانگین زمان ارسال: {avg_ship_text}\n"
        f"📈 انطباق SLA: {sla_text}\n"
    )

    await update.message.reply_text(msg, reply_markup=get_printshop_menu_keyboard())


# ==================== Settlements ====================

async def show_settlements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settlement/commission info."""
    set_step(context, 'printshop_settlements')

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات.")
        return

    result = await api_client.get_printshop_settlements(user['id'])
    if not result or not result.get('items'):
        await update.message.reply_text(
            "💰 تسویه‌حساب\n\nهنوز تسویه‌حسابی ثبت نشده.",
            reply_markup=get_printshop_menu_keyboard(),
        )
        return

    settlements = result['items']
    msg = f"💰 تسویه‌حساب ({result['total']} دوره):\n\n"

    for s in settlements[:5]:
        status_label = "✅ پرداخت شده" if s['status'] == 'PAID' else "⏳ در انتظار"
        net = int(float(s.get('net_amount', 0)))
        msg += (
            f"📅 {s['period_start']} تا {s['period_end']}\n"
            f"   سفارش‌ها: {s['total_orders']} | خالص: {net:,} تومان | {status_label}\n\n"
        )

    await update.message.reply_text(msg, reply_markup=get_printshop_menu_keyboard())


# ==================== Tracking Code Input ====================

async def handle_tracking_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tracking code text input."""
    tracking_code = update.message.text.strip()
    order_id = get_flow_data_item(context, 'shipping_order_id')

    if not order_id:
        await update.message.reply_text(
            "❌ خطا: سفارشی انتخاب نشده.",
            reply_markup=get_printshop_menu_keyboard(),
        )
        set_step(context, 'printshop_menu')
        return

    if len(tracking_code) < 5:
        await update.message.reply_text(
            "⚠️ کد رهگیری باید حداقل ۵ کاراکتر باشد.\nلطفاً دوباره وارد کنید:"
        )
        return

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات کاربر.")
        return

    result = await api_client.printshop_ship_order(
        printshop_id=user['id'],
        order_id=order_id,
        tracking_code=tracking_code,
    )

    if result:
        await update.message.reply_text(
            f"✅ سفارش #{order_id[:8]} با موفقیت ارسال شد!\n"
            f"کد رهگیری: {tracking_code}",
            reply_markup=get_printshop_menu_keyboard(),
        )
        set_step(context, 'printshop_menu')
    else:
        await update.message.reply_text(
            "❌ خطا در ثبت ارسال. لطفاً دوباره تلاش کنید.",
            reply_markup=get_printshop_menu_keyboard(),
        )
        set_step(context, 'printshop_menu')


# ==================== Callback Handler ====================

async def handle_printshop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle print shop related callbacks. Returns True if handled."""
    query = update.callback_query
    data = query.data

    if not data.startswith("ps_"):
        return False

    await query.answer()

    user = await api_client.get_user(update.effective_user.id)
    if not user:
        await query.edit_message_text("❌ خطا در دریافت اطلاعات کاربر.")
        return True

    # Back to menu
    if data == "ps_back_menu":
        set_step(context, 'printshop_menu')
        await query.edit_message_text("🏭 پنل چاپخانه\n\nاز منوی پایین انتخاب کنید.")
        return True

    # Refresh queue
    if data == "ps_refresh_queue":
        result = await api_client.get_printshop_queue(user['id'])
        if not result or not result.get('items'):
            await query.edit_message_text(
                "📋 صف سفارش‌ها خالی است.",
                reply_markup=get_order_queue_keyboard([]),
            )
        else:
            orders = result['items']
            update_flow_data(context, 'queue_orders', orders)
            await query.edit_message_text(
                f"📋 سفارش‌های آماده چاپ ({result['total']} مورد):",
                reply_markup=get_order_queue_keyboard(orders),
            )
        return True

    # Queue order detail
    if data.startswith("ps_queue_"):
        order_id = data.replace("ps_queue_", "")
        await show_queue_order_detail(update, context, order_id)
        return True

    # Accept order
    if data.startswith("ps_accept_"):
        order_id = data.replace("ps_accept_", "")
        result = await api_client.printshop_accept_order(user['id'], order_id)
        if result:
            await query.edit_message_text(
                f"✅ سفارش #{order_id[:8]} با موفقیت قبول شد!\n\n"
                "سفارش به لیست «سفارش‌های من» اضافه شد."
            )
        else:
            await query.edit_message_text("❌ خطا در قبول سفارش. ممکن است قبلاً توسط چاپخانه دیگری قبول شده باشد.")
        return True

    # My orders filter
    if data.startswith("ps_myorders_"):
        status_filter = data.replace("ps_myorders_", "")
        if status_filter == "all":
            status_filter = None
        await show_my_orders(update, context, status_filter)
        return True

    # My order detail
    if data.startswith("ps_myorder_"):
        order_id = data.replace("ps_myorder_", "")
        await show_my_order_detail(update, context, order_id)
        return True

    # Complete printing
    if data.startswith("ps_complete_"):
        order_id = data.replace("ps_complete_", "")
        result = await api_client.printshop_complete_order(user['id'], order_id)
        if result:
            await query.edit_message_text(
                f"✅ چاپ سفارش #{order_id[:8]} تکمیل شد!\n\n"
                "اکنون می‌توانید سفارش را ارسال کنید."
            )
        else:
            await query.edit_message_text("❌ خطا در ثبت تکمیل چاپ.")
        return True

    # Start shipping (ask for tracking code)
    if data.startswith("ps_ship_"):
        order_id = data.replace("ps_ship_", "")
        set_step(context, 'printshop_enter_tracking')
        update_flow_data(context, 'shipping_order_id', order_id)
        await query.edit_message_text(
            f"📮 ارسال سفارش #{order_id[:8]}\n\n"
            "لطفاً کد رهگیری پستی را وارد کنید:",
            reply_markup=get_tracking_confirm_keyboard(order_id),
        )
        return True

    return False
