from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from keyboards.main_menu import MenuButtons
from utils.api_client import api_client


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button selections."""
    text = update.message.text
    user = update.effective_user
    
    if text == MenuButtons.ORDER_LABEL:
        await update.message.reply_text(
            "🏷️ سفارش لیبل\n\n"
            "در حال حاضر این بخش در دست توسعه است.\n"
            "به زودی می‌توانید سفارش لیبل خود را ثبت کنید! 🚀"
        )
    
    elif text == MenuButtons.ORDER_BUSINESS_CARD:
        await update.message.reply_text(
            "💼 سفارش کارت ویزیت\n\n"
            "در حال حاضر این بخش در دست توسعه است.\n"
            "به زودی می‌توانید سفارش کارت ویزیت خود را ثبت کنید! 🚀"
        )
    
    elif text == MenuButtons.MY_ORDERS:
        await update.message.reply_text(
            "📦 سفارشات من\n\n"
            "هنوز سفارشی ثبت نکرده‌اید."
        )
    
    elif text == MenuButtons.MY_PROFILE:
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
            f"آدرس: {user_data.get('address', 'ثبت نشده') or 'ثبت نشده'}\n\n"
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
    
    elif text == MenuButtons.HELP:
        await update.message.reply_text(
            "❓ راهنما\n\n"
            "از منوی اصلی می‌توانید:\n\n"
            "🏷️ سفارش لیبل: برای ثبت سفارش لیبل جدید\n"
            "💼 سفارش کارت ویزیت: برای ثبت سفارش کارت ویزیت\n"
            "📦 سفارشات من: مشاهده و پیگیری سفارشات\n"
            "👤 پروفایل من: مشاهده اطلاعات پروفایل\n"
            "📞 پشتیبانی: ارتباط با پشتیبانی\n\n"
            "برای شروع، دستور /start را وارد کنید."
        )
    
    elif text == MenuButtons.SUPPORT:
        await update.message.reply_text(
            "📞 پشتیبانی\n\n"
            "برای ارتباط با پشتیبانی:\n"
            "📧 ایمیل: support@sheetaro.com\n"
            "📱 تلگرام: @sheetaro_support\n\n"
            "پاسخگویی: شنبه تا چهارشنبه، ۹ صبح تا ۶ عصر"
        )

