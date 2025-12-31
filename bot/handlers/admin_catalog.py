"""Admin handlers for managing categories, attributes, plans, questions, and templates."""

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
    CATALOG_MENU,
    CATEGORY_LIST,
    CATEGORY_ACTIONS,
    CATEGORY_CREATE_NAME,
    CATEGORY_CREATE_SLUG,
    CATEGORY_CREATE_ICON,
    ATTRIBUTE_LIST,
    ATTRIBUTE_ACTIONS,
    ATTRIBUTE_CREATE_NAME,
    ATTRIBUTE_CREATE_SLUG,
    ATTRIBUTE_CREATE_TYPE,
    OPTION_LIST,
    OPTION_CREATE_LABEL,
    OPTION_CREATE_VALUE,
    OPTION_CREATE_PRICE,
    PLAN_LIST,
    PLAN_ACTIONS,
    PLAN_CREATE_NAME,
    PLAN_CREATE_SLUG,
    PLAN_CREATE_PRICE,
    PLAN_CREATE_TYPE,
    QUESTION_LIST,
    QUESTION_ACTIONS,
    QUESTION_CREATE_TEXT,
    QUESTION_CREATE_TYPE,
    QUESTION_OPTION_LIST,
    QUESTION_OPTION_CREATE,
    TEMPLATE_LIST,
    TEMPLATE_ACTIONS,
    TEMPLATE_CREATE_NAME,
    TEMPLATE_UPLOAD_PREVIEW,
    TEMPLATE_SET_PLACEHOLDER,
) = range(32)


def get_catalog_menu_keyboard():
    """Get the catalog management menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📂 مدیریت دسته‌بندی‌ها", callback_data="catalog_categories")],
        [InlineKeyboardButton("🔙 بازگشت به پنل مدیریت", callback_data="admin_panel_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_category_list_keyboard(categories: list):
    """Get keyboard with list of categories."""
    keyboard = []
    for cat in categories:
        icon = cat.get('icon', '📁')
        name = cat.get('name_fa', 'بدون نام')
        keyboard.append([
            InlineKeyboardButton(f"{icon} {name}", callback_data=f"cat_{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ دسته جدید", callback_data="cat_create")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="catalog_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_category_actions_keyboard(category_id: str):
    """Get actions keyboard for a category."""
    keyboard = [
        [InlineKeyboardButton("📋 ویژگی‌ها", callback_data=f"cat_attrs_{category_id}")],
        [InlineKeyboardButton("🎯 پلن‌های طراحی", callback_data=f"cat_plans_{category_id}")],
        [InlineKeyboardButton("✏️ ویرایش", callback_data=f"cat_edit_{category_id}")],
        [InlineKeyboardButton("🗑️ حذف", callback_data=f"cat_delete_{category_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="catalog_categories")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_attribute_list_keyboard(attributes: list, category_id: str):
    """Get keyboard with list of attributes."""
    keyboard = []
    for attr in attributes:
        name = attr.get('name_fa', 'بدون نام')
        input_type = attr.get('input_type', '')
        keyboard.append([
            InlineKeyboardButton(f"📋 {name} ({input_type})", callback_data=f"attr_{attr['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ ویژگی جدید", callback_data=f"attr_create_{category_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_{category_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_attribute_actions_keyboard(attribute_id: str, category_id: str):
    """Get actions keyboard for an attribute."""
    keyboard = [
        [InlineKeyboardButton("🎨 گزینه‌ها", callback_data=f"attr_opts_{attribute_id}")],
        [InlineKeyboardButton("✏️ ویرایش", callback_data=f"attr_edit_{attribute_id}")],
        [InlineKeyboardButton("🗑️ حذف", callback_data=f"attr_delete_{attribute_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_attrs_{category_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_option_list_keyboard(options: list, attribute_id: str):
    """Get keyboard with list of attribute options."""
    keyboard = []
    for opt in options:
        label = opt.get('label_fa', 'بدون نام')
        price = int(float(opt.get('price_modifier', 0)))
        price_str = f"+{price:,}" if price > 0 else "رایگان"
        keyboard.append([
            InlineKeyboardButton(f"• {label} ({price_str})", callback_data=f"opt_{opt['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ گزینه جدید", callback_data=f"opt_create_{attribute_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"attr_{attribute_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_plan_list_keyboard(plans: list, category_id: str):
    """Get keyboard with list of design plans."""
    keyboard = []
    for plan in plans:
        name = plan.get('name_fa', 'بدون نام')
        price = int(float(plan.get('price', 0)))
        price_str = f"{price:,} تومان" if price > 0 else "رایگان"
        keyboard.append([
            InlineKeyboardButton(f"🎯 {name} ({price_str})", callback_data=f"plan_{plan['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ پلن جدید", callback_data=f"plan_create_{category_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_{category_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_plan_actions_keyboard(plan_id: str, category_id: str, has_questionnaire: bool, has_templates: bool):
    """Get actions keyboard for a design plan."""
    keyboard = []
    if has_questionnaire:
        keyboard.append([InlineKeyboardButton("📝 پرسشنامه", callback_data=f"plan_questions_{plan_id}")])
    if has_templates:
        keyboard.append([InlineKeyboardButton("🖼️ قالب‌ها", callback_data=f"plan_templates_{plan_id}")])
    keyboard.append([InlineKeyboardButton("✏️ ویرایش", callback_data=f"plan_edit_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🗑️ حذف", callback_data=f"plan_delete_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_plans_{category_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_question_list_keyboard(questions: list, plan_id: str):
    """Get keyboard with list of questions."""
    keyboard = []
    for i, q in enumerate(questions, 1):
        text = q.get('question_fa', 'بدون متن')[:30]
        input_type = q.get('input_type', '')
        keyboard.append([
            InlineKeyboardButton(f"{i}. {text}... ({input_type})", callback_data=f"question_{q['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ سوال جدید", callback_data=f"question_create_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"plan_{plan_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_template_list_keyboard(templates: list, plan_id: str):
    """Get keyboard with list of templates."""
    keyboard = []
    for t in templates:
        name = t.get('name_fa', 'بدون نام')
        keyboard.append([
            InlineKeyboardButton(f"🖼️ {name}", callback_data=f"template_{t['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ قالب جدید", callback_data=f"template_create_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"plan_{plan_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_input_type_keyboard():
    """Get keyboard for selecting attribute input type."""
    keyboard = [
        [InlineKeyboardButton("انتخابی", callback_data="input_SELECT")],
        [InlineKeyboardButton("چندگانه", callback_data="input_MULTI_SELECT")],
        [InlineKeyboardButton("عددی", callback_data="input_NUMBER")],
        [InlineKeyboardButton("متنی", callback_data="input_TEXT")],
        [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_question_type_keyboard():
    """Get keyboard for selecting question input type."""
    keyboard = [
        [InlineKeyboardButton("متنی", callback_data="qtype_TEXT")],
        [InlineKeyboardButton("تک‌گزینه‌ای", callback_data="qtype_SINGLE_CHOICE")],
        [InlineKeyboardButton("چندگزینه‌ای", callback_data="qtype_MULTI_CHOICE")],
        [InlineKeyboardButton("آپلود عکس", callback_data="qtype_IMAGE_UPLOAD")],
        [InlineKeyboardButton("انتخاب رنگ", callback_data="qtype_COLOR_PICKER")],
        [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_plan_type_keyboard():
    """Get keyboard for selecting plan type."""
    keyboard = [
        [InlineKeyboardButton("عمومی (با قالب)", callback_data="ptype_public")],
        [InlineKeyboardButton("نیمه‌خصوصی (با پرسشنامه)", callback_data="ptype_semi_private")],
        [InlineKeyboardButton("خصوصی (طراحی سفارشی)", callback_data="ptype_private")],
        [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Entry Points ====================

async def show_catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show catalog management menu."""
    user = update.effective_user
    query = update.callback_query
    
    # Check admin permission via API
    user_data = await api_client.get_user(user.id)
    if not user_data or user_data.get('role') != 'ADMIN':
        if query:
            await query.answer("شما به این بخش دسترسی ندارید", show_alert=True)
        else:
            await update.message.reply_text("❌ شما به این بخش دسترسی ندارید.")
        return ConversationHandler.END
    
    menu_text = (
        "🛠️ مدیریت کاتالوگ محصولات\n\n"
        "از این بخش می‌توانید:\n"
        "• دسته‌بندی‌های محصول را مدیریت کنید\n"
        "• ویژگی‌ها و گزینه‌ها را تعریف کنید\n"
        "• پلن‌های طراحی، پرسشنامه و قالب‌ها را مدیریت کنید"
    )
    
    if query:
        await query.answer()
        await query.message.edit_text(menu_text, reply_markup=get_catalog_menu_keyboard())
    else:
        await update.message.reply_text(menu_text, reply_markup=get_catalog_menu_keyboard())
    return CATALOG_MENU


# ==================== Category Handlers ====================

async def show_category_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of categories."""
    query = update.callback_query
    await query.answer()
    
    categories = await api_client.get_categories(active_only=False)
    if categories is None:
        await query.message.edit_text("❌ خطا در دریافت دسته‌بندی‌ها.")
        return CATALOG_MENU
    
    if not categories:
        await query.message.edit_text(
            "📂 هنوز هیچ دسته‌بندی تعریف نشده است.\n\n"
            "برای شروع، یک دسته‌بندی جدید ایجاد کنید.",
            reply_markup=get_category_list_keyboard([])
        )
    else:
        await query.message.edit_text(
            "📂 لیست دسته‌بندی‌ها:\n\n"
            "یک دسته را انتخاب کنید یا دسته جدید بسازید:",
            reply_markup=get_category_list_keyboard(categories)
        )
    return CATEGORY_LIST


async def show_category_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show actions for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_", "")
    context.user_data['current_category_id'] = category_id
    
    category = await api_client.get_category(category_id)
    if not category:
        await query.message.edit_text("❌ دسته‌بندی یافت نشد.")
        return CATEGORY_LIST
    
    icon = category.get('icon', '📁')
    name = category.get('name_fa', 'بدون نام')
    slug = category.get('slug', '')
    is_active = "✅ فعال" if category.get('is_active') else "❌ غیرفعال"
    
    await query.message.edit_text(
        f"{icon} {name}\n\n"
        f"📌 شناسه: {slug}\n"
        f"📊 وضعیت: {is_active}\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_category_actions_keyboard(category_id)
    )
    return CATEGORY_ACTIONS


async def start_category_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start category creation process."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['creating_category'] = {}
    
    await query.message.edit_text(
        "➕ ایجاد دسته‌بندی جدید\n\n"
        "لطفاً نام فارسی دسته‌بندی را وارد کنید:\n"
        "(مثال: لیبل، فاکتور، کارت ویزیت)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return CATEGORY_CREATE_NAME


async def category_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category name input."""
    name = update.message.text.strip()
    context.user_data['creating_category']['name_fa'] = name
    
    await update.message.reply_text(
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی و خط تیره، مثال: label)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return CATEGORY_CREATE_SLUG


async def category_create_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category slug input."""
    slug = update.message.text.strip().lower()
    # Simple validation
    if not slug.replace('-', '').replace('_', '').isalnum():
        await update.message.reply_text(
            "❌ شناسه نامعتبر است. فقط از حروف انگلیسی، اعداد و خط تیره استفاده کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
            ])
        )
        return CATEGORY_CREATE_SLUG
    
    context.user_data['creating_category']['slug'] = slug
    
    await update.message.reply_text(
        f"✅ شناسه: {slug}\n\n"
        "حالا یک ایموجی برای آیکون دسته وارد کنید:\n"
        "(مثال: 🏷️ برای لیبل، 📄 برای فاکتور)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return CATEGORY_CREATE_ICON


async def category_create_icon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category icon input and create category."""
    icon = update.message.text.strip()[:10]  # Limit icon length
    data = context.user_data.get('creating_category', {})
    data['icon'] = icon
    
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_category(admin_id, data)
    
    if result:
        await update.message.reply_text(
            f"✅ دسته‌بندی «{data['name_fa']}» با موفقیت ایجاد شد!\n\n"
            "اکنون می‌توانید ویژگی‌ها و پلن‌های طراحی را برای این دسته تعریف کنید.",
            reply_markup=get_category_actions_keyboard(result['id'])
        )
        context.user_data['current_category_id'] = result['id']
        return CATEGORY_ACTIONS
    else:
        await update.message.reply_text(
            "❌ خطا در ایجاد دسته‌بندی. لطفاً دوباره تلاش کنید.",
            reply_markup=get_category_list_keyboard([])
        )
        return CATEGORY_LIST


async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_delete_", "")
    admin_id = context.user_data.get('user_id', '')
    
    success = await api_client.delete_category(category_id, admin_id)
    
    if success:
        await query.message.edit_text("✅ دسته‌بندی با موفقیت حذف شد.")
    else:
        await query.message.edit_text("❌ خطا در حذف دسته‌بندی.")
    
    # Return to category list
    return await show_category_list(update, context)


# ==================== Attribute Handlers ====================

async def show_attribute_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of attributes for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_attrs_", "")
    context.user_data['current_category_id'] = category_id
    
    attributes = await api_client.get_attributes(category_id, active_only=False)
    if attributes is None:
        await query.message.edit_text("❌ خطا در دریافت ویژگی‌ها.")
        return CATEGORY_ACTIONS
    
    category = await api_client.get_category(category_id)
    cat_name = category.get('name_fa', '') if category else ''
    
    await query.message.edit_text(
        f"📋 ویژگی‌های دسته «{cat_name}»:\n\n"
        "یک ویژگی را انتخاب کنید یا ویژگی جدید بسازید:",
        reply_markup=get_attribute_list_keyboard(attributes, category_id)
    )
    return ATTRIBUTE_LIST


async def show_attribute_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show actions for an attribute."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("attr_", "")
    context.user_data['current_attribute_id'] = attribute_id
    
    # Get attribute details
    # Note: We need to fetch the attribute. For now, we'll use the category context.
    category_id = context.user_data.get('current_category_id', '')
    
    await query.message.edit_text(
        "📋 مدیریت ویژگی\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_attribute_actions_keyboard(attribute_id, category_id)
    )
    return ATTRIBUTE_ACTIONS


async def start_attribute_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start attribute creation process."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("attr_create_", "")
    context.user_data['current_category_id'] = category_id
    context.user_data['creating_attribute'] = {'category_id': category_id}
    
    await query.message.edit_text(
        "➕ ایجاد ویژگی جدید\n\n"
        "لطفاً نام فارسی ویژگی را وارد کنید:\n"
        "(مثال: سایز، جنس، تعداد)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return ATTRIBUTE_CREATE_NAME


async def attribute_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attribute name input."""
    name = update.message.text.strip()
    context.user_data['creating_attribute']['name_fa'] = name
    
    await update.message.reply_text(
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی، مثال: size)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return ATTRIBUTE_CREATE_SLUG


async def attribute_create_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attribute slug input."""
    slug = update.message.text.strip().lower()
    context.user_data['creating_attribute']['slug'] = slug
    
    await update.message.reply_text(
        f"✅ شناسه: {slug}\n\n"
        "نوع ورودی را انتخاب کنید:",
        reply_markup=get_input_type_keyboard()
    )
    return ATTRIBUTE_CREATE_TYPE


async def attribute_create_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle attribute input type selection and create attribute."""
    query = update.callback_query
    await query.answer()
    
    input_type = query.data.replace("input_", "")
    data = context.user_data.get('creating_attribute', {})
    data['input_type'] = input_type
    
    category_id = data.pop('category_id', context.user_data.get('current_category_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_attribute(category_id, admin_id, data)
    
    if result:
        await query.message.edit_text(
            f"✅ ویژگی «{data['name_fa']}» با موفقیت ایجاد شد!\n\n"
            "اکنون می‌توانید گزینه‌هایی برای این ویژگی تعریف کنید.",
            reply_markup=get_attribute_actions_keyboard(result['id'], category_id)
        )
        context.user_data['current_attribute_id'] = result['id']
        return ATTRIBUTE_ACTIONS
    else:
        await query.message.edit_text("❌ خطا در ایجاد ویژگی.")
        return ATTRIBUTE_LIST


# ==================== Option Handlers ====================

async def show_option_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of options for an attribute."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("attr_opts_", "")
    context.user_data['current_attribute_id'] = attribute_id
    
    # Get attribute with options
    category_id = context.user_data.get('current_category_id', '')
    attributes = await api_client.get_attributes(category_id, active_only=False)
    
    options = []
    for attr in (attributes or []):
        if attr['id'] == attribute_id:
            options = attr.get('options', [])
            break
    
    await query.message.edit_text(
        "🎨 گزینه‌های ویژگی:\n\n"
        "یک گزینه را انتخاب کنید یا گزینه جدید بسازید:",
        reply_markup=get_option_list_keyboard(options, attribute_id)
    )
    return OPTION_LIST


async def start_option_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start option creation process."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("opt_create_", "")
    context.user_data['current_attribute_id'] = attribute_id
    context.user_data['creating_option'] = {'attribute_id': attribute_id}
    
    await query.message.edit_text(
        "➕ ایجاد گزینه جدید\n\n"
        "لطفاً نام فارسی گزینه را وارد کنید:\n"
        "(مثال: 5x5 سانتی‌متر، کاغذی)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return OPTION_CREATE_LABEL


async def option_create_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle option label input."""
    label = update.message.text.strip()
    context.user_data['creating_option']['label_fa'] = label
    
    await update.message.reply_text(
        f"✅ نام: {label}\n\n"
        "حالا مقدار انگلیسی (value) را وارد کنید:\n"
        "(این مقدار در سیستم ذخیره می‌شود، مثال: 5x5)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return OPTION_CREATE_VALUE


async def option_create_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle option value input."""
    value = update.message.text.strip()
    context.user_data['creating_option']['value'] = value
    
    await update.message.reply_text(
        f"✅ مقدار: {value}\n\n"
        "مبلغ اضافه قیمت را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return OPTION_CREATE_PRICE


async def option_create_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle option price input and create option."""
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")
        return OPTION_CREATE_PRICE
    
    data = context.user_data.get('creating_option', {})
    data['price_modifier'] = price
    
    attribute_id = data.pop('attribute_id', context.user_data.get('current_attribute_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_attribute_option(attribute_id, admin_id, data)
    
    if result:
        await update.message.reply_text(
            f"✅ گزینه «{data['label_fa']}» با موفقیت ایجاد شد!"
        )
        # Return to option list
        context.user_data['current_attribute_id'] = attribute_id
        # We need to trigger show_option_list
        return OPTION_LIST
    else:
        await update.message.reply_text("❌ خطا در ایجاد گزینه.")
        return OPTION_LIST


# ==================== Plan Handlers ====================

async def show_plan_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of design plans for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_plans_", "")
    context.user_data['current_category_id'] = category_id
    
    plans = await api_client.get_design_plans(category_id, active_only=False)
    if plans is None:
        await query.message.edit_text("❌ خطا در دریافت پلن‌ها.")
        return CATEGORY_ACTIONS
    
    category = await api_client.get_category(category_id)
    cat_name = category.get('name_fa', '') if category else ''
    
    await query.message.edit_text(
        f"🎯 پلن‌های طراحی دسته «{cat_name}»:\n\n"
        "یک پلن را انتخاب کنید یا پلن جدید بسازید:",
        reply_markup=get_plan_list_keyboard(plans, category_id)
    )
    return PLAN_LIST


async def show_plan_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show actions for a design plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_", "")
    context.user_data['current_plan_id'] = plan_id
    
    plan = await api_client.get_design_plan(plan_id)
    if not plan:
        await query.message.edit_text("❌ پلن یافت نشد.")
        return PLAN_LIST
    
    name = plan.get('name_fa', 'بدون نام')
    price = int(float(plan.get('price', 0)))
    price_str = f"{price:,} تومان" if price > 0 else "رایگان"
    has_questionnaire = plan.get('has_questionnaire', False)
    has_templates = plan.get('has_templates', False)
    
    type_str = []
    if has_questionnaire:
        type_str.append("📝 پرسشنامه")
    if has_templates:
        type_str.append("🖼️ قالب")
    if plan.get('has_file_upload'):
        type_str.append("📤 آپلود فایل")
    
    category_id = context.user_data.get('current_category_id', '')
    
    await query.message.edit_text(
        f"🎯 {name}\n\n"
        f"💰 قیمت: {price_str}\n"
        f"📊 نوع: {', '.join(type_str) if type_str else 'ساده'}\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_plan_actions_keyboard(plan_id, category_id, has_questionnaire, has_templates)
    )
    return PLAN_ACTIONS


async def start_plan_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start plan creation process."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("plan_create_", "")
    context.user_data['current_category_id'] = category_id
    context.user_data['creating_plan'] = {'category_id': category_id}
    
    await query.message.edit_text(
        "➕ ایجاد پلن طراحی جدید\n\n"
        "لطفاً نام فارسی پلن را وارد کنید:\n"
        "(مثال: عمومی، نیمه‌خصوصی، خصوصی)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return PLAN_CREATE_NAME


async def plan_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan name input."""
    name = update.message.text.strip()
    context.user_data['creating_plan']['name_fa'] = name
    
    await update.message.reply_text(
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(مثال: public, semi_private, private)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return PLAN_CREATE_SLUG


async def plan_create_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan slug input."""
    slug = update.message.text.strip().lower()
    context.user_data['creating_plan']['slug'] = slug
    
    await update.message.reply_text(
        f"✅ شناسه: {slug}\n\n"
        "قیمت طراحی را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return PLAN_CREATE_PRICE


async def plan_create_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan price input."""
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")
        return PLAN_CREATE_PRICE
    
    context.user_data['creating_plan']['price'] = price
    
    await update.message.reply_text(
        f"✅ قیمت: {price:,} تومان\n\n"
        "نوع پلن را انتخاب کنید:",
        reply_markup=get_plan_type_keyboard()
    )
    return PLAN_CREATE_TYPE


async def plan_create_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan type selection and create plan."""
    query = update.callback_query
    await query.answer()
    
    plan_type = query.data.replace("ptype_", "")
    data = context.user_data.get('creating_plan', {})
    
    # Set plan type flags
    if plan_type == "public":
        data['has_templates'] = True
        data['has_questionnaire'] = False
    elif plan_type == "semi_private":
        data['has_questionnaire'] = True
        data['has_templates'] = False
    else:  # private
        data['has_questionnaire'] = False
        data['has_templates'] = False
        data['has_file_upload'] = True
    
    category_id = data.pop('category_id', context.user_data.get('current_category_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_design_plan(category_id, admin_id, data)
    
    if result:
        msg = f"✅ پلن «{data['name_fa']}» با موفقیت ایجاد شد!\n\n"
        if result.get('has_questionnaire'):
            msg += "اکنون می‌توانید پرسشنامه را برای این پلن تعریف کنید."
        elif result.get('has_templates'):
            msg += "اکنون می‌توانید قالب‌ها را برای این پلن آپلود کنید."
        
        await query.message.edit_text(
            msg,
            reply_markup=get_plan_actions_keyboard(
                result['id'],
                category_id,
                result.get('has_questionnaire', False),
                result.get('has_templates', False)
            )
        )
        context.user_data['current_plan_id'] = result['id']
        return PLAN_ACTIONS
    else:
        await query.message.edit_text("❌ خطا در ایجاد پلن.")
        return PLAN_LIST


# ==================== Question Handlers ====================

async def show_question_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of questions for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_questions_", "")
    context.user_data['current_plan_id'] = plan_id
    
    questions = await api_client.get_questions(plan_id, active_only=False)
    if questions is None:
        await query.message.edit_text("❌ خطا در دریافت سوالات.")
        return PLAN_ACTIONS
    
    await query.message.edit_text(
        "📝 سوالات پرسشنامه:\n\n"
        "یک سوال را انتخاب کنید یا سوال جدید بسازید:",
        reply_markup=get_question_list_keyboard(questions, plan_id)
    )
    return QUESTION_LIST


async def start_question_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start question creation process."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("question_create_", "")
    context.user_data['current_plan_id'] = plan_id
    context.user_data['creating_question'] = {'plan_id': plan_id}
    
    await query.message.edit_text(
        "➕ ایجاد سوال جدید\n\n"
        "متن سوال را به فارسی وارد کنید:\n"
        "(مثال: کسب‌وکار شما چیست؟)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return QUESTION_CREATE_TEXT


async def question_create_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle question text input."""
    text = update.message.text.strip()
    context.user_data['creating_question']['question_fa'] = text
    
    await update.message.reply_text(
        f"✅ سوال: {text}\n\n"
        "نوع پاسخ را انتخاب کنید:",
        reply_markup=get_question_type_keyboard()
    )
    return QUESTION_CREATE_TYPE


async def question_create_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle question type selection and create question."""
    query = update.callback_query
    await query.answer()
    
    question_type = query.data.replace("qtype_", "")
    data = context.user_data.get('creating_question', {})
    data['input_type'] = question_type
    
    plan_id = data.pop('plan_id', context.user_data.get('current_plan_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_question(plan_id, admin_id, data)
    
    if result:
        msg = f"✅ سوال با موفقیت ایجاد شد!\n\n"
        if question_type in ['SINGLE_CHOICE', 'MULTI_CHOICE']:
            msg += "اکنون می‌توانید گزینه‌های پاسخ را اضافه کنید."
        
        await query.message.edit_text(msg)
        # Return to question list
        return QUESTION_LIST
    else:
        await query.message.edit_text("❌ خطا در ایجاد سوال.")
        return QUESTION_LIST


# ==================== Template Handlers ====================

async def show_template_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show list of templates for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_templates_", "")
    context.user_data['current_plan_id'] = plan_id
    
    templates = await api_client.get_templates(plan_id, active_only=False)
    if templates is None:
        await query.message.edit_text("❌ خطا در دریافت قالب‌ها.")
        return PLAN_ACTIONS
    
    await query.message.edit_text(
        "🖼️ قالب‌های طراحی:\n\n"
        "یک قالب را انتخاب کنید یا قالب جدید آپلود کنید:",
        reply_markup=get_template_list_keyboard(templates, plan_id)
    )
    return TEMPLATE_LIST


async def start_template_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start template creation process."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("template_create_", "")
    context.user_data['current_plan_id'] = plan_id
    context.user_data['creating_template'] = {'plan_id': plan_id}
    
    await query.message.edit_text(
        "➕ ایجاد قالب جدید\n\n"
        "لطفاً نام فارسی قالب را وارد کنید:\n"
        "(مثال: قالب مدرن، قالب کلاسیک)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return TEMPLATE_CREATE_NAME


async def template_create_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle template name input."""
    name = update.message.text.strip()
    context.user_data['creating_template']['name_fa'] = name
    
    await update.message.reply_text(
        f"✅ نام: {name}\n\n"
        "حالا تصویر قالب را با مربع قرمز (placeholder) ارسال کنید:\n\n"
        "⚠️ مربع قرمز نشان‌دهنده جایی است که لوگوی کاربر قرار می‌گیرد.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return TEMPLATE_UPLOAD_PREVIEW


async def template_upload_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle template preview image upload."""
    if not update.message.photo:
        await update.message.reply_text(
            "❌ لطفاً یک تصویر ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
            ])
        )
        return TEMPLATE_UPLOAD_PREVIEW
    
    # Get the largest photo
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # Store file URL
    if file.file_path.startswith("https://"):
        file_url = file.file_path
    else:
        bot_token = context.bot.token
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    context.user_data['creating_template']['preview_url'] = file_url
    context.user_data['creating_template']['file_url'] = file_url
    
    await update.message.reply_text(
        "✅ تصویر دریافت شد!\n\n"
        "حالا مختصات مربع قرمز را وارد کنید:\n"
        "فرمت: x,y,width,height\n"
        "(مثال: 100,50,200,200)\n\n"
        "این مختصات نشان می‌دهد لوگوی کاربر کجا قرار می‌گیرد.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
        ])
    )
    return TEMPLATE_SET_PLACEHOLDER


async def template_set_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle placeholder coordinates and create template."""
    text = update.message.text.strip()
    
    try:
        parts = [int(p.strip()) for p in text.split(',')]
        if len(parts) != 4:
            raise ValueError("Need 4 values")
        x, y, w, h = parts
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ فرمت نادرست. لطفاً 4 عدد با کاما جدا شده وارد کنید:\n"
            "x,y,width,height\n"
            "(مثال: 100,50,200,200)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel_create")]
            ])
        )
        return TEMPLATE_SET_PLACEHOLDER
    
    data = context.user_data.get('creating_template', {})
    data['placeholder_x'] = x
    data['placeholder_y'] = y
    data['placeholder_width'] = w
    data['placeholder_height'] = h
    
    plan_id = data.pop('plan_id', context.user_data.get('current_plan_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_template(plan_id, admin_id, data)
    
    if result:
        await update.message.reply_text(
            f"✅ قالب «{data['name_fa']}» با موفقیت ایجاد شد!\n\n"
            f"📍 مختصات: ({x}, {y}) - {w}x{h}"
        )
        return TEMPLATE_LIST
    else:
        await update.message.reply_text("❌ خطا در ایجاد قالب.")
        return TEMPLATE_LIST


# ==================== Cancel Handler ====================

async def cancel_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel any creation process."""
    query = update.callback_query
    await query.answer()
    
    # Clear any creation data
    context.user_data.pop('creating_category', None)
    context.user_data.pop('creating_attribute', None)
    context.user_data.pop('creating_option', None)
    context.user_data.pop('creating_plan', None)
    context.user_data.pop('creating_question', None)
    context.user_data.pop('creating_template', None)
    
    await query.message.edit_text("❌ عملیات لغو شد.")
    return await show_catalog_menu(update, context)


# ==================== Conversation Handler ====================

catalog_conversation = ConversationHandler(
    entry_points=[
        # Text message entry handled by menu.py which checks admin role via API
        MessageHandler(filters.Regex("مدیریت کاتالوگ"), show_catalog_menu),
        CallbackQueryHandler(show_catalog_menu, pattern="^catalog_menu$"),
        CallbackQueryHandler(show_catalog_menu, pattern="^admin_catalog$"),
    ],
    states={
        CATALOG_MENU: [
            CallbackQueryHandler(show_category_list, pattern="^catalog_categories$"),
            CallbackQueryHandler(cancel_create, pattern="^admin_panel_back$"),
        ],
        CATEGORY_LIST: [
            CallbackQueryHandler(start_category_create, pattern="^cat_create$"),
            CallbackQueryHandler(show_category_actions, pattern="^cat_[a-f0-9-]+$"),
            CallbackQueryHandler(show_catalog_menu, pattern="^catalog_menu$"),
        ],
        CATEGORY_ACTIONS: [
            CallbackQueryHandler(show_attribute_list, pattern="^cat_attrs_"),
            CallbackQueryHandler(show_plan_list, pattern="^cat_plans_"),
            CallbackQueryHandler(delete_category, pattern="^cat_delete_"),
            CallbackQueryHandler(show_category_list, pattern="^catalog_categories$"),
        ],
        CATEGORY_CREATE_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, category_create_name),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        CATEGORY_CREATE_SLUG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, category_create_slug),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        CATEGORY_CREATE_ICON: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, category_create_icon),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        ATTRIBUTE_LIST: [
            CallbackQueryHandler(start_attribute_create, pattern="^attr_create_"),
            CallbackQueryHandler(show_attribute_actions, pattern="^attr_[a-f0-9-]+$"),
            CallbackQueryHandler(show_category_actions, pattern="^cat_"),
        ],
        ATTRIBUTE_ACTIONS: [
            CallbackQueryHandler(show_option_list, pattern="^attr_opts_"),
            CallbackQueryHandler(show_attribute_list, pattern="^cat_attrs_"),
        ],
        ATTRIBUTE_CREATE_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, attribute_create_name),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        ATTRIBUTE_CREATE_SLUG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, attribute_create_slug),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        ATTRIBUTE_CREATE_TYPE: [
            CallbackQueryHandler(attribute_create_type, pattern="^input_"),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        OPTION_LIST: [
            CallbackQueryHandler(start_option_create, pattern="^opt_create_"),
            CallbackQueryHandler(show_attribute_actions, pattern="^attr_"),
        ],
        OPTION_CREATE_LABEL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, option_create_label),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        OPTION_CREATE_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, option_create_value),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        OPTION_CREATE_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, option_create_price),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        PLAN_LIST: [
            CallbackQueryHandler(start_plan_create, pattern="^plan_create_"),
            CallbackQueryHandler(show_plan_actions, pattern="^plan_[a-f0-9-]+$"),
            CallbackQueryHandler(show_category_actions, pattern="^cat_"),
        ],
        PLAN_ACTIONS: [
            CallbackQueryHandler(show_question_list, pattern="^plan_questions_"),
            CallbackQueryHandler(show_template_list, pattern="^plan_templates_"),
            CallbackQueryHandler(show_plan_list, pattern="^cat_plans_"),
        ],
        PLAN_CREATE_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, plan_create_name),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        PLAN_CREATE_SLUG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, plan_create_slug),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        PLAN_CREATE_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, plan_create_price),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        PLAN_CREATE_TYPE: [
            CallbackQueryHandler(plan_create_type, pattern="^ptype_"),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        QUESTION_LIST: [
            CallbackQueryHandler(start_question_create, pattern="^question_create_"),
            CallbackQueryHandler(show_plan_actions, pattern="^plan_"),
        ],
        QUESTION_CREATE_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, question_create_text),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        QUESTION_CREATE_TYPE: [
            CallbackQueryHandler(question_create_type, pattern="^qtype_"),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        TEMPLATE_LIST: [
            CallbackQueryHandler(start_template_create, pattern="^template_create_"),
            CallbackQueryHandler(show_plan_actions, pattern="^plan_"),
        ],
        TEMPLATE_CREATE_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, template_create_name),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        TEMPLATE_UPLOAD_PREVIEW: [
            MessageHandler(filters.PHOTO, template_upload_preview),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
        TEMPLATE_SET_PLACEHOLDER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, template_set_placeholder),
            CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_create, pattern="^cancel_create$"),
    ],
    name="catalog_conversation",
    persistent=False,
)

