from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.main_menu import MenuButtons


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
        await update.message.reply_text(
            f"👤 پروفایل من\n\n"
            f"نام: {user.first_name or 'ندارد'}\n"
            f"نام کاربری: @{user.username or 'ندارد'}\n"
            f"شناسه تلگرام: {user.id}"
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

