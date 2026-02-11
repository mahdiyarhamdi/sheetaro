"""Notification utilities for sending messages to users."""

import logging
from typing import Optional, List

from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def get_admin_telegram_ids() -> List[int]:
    """Get admin telegram IDs from database via API."""
    result = await api_client.get_admin_telegram_ids()
    if result:
        return result
    return []


async def notify_admin_new_receipt(
    bot,
    payment_id: str,
    amount: int,
    customer_name: str,
    customer_telegram_id: int,
) -> bool:
    """Notify admin about a new receipt upload."""
    admin_telegram_ids = await get_admin_telegram_ids()
    
    if not admin_telegram_ids:
        logger.warning("No admin telegram IDs found in database for notifications")
        return False
    
    message = (
        "🔔 رسید جدید دریافت شد!\n\n"
        f"شماره پرداخت: #{payment_id[:8]}\n"
        f"مبلغ: {amount:,} تومان\n"
        f"مشتری: {customer_name}\n\n"
        "برای بررسی به بخش «پرداخت‌های در انتظار تأیید» مراجعه کنید."
    )
    
    success = False
    for admin_id in admin_telegram_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
            )
            success = True
            logger.info(f"Notified admin {admin_id} about new receipt {payment_id}")
        except Exception as e:
            logger.error(f"Error notifying admin {admin_id}: {e}")
    
    return success


async def notify_customer_payment_approved(
    bot,
    customer_telegram_id: int,
    payment_id: str,
    amount: int,
) -> bool:
    """Notify customer that their payment was approved."""
    message = (
        "✅ پرداخت شما تأیید شد!\n\n"
        f"شماره پرداخت: #{payment_id[:8]}\n"
        f"مبلغ: {amount:,} تومان\n\n"
        "سفارش شما در حال پردازش است."
    )
    
    try:
        await bot.send_message(
            chat_id=customer_telegram_id,
            text=message,
        )
        logger.info(f"Notified customer {customer_telegram_id} about approved payment {payment_id}")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_customer_payment_rejected(
    bot,
    customer_telegram_id: int,
    payment_id: str,
    amount: int,
    reason: str,
) -> bool:
    """Notify customer that their payment was rejected."""
    message = (
        "❌ رسید پرداخت شما رد شد\n\n"
        f"شماره پرداخت: #{payment_id[:8]}\n"
        f"مبلغ: {amount:,} تومان\n\n"
        f"علت رد: {reason}\n\n"
        "لطفاً رسید صحیح را مجدداً آپلود کنید."
    )
    
    try:
        await bot.send_message(
            chat_id=customer_telegram_id,
            text=message,
        )
        logger.info(f"Notified customer {customer_telegram_id} about rejected payment {payment_id}")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


# ==================== Validation Notifications ====================

async def notify_customer_validation_approved(
    bot,
    customer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify customer that their design validation was approved."""
    message = (
        "✅ اعتبارسنجی طرح شما تأیید شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "طرح شما تأیید شده و سفارش در حال پردازش است."
    )
    
    try:
        await bot.send_message(
            chat_id=customer_telegram_id,
            text=message,
        )
        logger.info(f"Notified customer {customer_telegram_id} about approved validation {order_id}")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_customer_validation_rejected(
    bot,
    customer_telegram_id: int,
    order_id: str,
    comment: str,
) -> bool:
    """Notify customer that their design validation was rejected with correction comments."""
    message = (
        "⚠️ طرح شما نیاز به اصلاح دارد\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        f"📝 موارد اصلاحی:\n{comment}\n\n"
        "لطفاً طرح را اصلاح کرده و مجدداً ارسال کنید."
    )
    
    try:
        await bot.send_message(
            chat_id=customer_telegram_id,
            text=message,
        )
        logger.info(f"Notified customer {customer_telegram_id} about rejected validation {order_id}")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_admin_new_validation(
    bot,
    order_id: str,
    customer_name: str,
    category_name: str,
) -> bool:
    """Notify admin about a new validation request."""
    admin_telegram_ids = await get_admin_telegram_ids()
    
    if not admin_telegram_ids:
        logger.warning("No admin telegram IDs found in database for notifications")
        return False
    
    message = (
        "🔔 درخواست اعتبارسنجی جدید!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"مشتری: {customer_name}\n"
        f"دسته‌بندی: {category_name}\n\n"
        "برای بررسی به بخش «اعتبارسنجی‌های در انتظار» مراجعه کنید."
    )
    
    success = False
    for admin_id in admin_telegram_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
            )
            success = True
            logger.info(f"Notified admin {admin_id} about new validation {order_id}")
        except Exception as e:
            logger.error(f"Error notifying admin {admin_id}: {e}")
    
    return success


# ==================== Print Shop Notifications ====================

async def get_printshop_telegram_ids() -> List[int]:
    """Get print shop telegram IDs from database via API."""
    result = await api_client.get_printshop_telegram_ids()
    if result:
        return result
    return []


async def notify_printshops_new_order(
    bot,
    order_id: str,
    quantity: int,
    customer_city: str,
) -> bool:
    """Notify all active print shops about a new order in queue."""
    printshop_ids = await get_printshop_telegram_ids()

    if not printshop_ids:
        logger.warning("No print shop telegram IDs found for notifications")
        return False

    message = (
        "🔔 سفارش جدید آماده چاپ!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"تعداد: {quantity}\n"
        f"شهر: {customer_city or 'نامشخص'}\n\n"
        "برای مشاهده و قبول سفارش، به «صف سفارش‌ها» مراجعه کنید."
    )

    success = False
    for ps_id in printshop_ids:
        try:
            await bot.send_message(chat_id=ps_id, text=message)
            success = True
            logger.info(f"Notified print shop {ps_id} about new order {order_id}")
        except Exception as e:
            logger.error(f"Error notifying print shop {ps_id}: {e}")

    return success


async def notify_customer_order_printing(
    bot,
    customer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify customer that their order has been accepted by print shop."""
    message = (
        "🖨 سفارش شما در حال چاپ است!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "سفارش شما توسط چاپخانه قبول شده و در حال چاپ است."
    )

    try:
        await bot.send_message(chat_id=customer_telegram_id, text=message)
        logger.info(f"Notified customer {customer_telegram_id} order {order_id} is printing")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_customer_order_printed(
    bot,
    customer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify customer that their order has been printed."""
    message = (
        "✅ چاپ سفارش شما تکمیل شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "سفارش شما با موفقیت چاپ شده و آماده ارسال است."
    )

    try:
        await bot.send_message(chat_id=customer_telegram_id, text=message)
        logger.info(f"Notified customer {customer_telegram_id} order {order_id} is printed")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_customer_order_shipped(
    bot,
    customer_telegram_id: int,
    order_id: str,
    tracking_code: str,
) -> bool:
    """Notify customer that their order has been shipped."""
    message = (
        "📮 سفارش شما ارسال شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"کد رهگیری: {tracking_code}\n\n"
        "می‌توانید با کد رهگیری بالا وضعیت مرسوله را پیگیری کنید."
    )

    try:
        await bot.send_message(chat_id=customer_telegram_id, text=message)
        logger.info(f"Notified customer {customer_telegram_id} order {order_id} shipped")
        return True
    except Exception as e:
        logger.error(f"Error notifying customer {customer_telegram_id}: {e}")
        return False


async def notify_admin_sla_breach(
    bot,
    order_id: str,
    age_minutes: float,
) -> bool:
    """Notify admin about SLA breach (order not accepted in 30 minutes)."""
    admin_telegram_ids = await get_admin_telegram_ids()

    if not admin_telegram_ids:
        return False

    message = (
        "⚠️ هشدار نقض SLA!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"زمان انتظار: {int(age_minutes)} دقیقه\n\n"
        "این سفارش بیش از ۳۰ دقیقه بدون قبول در صف مانده است.\n"
        "لطفاً بررسی و در صورت نیاز به چاپخانه اختصاص دهید."
    )

    success = False
    for admin_id in admin_telegram_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=message)
            success = True
        except Exception as e:
            logger.error(f"Error notifying admin {admin_id} about SLA breach: {e}")

    return success


async def notify_printshop_sla_warning(
    bot,
    order_id: str,
    age_minutes: float,
) -> bool:
    """Warn print shops about order approaching SLA limit."""
    printshop_ids = await get_printshop_telegram_ids()

    if not printshop_ids:
        return False

    message = (
        "⏰ سفارش در انتظار!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"زمان انتظار: {int(age_minutes)} دقیقه\n\n"
        "لطفاً برای قبول سفارش اقدام کنید."
    )

    success = False
    for ps_id in printshop_ids:
        try:
            await bot.send_message(chat_id=ps_id, text=message)
            success = True
        except Exception as e:
            logger.error(f"Error notifying print shop {ps_id} about SLA warning: {e}")

    return success

