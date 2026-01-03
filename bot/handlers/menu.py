"""Menu handler for the bot - Using unified flow manager."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utils.api_client import api_client
from utils.flow_manager import set_flow, FLOW_ORDERS, FLOW_TRACKING, FLOW_ADMIN
from keyboards.manager import get_main_menu_keyboard, get_admin_menu_keyboard


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button selections."""
    text = update.message.text
    user = update.effective_user
    is_admin = context.user_data.get('is_admin', False)
    
    # ============== Order related ==============
    if "ثبت سفارش" in text or "سفارش جدید" in text:
        # TODO: Start product/dynamic order flow
        await update.message.reply_text(
            "برای ثبت سفارش، نوع محصول را انتخاب کنید:\n\n"
            "(در حال توسعه...)"
        )
        return
    
    if "سفارشات من" in text:
        from handlers.flows.order_flow import show_orders_menu
        await show_orders_menu(update, context)
        return
    
    # ============== Profile ==============
    if "پروفایل" in text:
        user_data = await api_client.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text(
                "خطا در دریافت اطلاعات پروفایل.\n"
                "لطفا دوباره تلاش کنید."
            )
            return
        
        profile_text = (
            "پروفایل من\n\n"
            f"نام: {user_data.get('first_name', 'ندارد')}\n"
            f"نام خانوادگی: {user_data.get('last_name', 'ندارد') or 'ندارد'}\n"
            f"نام کاربری: @{user_data.get('username', 'ندارد') or 'ندارد'}\n"
            f"شماره تماس: {user_data.get('phone_number', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"شهر: {user_data.get('city', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"آدرس: {user_data.get('address', 'ثبت نشده') or 'ثبت نشده'}\n"
            f"نقش: {user_data.get('role', 'CUSTOMER')}\n\n"
            "برای ویرایش اطلاعات، روی دکمه زیر کلیک کنید:"
        )
        
        keyboard = [
            [InlineKeyboardButton("ویرایش پروفایل", callback_data="show_profile_edit")],
        ]
        
        await update.message.reply_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # ============== Tracking ==============
    if "رهگیری" in text:
        set_flow(context, FLOW_TRACKING, 'awaiting_code')
        await update.message.reply_text(
            "لطفا کد رهگیری سفارش را وارد کنید:"
        )
        return
    
    # ============== Help ==============
    if "راهنما" in text:
        await update.message.reply_text(
            "راهنما\n\n"
            "از منوی اصلی می توانید:\n\n"
            "- ثبت سفارش: برای ثبت سفارش لیبل یا فاکتور\n"
            "- سفارشات من: مشاهده و پیگیری سفارشات\n"
            "- پروفایل: مشاهده و ویرایش اطلاعات\n"
            "- رهگیری سفارش: پیگیری سریع سفارش\n"
            "- پشتیبانی: ارتباط با پشتیبانی\n\n"
            "برای شروع مجدد، دستور /start را وارد کنید."
        )
        return
    
    # ============== Support ==============
    if "پشتیبانی" in text:
        await update.message.reply_text(
            "پشتیبانی\n\n"
            "برای ارتباط با پشتیبانی:\n"
            "ایمیل: support@sheetaro.com\n"
            "تلگرام: @sheetaro_support\n\n"
            "پاسخگویی: شنبه تا چهارشنبه، ۹ صبح تا ۶ عصر"
        )
        return
    
    # ============== Admin Panel ==============
    if "پنل مدیریت" in text or "مدیریت" in text:
        if not is_admin:
            await update.message.reply_text(
                "شما به این بخش دسترسی ندارید."
            )
            return
        
        from handlers.flows.admin_flow import show_admin_menu
        await show_admin_menu(update, context)
        return
    
    # ============== Unknown ==============
    await update.message.reply_text(
        "لطفا از منوی زیر استفاده کنید:",
        reply_markup=get_main_menu_keyboard(is_admin)
    )
