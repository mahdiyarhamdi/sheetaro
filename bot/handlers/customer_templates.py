"""Customer handlers for template selection and logo placement (public plans)."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

from utils.api_client import api_client

logger = logging.getLogger(__name__)


async def start_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the template selection flow after public plan selection."""
    query = update.callback_query
    
    plan_id = context.user_data.get('selected_plan_id')
    if not plan_id:
        await query.answer("خطا: پلن انتخاب نشده است", show_alert=True)
        return
    
    # Get templates for the plan
    templates = await api_client.get_templates(plan_id, active_only=True)
    
    if not templates:
        await query.message.edit_text("❌ هیچ قالبی برای این پلن تعریف نشده است.")
        return
    
    # Store templates in context
    context.user_data['template_selection'] = {
        'plan_id': plan_id,
        'templates': templates,
        'current_index': 0,
    }
    
    await show_template_gallery(update, context)


async def show_template_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display template gallery with preview images."""
    query = update.callback_query if update.callback_query else None
    
    t_data = context.user_data.get('template_selection', {})
    templates = t_data.get('templates', [])
    
    if not templates:
        if query:
            await query.message.edit_text("❌ هیچ قالبی موجود نیست.")
        return
    
    # Send all templates as photos
    for template in templates:
        name = template.get('name_fa', 'بدون نام')
        template_id = template.get('id')
        preview_url = template.get('preview_url', '')
        desc = template.get('description_fa', '')
        
        caption = f"🖼️ {name}\n"
        if desc:
            caption += f"{desc}\n"
        caption += "\nلوگوی شما در محل مربع قرمز قرار می‌گیرد."
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ انتخاب این قالب", callback_data=f"select_tpl_{template_id}")]
        ])
        
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=preview_url,
                caption=caption,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error sending template preview: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🖼️ {name}\n\n(خطا در نمایش تصویر)\n\nلوگوی شما در محل مربع قرمز قرار می‌گیرد.",
                reply_markup=keyboard
            )
    
    # Send navigation message
    keyboard = [
        [InlineKeyboardButton("🔙 انتخاب پلن دیگر", callback_data="order_back_plan")],
        [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
    ]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👆 یک قالب از بالا انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle template selection callback."""
    query = update.callback_query
    await query.answer()
    
    template_id = query.data.replace("select_tpl_", "")
    
    # Find the selected template
    t_data = context.user_data.get('template_selection', {})
    templates = t_data.get('templates', [])
    selected_template = None
    
    for t in templates:
        if t.get('id') == template_id:
            selected_template = t
            break
    
    if not selected_template:
        await query.message.edit_text("❌ قالب یافت نشد.")
        return
    
    # Store selected template
    context.user_data['selected_template'] = selected_template
    context.user_data['selected_template_id'] = template_id
    
    name = selected_template.get('name_fa', '')
    
    await query.message.reply_text(
        f"✅ قالب «{name}» انتخاب شد!\n\n"
        f"📤 آپلود لوگو\n\n"
        f"لوگوی خود را ارسال کنید:\n\n"
        f"⚠️ نکات:\n"
        f"• PNG با پس‌زمینه شفاف بهترین نتیجه\n"
        f"• حداکثر: ۵ مگابایت\n"
        f"• کیفیت بالا = چاپ بهتر",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انتخاب قالب دیگر", callback_data="order_back_tpl")],
            [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
        ])
    )
    
    # Set awaiting logo state
    context.user_data['awaiting_logo'] = True


async def handle_logo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle logo upload for template. Returns True if handled."""
    if not context.user_data.get('awaiting_logo'):
        return False
    
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "❌ لطفا یک تصویر ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انتخاب قالب دیگر", callback_data="order_back_tpl")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
            ])
        )
        return True
    
    # Get file URL
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
    else:
        file = await context.bot.get_file(update.message.document.file_id)
    
    if file.file_path.startswith("https://"):
        logo_url = file.file_path
    else:
        bot_token = context.bot.token
        logo_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    context.user_data['logo_url'] = logo_url
    context.user_data.pop('awaiting_logo', None)
    
    # Send processing message
    processing_msg = await update.message.reply_text("⏳ در حال پردازش...")
    
    # Apply logo to template
    template_id = context.user_data.get('selected_template_id')
    result = await api_client.apply_logo_to_template(template_id, logo_url)
    
    if not result:
        await processing_msg.edit_text(
            "❌ خطا در پردازش تصویر. لطفا دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="retry_logo")],
                [InlineKeyboardButton("🔙 انتخاب قالب دیگر", callback_data="order_back_tpl")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
            ])
        )
        return True
    
    # Store processed design info
    context.user_data['processed_design'] = result
    
    # Delete processing message
    await processing_msg.delete()
    
    # Send preview
    preview_url = result.get('preview_url', '')
    try:
        await update.message.reply_photo(
            photo=preview_url,
            caption="🎨 پیش‌نمایش طرح شما\n\nآیا این طرح را تایید می‌کنید?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید و ادامه", callback_data="confirm_design")],
                [InlineKeyboardButton("🔄 تغییر لوگو", callback_data="change_logo")],
                [InlineKeyboardButton("🔄 قالب دیگر", callback_data="order_back_tpl")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
            ])
        )
    except Exception as e:
        logger.error(f"Error sending preview: {e}")
        await update.message.reply_text(
            "🎨 پیش‌نمایش طرح شما\n\n"
            "(خطا در نمایش تصویر)\n\n"
            "آیا این طرح را تایید می‌کنید?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید و ادامه", callback_data="confirm_design")],
                [InlineKeyboardButton("🔄 تغییر لوگو", callback_data="change_logo")],
                [InlineKeyboardButton("🔄 قالب دیگر", callback_data="order_back_tpl")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
            ])
        )
    
    return True


async def handle_template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle various template-related callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "confirm_design":
        # Design confirmed, proceed to next step
        await query.message.edit_caption(
            caption="✅ طرح شما تایید شد!\n\n"
            "در حال پردازش سفارش...",
            reply_markup=None
        )
        
        # Trigger next step in order flow
        from handlers.dynamic_order import continue_after_template
        await continue_after_template(update, context)
        return
    
    if data == "change_logo":
        # Ask for new logo
        context.user_data['awaiting_logo'] = True
        await query.message.reply_text(
            "📤 لوگوی جدید خود را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="order_back_tpl")]
            ])
        )
        return
    
    if data == "retry_logo":
        # Retry logo upload
        context.user_data['awaiting_logo'] = True
        await query.message.edit_text(
            "📤 لوگوی خود را مجددا ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انتخاب قالب دیگر", callback_data="order_back_tpl")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")]
            ])
        )
        return
    
    if data == "order_back_tpl":
        # Go back to template selection
        context.user_data.pop('awaiting_logo', None)
        context.user_data.pop('selected_template', None)
        context.user_data.pop('selected_template_id', None)
        context.user_data.pop('logo_url', None)
        context.user_data.pop('processed_design', None)
        await show_template_gallery(update, context)
        return


async def handle_back_to_templates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle going back to template selection."""
    query = update.callback_query
    await query.answer()
    
    # Clear template-related state
    context.user_data.pop('awaiting_logo', None)
    context.user_data.pop('selected_template', None)
    context.user_data.pop('selected_template_id', None)
    context.user_data.pop('logo_url', None)
    context.user_data.pop('processed_design', None)
    
    await show_template_gallery(update, context)

