"""Catalog Flow - Admin catalog management handlers.

This module handles all catalog-related operations using the unified flow manager.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.api_client import api_client
from utils.flow_manager import (
    set_flow, set_step, get_step, clear_flow,
    update_flow_data, get_flow_data_item, clear_flow_data,
    FLOW_CATALOG, CATALOG_STEPS
)
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
        'template_create_name': handle_template_name,
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
    
    menu_text = (
        "مدیریت کاتالوگ محصولات\n\n"
        "از این بخش می توانید:\n"
        "- دسته بندی های محصول را مدیریت کنید\n"
        "- ویژگی ها و گزینه ها را تعریف کنید\n"
        "- پلن های طراحی، پرسشنامه و قالب ها را مدیریت کنید"
    )
    
    if query:
        await query.answer()
        await query.message.edit_text(menu_text, reply_markup=get_catalog_menu_keyboard())
    else:
        await update.message.reply_text(menu_text, reply_markup=get_catalog_menu_keyboard())


async def show_category_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of categories."""
    query = update.callback_query
    await query.answer()
    
    set_step(context, 'category_list')
    
    categories = await api_client.get_categories(active_only=False)
    
    if categories is None:
        await query.message.edit_text(
            "خطا در دریافت دسته بندی ها.",
            reply_markup=get_catalog_menu_keyboard()
        )
        return
    
    await query.message.edit_text(
        f"دسته بندی ها ({len(categories)} مورد):\n\n"
        "یک دسته را انتخاب کنید یا دسته جدید بسازید:",
        reply_markup=get_category_list_keyboard(categories)
    )


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
        await query.message.edit_text(
            "دسته بندی یافت نشد.",
            reply_markup=get_catalog_menu_keyboard()
        )
        return
    
    name = category.get('name_fa', 'بدون نام')
    slug = category.get('slug', '')
    icon = category.get('icon', '')
    price = category.get('base_price', 0)
    is_active = "فعال" if category.get('is_active') else "غیرفعال"
    
    await query.message.edit_text(
        f"دسته بندی: {icon} {name}\n"
        f"شناسه: {slug}\n"
        f"قیمت پایه: {int(float(price)):,} تومان\n"
        f"وضعیت: {is_active}\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_category_actions_keyboard(category_id)
    )


# ============== Category Creation ==============

async def start_category_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start category creation process."""
    query = update.callback_query
    await query.answer()
    
    set_step(context, 'category_create_name')
    update_flow_data(context, 'creating_category', {})
    
    await query.message.edit_text(
        "ایجاد دسته بندی جدید\n\n"
        "لطفا نام فارسی دسته بندی را وارد کنید:\n"
        "(مثال: لیبل، فاکتور، کارت ویزیت)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_slug')
    
    await update.message.reply_text(
        f"نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی و خط تیره، مثال: label)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_category_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category slug input."""
    slug = update.message.text.strip().lower()
    
    if not slug.replace('-', '').replace('_', '').isalnum():
        await update.message.reply_text(
            "شناسه نامعتبر است. فقط از حروف انگلیسی، اعداد و خط تیره استفاده کنید.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_icon')
    
    await update.message.reply_text(
        f"شناسه: {slug}\n\n"
        "حالا یک نماد برای آیکون دسته وارد کنید:\n"
        "(یک حرف یا کلمه کوتاه)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_category_icon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category icon input."""
    icon = update.message.text.strip()[:10]
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['icon'] = icon
    update_flow_data(context, 'creating_category', creating)
    set_step(context, 'category_create_price')
    
    await update.message.reply_text(
        f"نماد: {icon}\n\n"
        "حالا قیمت پایه را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_category_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category base price input and create category."""
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کنید.")
        return
    
    creating = get_flow_data_item(context, 'creating_category', {})
    creating['base_price'] = price
    
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_category(admin_id, creating)
    
    if result:
        update_flow_data(context, 'current_category_id', result['id'])
        set_step(context, 'category_actions')
        
        await update.message.reply_text(
            f"دسته بندی {creating['name_fa']} با موفقیت ایجاد شد!\n"
            f"قیمت پایه: {price:,} تومان\n\n"
            "اکنون می توانید ویژگی ها و پلن های طراحی را برای این دسته تعریف کنید.",
            reply_markup=get_category_actions_keyboard(result['id'])
        )
    else:
        await update.message.reply_text(
            "خطا در ایجاد دسته بندی. لطفا دوباره تلاش کنید.",
            reply_markup=get_category_list_keyboard([])
        )


async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_delete_", "")
    admin_id = context.user_data.get('user_id', '')
    
    success = await api_client.delete_category(category_id, admin_id)
    
    if success:
        await query.message.edit_text("دسته بندی با موفقیت حذف شد.")
    else:
        await query.message.edit_text("خطا در حذف دسته بندی.")
    
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
    for cat in (categories or []):
        if cat['id'] == category_id:
            cat_name = cat.get('name_fa', 'نامشخص')
            break
    
    await query.message.edit_text(
        f"ویژگی های دسته {cat_name}:\n\n"
        "یک ویژگی را انتخاب کنید یا ویژگی جدید بسازید:",
        reply_markup=get_attribute_list_keyboard(attributes or [], category_id)
    )


async def start_attribute_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start attribute creation."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("attr_create_", "")
    update_flow_data(context, 'current_category_id', category_id)
    update_flow_data(context, 'creating_attribute', {'category_id': category_id})
    set_step(context, 'attribute_create_name')
    
    await query.message.edit_text(
        "ایجاد ویژگی جدید\n\n"
        "لطفا نام فارسی ویژگی را وارد کنید:\n"
        "(مثال: سایز، جنس، تعداد)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_attribute_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle attribute name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_attribute', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_attribute', creating)
    set_step(context, 'attribute_create_slug')
    
    await update.message.reply_text(
        f"نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(فقط حروف کوچک انگلیسی، مثال: size)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_attribute_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle attribute slug input."""
    slug = update.message.text.strip().lower()
    
    creating = get_flow_data_item(context, 'creating_attribute', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_attribute', creating)
    set_step(context, 'attribute_create_type')
    
    await update.message.reply_text(
        f"شناسه: {slug}\n\n"
        "نوع ورودی را انتخاب کنید:",
        reply_markup=get_input_type_keyboard()
    )


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
    
    if result:
        update_flow_data(context, 'current_attribute_id', result['id'])
        set_step(context, 'attribute_actions')
        
        await query.message.edit_text(
            f"ویژگی {creating['name_fa']} با موفقیت ایجاد شد!\n\n"
            "اکنون می توانید گزینه هایی برای این ویژگی تعریف کنید.",
            reply_markup=get_attribute_actions_keyboard(result['id'], category_id)
        )
    else:
        await query.message.edit_text("خطا در ایجاد ویژگی.")
        set_step(context, 'attribute_list')


async def show_attribute_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show attribute actions."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("attr_", "")
    update_flow_data(context, 'current_attribute_id', attribute_id)
    set_step(context, 'attribute_actions')
    
    category_id = get_flow_data_item(context, 'current_category_id', '')
    
    await query.message.edit_text(
        "ویژگی انتخاب شده:\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_attribute_actions_keyboard(attribute_id, category_id)
    )


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
    for attr in (attributes or []):
        if attr['id'] == attribute_id:
            options = attr.get('options', [])
            break
    
    await query.message.edit_text(
        f"گزینه های ویژگی ({len(options)} مورد):\n\n"
        "یک گزینه را انتخاب کنید یا گزینه جدید بسازید:",
        reply_markup=get_option_list_keyboard(options, attribute_id)
    )


async def start_option_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start option creation."""
    query = update.callback_query
    await query.answer()
    
    attribute_id = query.data.replace("opt_create_", "")
    update_flow_data(context, 'current_attribute_id', attribute_id)
    update_flow_data(context, 'creating_option', {'attribute_id': attribute_id})
    set_step(context, 'option_create_label')
    
    await query.message.edit_text(
        "ایجاد گزینه جدید\n\n"
        "لطفا نام فارسی گزینه را وارد کنید:\n"
        "(مثال: 5x5 سانتی متر، کاغذی)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_option_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option label input."""
    label = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['label_fa'] = label
    update_flow_data(context, 'creating_option', creating)
    set_step(context, 'option_create_value')
    
    await update.message.reply_text(
        f"نام: {label}\n\n"
        "حالا مقدار انگلیسی (value) را وارد کنید:\n"
        "(این مقدار در سیستم ذخیره می شود، مثال: 5x5)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_option_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option value input."""
    value = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['value'] = value
    update_flow_data(context, 'creating_option', creating)
    set_step(context, 'option_create_price')
    
    await update.message.reply_text(
        f"مقدار: {value}\n\n"
        "مبلغ اضافه قیمت را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_option_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle option price input and create option."""
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کنید.")
        return
    
    creating = get_flow_data_item(context, 'creating_option', {})
    creating['price_modifier'] = price
    
    attribute_id = creating.pop('attribute_id', get_flow_data_item(context, 'current_attribute_id', ''))
    admin_id = context.user_data.get('user_id', '')
    
    result = await api_client.create_attribute_option(attribute_id, admin_id, creating)
    
    if result:
        set_step(context, 'option_list')
        await update.message.reply_text(
            f"گزینه {creating['label_fa']} با موفقیت ایجاد شد!"
        )
        # Show option list
        category_id = get_flow_data_item(context, 'current_category_id', '')
        attributes = await api_client.get_attributes(category_id, active_only=False)
        options = []
        for attr in (attributes or []):
            if attr['id'] == attribute_id:
                options = attr.get('options', [])
                break
        await update.message.reply_text(
            "گزینه ها:",
            reply_markup=get_option_list_keyboard(options, attribute_id)
        )
    else:
        await update.message.reply_text("خطا در ایجاد گزینه.")


# ============== Plan Handlers ==============

async def show_plan_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of design plans for a category."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("cat_plans_", "")
    update_flow_data(context, 'current_category_id', category_id)
    set_step(context, 'plan_list')
    
    plans = await api_client.get_design_plans(category_id, active_only=False)
    
    await query.message.edit_text(
        f"پلن های طراحی ({len(plans or [])}) مورد:\n\n"
        "یک پلن را انتخاب کنید یا پلن جدید بسازید:",
        reply_markup=get_plan_list_keyboard(plans or [], category_id)
    )


async def start_plan_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start plan creation."""
    query = update.callback_query
    await query.answer()
    
    category_id = query.data.replace("plan_create_", "")
    update_flow_data(context, 'current_category_id', category_id)
    update_flow_data(context, 'creating_plan', {'category_id': category_id})
    set_step(context, 'plan_create_name')
    
    await query.message.edit_text(
        "ایجاد پلن طراحی جدید\n\n"
        "لطفا نام فارسی پلن را وارد کنید:\n"
        "(مثال: عمومی، نیمه خصوصی، خصوصی)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_plan_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan name input."""
    name = update.message.text.strip()
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['name_fa'] = name
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_slug')
    
    await update.message.reply_text(
        f"نام: {name}\n\n"
        "حالا شناسه انگلیسی (slug) را وارد کنید:\n"
        "(مثال: public, semi_private, private)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_plan_slug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan slug input."""
    slug = update.message.text.strip().lower()
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['slug'] = slug
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_price')
    
    await update.message.reply_text(
        f"شناسه: {slug}\n\n"
        "قیمت طراحی را به تومان وارد کنید:\n"
        "(برای رایگان، 0 وارد کنید)",
        reply_markup=get_cancel_keyboard()
    )


async def handle_plan_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plan price input."""
    try:
        price = int(update.message.text.strip().replace(',', ''))
    except ValueError:
        await update.message.reply_text("لطفا یک عدد معتبر وارد کنید.")
        return
    
    creating = get_flow_data_item(context, 'creating_plan', {})
    creating['price'] = price
    update_flow_data(context, 'creating_plan', creating)
    set_step(context, 'plan_create_type')
    
    await update.message.reply_text(
        f"قیمت: {price:,} تومان\n\n"
        "نوع پلن را انتخاب کنید:",
        reply_markup=get_plan_type_keyboard()
    )


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
    
    if result:
        update_flow_data(context, 'current_plan_id', result['id'])
        set_step(context, 'plan_actions')
        
        await query.message.edit_text(
            f"پلن {creating['name_fa']} با موفقیت ایجاد شد!",
            reply_markup=get_plan_actions_keyboard(result['id'], category_id)
        )
    else:
        await query.message.edit_text("خطا در ایجاد پلن.")


async def show_plan_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show plan actions."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'plan_actions')
    
    category_id = get_flow_data_item(context, 'current_category_id', '')
    
    await query.message.edit_text(
        "پلن انتخاب شده:\n\n"
        "یک عملیات را انتخاب کنید:",
        reply_markup=get_plan_actions_keyboard(plan_id, category_id)
    )


# ============== Question Handlers ==============

async def show_question_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of questions for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_questions_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'question_list')
    
    # TODO: Implement question list keyboard
    await query.message.edit_text(
        "سوالات پرسشنامه:\n\n"
        "(در حال توسعه...)",
        reply_markup=get_cancel_keyboard("بازگشت")
    )


async def handle_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle question text input."""
    # TODO: Implement
    pass


# ============== Template Handlers ==============

async def show_template_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of templates for a plan."""
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.replace("plan_templates_", "")
    update_flow_data(context, 'current_plan_id', plan_id)
    set_step(context, 'template_list')
    
    # TODO: Implement template list keyboard
    await query.message.edit_text(
        "قالب های طراحی:\n\n"
        "(در حال توسعه...)",
        reply_markup=get_cancel_keyboard("بازگشت")
    )


async def handle_template_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle template name input."""
    # TODO: Implement
    pass


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
    else:
        await show_catalog_menu(update, context)


async def handle_back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to admin menu."""
    query = update.callback_query
    await query.answer()
    
    clear_flow(context)
    
    await query.message.edit_text("بازگشت به پنل مدیریت...")
    await query.message.reply_text(
        "پنل مدیریت\n\nیکی را انتخاب کنید:",
        reply_markup=get_admin_menu_keyboard()
    )

