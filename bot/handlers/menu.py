"""Menu handler for the bot."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utils.api_client import api_client
from utils.helpers import get_user_menu_keyboard


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button selections."""
    text = update.message.text
    user = update.effective_user
    
    # Skip if in a conversation
    if context.user_data.get('awaiting_tracking'):
        from handlers.tracking import handle_tracking_input
        await handle_tracking_input(update, context)
        return
    
    if text == "👤 پروفایل":
        # Get user data from backend
        user_data = await api_client.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text(
                "❌ خطا در دریافت اطلاعات پروفایل.\n"
                "لطفاً دوباره تلاش کنید."
            )
            return
        
        # Format profile message
        profile_text = (
            "👤 پروفایل من\n\n"
            f"نام: {user_data.get('first_name', 'ندارد')}\n"
            f"نام خانوادگی: {user_data.get('last_name', 'ندارد') or 'ندارد'}\n"
            f"نام کاربری: @{user_data.get('username', 'ندارد') or 'ندارد'}\n"
            f"شماره تماس: {user_data.get('phone_number', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"شهر: {user_data.get('city', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"آدرس: {user_data.get('address', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"نقش: {user_data.get('role', 'CUSTOMER')}\n\n"
            "برای ویرایش اطلاعات، روی دکمه زیر کلیک کنید:"
        )
        
        # Create inline keyboard for editing
        keyboard = [
            [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="show_profile_edit")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_text,
            reply_markup=reply_markup
        )
    
    elif text == "ℹ️ راهنما":
        await update.message.reply_text(
            "❓ راهنما\n\n"
            "از منوی اصلی می‌توانید:\n\n"
            "🛒 ثبت سفارش: برای ثبت سفارش لیبل یا فاکتور\n"
            "📦 سفارشات من: مشاهده و پیگیری سفارشات\n"
            "👤 پروفایل: مشاهده و ویرایش اطلاعات\n"
            "🔍 رهگیری سفارش: پیگیری سریع سفارش\n"
            "📞 پشتیبانی: ارتباط با پشتیبانی\n\n"
            "برای شروع مجدد، دستور /start را وارد کنید."
        )
    
    elif text == "📞 پشتیبانی":
        await update.message.reply_text(
            "📞 پشتیبانی\n\n"
            "برای ارتباط با پشتیبانی:\n"
            "📧 ایمیل: support@sheetaro.com\n"
            "📱 تلگرام: @sheetaro_support\n\n"
            "پاسخگویی: شنبه تا چهارشنبه، ۹ صبح تا ۶ عصر"
        )
    
    elif text == "📂 مدیریت کاتالوگ":
        # Check if user is admin
        if context.user_data.get('is_admin'):
            from handlers.admin_catalog import show_catalog_menu
            await show_catalog_menu(update, context)
        else:
            await update.message.reply_text("❌ شما به این بخش دسترسی ندارید.")
    
    else:
        # Unknown command - show help
        await update.message.reply_text(
            "لطفاً از منوی زیر استفاده کنید:",
            reply_markup=get_user_menu_keyboard(context)
        )
