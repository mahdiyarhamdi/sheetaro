"""Helper utilities for the bot."""

from telegram import ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu_keyboard
from utils.api_client import api_client


def get_user_menu_keyboard(context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """Get appropriate menu keyboard based on user role stored in context."""
    is_admin = context.user_data.get('is_admin', False)
    return get_main_menu_keyboard(is_admin=is_admin)


async def get_user_menu_keyboard_async(
    context: ContextTypes.DEFAULT_TYPE,
    telegram_id: int
) -> ReplyKeyboardMarkup:
    """Get menu keyboard, fetching role from API if not in context.
    
    Use this when context might not have is_admin set (e.g., after bot restart).
    """
    if 'is_admin' not in context.user_data:
        user = await api_client.get_user(telegram_id)
        if user:
            context.user_data['is_admin'] = user.get('role') == 'ADMIN'
            context.user_data['user_role'] = user.get('role', 'CUSTOMER')
            context.user_data['user_id'] = user.get('id')
    return get_main_menu_keyboard(is_admin=context.user_data.get('is_admin', False))

