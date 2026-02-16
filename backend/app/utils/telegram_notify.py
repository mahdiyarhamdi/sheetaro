"""Lightweight Telegram notification utility for backend-triggered events.

Sends messages via Telegram Bot API using httpx.
Uses V2Ray/Xray SOCKS5 proxy when configured (required for Iran servers).
Falls back silently when TELEGRAM_BOT_TOKEN is not configured.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"
PROXY_STATUS_PATH = Path("/app/proxy_config/status.json")


def _get_proxy_url() -> str | None:
    """Read SOCKS5 proxy URL from shared xray config if enabled."""
    if PROXY_STATUS_PATH.exists():
        try:
            data = json.loads(PROXY_STATUS_PATH.read_text())
            if data.get("enabled"):
                return "socks5://xray:10808"
        except Exception:
            pass
    return None


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send a message to a Telegram chat via Bot API."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.debug("TELEGRAM_BOT_TOKEN not set, skipping notification")
        return False

    url = f"{TELEGRAM_API}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    client_kwargs: dict = dict(timeout=15, verify=False)
    proxy_url = _get_proxy_url()
    if proxy_url:
        client_kwargs["proxy"] = proxy_url

    try:
        async with httpx.AsyncClient(**client_kwargs) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info(f"Telegram notification sent to {chat_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to send Telegram notification to {chat_id}: {e}")
        return False


async def notify_telegram_ids(telegram_ids: list[int], text: str) -> bool:
    """Send a message to multiple Telegram users."""
    if not telegram_ids:
        return False

    success = False
    for tid in telegram_ids:
        if await send_telegram_message(tid, text):
            success = True
    return success


async def notify_admins_new_receipt(
    admin_telegram_ids: list[int],
    payment_id: str,
    amount: int,
    customer_name: str,
) -> bool:
    """Notify admins about a new payment receipt upload."""
    text = (
        "🔔 رسید پرداخت جدید!\n\n"
        f"شماره پرداخت: #{payment_id[:8]}\n"
        f"مبلغ: {amount:,} تومان\n"
        f"مشتری: {customer_name}\n\n"
        "برای بررسی به بخش «پرداخت‌های در انتظار تأیید» مراجعه کنید."
    )
    return await notify_telegram_ids(admin_telegram_ids, text)


async def notify_admins_new_validation(
    admin_telegram_ids: list[int],
    order_id: str,
    customer_name: str,
    category_name: str,
) -> bool:
    """Notify admins about a new validation request."""
    text = (
        "🔔 درخواست اعتبارسنجی جدید!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"مشتری: {customer_name}\n"
        f"دسته‌بندی: {category_name}\n\n"
        "برای بررسی به بخش «اعتبارسنجی‌های در انتظار» مراجعه کنید."
    )
    return await notify_telegram_ids(admin_telegram_ids, text)


async def notify_designers_new_order(
    designer_telegram_ids: list[int],
    order_id: str,
    category_name: str,
) -> bool:
    """Notify designers about a new order in their queue."""
    text = (
        "🎨 سفارش جدید در صف طراحی!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"دسته‌بندی: {category_name}\n\n"
        "برای مشاهده جزئیات به پنل طراح مراجعه کنید."
    )
    return await notify_telegram_ids(designer_telegram_ids, text)


async def notify_designer_assigned(
    designer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify a designer they were assigned to an order."""
    text = (
        "📋 سفارش جدید به شما اختصاص داده شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "لطفاً برای مشاهده جزئیات و شروع طراحی به پنل خود مراجعه کنید."
    )
    return await send_telegram_message(designer_telegram_id, text)


async def notify_customer_designer_assigned(
    customer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify customer that a designer was assigned."""
    text = (
        "👨‍🎨 طراح برای سفارش شما اختصاص داده شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "طراح در حال بررسی و شروع طراحی سفارش شماست."
    )
    return await send_telegram_message(customer_telegram_id, text)


async def notify_customer_new_design_revision(
    customer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify customer about a new design revision."""
    text = (
        "🖼 ویرایش جدید طراحی آماده بررسی است!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "لطفاً طرح را بررسی و تأیید یا رد کنید.\n"
        "🔗 sheetaro.com"
    )
    return await send_telegram_message(customer_telegram_id, text)


async def notify_designer_design_approved(
    designer_telegram_id: int,
    order_id: str,
) -> bool:
    """Notify designer their design was approved."""
    text = (
        "✅ طرح شما تأیید شد!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        "مشتری طرح شما را تأیید کرد. سفارش به مرحله بعد منتقل می‌شود."
    )
    return await send_telegram_message(designer_telegram_id, text)


async def notify_designer_design_rejected(
    designer_telegram_id: int,
    order_id: str,
    feedback: str,
) -> bool:
    """Notify designer their design was rejected."""
    text = (
        "🔄 طرح شما نیاز به بازنگری دارد\n\n"
        f"شماره سفارش: #{order_id[:8]}\n\n"
        f"📝 بازخورد مشتری:\n{feedback}\n\n"
        "لطفاً طرح را اصلاح و مجدداً ارسال کنید."
    )
    return await send_telegram_message(designer_telegram_id, text)


async def notify_printshops_new_order(
    printshop_telegram_ids: list[int],
    order_id: str,
    quantity: int,
    customer_city: str,
) -> bool:
    """Notify print shops about a new order ready for printing."""
    text = (
        "🔔 سفارش جدید آماده چاپ!\n\n"
        f"شماره سفارش: #{order_id[:8]}\n"
        f"تعداد: {quantity}\n"
        f"شهر: {customer_city or 'نامشخص'}\n\n"
        "برای مشاهده و قبول سفارش، به «صف سفارش‌ها» مراجعه کنید."
    )
    return await notify_telegram_ids(printshop_telegram_ids, text)
