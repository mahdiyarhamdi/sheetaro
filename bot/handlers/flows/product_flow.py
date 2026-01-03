"""Product Flow - Product ordering handlers (legacy).

This module handles product ordering using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    FLOW_PRODUCTS, PRODUCT_STEPS
)

logger = logging.getLogger(__name__)


async def handle_products_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for products flow."""
    # TODO: Implement product flow text handlers
    logger.warning(f"Product flow text handler not yet implemented for step: {step}")
    pass

