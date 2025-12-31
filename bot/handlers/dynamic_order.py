"""Dynamic order handler using dynamic categories, attributes, and plans."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from utils.api_client import api_client
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
(
    SELECT_CATEGORY,
    SELECT_ATTRIBUTE,
    SELECT_ATTRIBUTE_OPTION,
    ENTER_ATTRIBUTE_VALUE,
    SELECT_PLAN,
    SELECT_TEMPLATE,
    UPLOAD_LOGO,
    QUESTIONNAIRE,
    ORDER_SUMMARY,
    PAYMENT,
    AWAITING_RECEIPT,
) = range(11)


def get_category_keyboard(categories: list):
    """Get keyboard with list of categories for ordering."""
    keyboard = []
    for cat in categories:
        icon = cat.get('icon', '📁')
        name = cat.get('name_fa', 'بدون نام')
        keyboard.append([
            InlineKeyboardButton(f"{icon} {name}", callback_data=f"order_cat_{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 انصراف", callback_data="order_cancel")])
    return InlineKeyboardMarkup(keyboard)


def get_attribute_options_keyboard(options: list, attribute_id: str):
    """Get keyboard for selecting attribute options."""
    keyboard = []
    for opt in options:
        label = opt.get('label_fa', 'بدون نام')
        price = int(float(opt.get('price_modifier', 0)))
        if price > 0:
            label += f" (+{price:,} تومان)"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"opt_{opt['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="order_back")])
    return InlineKeyboardMarkup(keyboard)


def get_plan_keyboard(plans: list):
    """Get keyboard for selecting design plan."""
    keyboard = []
    for plan in plans:
        name = plan.get('name_fa', 'بدون نام')
        price = int(float(plan.get('price', 0)))
        price_str = f"{price:,} تومان" if price > 0 else "رایگان"
        keyboard.append([
            InlineKeyboardButton(f"🎯 {name} ({price_str})", callback_data=f"plan_{plan['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="order_back")])
    return InlineKeyboardMarkup(keyboard)


def get_template_keyboard(templates: list):
    """Get keyboard for selecting design template."""
    keyboard = []
    for t in templates:
        name = t.get('name_fa', 'بدون نام')
        keyboard.append([
            InlineKeyboardButton(f"🖼️ {name}", callback_data=f"template_{t['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="order_back")])
    return InlineKeyboardMarkup(keyboard)


def get_question_options_keyboard(options: list, question_id: str, is_multi: bool = False):
    """Get keyboard for question options."""
    keyboard = []
    for opt in options:
        label = opt.get('label_fa', 'بدون نام')
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"qopt_{opt['id']}")
        ])
    if is_multi:
        keyboard.append([InlineKeyboardButton("✅ تایید انتخاب‌ها", callback_data="qopt_done")])
    keyboard.append([InlineKeyboardButton("🔙 قبلی", callback_data="question_back")])
    return InlineKeyboardMarkup(keyboard)


# ==================== Entry Point ====================

async def start_dynamic_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the dynamic ordering process."""
    # Get active categories
    categories = await api_client.get_categories(active_only=True)
    
    if not categories:
        is_admin = context.user_data.get('is_admin', False)
        if update.message:
            await update.message.reply_text(
                "متأسفانه در حال حاضر هیچ دسته‌بندی فعالی وجود ندارد.\n"
                "لطفاً بعداً مراجعه کنید.",
                reply_markup=get_main_menu_keyboard(is_admin=is_admin)
            )
        else:
            await update.callback_query.message.edit_text(
                "متأسفانه در حال حاضر هیچ دسته‌بندی فعالی وجود ندارد."
            )
        return ConversationHandler.END
    
    # Initialize order data
    context.user_data['order'] = {
        'attributes': {},
        'selected_options': [],
        'answers': [],
        'total_price': 0,
    }
    
    if update.message:
        await update.message.reply_text(
            "🛒 ثبت سفارش جدید\n\n"
            "لطفاً نوع محصول را انتخاب کنید:",
            reply_markup=get_category_keyboard(categories)
        )
    else:
        await update.callback_query.message.edit_text(
            "🛒 ثبت سفارش جدید\n\n"
            "لطفاً نوع محصول را انتخاب کنید:",
            reply_markup=get_category_keyboard(categories)
        )
    
    return SELECT_CATEGORY


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category selection."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("order_cat_", "")
    
    # Get category details with attributes and plans
    category = await api_client.get_category_details(category_id)
    if not category:
        await query.message.edit_text("❌ خطا در دریافت اطلاعات دسته‌بندی.")
        return SELECT_CATEGORY
    
    context.user_data['order']['category'] = category
    context.user_data['order']['category_id'] = category_id
    
    # Get attributes
    attributes = category.get('attributes', [])
    if not attributes:
        # No attributes, go directly to plan selection
        return await show_plan_selection(update, context)
    
    # Store attributes for sequential selection
    context.user_data['order']['pending_attributes'] = attributes.copy()
    context.user_data['order']['current_attr_index'] = 0
    
    # Show first attribute
    return await show_next_attribute(update, context)


async def show_next_attribute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the next attribute for selection."""
    query = update.callback_query
    order = context.user_data.get('order', {})
    attributes = order.get('pending_attributes', [])
    index = order.get('current_attr_index', 0)
    
    if index >= len(attributes):
        # All attributes selected, go to plan selection
        return await show_plan_selection(update, context)
    
    attr = attributes[index]
    attr_name = attr.get('name_fa', 'ویژگی')
    attr_type = attr.get('input_type', 'SELECT')
    options = attr.get('options', [])
    
    context.user_data['order']['current_attribute'] = attr
    
    if attr_type == 'NUMBER':
        # Numeric input
        min_val = attr.get('min_value', 1)
        max_val = attr.get('max_value', 10000)
        await query.message.edit_text(
            f"📊 {attr_name}\n\n"
            f"لطفاً یک عدد بین {min_val:,} تا {max_val:,} وارد کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="order_cancel")]
            ])
        )
        return ENTER_ATTRIBUTE_VALUE
    
    elif attr_type == 'TEXT':
        # Text input
        await query.message.edit_text(
            f"✏️ {attr_name}\n\n"
            "لطفاً متن مورد نظر را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="order_cancel")]
            ])
        )
        return ENTER_ATTRIBUTE_VALUE
    
    else:
        # SELECT or MULTI_SELECT
        if not options:
            # Skip if no options
            order['current_attr_index'] = index + 1
            return await show_next_attribute(update, context)
        
        await query.message.edit_text(
            f"📋 {attr_name}\n\n"
            "لطفاً یک گزینه انتخاب کنید:",
            reply_markup=get_attribute_options_keyboard(options, attr['id'])
        )
        return SELECT_ATTRIBUTE_OPTION


async def handle_option_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attribute option selection."""
    query = update.callback_query
    await query.answer()
    
    option_id = query.data.replace("opt_", "")
    order = context.user_data.get('order', {})
    attr = order.get('current_attribute', {})
    
    # Find selected option
    selected_option = None
    for opt in attr.get('options', []):
        if opt['id'] == option_id:
            selected_option = opt
            break
    
    if selected_option:
        # Store selection
        order['attributes'][attr['slug']] = {
            'attribute_id': attr['id'],
            'option_id': option_id,
            'value': selected_option.get('value'),
            'label': selected_option.get('label_fa'),
            'price_modifier': int(float(selected_option.get('price_modifier', 0))),
        }
        order['selected_options'].append(selected_option)
        order['total_price'] += int(float(selected_option.get('price_modifier', 0)))
    
    # Move to next attribute
    order['current_attr_index'] = order.get('current_attr_index', 0) + 1
    
    return await show_next_attribute(update, context)


async def handle_attribute_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text/numeric attribute value input."""
    text = update.message.text.strip()
    order = context.user_data.get('order', {})
    attr = order.get('current_attribute', {})
    
    attr_type = attr.get('input_type', 'TEXT')
    
    if attr_type == 'NUMBER':
        try:
            value = int(text.replace(',', ''))
            min_val = attr.get('min_value', 1)
            max_val = attr.get('max_value', 10000)
            if value < min_val or value > max_val:
                await update.message.reply_text(
                    f"❌ عدد باید بین {min_val:,} تا {max_val:,} باشد.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 انصراف", callback_data="order_cancel")]
                    ])
                )
                return ENTER_ATTRIBUTE_VALUE
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 انصراف", callback_data="order_cancel")]
                ])
            )
            return ENTER_ATTRIBUTE_VALUE
    else:
        value = text
    
    # Store value
    order['attributes'][attr['slug']] = {
        'attribute_id': attr['id'],
        'value': value,
        'label': str(value),
        'price_modifier': 0,
    }
    
    # Move to next attribute
    order['current_attr_index'] = order.get('current_attr_index', 0) + 1
    
    # Create a fake query for show_next_attribute
    class FakeQuery:
        message = update.message
        async def answer(self): pass
    
    fake_update = type('Update', (), {'callback_query': FakeQuery()})()
    
    return await show_next_attribute(fake_update, context)


async def show_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show design plan selection."""
    query = update.callback_query
    order = context.user_data.get('order', {})
    category = order.get('category', {})
    
    plans = category.get('design_plans', [])
    if not plans:
        await query.message.edit_text(
            "❌ هیچ پلن طراحی برای این دسته تعریف نشده است."
        )
        return ConversationHandler.END
    
    await query.message.edit_text(
        "🎯 انتخاب پلن طراحی\n\n"
        "لطفاً پلن مورد نظر را انتخاب کنید:",
        reply_markup=get_plan_keyboard(plans)
    )
    return SELECT_PLAN


async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle design plan selection."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_", "")
    order = context.user_data.get('order', {})
    
    # Get plan details
    plan = await api_client.get_design_plan_details(plan_id)
    if not plan:
        await query.message.edit_text("❌ خطا در دریافت اطلاعات پلن.")
        return SELECT_PLAN
    
    order['plan'] = plan
    order['plan_id'] = plan_id
    order['total_price'] += int(float(plan.get('price', 0)))
    
    # Check plan type
    if plan.get('has_templates'):
        # Public plan - show template gallery
        templates = plan.get('templates', [])
        if templates:
            await query.message.edit_text(
                "🖼️ انتخاب قالب\n\n"
                "لطفاً یک قالب انتخاب کنید:",
                reply_markup=get_template_keyboard(templates)
            )
            return SELECT_TEMPLATE
    
    elif plan.get('has_questionnaire'):
        # Semi-private plan - show questionnaire
        questions = plan.get('questions', [])
        if questions:
            order['pending_questions'] = questions.copy()
            order['current_question_index'] = 0
            return await show_next_question(update, context)
    
    # Private or simple plan - go to summary
    return await show_order_summary(update, context)


async def handle_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle template selection."""
    query = update.callback_query
    await query.answer()
    
    template_id = query.data.replace("template_", "")
    order = context.user_data.get('order', {})
    
    # Store selected template
    templates = order.get('plan', {}).get('templates', [])
    for t in templates:
        if t['id'] == template_id:
            order['template'] = t
            break
    
    await query.message.edit_text(
        "📤 آپلود لوگو\n\n"
        "لطفاً لوگوی خود را ارسال کنید.\n"
        "لوگو در محل مشخص شده روی قالب قرار می‌گیرد.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انتخاب قالب دیگر", callback_data="order_back")],
            [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
        ])
    )
    return UPLOAD_LOGO


async def handle_logo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle logo upload for template."""
    if not update.message.photo:
        await update.message.reply_text(
            "❌ لطفاً یک تصویر ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="order_back")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
        return UPLOAD_LOGO
    
    order = context.user_data.get('order', {})
    template = order.get('template', {})
    
    # Get photo file
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    if file.file_path.startswith("https://"):
        logo_url = file.file_path
    else:
        bot_token = context.bot.token
        logo_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    order['logo_url'] = logo_url
    
    # Apply logo to template
    await update.message.reply_text("⏳ در حال پردازش تصویر...")
    
    result = await api_client.apply_logo_to_template(template['id'], logo_url)
    
    if result:
        order['preview_url'] = result.get('preview_url')
        order['final_url'] = result.get('final_url')
        
        # Show preview
        try:
            await update.message.reply_photo(
                photo=result['preview_url'],
                caption="🖼️ پیش‌نمایش طرح شما\n\n"
                        "آیا این طرح را تایید می‌کنید؟",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ تایید و ادامه", callback_data="confirm_design")],
                    [InlineKeyboardButton("🔄 تغییر لوگو", callback_data="change_logo")],
                    [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
                ])
            )
        except Exception as e:
            logger.error(f"Error sending preview: {e}")
            await update.message.reply_text(
                f"پیش‌نمایش: {result['preview_url']}\n\n"
                "آیا این طرح را تایید می‌کنید؟",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ تایید و ادامه", callback_data="confirm_design")],
                    [InlineKeyboardButton("🔄 تغییر لوگو", callback_data="change_logo")],
                    [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
                ])
            )
    else:
        await update.message.reply_text(
            "❌ خطا در پردازش تصویر. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="retry_logo")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
    
    return UPLOAD_LOGO


async def confirm_design(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm the design and proceed to summary."""
    query = update.callback_query
    await query.answer()
    
    return await show_order_summary(update, context)


async def show_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show next questionnaire question."""
    query = update.callback_query
    order = context.user_data.get('order', {})
    questions = order.get('pending_questions', [])
    index = order.get('current_question_index', 0)
    
    if index >= len(questions):
        # All questions answered, go to summary
        return await show_order_summary(update, context)
    
    question = questions[index]
    order['current_question'] = question
    
    question_text = question.get('question_fa', 'سوال')
    input_type = question.get('input_type', 'TEXT')
    options = question.get('options', [])
    
    if input_type in ['SINGLE_CHOICE', 'MULTI_CHOICE']:
        await query.message.edit_text(
            f"📝 سوال {index + 1} از {len(questions)}\n\n"
            f"{question_text}",
            reply_markup=get_question_options_keyboard(options, question['id'], input_type == 'MULTI_CHOICE')
        )
    elif input_type == 'IMAGE_UPLOAD':
        await query.message.edit_text(
            f"📝 سوال {index + 1} از {len(questions)}\n\n"
            f"{question_text}\n\n"
            "لطفاً یک تصویر ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭️ رد کردن", callback_data="skip_question")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
    else:  # TEXT or COLOR_PICKER
        placeholder = question.get('placeholder_fa', '')
        await query.message.edit_text(
            f"📝 سوال {index + 1} از {len(questions)}\n\n"
            f"{question_text}\n\n"
            f"{'(' + placeholder + ')' if placeholder else ''}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭️ رد کردن", callback_data="skip_question")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
    
    return QUESTIONNAIRE


async def handle_question_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle question option selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "skip_question":
        return await move_to_next_question(update, context)
    
    if query.data == "qopt_done":
        return await move_to_next_question(update, context)
    
    option_id = query.data.replace("qopt_", "")
    order = context.user_data.get('order', {})
    question = order.get('current_question', {})
    
    # Find selected option
    for opt in question.get('options', []):
        if opt['id'] == option_id:
            order['answers'].append({
                'question_id': question['id'],
                'answer_text': opt.get('label_fa'),
                'answer_values': [opt.get('value')],
            })
            break
    
    return await move_to_next_question(update, context)


async def handle_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text/image answer for question."""
    order = context.user_data.get('order', {})
    question = order.get('current_question', {})
    input_type = question.get('input_type', 'TEXT')
    
    if input_type == 'IMAGE_UPLOAD' and update.message.photo:
        # Handle image upload
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        if file.file_path.startswith("https://"):
            file_url = file.file_path
        else:
            bot_token = context.bot.token
            file_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
        
        order['answers'].append({
            'question_id': question['id'],
            'answer_file_url': file_url,
        })
    else:
        # Text answer
        text = update.message.text.strip()
        order['answers'].append({
            'question_id': question['id'],
            'answer_text': text,
        })
    
    # Create fake query for next question
    class FakeQuery:
        message = update.message
        async def answer(self): pass
    
    fake_update = type('Update', (), {'callback_query': FakeQuery()})()
    
    return await move_to_next_question(fake_update, context)


async def move_to_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Move to the next question."""
    order = context.user_data.get('order', {})
    order['current_question_index'] = order.get('current_question_index', 0) + 1
    
    return await show_next_question(update, context)


async def show_order_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show order summary before confirmation."""
    query = update.callback_query
    order = context.user_data.get('order', {})
    category = order.get('category', {})
    plan = order.get('plan', {})
    
    # Build summary text
    summary = f"📋 خلاصه سفارش:\n\n"
    summary += f"📂 دسته: {category.get('name_fa', '')}\n"
    
    # Attributes
    for slug, attr_data in order.get('attributes', {}).items():
        summary += f"• {slug}: {attr_data.get('label', attr_data.get('value', ''))}\n"
    
    summary += f"\n🎯 پلن: {plan.get('name_fa', '')}\n"
    
    # Template
    if order.get('template'):
        summary += f"🖼️ قالب: {order['template'].get('name_fa', '')}\n"
    
    # Price
    total_price = order.get('total_price', 0)
    summary += f"\n💰 جمع کل: {total_price:,} تومان\n"
    
    if query.message.photo:
        await query.message.reply_text(
            summary,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید و پرداخت", callback_data="confirm_order")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
    else:
        await query.message.edit_text(
            summary,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید و پرداخت", callback_data="confirm_order")],
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
    
    return ORDER_SUMMARY


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm order and proceed to payment."""
    query = update.callback_query
    await query.answer()
    
    order = context.user_data.get('order', {})
    user_id = context.user_data.get('user_id', '')
    
    # Create order in backend
    order_data = {
        'category_id': order.get('category_id'),
        'plan_id': order.get('plan_id'),
        'template_id': order.get('template', {}).get('id'),
        'attributes': order.get('attributes'),
        'answers': order.get('answers'),
        'design_file_url': order.get('final_url'),
        'total_price': order.get('total_price', 0),
    }
    
    result = await api_client.create_order(user_id, order_data)
    
    if result:
        order['order_id'] = result.get('id')
        
        # Get payment card info
        card_info = await api_client.get_payment_card()
        
        if not card_info:
            is_admin = context.user_data.get('is_admin', False)
            await query.message.edit_text(
                "❌ اطلاعات کارت بانکی تنظیم نشده است.\n"
                "لطفاً با پشتیبانی تماس بگیرید.",
                reply_markup=get_main_menu_keyboard(is_admin=is_admin)
            )
            return ConversationHandler.END
        
        card_number = card_info.get('card_number', '').replace('-', '')
        card_holder = card_info.get('card_holder', '')
        total = order.get('total_price', 0)
        
        await query.message.edit_text(
            f"💳 پرداخت کارت به کارت\n\n"
            f"مبلغ: {total:,} تومان\n\n"
            f"شماره کارت:\n`{card_number}`\n\n"
            f"به نام: {card_holder}\n\n"
            "⚠️ پس از واریز، عکس رسید را ارسال کنید.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
        return AWAITING_RECEIPT
    else:
        await query.message.edit_text(
            "❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def handle_receipt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle receipt image upload."""
    if not update.message.photo:
        await update.message.reply_text(
            "❌ لطفاً عکس رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
            ])
        )
        return AWAITING_RECEIPT
    
    order = context.user_data.get('order', {})
    user_id = context.user_data.get('user_id', '')
    
    # Get photo URL
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    if file.file_path.startswith("https://"):
        receipt_url = file.file_path
    else:
        bot_token = context.bot.token
        receipt_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    # Initiate payment
    payment = await api_client.initiate_payment(
        user_id=user_id,
        order_id=order.get('order_id'),
        payment_type='PRINT',
        callback_url='',
    )
    
    if payment:
        # Upload receipt
        result = await api_client.upload_receipt(
            payment_id=payment.get('id'),
            user_id=user_id,
            receipt_image_url=receipt_url,
        )
        
        if result:
            is_admin = context.user_data.get('is_admin', False)
            await update.message.reply_text(
                "✅ رسید با موفقیت ارسال شد!\n\n"
                "سفارش شما در انتظار تایید پرداخت است.\n"
                "پس از تایید، سفارش شما پردازش می‌شود.",
                reply_markup=get_main_menu_keyboard(is_admin=is_admin)
            )
            
            # Clear order data
            context.user_data.pop('order', None)
            
            return ConversationHandler.END
    
    await update.message.reply_text(
        "❌ خطا در ارسال رسید. لطفاً دوباره تلاش کنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="retry_receipt")],
            [InlineKeyboardButton("❌ انصراف", callback_data="order_cancel")],
        ])
    )
    return AWAITING_RECEIPT


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the order process."""
    query = update.callback_query
    await query.answer()
    
    # Clear order data
    context.user_data.pop('order', None)
    
    is_admin = context.user_data.get('is_admin', False)
    await query.message.edit_text(
        "❌ سفارش لغو شد.",
    )
    
    return ConversationHandler.END


# ==================== Conversation Handler ====================

dynamic_order_conversation = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^(🛒 ثبت سفارش|ثبت سفارش)$"), start_dynamic_order),
        CallbackQueryHandler(start_dynamic_order, pattern="^start_order$"),
    ],
    states={
        SELECT_CATEGORY: [
            CallbackQueryHandler(select_category, pattern="^order_cat_"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        SELECT_ATTRIBUTE: [
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        SELECT_ATTRIBUTE_OPTION: [
            CallbackQueryHandler(handle_option_selection, pattern="^opt_"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        ENTER_ATTRIBUTE_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_attribute_value),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        SELECT_PLAN: [
            CallbackQueryHandler(handle_plan_selection, pattern="^plan_"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        SELECT_TEMPLATE: [
            CallbackQueryHandler(handle_template_selection, pattern="^template_"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        UPLOAD_LOGO: [
            MessageHandler(filters.PHOTO, handle_logo_upload),
            CallbackQueryHandler(confirm_design, pattern="^confirm_design$"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        QUESTIONNAIRE: [
            CallbackQueryHandler(handle_question_option, pattern="^qopt_"),
            CallbackQueryHandler(move_to_next_question, pattern="^skip_question$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question_text),
            MessageHandler(filters.PHOTO, handle_question_text),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        ORDER_SUMMARY: [
            CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
        AWAITING_RECEIPT: [
            MessageHandler(filters.PHOTO, handle_receipt_upload),
            CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_order, pattern="^order_cancel$"),
    ],
    name="dynamic_order_conversation",
    persistent=False,
)

