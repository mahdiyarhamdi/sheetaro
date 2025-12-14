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

