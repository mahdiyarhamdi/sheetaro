"""Main bot entry point."""

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
from handlers.menu import handle_menu_selection
from handlers.profile import profile_conversation, show_profile_edit_options
from handlers.products import product_conversation
from handlers.orders import orders_conversation
from handlers.tracking import track_order, handle_tracking_input
from handlers.admin_payments import admin_payments_conversation
from handlers.admin_settings import admin_settings_conversation
from handlers.admin_catalog import catalog_conversation
from handlers.dynamic_order import dynamic_order_conversation

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
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("makeadmin", make_admin_command))
    
    # Product ordering conversation (legacy)
    application.add_handler(product_conversation)
    
    # Dynamic product ordering conversation (new)
    application.add_handler(dynamic_order_conversation)
    
    # Orders management conversation
    application.add_handler(orders_conversation)
    
    # Admin handlers
    application.add_handler(admin_payments_conversation)
    application.add_handler(admin_settings_conversation)
    application.add_handler(catalog_conversation)
    
    # Profile editing handlers
    application.add_handler(CallbackQueryHandler(show_profile_edit_options, pattern="^show_profile_edit$"))
    application.add_handler(profile_conversation)
    
    # Tracking handler
    application.add_handler(MessageHandler(filters.Regex("^(🔍 رهگیری سفارش|رهگیری)$"), track_order))
    
    # Menu handler (should be last to avoid conflicts)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection))
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
