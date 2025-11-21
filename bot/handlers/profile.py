import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from utils.api_client import APIClient
from keyboards.profile import get_profile_edit_keyboard, get_cancel_keyboard

# Conversation states
TYPING_PHONE, TYPING_ADDRESS = range(2)


async def show_profile_edit_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show profile editing options when user clicks edit button."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    api_client = APIClient()
    
    # Get user data from backend
    user_data = await api_client.get_user(user.id)
    
    if not user_data:
        await query.edit_message_text(
            "❌ خطا در دریافت اطلاعات پروفایل.\n"
            "لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END
    
    # Format profile message
    profile_text = (
        "👤 پروفایل من\n\n"
        f"نام: {user_data.get('first_name', 'ندارد')}\n"
        f"نام خانوادگی: {user_data.get('last_name', 'ندارد') or 'ندارد'}\n"
        f"نام کاربری: @{user_data.get('username', 'ندارد') or 'ندارد'}\n"
        f"شماره تماس: {user_data.get('phone_number', 'ثبت نشده') or 'ثبت نشده'}\n"
        f"آدرس: {user_data.get('address', 'ثبت نشده') or 'ثبت نشده'}\n\n"
        "برای ویرایش اطلاعات، یکی از گزینه‌های زیر را انتخاب کنید:"
    )
    
    await query.edit_message_text(
        profile_text,
        reply_markup=get_profile_edit_keyboard()
    )
    
    return ConversationHandler.END


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user profile with edit options."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    api_client = APIClient()
    
    # Get user data from backend
    user_data = await api_client.get_user(user.id)
    
    if not user_data:
        await query.edit_message_text(
            "❌ خطا در دریافت اطلاعات پروفایل.\n"
            "لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END
    
    # Format profile message
    profile_text = (
        "👤 پروفایل من\n\n"
        f"نام: {user_data.get('first_name', 'ندارد')}\n"
        f"نام خانوادگی: {user_data.get('last_name', 'ندارد') or 'ندارد'}\n"
        f"نام کاربری: @{user_data.get('username', 'ندارد') or 'ندارد'}\n"
        f"شماره تماس: {user_data.get('phone_number', 'ثبت نشده') or 'ثبت نشده'}\n"
        f"آدرس: {user_data.get('address', 'ثبت نشده') or 'ثبت نشده'}\n\n"
        "برای ویرایش اطلاعات، یکی از گزینه‌های زیر را انتخاب کنید:"
    )
    
    await query.edit_message_text(
        profile_text,
        reply_markup=get_profile_edit_keyboard()
    )
    
    return ConversationHandler.END


async def start_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start phone number editing process."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📞 ویرایش شماره تماس\n\n"
        "لطفاً شماره تماس خود را به یکی از فرمت‌های زیر وارد کنید:\n"
        "• 09xxxxxxxxx (11 رقم)\n"
        "• +98xxxxxxxxxx (با کد کشور)\n\n"
        "برای انصراف روی دکمه زیر کلیک کنید.",
        reply_markup=get_cancel_keyboard()
    )
    
    return TYPING_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate phone number."""
    phone = update.message.text.strip()
    user = update.effective_user
    
    # Validate phone format
    pattern_09 = r'^09\d{9}$'
    pattern_98 = r'^\+98\d{10}$'
    
    if not (re.match(pattern_09, phone) or re.match(pattern_98, phone)):
        await update.message.reply_text(
            "❌ فرمت شماره تماس صحیح نیست!\n\n"
            "لطفاً شماره را به یکی از فرمت‌های زیر وارد کنید:\n"
            "• 09xxxxxxxxx (11 رقم)\n"
            "• +98xxxxxxxxxx (با کد کشور)\n\n"
            "برای انصراف /cancel را ارسال کنید.",
            reply_markup=get_cancel_keyboard()
        )
        return TYPING_PHONE
    
    # Update user in backend
    api_client = APIClient()
    result = await api_client.update_user(
        user.id,
        {"phone_number": phone}
    )
    
    if result:
        await update.message.reply_text(
            f"✅ شماره تماس با موفقیت به‌روزرسانی شد.\n\n"
            f"شماره جدید: {phone}"
        )
    else:
        await update.message.reply_text(
            "❌ خطا در به‌روزرسانی شماره تماس.\n"
            "لطفاً دوباره تلاش کنید."
        )
    
    return ConversationHandler.END


async def start_edit_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start address editing process."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📍 ویرایش آدرس\n\n"
        "لطفاً آدرس کامل خود را برای ارسال سفارشات وارد کنید:\n\n"
        "برای انصراف روی دکمه زیر کلیک کنید.",
        reply_markup=get_cancel_keyboard()
    )
    
    return TYPING_ADDRESS


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and save address."""
    address = update.message.text.strip()
    user = update.effective_user
    
    if len(address) < 10:
        await update.message.reply_text(
            "❌ آدرس وارد شده بسیار کوتاه است!\n\n"
            "لطفاً آدرس کامل خود را وارد کنید.\n"
            "برای انصراف /cancel را ارسال کنید.",
            reply_markup=get_cancel_keyboard()
        )
        return TYPING_ADDRESS
    
    # Update user in backend
    api_client = APIClient()
    result = await api_client.update_user(
        user.id,
        {"address": address}
    )
    
    if result:
        await update.message.reply_text(
            f"✅ آدرس با موفقیت به‌روزرسانی شد.\n\n"
            f"آدرس جدید: {address}"
        )
    else:
        await update.message.reply_text(
            "❌ خطا در به‌روزرسانی آدرس.\n"
            "لطفاً دوباره تلاش کنید."
        )
    
    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the editing process."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "❌ عملیات لغو شد.\n\n"
            "برای بازگشت به منو از /start استفاده کنید."
        )
    else:
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "برای بازگشت به منو از /start استفاده کنید."
        )
    
    return ConversationHandler.END


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to main menu."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "بازگشت به منوی اصلی...\n\n"
        "از دستور /start استفاده کنید."
    )
    
    return ConversationHandler.END


# Create the conversation handler
profile_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_edit_phone, pattern="^edit_phone$"),
        CallbackQueryHandler(start_edit_address, pattern="^edit_address$"),
    ],
    states={
        TYPING_PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone),
        ],
        TYPING_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_edit, pattern="^cancel$"),
        CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
    ],
    allow_reentry=True,
)

