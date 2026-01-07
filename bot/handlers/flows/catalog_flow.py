"""Catalog Flow - Admin catalog management handlers.

This module handles all catalog-related operations using the unified flow manager.
All admin messages include breadcrumb navigation for better UX.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.api_client import api_client
from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item, clear_flow_data,
    FLOW_CATALOG, CATALOG_STEPS
)
from utils.breadcrumb import Breadcrumb, BreadcrumbPath, get_breadcrumb, format_admin_message
from keyboards.manager import (
    get_catalog_menu_keyboard, get_category_list_keyboard,
    get_category_actions_keyboard, get_attribute_list_keyboard,
    get_attribute_actions_keyboard, get_option_list_keyboard,
    get_plan_list_keyboard, get_plan_actions_keyboard,
    get_input_type_keyboard, get_plan_type_keyboard,
    get_question_type_keyboard, get_cancel_keyboard,
    get_admin_menu_keyboard
)

logger = logging.getLogger(__name__)


# ============== Helper Functions ==============

def _store_category_name(context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    """Store category name for breadcrumb display."""
    context.user_data['current_category_name'] = name


def _store_plan_name(context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    """Store plan name for breadcrumb display."""
    context.user_data['current_plan_name'] = name


def _store_attribute_name(context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    """Store attribute name for breadcrumb display."""
    context.user_data['current_attribute_name'] = name


def _get_category_name(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get stored category name."""
    return context.user_data.get('current_category_name', '')


def _get_plan_name(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get stored plan name."""
    return context.user_data.get('current_plan_name', '')


def _get_attribute_name(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get stored attribute name."""
    return context.user_data.get('current_attribute_name', '')


# ============== Text Input Handler ==============

async def handle_catalog_text(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    """Handle text input for catalog flow based on current step."""
    
    handlers = {
        'category_create_name': handle_category_name,
        'category_create_slug': handle_category_slug,
        'category_create_icon': handle_category_icon,
        'category_create_price': handle_category_price,
        'attribute_create_name': handle_attribute_name,
        'attribute_create_slug': handle_attribute_slug,
        'option_create_label': handle_option_label,
        'option_create_value': handle_option_value,
        'option_create_price': handle_option_price,
        'plan_create_name': handle_plan_name,
        'plan_create_slug': handle_plan_slug,
        'plan_create_price': handle_plan_price,
        'question_create_text': handle_question_text,
        'question_option_create': handle_question_option_text,
        'template_create_name': handle_template_name,
        'template_set_placeholder': handle_template_placeholder,
    }
    
    handler = handlers.get(step)
    if handler:
        await handler(update, context)
    else:
        logger.warning(f"Unknown catalog step for text: {step}")
        await show_catalog_menu(update, context)


# ============== Menu Handlers ==============

async def show_catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show catalog management menu."""
    user = update.effective_user
    query = update.callback_query
    
    # Check admin permission via API
    user_data = await api_client.get_user(user.id)
    if not user_data or user_data.get('role') != 'ADMIN':
        if query:
            await query.answer("شما به این بخش دسترسی ندارید", show_alert=True)
        else:
            await update.message.reply_text("شما به این بخش دسترسی ندارید.")
        clear_flow(context)
        return
    
    # Set flow state
    set_flow(context, FLOW_CATALOG, 'catalog_menu')
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_MENU)
    
    menu_text = (
        "📂 مدیریت کاتالوگ محصولات\n\n"
        "از این بخش می توانید:\n"
        "• دسته بندی های محصول را مدیریت کنید\n"
        "• ویژگی ها و گزینه ها را تعریف کنید\n"
        "• پلن های طراحی، پرسشنامه و قالب ها را مدیریت کنید"
    )
    
    msg = bc.format_message(menu_text)
    
    if query:
        await query.answer()
        await query.message.edit_text(msg, reply_markup=get_catalog_menu_keyboard())
    else:
        await update.message.reply_text(msg, reply_markup=get_catalog_menu_keyboard())


async def show_category_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of categories."""
    query = update.callback_query
    await query.answer()
    
    set_step(context, 'category_list')
    
    categories = await api_client.get_categories(active_only=False)
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
    
    if categories is None:
        msg = bc.format_message("❌ خطا در دریافت دسته بندی ها.")
        await query.message.edit_text(msg, reply_markup=get_catalog_menu_keyboard())
        return
    
    text = (
        f"📂 دسته بندی ها ({len(categories)} مورد):\n\n"
        "یک دسته را انتخاب کنید یا دسته جدید بسازید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_category_list_keyboard(categories))


async def show_category_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show category details and actions."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_", "")
    update_flow_data(context, 'current_category_id', category_id)
    set_step(context, 'category_actions')
    
    # Get category details
    categories = await api_client.get_categories(active_only=False)
    category = None
    for cat in (categories or []):
        if cat['id'] == category_id:
            category = cat
            break
    
    if not category:
        bc = get_breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
        msg = bc.format_message("❌ دسته بندی یافت نشد.")
        await query.message.edit_text(msg, reply_markup=get_catalog_menu_keyboard())
        return
    
    name = category.get('name_fa', 'بدون نام')
    slug = category.get('slug', '')
    icon = category.get('icon', '')
    price = category.get('base_price', 0)
    is_active = "✅ فعال" if category.get('is_active') else "❌ غیرفعال"
    
    # Store name for breadcrumb
    _store_category_name(context, f"{icon} {name}")
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATEGORY_VIEW, f"{icon} {name}")
    
    text = (
        f"📁 دسته بندی: {icon} {name}\n\n"
        f"🔗 شناسه: {slug}\n"
        f"💰 قیمت پایه: {int(float(price)):,} تومان\n"
        f"📊 وضعیت: {is_active}\n\n"
        "یک عملیات را انتخاب کنید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_category_actions_keyboard(category_id))


# ============== Category Creation ==============

async def start_category_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start category creation process."""
    query = update.callback_query
    await query.answer()
    
    set_step(context, 'category_create_name')
    update_flow_data(context, 'creating_category', {})
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORY_CREATE)
    
    text = (
        "➕ ایجاد دسته بندی جدید\n\n"
        "لطفا نام فارسی دسته بندی را وارد کنید:\n"
        "(مثال: لیبل، فاکتور، کارت ویزیت)"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_cancel_keyboard())


async def handle_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_slug')
    
    # Update breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORY_CREATE)
    bc.push("نام دسته")
    
    text = (
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی و خط تیره، مثال: label)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_category_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category slug input."""
    slug = update.message.text.strip().lower()
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORY_CREATE)
    
    if not slug.replace('-', '').replace('_', '').isalnum():
        bc.push("شناسه")
        msg = bc.format_message(
            "❌ شناسه نامعتبر است.\n"
            "فقط از حروف انگلیسی، اعداد و خط تیره استفاده کنید."
        )
        await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())
        return
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_icon')
    
    bc.push("آیکون")
    text = (
        f"✅ شناسه: {slug}\n\n"
        "حالا یک ایموجی یا نماد برای آیکون دسته وارد کنید:\n"
        "(مثال: 🏷️ یا 📄)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_category_icon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category icon input."""
    icon = update.message.text.strip()[:10]
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['icon'] = icon
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_price')
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORY_CREATE)
    bc.push("قیمت پایه")
    
    text = (
        f"✅ نماد: {icon}\n\n"
        "حالا قیمت پایه را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_category_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category base price input and create category."""
    bc = get_breadcrumb(context)
    
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORY_CREATE)
        bc.push("قیمت پایه")
        msg = bc.format_message("❌ لطفا یک عدد معتبر وارد کنید.")
        await update.message.reply_text(msg)
        return
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['base_price'] = price
    
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_category(admin_id, creating)
    
    if result:
        update_flow_data(context, 'current_category_id', result['id'])
        set_step(context, 'category_actions')
        
        name = creating['name_fa']
        icon = creating.get('icon', '')
        _store_category_name(context, f"{icon} {name}")
        
        bc.set_path(BreadcrumbPath.CATEGORY_VIEW, f"{icon} {name}")
        
        text = (
            f"✅ دسته بندی «{name}» با موفقیت ایجاد شد!\n\n"
            f"💰 قیمت پایه: {price:,} تومان\n\n"
            "اکنون می توانید ویژگی ها و پلن های طراحی را برای این دسته تعریف کنید."
        )
        msg = bc.format_message(text)
        
        await update.message.reply_text(msg, reply_markup=get_category_actions_keyboard(result['id']))
    else:
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
        msg = bc.format_message("❌ خطا در ایجاد دسته بندی. لطفا دوباره تلاش کنید.")
        await update.message.reply_text(msg, reply_markup=get_category_list_keyboard([]))


async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_delete_", "")
    admin_id = context.user_data.get('user_id', '')
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
    
    success = await api_client.delete_category(category_id, admin_id)
    
    if success:
        msg = bc.format_message("✅ دسته بندی با موفقیت حذف شد.")
        await query.message.edit_text(msg)
    else:
        msg = bc.format_message("❌ خطا در حذف دسته بندی.")
        await query.message.edit_text(msg)
    
    # Refresh list
    await show_category_list(update, context)


# ============== Attribute Handlers ==============

async def show_attribute_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of attributes for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_attrs_", "")
    update_flow_data(context, 'current_category_id', category_id)
    set_step(context, 'attribute_list')
    
    attributes = await api_client.get_attributes(category_id, active_only=False)
    
    # Get category name
    categories = await api_client.get_categories(active_only=False)
    cat_name = "نامشخص"
    cat_icon = ""
    for cat in (categories or []):
        if cat['id'] == category_id:
            cat_name = cat.get('name_fa', 'نامشخص')
            cat_icon = cat.get('icon', '')
            break
    
    _store_category_name(context, f"{cat_icon} {cat_name}")
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATEGORY_ATTRIBUTES, f"{cat_icon} {cat_name}", "ویژگی‌ها")
    
    text = (
        f"🔧 ویژگی های دسته «{cat_name}»\n\n"
        f"تعداد: {len(attributes or [])} مورد\n\n"
        "یک ویژگی را انتخاب کنید یا ویژگی جدید بسازید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_attribute_list_keyboard(attributes or [], category_id))


async def start_attribute_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start attribute creation."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("attr_create_", "")
    update_flow_data(context, 'current_category_id', category_id)
    update_flow_data(context, 'creating_attribute', {'category_id': category_id})
    set_step(context, 'attribute_create_name')
    
    cat_name = _get_category_name(context)
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ATTRIBUTE_CREATE, cat_name, "ویژگی‌ها", "➕ ویژگی جدید")
    
    text = (
        "➕ ایجاد ویژگی جدید\n\n"
        "لطفا نام فارسی ویژگی را وارد کنید:\n"
        "(مثال: سایز، جنس، تعداد)"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_cancel_keyboard())


async def handle_attribute_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle attribute name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_attribute', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_attribute', creating)
    set_step(context, 'attribute_create_slug')
    
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ATTRIBUTE_CREATE, cat_name, "ویژگی‌ها", "➕ ویژگی جدید", "نام")
    
    text = (
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی، مثال: size)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_attribute_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle attribute slug input."""
    slug = update.message.text.strip().lower()
    
    creating = get_flow_data_item(context, 'creating_attribute', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_attribute', creating)
    set_step(context, 'attribute_create_type')
    
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ATTRIBUTE_CREATE, cat_name, "ویژگی‌ها", "➕ ویژگی جدید", "نوع ورودی")
    
    text = (
        f"✅ شناسه: {slug}\n\n"
        "نوع ورودی را انتخاب کنید:"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_input_type_keyboard())


async def handle_attribute_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle attribute input type selection and create attribute."""
    query = update.callback_query
    await query.answer()
    
    input_type = query.data.replace("input_", "")
    creating = get_flow_data_item(context, 'creating_attribute', {})
    creating['input_type'] = input_type
    
    category_id = creating.pop('category_id', get_flow_data_item(context, 'current_category_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_attribute(category_id, admin_id, creating)
    
    cat_name = _get_category_name(context)
    bc = get_breadcrumb(context)
    
    if result:
        update_flow_data(context, 'current_attribute_id', result['id'])
        set_step(context, 'attribute_actions')
        
        attr_name = creating['name_fa']
        _store_attribute_name(context, attr_name)
        
        bc.set_path(BreadcrumbPath.ATTRIBUTE_VIEW, cat_name, "ویژگی‌ها", attr_name)
        
        text = (
            f"✅ ویژگی «{attr_name}» با موفقیت ایجاد شد!\n\n"
            "اکنون می توانید گزینه هایی برای این ویژگی تعریف کنید."
        )
        msg = bc.format_message(text)
        
        await query.message.edit_text(msg, reply_markup=get_attribute_actions_keyboard(result['id'], category_id))
    else:
        bc.set_path(BreadcrumbPath.CATEGORY_ATTRIBUTES, cat_name, "ویژگی‌ها")
        msg = bc.format_message("❌ خطا در ایجاد ویژگی.")
        await query.message.edit_text(msg)
        set_step(context, 'attribute_list')


async def show_attribute_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show attribute actions."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("attr_", "")
    update_flow_data(context, 'current_attribute_id', attribute_id)
    set_step(context, 'attribute_actions')
    
    category_id = get_flow_data_item(context, 'current_category_id', '')
    cat_name = _get_category_name(context)
    
    # Get attribute name
    attributes = await api_client.get_attributes(category_id, active_only=False)
    attr_name = "نامشخص"
    for attr in (attributes or []):
        if attr['id'] == attribute_id:
            attr_name = attr.get('name_fa', 'نامشخص')
            break
    
    _store_attribute_name(context, attr_name)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ATTRIBUTE_VIEW, cat_name, "ویژگی‌ها", attr_name)
    
    text = (
        f"🔧 ویژگی: {attr_name}\n\n"
        "یک عملیات را انتخاب کنید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_attribute_actions_keyboard(attribute_id, category_id))


# ============== Option Handlers ==============

async def show_option_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of options for an attribute."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("attr_opts_", "")
    update_flow_data(context, 'current_attribute_id', attribute_id)
    set_step(context, 'option_list')
    
    category_id = get_flow_data_item(context, 'current_category_id', '')
    attributes = await api_client.get_attributes(category_id, active_only=False)
    
    options = []
    attr_name = _get_attribute_name(context)
    for attr in (attributes or []):
        if attr['id'] == attribute_id:
            options = attr.get('options', [])
            attr_name = attr.get('name_fa', attr_name)
            break
    
    _store_attribute_name(context, attr_name)
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ATTRIBUTE_OPTIONS, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها")
    
    text = (
        f"📋 گزینه های ویژگی «{attr_name}»\n\n"
        f"تعداد: {len(options)} مورد\n\n"
        "یک گزینه را انتخاب کنید یا گزینه جدید بسازید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_option_list_keyboard(options, attribute_id))


async def start_option_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start option creation."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("opt_create_", "")
    update_flow_data(context, 'current_attribute_id', attribute_id)
    update_flow_data(context, 'creating_option', {'attribute_id': attribute_id})
    set_step(context, 'option_create_label')
    
    cat_name = _get_category_name(context)
    attr_name = _get_attribute_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.OPTION_CREATE, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها", "➕ گزینه جدید")
    
    text = (
        "➕ ایجاد گزینه جدید\n\n"
        "لطفا نام فارسی گزینه را وارد کنید:\n"
        "(مثال: 5x5 سانتی متر، کاغذی)"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_cancel_keyboard())


async def handle_option_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option label input."""
    label = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['label_fa'] = label
    update_flow_data(context, 'creating_option', creating)
    set_step(context, 'option_create_value')
    
    cat_name = _get_category_name(context)
    attr_name = _get_attribute_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.OPTION_CREATE, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها", "➕ گزینه جدید", "مقدار")
    
    text = (
        f"✅ نام: {label}\n\n"
        "حالا مقدار انگلیسی (value) را وارد کنید:\n"
        "(این مقدار در سیستم ذخیره می شود، مثال: 5x5)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_option_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option value input."""
    value = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['value'] = value
    update_flow_data(context, 'creating_option', creating)
    set_step(context, 'option_create_price')
    
    cat_name = _get_category_name(context)
    attr_name = _get_attribute_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.OPTION_CREATE, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها", "➕ گزینه جدید", "قیمت")
    
    text = (
        f"✅ مقدار: {value}\n\n"
        "مبلغ اضافه قیمت را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_option_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option price input and create option."""
    bc = get_breadcrumb(context)
    cat_name = _get_category_name(context)
    attr_name = _get_attribute_name(context)
    
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        bc.set_path(BreadcrumbPath.OPTION_CREATE, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها", "➕ گزینه جدید", "قیمت")
        msg = bc.format_message("❌ لطفا یک عدد معتبر وارد کنید.")
        await update.message.reply_text(msg)
        return
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['price_modifier'] = price
    
    attribute_id = creating.pop('attribute_id', get_flow_data_item(context, 'current_attribute_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_attribute_option(attribute_id, admin_id, creating)
    
    if result:
        set_step(context, 'option_list')
        
        bc.set_path(BreadcrumbPath.ATTRIBUTE_OPTIONS, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها")
        msg = bc.format_message(f"✅ گزینه «{creating['label_fa']}» با موفقیت ایجاد شد!")
        await update.message.reply_text(msg)
        
        # Show option list
        category_id = get_flow_data_item(context, 'current_category_id', '')
        attributes = await api_client.get_attributes(category_id, active_only=False)
        options = []
        for attr in (attributes or []):
            if attr['id'] == attribute_id:
                options = attr.get('options', [])
                break
        
        text = (
            f"📋 گزینه های ویژگی «{attr_name}»\n\n"
            f"تعداد: {len(options)} مورد"
        )
        msg = bc.format_message(text)
        await update.message.reply_text(msg, reply_markup=get_option_list_keyboard(options, attribute_id))
    else:
        bc.set_path(BreadcrumbPath.ATTRIBUTE_OPTIONS, cat_name, "ویژگی‌ها", attr_name, "گزینه‌ها")
        msg = bc.format_message("❌ خطا در ایجاد گزینه.")
        await update.message.reply_text(msg)


# ============== Plan Handlers ==============

async def show_plan_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of design plans for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_plans_", "")
    update_flow_data(context, 'current_category_id', category_id)
    set_step(context, 'plan_list')
    
    plans = await api_client.get_design_plans(category_id, active_only=False)
    cat_name = _get_category_name(context)
    
    # Set breadcrumb
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATEGORY_PLANS, cat_name, "پلن‌ها")
    
    text = (
        f"📋 پلن های طراحی ({len(plans or [])}) مورد:\n\n"
        "یک پلن را انتخاب کنید یا پلن جدید بسازید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_plan_list_keyboard(plans or [], category_id))


async def start_plan_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start plan creation."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("plan_create_", "")
    update_flow_data(context, 'current_category_id', category_id)
    update_flow_data(context, 'creating_plan', {'category_id': category_id})
    set_step(context, 'plan_create_name')
    
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_CREATE, cat_name, "پلن‌ها", "➕ پلن جدید")
    
    text = (
        "➕ ایجاد پلن طراحی جدید\n\n"
        "لطفا نام فارسی پلن را وارد کنید:\n"
        "(مثال: عمومی، نیمه خصوصی، خصوصی)"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_cancel_keyboard())


async def handle_plan_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_slug')
    
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_CREATE, cat_name, "پلن‌ها", "➕ پلن جدید", "نام")
    
    text = (
        f"✅ نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(مثال: public, semi_private, private)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_plan_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan slug input."""
    slug = update.message.text.strip().lower()
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_price')
    
    cat_name = _get_category_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_CREATE, cat_name, "پلن‌ها", "➕ پلن جدید", "قیمت")
    
    text = (
        f"✅ شناسه: {slug}\n\n"
        "قیمت طراحی را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_cancel_keyboard())


async def handle_plan_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan price input."""
    bc = get_breadcrumb(context)
    cat_name = _get_category_name(context)
    
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        bc.set_path(BreadcrumbPath.PLAN_CREATE, cat_name, "پلن‌ها", "➕ پلن جدید", "قیمت")
        msg = bc.format_message("❌ لطفا یک عدد معتبر وارد کنید.")
        await update.message.reply_text(msg)
        return
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['price'] = price
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_type')
    
    bc.set_path(BreadcrumbPath.PLAN_CREATE, cat_name, "پلن‌ها", "➕ پلن جدید", "نوع")
    
    text = (
        f"✅ قیمت: {price:,} تومان\n\n"
        "نوع پلن را انتخاب کنید:"
    )
    msg = bc.format_message(text)
    
    await update.message.reply_text(msg, reply_markup=get_plan_type_keyboard())


async def handle_plan_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan type selection and create plan."""
    query = update.callback_query
    await query.answer()
    
    plan_type = query.data.replace("ptype_", "")
    creating = get_flow_data_item(context, 'creating_plan', {})
    
    # Set flags based on type
    if plan_type == "PUBLIC":
        creating['has_templates'] = True
        creating['has_questionnaire'] = False
        creating['has_file_upload'] = False
    elif plan_type == "SEMI_PRIVATE":
        creating['has_templates'] = False
        creating['has_questionnaire'] = True
        creating['has_file_upload'] = False
    else:  # PRIVATE
        creating['has_templates'] = False
        creating['has_questionnaire'] = False
        creating['has_file_upload'] = True
    
    category_id = creating.pop('category_id', get_flow_data_item(context, 'current_category_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_design_plan(category_id, admin_id, creating)
    
    cat_name = _get_category_name(context)
    bc = get_breadcrumb(context)
    
    if result:
        update_flow_data(context, 'current_plan_id', result['id'])
        set_step(context, 'plan_actions')
        
        plan_name = creating['name_fa']
        _store_plan_name(context, plan_name)
        
        bc.set_path(BreadcrumbPath.PLAN_VIEW, cat_name, "پلن‌ها", plan_name)
        
        text = f"✅ پلن «{plan_name}» با موفقیت ایجاد شد!"
        msg = bc.format_message(text)
        
        await query.message.edit_text(msg, reply_markup=get_plan_actions_keyboard(result['id'], category_id))
    else:
        bc.set_path(BreadcrumbPath.CATEGORY_PLANS, cat_name, "پلن‌ها")
        msg = bc.format_message("❌ خطا در ایجاد پلن.")
        await query.message.edit_text(msg)


async def show_plan_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show plan actions."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'plan_actions')
    
    category_id = get_flow_data_item(context, 'current_category_id', '')
    cat_name = _get_category_name(context)
    
    # Get plan name
    plans = await api_client.get_design_plans(category_id, active_only=False)
    plan_name = "نامشخص"
    for plan in (plans or []):
        if plan['id'] == plan_id:
            plan_name = plan.get('name_fa', 'نامشخص')
            break
    
    _store_plan_name(context, plan_name)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_VIEW, cat_name, "پلن‌ها", plan_name)
    
    text = (
        f"📋 پلن: {plan_name}\n\n"
        "یک عملیات را انتخاب کنید:"
    )
    msg = bc.format_message(text)
    
    await query.message.edit_text(msg, reply_markup=get_plan_actions_keyboard(plan_id, category_id))


# ============== Question Handlers ==============

async def show_question_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of questions for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_questions_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'question_list')
    
    # Get questions from API
    questions = await api_client.get_questions(plan_id, active_only=False)
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_QUESTIONNAIRE, cat_name, "پلن‌ها", plan_name, "پرسشنامه")
    
    keyboard = []
    if questions:
        for q in questions:
            text = q.get('question_fa', q.get('text_fa', 'بدون متن'))[:30]
            is_active = q.get('is_active', True)
            status = "✅" if is_active else "❌"
            keyboard.append([InlineKeyboardButton(
                f"{status} {text}...",
                callback_data=f"question_{q['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton("➕ سوال جدید", callback_data=f"q_create_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"plan_{plan_id}")])
    
    msg_text = (
        f"📝 سوالات پرسشنامه\n\n"
        f"پلن: {plan_name}\n"
        f"تعداد سوالات: {len(questions) if questions else 0}"
    )
    msg = bc.format_message(msg_text)
    
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle question text input."""
    text = update.message.text.strip()
    step = get_step(context)
    
    if step == 'question_create_text':
        update_flow_data(context, 'question_text', text)
        set_step(context, 'question_create_type')
        
        cat_name = _get_category_name(context)
        plan_name = _get_plan_name(context)
        
        bc = get_breadcrumb(context)
        bc.set_path(BreadcrumbPath.QUESTION_CREATE, cat_name, "پلن‌ها", plan_name, "پرسشنامه", "➕ سوال جدید", "نوع ورودی")
        
        keyboard = [
            [InlineKeyboardButton("📝 متن کوتاه", callback_data="qtype_TEXT")],
            [InlineKeyboardButton("📄 متن بلند", callback_data="qtype_TEXTAREA")],
            [InlineKeyboardButton("🔢 عدد", callback_data="qtype_NUMBER")],
            [InlineKeyboardButton("🔘 انتخاب تکی", callback_data="qtype_SINGLE_CHOICE")],
            [InlineKeyboardButton("☑️ انتخاب چندتایی", callback_data="qtype_MULTI_CHOICE")],
            [InlineKeyboardButton("🎨 انتخاب رنگ", callback_data="qtype_COLOR_PICKER")],
            [InlineKeyboardButton("📅 تاریخ", callback_data="qtype_DATE_PICKER")],
            [InlineKeyboardButton("⭐ امتیاز", callback_data="qtype_SCALE")],
            [InlineKeyboardButton("📷 آپلود تصویر", callback_data="qtype_IMAGE_UPLOAD")],
            [InlineKeyboardButton("📎 آپلود فایل", callback_data="qtype_FILE_UPLOAD")],
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")],
        ]
        
        msg_text = (
            f"✅ متن سوال: {text[:50]}...\n\n"
            "نوع ورودی سوال را انتخاب کنید:"
        )
        msg = bc.format_message(msg_text)
        
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def start_question_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start creating a new question."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("q_create_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'question_create_text')
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.QUESTION_CREATE, cat_name, "پلن‌ها", plan_name, "پرسشنامه", "➕ سوال جدید")
    
    msg_text = (
        "➕ ایجاد سوال جدید\n\n"
        "متن سوال را به فارسی وارد کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await query.message.edit_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
        ])
    )


async def handle_question_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle question type selection."""
    query = update.callback_query
    await query.answer()
    
    input_type = query.data.replace("qtype_", "")
    update_flow_data(context, 'question_type', input_type)
    
    plan_id = get_flow_data_item(context, 'current_plan_id', '')
    question_text = get_flow_data_item(context, 'question_text', '')
    admin_id = context.user_data.get('user_id', '')
    
    # Create question
    data = {
        'question_fa': question_text,
        'input_type': input_type,
        'is_required': True,
        'sort_order': 0
    }
    
    result = await api_client.create_question(plan_id, admin_id, data)
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    bc = get_breadcrumb(context)
    
    if result:
        question_id = result.get('id', '')
        
        # If choice type, prompt to add options
        if input_type in ['SINGLE_CHOICE', 'MULTI_CHOICE']:
            update_flow_data(context, 'current_question_id', question_id)
            set_step(context, 'question_option_create')
            
            bc.set_path(BreadcrumbPath.QUESTION_CREATE, cat_name, "پلن‌ها", plan_name, "پرسشنامه", f"سوال: {question_text[:15]}...", "گزینه‌ها")
            
            msg_text = (
                f"✅ سوال ایجاد شد!\n\n"
                f"حالا گزینه‌های سوال را اضافه کنید.\n"
                f"هر گزینه را در یک خط وارد کنید:\n"
                f"(مثال: قرمز)"
            )
            msg = bc.format_message(msg_text)
            
            await query.message.edit_text(
                msg,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ اتمام", callback_data=f"qopt_done_{question_id}")],
                    [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
                ])
            )
        else:
            # Show success message with navigation buttons
            bc.set_path(BreadcrumbPath.PLAN_QUESTIONNAIRE, cat_name, "پلن‌ها", plan_name, "پرسشنامه")
            
            msg_text = f"✅ سوال «{question_text[:30]}» با موفقیت ایجاد شد!"
            msg = bc.format_message(msg_text)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ سوال دیگر", callback_data=f"q_create_{plan_id}")],
                [InlineKeyboardButton("🔙 بازگشت به پرسشنامه", callback_data=f"plan_questions_{plan_id}")]
            ])
            await query.message.edit_text(msg, reply_markup=keyboard)
    else:
        bc.set_path(BreadcrumbPath.PLAN_QUESTIONNAIRE, cat_name, "پلن‌ها", plan_name, "پرسشنامه")
        msg = bc.format_message("❌ خطا در ایجاد سوال.")
        await query.message.edit_text(msg)


async def handle_question_option_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle question option text input."""
    text = update.message.text.strip()
    question_id = get_flow_data_item(context, 'current_question_id', '')
    admin_id = context.user_data.get('user_id', '')
    
    # Create option
    data = {
        'label_fa': text,
        'value': text.lower().replace(' ', '_'),
        'sort_order': 0
    }
    
    result = await api_client.create_question_option(question_id, admin_id, data)
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.QUESTION_CREATE, cat_name, "پلن‌ها", plan_name, "پرسشنامه", "سوال", "گزینه‌ها")
    
    if result:
        msg_text = (
            f"✅ گزینه «{text}» اضافه شد.\n\n"
            f"گزینه بعدی را وارد کنید یا «اتمام» را بزنید."
        )
        msg = bc.format_message(msg_text)
        
        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ اتمام", callback_data=f"qopt_done_{question_id}")],
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
            ])
        )
    else:
        msg = bc.format_message("❌ خطا در افزودن گزینه.")
        await update.message.reply_text(msg)


async def finish_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finish adding options to a question."""
    query = update.callback_query
    await query.answer()
    
    plan_id = get_flow_data_item(context, 'current_plan_id', '')
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_QUESTIONNAIRE, cat_name, "پلن‌ها", plan_name, "پرسشنامه")
    
    msg = bc.format_message("✅ سوال با موفقیت ایجاد شد!")
    await query.message.edit_text(msg)
    
    # Return to question list
    query.data = f"plan_questions_{plan_id}"
    await show_question_list(update, context)


# ============== Template Handlers ==============

async def show_template_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of templates for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_templates_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'template_list')
    
    # Get templates from API
    templates = await api_client.get_templates(plan_id, active_only=False)
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.PLAN_TEMPLATES, cat_name, "پلن‌ها", plan_name, "قالب‌ها")
    
    keyboard = []
    if templates:
        for t in templates:
            name = t.get('name_fa', 'بدون نام')
            is_active = t.get('is_active', True)
            status = "✅" if is_active else "❌"
            keyboard.append([InlineKeyboardButton(
                f"{status} 🖼️ {name}",
                callback_data=f"template_{t['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton("➕ قالب جدید", callback_data=f"tpl_create_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"plan_{plan_id}")])
    
    msg_text = (
        f"🖼️ قالب‌های طراحی\n\n"
        f"پلن: {plan_name}\n"
        f"تعداد قالب‌ها: {len(templates) if templates else 0}"
    )
    msg = bc.format_message(msg_text)
    
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_template_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle template name input."""
    text = update.message.text.strip()
    step = get_step(context)
    
    if step == 'template_create_name':
        update_flow_data(context, 'template_name', text)
        set_step(context, 'template_upload_image')
        
        cat_name = _get_category_name(context)
        plan_name = _get_plan_name(context)
        
        bc = get_breadcrumb(context)
        bc.set_path(BreadcrumbPath.TEMPLATE_CREATE, cat_name, "پلن‌ها", plan_name, "قالب‌ها", "➕ قالب جدید", "تصویر")
        
        msg_text = (
            "📤 تصویر قالب را ارسال کنید:\n\n"
            "این تصویر به عنوان پس‌زمینه استفاده می‌شود.\n"
            "محل لوگو در مرحله بعد مشخص می‌شود."
        )
        msg = bc.format_message(msg_text)
        
        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
            ])
        )


async def start_template_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start creating a new template."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("tpl_create_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'template_create_name')
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.TEMPLATE_CREATE, cat_name, "پلن‌ها", plan_name, "قالب‌ها", "➕ قالب جدید")
    
    msg_text = (
        "➕ ایجاد قالب جدید\n\n"
        "نام قالب را به فارسی وارد کنید:"
    )
    msg = bc.format_message(msg_text)
    
    await query.message.edit_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
        ])
    )


async def handle_template_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle template image upload."""
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    bc = get_breadcrumb(context)
    
    if not update.message.photo:
        bc.set_path(BreadcrumbPath.TEMPLATE_CREATE, cat_name, "پلن‌ها", plan_name, "قالب‌ها", "➕ قالب جدید", "تصویر")
        msg = bc.format_message("❌ لطفا یک تصویر ارسال کنید.")
        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
            ])
        )
        return
    
    # Get photo file URL
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    if file.file_path.startswith("https://"):
        image_url = file.file_path
    else:
        bot_token = context.bot.token
        image_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"
    
    update_flow_data(context, 'template_image_url', image_url)
    update_flow_data(context, 'template_image_width', photo.width)
    update_flow_data(context, 'template_image_height', photo.height)
    
    set_step(context, 'template_set_placeholder')
    
    bc.set_path(BreadcrumbPath.TEMPLATE_CREATE, cat_name, "پلن‌ها", plan_name, "قالب‌ها", "➕ قالب جدید", "محل لوگو")
    
    msg_text = (
        f"✅ تصویر دریافت شد!\n\n"
        f"📐 ابعاد: {photo.width}x{photo.height}\n\n"
        f"محل قرارگیری لوگو را مشخص کنید:\n"
        f"فرمت: x,y,width,height\n\n"
        f"مثال: 100,100,200,200\n"
        f"(یعنی از نقطه 100,100 با ابعاد 200x200)"
    )
    msg = bc.format_message(msg_text)
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
        ])
    )


async def handle_template_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle template placeholder coordinates input."""
    text = update.message.text.strip()
    
    cat_name = _get_category_name(context)
    plan_name = _get_plan_name(context)
    bc = get_breadcrumb(context)
    
    try:
        parts = [int(p.strip()) for p in text.split(',')]
        if len(parts) != 4:
            raise ValueError("Need 4 values")
        x, y, w, h = parts
    except (ValueError, IndexError):
        bc.set_path(BreadcrumbPath.TEMPLATE_CREATE, cat_name, "پلن‌ها", plan_name, "قالب‌ها", "➕ قالب جدید", "محل لوگو")
        msg = bc.format_message(
            "❌ فرمت نادرست. لطفاً 4 عدد با کاما جدا شده وارد کنید:\n"
            "x,y,width,height\n"
            "(مثال: 100,50,200,200)"
        )
        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="cancel")]
            ])
        )
        return
    
    # Get stored data
    plan_id = get_flow_data_item(context, 'current_plan_id', '')
    name = get_flow_data_item(context, 'template_name', '')
    image_url = get_flow_data_item(context, 'template_image_url', '')
    image_width = get_flow_data_item(context, 'template_image_width', 0)
    image_height = get_flow_data_item(context, 'template_image_height', 0)
    admin_id = context.user_data.get('user_id', '')
    
    # Create template
    data = {
        'name_fa': name,
        'image_url': image_url,
        'image_width': image_width,
        'image_height': image_height,
        'placeholder_x': x,
        'placeholder_y': y,
        'placeholder_width': w,
        'placeholder_height': h,
        'is_active': True
    }
    
    result = await api_client.create_template(plan_id, admin_id, data)
    
    if result:
        bc.set_path(BreadcrumbPath.PLAN_TEMPLATES, cat_name, "پلن‌ها", plan_name, "قالب‌ها")
        
        msg = bc.format_message(
            f"✅ قالب «{name}» با موفقیت ایجاد شد!\n\n"
            f"📍 محل لوگو: ({x}, {y}) - {w}x{h}"
        )
        await update.message.reply_text(msg)
        
        # Clear flow data and return to template list
        clear_flow_data(context)
        
        # Create a fake query to return to list
        class FakeQuery:
            message = update.message
            data = f"plan_templates_{plan_id}"
            async def answer(self): pass
        
        fake_update = type('Update', (), {'callback_query': FakeQuery()})()
        await show_template_list(fake_update, context)
    else:
        bc.set_path(BreadcrumbPath.PLAN_TEMPLATES, cat_name, "پلن‌ها", plan_name, "قالب‌ها")
        msg = bc.format_message("❌ خطا در ایجاد قالب.")
        await update.message.reply_text(msg)


# ============== Cancel/Back Handlers ==============

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle cancel button."""
    query = update.callback_query
    await query.answer()
    
    step = get_step(context)
    
    # Determine where to go back based on current step
    if step and 'category_create' in step:
        await show_category_list(update, context)
    elif step and 'attribute_create' in step:
        category_id = get_flow_data_item(context, 'current_category_id', '')
        # Simulate callback data
        query.data = f"cat_attrs_{category_id}"
        await show_attribute_list(update, context)
    elif step and 'option_create' in step:
        attribute_id = get_flow_data_item(context, 'current_attribute_id', '')
        query.data = f"attr_opts_{attribute_id}"
        await show_option_list(update, context)
    elif step and 'plan_create' in step:
        category_id = get_flow_data_item(context, 'current_category_id', '')
        query.data = f"cat_plans_{category_id}"
        await show_plan_list(update, context)
    elif step and 'question' in step:
        plan_id = get_flow_data_item(context, 'current_plan_id', '')
        query.data = f"plan_questions_{plan_id}"
        await show_question_list(update, context)
    elif step and 'template' in step:
        plan_id = get_flow_data_item(context, 'current_plan_id', '')
        query.data = f"plan_templates_{plan_id}"
        await show_template_list(update, context)
    else:
        await show_catalog_menu(update, context)


async def handle_back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to admin menu."""
    query = update.callback_query
    await query.answer()
    
    clear_flow(context)
    
    bc = get_breadcrumb(context)
    bc.set_path(BreadcrumbPath.ADMIN_MENU)
    
    msg = bc.format_message("🔧 پنل مدیریت\n\nیکی را انتخاب کنید:")
    
    await query.message.edit_text("بازگشت به پنل مدیریت...")
    await query.message.reply_text(msg, reply_markup=get_admin_menu_keyboard())
