import logging

from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu_keyboard
from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    
    if not user:
        return
    
    # Prepare user data
    user_data = {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name or "کاربر",
        "last_name": user.last_name,
        "phone_number": None,
        "profile_photo_url": None,
    }
    
    # Get profile photo URL if available
    if user.id:
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][0]
                file = await context.bot.get_file(photo.file_id)
                user_data["profile_photo_url"] = file.file_path
        except Exception as e:
            logger.warning(f"Could not get profile photo: {e}")
    
    # Save user to database via API
    result = await api_client.create_or_update_user(user_data)
    
    if result:
        logger.info(f"User saved: telegram_id={user.id}, username={user.username}")
    
    # Send welcome message with main menu
    welcome_message = f"""سلام {user.first_name} عزیز! 👋

به ربات چاپ شیتارو خوش آمدید ✨

با این ربات می‌توانید:
🏷️ لیبل‌های حرفه‌ای سفارش دهید
💼 کارت ویزیت طراحی کنید
📦 سفارشات خود را پیگیری کنید

برای شروع، یکی از گزینه‌های زیر را انتخاب کنید:"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard()
    )

