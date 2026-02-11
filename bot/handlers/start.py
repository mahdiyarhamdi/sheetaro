import logging

from telegram import Update
from telegram.ext import ContextTypes

from keyboards.manager import get_main_menu_keyboard
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
                # file.file_path might already be a full URL or just a path
                if file.file_path.startswith("https://"):
                    user_data["profile_photo_url"] = file.file_path
                else:
                    bot_token = context.bot.token
                    user_data["profile_photo_url"] = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
        except Exception as e:
            logger.warning(f"Could not get profile photo: {e}")
    
    # Save user to database via API
    result = await api_client.create_or_update_user(user_data)
    
    # Store user role in context for menu display
    is_admin = False
    is_printshop = False
    if result:
        logger.info(f"User saved: telegram_id={user.id}, username={user.username}, role={result.get('role')}")
        role = result.get('role', 'CUSTOMER')
        is_admin = role == 'ADMIN'
        is_printshop = role == 'PRINT_SHOP'
        context.user_data['is_admin'] = is_admin
        context.user_data['is_printshop'] = is_printshop
        context.user_data['user_role'] = role
        context.user_data['user_id'] = result.get('id')
        logger.info(f"is_admin={is_admin}, is_printshop={is_printshop}")
    else:
        logger.warning(f"Failed to get user data from API for telegram_id={user.id}")
    
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
        reply_markup=get_main_menu_keyboard(is_admin=is_admin, is_printshop=is_printshop)
    )


async def make_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /makeadmin912 command - promotes user to admin (secret code)."""
    user = update.effective_user
    
    if not user:
        return
    
    logger.info(f"makeadmin912 called by telegram_id={user.id}")
    
    # Get user from API
    user_info = await api_client.get_user_by_telegram_id(user.id)
    
    if not user_info:
        logger.warning(f"User not found in DB, telegram_id={user.id}")
        await update.message.reply_text("❌ ابتدا /start بزنید.")
        return
    
    logger.info(f"User found: id={user_info.get('id')}, role={user_info.get('role')}")
    
    # Check if already admin
    if user_info.get('role') == 'ADMIN':
        context.user_data['is_admin'] = True
        context.user_data['user_role'] = 'ADMIN'
        await update.message.reply_text(
            "✅ شما قبلاً ادمین هستید.\n\n"
            "برای دسترسی به پنل مدیریت، /start بزنید.",
            reply_markup=get_main_menu_keyboard(is_admin=True)
        )
        return
    
    # Promote to admin
    logger.info(f"Attempting to promote user {user_info['id']} to admin")
    result = await api_client.promote_to_admin(user_info['id'])
    
    if result:
        # Update context
        context.user_data['is_admin'] = True
        context.user_data['user_role'] = 'ADMIN'
        
        logger.info(f"User promoted to admin via /makeadmin912: telegram_id={user.id}, user_id={user_info['id']}")
        
        await update.message.reply_text(
            "🎉 تبریک! شما اکنون ادمین هستید.\n\n"
            "برای دسترسی به پنل مدیریت، /start بزنید.",
            reply_markup=get_main_menu_keyboard(is_admin=True)
        )
    else:
        logger.error(f"Failed to promote user to admin: telegram_id={user.id}, user_id={user_info['id']}")
        await update.message.reply_text("❌ خطا در ارتقا به ادمین. لطفاً دوباره تلاش کنید.")
