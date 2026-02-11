"""Print shop SLA enforcement background task.

Runs periodically to check for READY_FOR_PRINT orders that have exceeded
the 30-minute SLA acceptance window. Logs SLA breaches and can notify admins.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.repositories.order_repository import OrderRepository
from app.utils.logger import log_event

logger = logging.getLogger(__name__)

# SLA threshold in minutes
SLA_ACCEPT_THRESHOLD_MINUTES = 30

# Check interval in seconds (every 5 minutes)
SLA_CHECK_INTERVAL_SECONDS = 300


async def check_sla_breaches(db: AsyncSession) -> list[dict]:
    """Check for orders that have breached the SLA acceptance window.

    Returns a list of breach info dicts for notification purposes.
    """
    repo = OrderRepository(db)
    stale_orders = await repo.get_stale_ready_orders(
        threshold_minutes=SLA_ACCEPT_THRESHOLD_MINUTES
    )

    breaches = []
    for order in stale_orders:
        age_minutes = (
            datetime.now(timezone.utc) - order.created_at.replace(tzinfo=timezone.utc)
        ).total_seconds() / 60

        breach_info = {
            "order_id": str(order.id),
            "created_at": order.created_at.isoformat(),
            "age_minutes": round(age_minutes, 1),
            "customer_name": None,
        }

        if order.user:
            breach_info["customer_name"] = (
                f"{order.user.first_name} {order.user.last_name or ''}".strip()
            )

        log_event(
            event_type="printshop.sla_breach",
            order_id=str(order.id),
            age_minutes=str(round(age_minutes, 1)),
        )

        breaches.append(breach_info)

    if breaches:
        logger.warning(
            f"SLA breach: {len(breaches)} orders waiting > {SLA_ACCEPT_THRESHOLD_MINUTES} minutes"
        )

    return breaches


async def run_sla_check_loop() -> None:
    """Run the SLA check in a loop. Designed to be started as a background task."""
    logger.info("Starting print shop SLA check loop")

    while True:
        try:
            async with get_db_context() as db:
                breaches = await check_sla_breaches(db)
                if breaches:
                    logger.info(f"Found {len(breaches)} SLA breaches")
        except Exception as e:
            logger.error(f"Error in SLA check loop: {e}", exc_info=True)

        await asyncio.sleep(SLA_CHECK_INTERVAL_SECONDS)
