"""Main bot entry point - Using unified flow manager."""

import os
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from handlers.start import start_command, make_admin_command
from handlers.text_router import route_text_input

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
    handle_cancel,
    handle_back_to_admin,
)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # ============== Command Handlers ==============
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("makeadmin", make_admin_command))
    
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
    
    # ============== Central Text Router ==============
    # This handles all text messages and routes them to the appropriate flow
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_input))
    
    # ============== Photo Handler for Receipts ==============
    # TODO: Add photo handler for receipt uploads
    
    # Start bot
    logger.info("Starting bot with unified flow manager...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
