"""Central Text Router - Routes all text input to appropriate handlers.

This module provides a single entry point for all text messages,
routing them to the correct flow handler based on user_data state.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.flow_manager import (
    get_flow, get_step, clear_flow,
    FLOW_ADMIN, FLOW_CATALOG, FLOW_ORDERS, FLOW_PRODUCTS, FLOW_PROFILE, FLOW_TRACKING
)

logger = logging.getLogger(__name__)


async def route_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route text input to the appropriate flow handler.
    
    This is the central router for all text messages. It checks the current
    flow and step, then delegates to the appropriate handler.
    """
    text = update.message.text
    current_flow = get_flow(context)
    current_step = get_step(context)
    
    logger.info(f"Text router: flow={current_flow}, step={current_step}, text={text[:50]}")
    
    # If no flow is active, handle as menu selection
    if current_flow is None:
        await handle_menu_text(update, context)
        return
    
    # Route to appropriate flow
    if current_flow == FLOW_CATALOG:
        await route_catalog_text(update, context, current_step)
    elif current_flow == FLOW_ADMIN:
        await route_admin_text(update, context, current_step)
    elif current_flow == FLOW_ORDERS:
        await route_orders_text(update, context, current_step)
    elif current_flow == FLOW_PRODUCTS:
        await route_products_text(update, context, current_step)
    elif current_flow == FLOW_PROFILE:
        await route_profile_text(update, context, current_step)
    elif current_flow == FLOW_TRACKING:
        await route_tracking_text(update, context, current_step)
    else:
        # Unknown flow, treat as menu
        logger.warning(f"Unknown flow: {current_flow}")
        clear_flow(context)
        await handle_menu_text(update, context)


async def handle_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text when no flow is active (main menu)."""
    from handlers.menu import handle_menu_selection
    await handle_menu_selection(update, context)


async def route_catalog_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for catalog flow."""
    from handlers.flows.catalog_flow import handle_catalog_text
    await handle_catalog_text(update, context, step)


async def route_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for admin flow."""
    from handlers.flows.admin_flow import handle_admin_text
    await handle_admin_text(update, context, step)


async def route_orders_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for orders flow."""
    from handlers.flows.order_flow import handle_orders_text
    await handle_orders_text(update, context, step)


async def route_products_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for products flow."""
    from handlers.flows.product_flow import handle_products_text
    await handle_products_text(update, context, step)


async def route_profile_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for profile flow."""
    from handlers.flows.profile_flow import handle_profile_text
    await handle_profile_text(update, context, step)


async def route_tracking_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Route text input for tracking flow."""
    from handlers.tracking import handle_tracking_input
    await handle_tracking_input(update, context)

