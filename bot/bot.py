"""Main bot entry point - Using unified flow manager."""

import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.request import HTTPXRequest

from handlers.start import start_command, make_admin_command
from handlers.text_router import route_text_input
from handlers.web_link import get_web_link_handler, cancel_linkweb_handler

# Import catalog flow handlers
from handlers.flows.catalog_flow import (
    show_catalog_menu,
    show_category_list,
    show_category_actions,
    start_category_create,
    delete_category,
    show_attribute_list,
    show_attribute_actions,
    start_attribute_create,
    handle_attribute_type,
    show_option_list,
    start_option_create,
    show_plan_list,
    show_plan_actions,
    start_plan_create,
    handle_plan_type,
    show_question_list,
    show_template_list,
    start_question_create,
    handle_question_type,
    finish_question_options,
    start_template_create,
    handle_template_image,
    handle_cancel,
    handle_back_to_admin,
)
from utils.flow_manager import get_step, FLOW_CATALOG, get_flow

# Import customer flow handlers
from handlers.customer_questionnaire import (
    handle_question_callback,
    handle_question_text_input,
    handle_question_photo_input,
)
from handlers.customer_templates import (
    handle_template_selection,
    handle_logo_upload,
    handle_template_callback,
)

# Import print shop flow handlers
from handlers.flows.printshop_flow import handle_printshop_callback

# Import admin flow validation callback handler
from handlers.flows.admin_flow import handle_validation_callback

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def _get_proxy_url() -> str | None:
    """Read proxy URL from shared config if enabled."""
    status_path = Path("/app/proxy_config/status.json")
    if status_path.exists():
        try:
            data = json.loads(status_path.read_text())
            if data.get("enabled"):
                proxy_url = f"socks5://xray:10808"
                logger.info(f"Proxy enabled: {data.get('protocol', '?')} via {data.get('server', '?')}")
                return proxy_url
        except Exception as e:
            logger.warning(f"Failed to read proxy config: {e}")

    # Fallback to environment variable
    env_proxy = os.getenv("TELEGRAM_PROXY_URL")
    if env_proxy:
        logger.info(f"Using proxy from env: {env_proxy}")
        return env_proxy

    return None


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    
    # Check for proxy configuration
    proxy_url = _get_proxy_url()
    builder = Application.builder().token(token)

    if proxy_url:
        logger.info(f"Configuring bot with SOCKS5 proxy: {proxy_url}")
        request = HTTPXRequest(proxy=proxy_url, connect_timeout=30.0, read_timeout=30.0)
        get_updates_request = HTTPXRequest(proxy=proxy_url, connect_timeout=30.0, read_timeout=60.0)
        builder = builder.request(request).get_updates_request(get_updates_request)
    else:
        logger.info("No proxy configured, connecting directly to Telegram")

    application = builder.build()
    
    # ============== Web Link Handler (must be before /start to catch /start linkweb) ==============
    application.add_handler(get_web_link_handler())
    application.add_handler(cancel_linkweb_handler)

    # ============== Command Handlers ==============
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("makeadmin912", make_admin_command))
    
    # ============== Catalog Callback Handlers ==============
    # Menu navigation
    application.add_handler(CallbackQueryHandler(show_catalog_menu, pattern="^catalog_menu$"))
    application.add_handler(CallbackQueryHandler(show_category_list, pattern="^catalog_categories$"))
    application.add_handler(CallbackQueryHandler(handle_back_to_admin, pattern="^back_to_admin$"))
    application.add_handler(CallbackQueryHandler(handle_cancel, pattern="^cancel$"))
    
    # Category handlers
    application.add_handler(CallbackQueryHandler(start_category_create, pattern="^cat_create$"))
    application.add_handler(CallbackQueryHandler(delete_category, pattern="^cat_delete_"))
    application.add_handler(CallbackQueryHandler(show_attribute_list, pattern="^cat_attrs_"))
    application.add_handler(CallbackQueryHandler(show_plan_list, pattern="^cat_plans_"))
    application.add_handler(CallbackQueryHandler(show_category_actions, pattern="^cat_[a-f0-9-]+$"))
    
    # Attribute handlers
    application.add_handler(CallbackQueryHandler(start_attribute_create, pattern="^attr_create_"))
    application.add_handler(CallbackQueryHandler(show_option_list, pattern="^attr_opts_"))
    application.add_handler(CallbackQueryHandler(show_attribute_actions, pattern="^attr_[a-f0-9-]+$"))
    application.add_handler(CallbackQueryHandler(handle_attribute_type, pattern="^input_"))
    
    # Option handlers
    application.add_handler(CallbackQueryHandler(start_option_create, pattern="^opt_create_"))
    
    # Plan handlers
    application.add_handler(CallbackQueryHandler(start_plan_create, pattern="^plan_create_"))
    application.add_handler(CallbackQueryHandler(show_question_list, pattern="^plan_questions_"))
    application.add_handler(CallbackQueryHandler(show_template_list, pattern="^plan_templates_"))
    application.add_handler(CallbackQueryHandler(handle_plan_type, pattern="^ptype_"))
    application.add_handler(CallbackQueryHandler(show_plan_actions, pattern="^plan_[a-f0-9-]+$"))
    
    # Question handlers (admin)
    application.add_handler(CallbackQueryHandler(start_question_create, pattern="^q_create_"))
    application.add_handler(CallbackQueryHandler(handle_question_type, pattern="^qtype_"))
    application.add_handler(CallbackQueryHandler(finish_question_options, pattern="^qopt_done_"))
    
    # Template handlers (admin)
    application.add_handler(CallbackQueryHandler(start_template_create, pattern="^tpl_create_"))
    
    # ============== Customer Questionnaire Handlers ==============
    # Questionnaire navigation
    application.add_handler(CallbackQueryHandler(handle_question_callback, pattern="^q_"))
    application.add_handler(CallbackQueryHandler(handle_question_callback, pattern="^qans_"))
    application.add_handler(CallbackQueryHandler(handle_question_callback, pattern="^qmulti_"))
    application.add_handler(CallbackQueryHandler(handle_question_callback, pattern="^qcolor_"))
    application.add_handler(CallbackQueryHandler(handle_question_callback, pattern="^qscale_"))
    
    # ============== Customer Template Handlers ==============
    application.add_handler(CallbackQueryHandler(handle_template_selection, pattern="^select_tpl_"))
    application.add_handler(CallbackQueryHandler(handle_template_callback, pattern="^confirm_design$"))
    application.add_handler(CallbackQueryHandler(handle_template_callback, pattern="^change_logo$"))
    application.add_handler(CallbackQueryHandler(handle_template_callback, pattern="^retry_logo$"))
    application.add_handler(CallbackQueryHandler(handle_template_callback, pattern="^order_back_tpl$"))
    
    # ============== Print Shop Callback Handlers ==============
    async def ps_callback_router(update: Update, context):
        """Route print shop callbacks."""
        await handle_printshop_callback(update, context)

    application.add_handler(CallbackQueryHandler(ps_callback_router, pattern="^ps_"))

    # ============== Validation Callback Handlers ==============
    async def validation_callback_router(update: Update, context):
        """Route validation callbacks."""
        await handle_validation_callback(update, context)

    application.add_handler(CallbackQueryHandler(validation_callback_router, pattern="^(review_validation_|approve_validation_|reject_validation_|back_to_validations_list)"))

    # ============== Central Text Router ==============
    # This handles all text messages and routes them to the appropriate flow
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_input))
    
    # ============== Photo Handler ==============
    async def handle_photo(update: Update, context):
        """Route photo uploads to appropriate handler."""
        # Check if in catalog flow for template image upload
        current_flow = get_flow(context)
        current_step = get_step(context)
        
        if current_flow == FLOW_CATALOG and current_step == 'template_upload_image':
            await handle_template_image(update, context)
            return
        
        # Try questionnaire first
        if await handle_question_photo_input(update, context):
            return
        # Try template logo upload
        if await handle_logo_upload(update, context):
            return
        # Default: ignore
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Start bot with restart signal watcher
    logger.info("Starting bot with unified flow manager...")
    
    # Register a job to check for restart signal every 15 seconds
    restart_signal_path = Path("/app/proxy_config/restart_signal")
    
    async def check_restart_signal(context):
        """Check if a restart signal has been written."""
        if restart_signal_path.exists():
            logger.info("Restart signal detected! Stopping bot...")
            restart_signal_path.unlink(missing_ok=True)
            # Stop the application gracefully - it will be restarted by Docker
            application.stop_running()

    if application.job_queue:
        application.job_queue.run_repeating(check_restart_signal, interval=15, first=10)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
