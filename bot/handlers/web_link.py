"""Handler for web-telegram account linking via OTP."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackQueryHandler

from utils.api_client import api_client
from keyboards.manager import get_back_keyboard, get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
WAITING_OTP = 1


class _StartLinkwebFilter(filters.BaseFilter):
    """Matches only /start linkweb deep-link."""

    def filter(self, message) -> bool:
        if not message or not message.text:
            return False
        return message.text.strip() in ("/start linkweb", "/start linkweb@sheetarobot")


async def linkweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /linkweb command - start web account linking process."""
    user = update.effective_user
    
    logger.info(f"User {user.id} started web link process")
    
    # Check if already linked (optional, skip if user not found)
    user_data = await api_client.get_user(user.id)
    if user_data and user_data.get('web_linked'):
        is_admin = user_data.get('role') == 'ADMIN'
        await update.message.reply_text(
            "✅ حساب تلگرام شما قبلاً به وب اپ متصل شده است.\n\n"
            "می‌توانید با همین حساب در وب اپ وارد شوید.",
            reply_markup=get_main_menu_keyboard(is_admin=is_admin)
        )
        return ConversationHandler.END
    
    # Prompt for OTP (no need to be registered first)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_linkweb")]
    ])
    
    await update.message.reply_text(
        "🔗 *اتصال به وب اپ*\n\n"
        "برای اتصال حساب تلگرام به وب اپ:\n\n"
        "1️⃣ ابتدا در وب اپ sheetaro.com ثبت‌نام کنید\n"
        "2️⃣ به بخش پروفایل و «اتصال تلگرام» بروید\n"
        "3️⃣ کد ۶ رقمی که در وب نمایش داده می‌شود را اینجا وارد کنید\n\n"
        "📝 لطفاً کد ۶ رقمی را وارد کنید:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    return WAITING_OTP


async def handle_otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle OTP code input from user."""
    user = update.effective_user
    otp = update.message.text.strip()
    
    # Validate OTP format
    if not otp.isdigit() or len(otp) != 6:
        await update.message.reply_text(
            "❌ کد وارد شده نامعتبر است.\n"
            "لطفاً یک کد ۶ رقمی وارد کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_linkweb")]
            ])
        )
        return WAITING_OTP
    
    # Verify OTP with backend
    try:
        result = await api_client.verify_telegram_link(otp, user.id)
        
        if result and result.get('success'):
            logger.info(f"User {user.id} successfully linked web account")
            
            # Get updated user data
            user_data = await api_client.get_user(user.id)
            is_admin = user_data and user_data.get('role') == 'ADMIN'
            
            await update.message.reply_text(
                "✅ *اتصال موفقیت‌آمیز!*\n\n"
                "حساب تلگرام شما با موفقیت به وب اپ متصل شد.\n"
                "اکنون می‌توانید از هر دو پلتفرم استفاده کنید.\n\n"
                "📱 سفارشات و اطلاعات شما در هر دو سمت همگام است.",
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard(is_admin=is_admin)
            )
            return ConversationHandler.END
        else:
            error_msg = result.get('message', 'کد نامعتبر یا منقضی شده است') if result else 'خطا در ارتباط با سرور'
            await update.message.reply_text(
                f"❌ {error_msg}\n\n"
                "لطفاً کد جدید از وب اپ دریافت کنید و مجدداً تلاش کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_linkweb")]
                ])
            )
            return WAITING_OTP
            
    except Exception as e:
        logger.error(f"Error verifying OTP for user {user.id}: {e}")
        await update.message.reply_text(
            "❌ خطا در اتصال به سرور. لطفاً مجدداً تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_linkweb")]
            ])
        )
        return WAITING_OTP


async def cancel_linkweb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the web linking process."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_data = await api_client.get_user(user.id)
    is_admin = user_data and user_data.get('role') == 'ADMIN'
    
    await query.message.edit_text(
        "❌ فرآیند اتصال لغو شد.\n\n"
        "هر زمان که خواستید می‌توانید با دستور /linkweb مجدداً تلاش کنید."
    )
    
    await query.message.reply_text(
        "🏠 منوی اصلی",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin)
    )
    
    return ConversationHandler.END


def get_web_link_handler() -> ConversationHandler:
    """Get the ConversationHandler for web linking.

    Entry points:
      - /linkweb command
      - /start linkweb deep link (via custom filter)
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler("linkweb", linkweb_command),
            MessageHandler(_StartLinkwebFilter(), linkweb_command),
        ],
        states={
            WAITING_OTP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp_input),
                CallbackQueryHandler(cancel_linkweb, pattern="^cancel_linkweb$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_linkweb),
            CallbackQueryHandler(cancel_linkweb, pattern="^cancel_linkweb$"),
        ],
        name="web_link",
        persistent=False,
    )


# Kept for standalone use if needed
cancel_linkweb_handler = CallbackQueryHandler(cancel_linkweb, pattern="^cancel_linkweb$")

