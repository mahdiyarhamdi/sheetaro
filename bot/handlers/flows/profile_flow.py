"""Profile Flow - User profile management handlers.

This module handles profile-related operations using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    FLOW_PROFILE, PROFILE_STEPS
)
from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def handle_profile_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for profile flow."""
    
    handlers = {
        'edit_phone': handle_phone_input,
        'edit_city': handle_city_input,
        'edit_address': handle_address_input,
    }
    
    handler = handlers.get(step)
    if handler:
        await handler(update, context)
    else:
        logger.warning(f"Unknown profile step for text: {step}")


async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle phone number input."""
    # TODO: Implement
    pass


async def handle_city_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle city input."""
    # TODO: Implement
    pass


async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle address input."""
    # TODO: Implement
    pass

