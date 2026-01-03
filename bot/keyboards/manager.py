"""Keyboard Manager - Centralized keyboard generation.

This module provides consistent keyboard generation with proper back button handling.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from typing import List, Optional


# ============== Reply Keyboards ==============

def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Get the main menu keyboard.
    
    Args:
        is_admin: Whether to show admin panel button
        
    Returns:
        ReplyKeyboardMarkup for main menu
    """
    keyboard = [
        ["ثبت سفارش جدید"],
        ["سفارشات من"],
        ["پروفایل", "رهگیری سفارش"],
        ["راهنما", "پشتیبانی"],
    ]
    
    if is_admin:
        keyboard.append(["پنل مدیریت"])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get the admin panel menu keyboard."""
    keyboard = [
        ["پرداخت های در انتظار تایید"],
        ["مدیریت کاتالوگ"],
        ["تنظیمات کارت بانکی"],
        ["مدیریت مدیران"],
        ["بازگشت به منو"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard(back_text: str = "بازگشت") -> ReplyKeyboardMarkup:
    """Get a simple back button keyboard."""
    return ReplyKeyboardMarkup([[back_text]], resize_keyboard=True)


# ============== Inline Keyboards ==============

def get_cancel_keyboard(cancel_text: str = "انصراف") -> InlineKeyboardMarkup:
    """Get a cancel button inline keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(cancel_text, callback_data="cancel")]
    ])


def get_confirm_cancel_keyboard(
    confirm_text: str = "تایید",
    cancel_text: str = "انصراف",
    confirm_data: str = "confirm",
    cancel_data: str = "cancel"
) -> InlineKeyboardMarkup:
    """Get confirm/cancel inline keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_data),
            InlineKeyboardButton(cancel_text, callback_data=cancel_data),
        ]
    ])


def get_back_inline_keyboard(
    back_text: str = "بازگشت",
    back_data: str = "back"
) -> InlineKeyboardMarkup:
    """Get a back button inline keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(back_text, callback_data=back_data)]
    ])


# ============== Catalog Keyboards ==============

def get_catalog_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the catalog management menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("مدیریت دسته بندی ها", callback_data="catalog_categories")],
        [InlineKeyboardButton("بازگشت به پنل مدیریت", callback_data="back_to_admin")],
    ])


def get_category_list_keyboard(categories: list) -> InlineKeyboardMarkup:
    """Get keyboard with list of categories."""
    keyboard = []
    for cat in categories:
        icon = cat.get('icon', '')
        name = cat.get('name_fa', 'بدون نام')
        price = cat.get('base_price', 0)
        label = f"{icon} {name}" if icon else name
        if price:
            label += f" ({price:,} تومان)"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"cat_{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("ایجاد دسته بندی جدید", callback_data="cat_create")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="catalog_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_category_actions_keyboard(category_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for category actions."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ویژگی ها", callback_data=f"cat_attrs_{category_id}")],
        [InlineKeyboardButton("پلن های طراحی", callback_data=f"cat_plans_{category_id}")],
        [InlineKeyboardButton("حذف دسته بندی", callback_data=f"cat_delete_{category_id}")],
        [InlineKeyboardButton("بازگشت", callback_data="catalog_categories")],
    ])


def get_attribute_list_keyboard(attributes: list, category_id: str) -> InlineKeyboardMarkup:
    """Get keyboard with list of attributes."""
    keyboard = []
    for attr in attributes:
        name = attr.get('name_fa', 'بدون نام')
        input_type = attr.get('input_type', '')
        keyboard.append([
            InlineKeyboardButton(f"{name} ({input_type})", callback_data=f"attr_{attr['id']}")
        ])
    keyboard.append([InlineKeyboardButton("ویژگی جدید", callback_data=f"attr_create_{category_id}")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data=f"cat_{category_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_attribute_actions_keyboard(attribute_id: str, category_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for attribute actions."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("گزینه ها", callback_data=f"attr_opts_{attribute_id}")],
        [InlineKeyboardButton("بازگشت", callback_data=f"cat_attrs_{category_id}")],
    ])


def get_option_list_keyboard(options: list, attribute_id: str) -> InlineKeyboardMarkup:
    """Get keyboard with list of options."""
    keyboard = []
    for opt in options:
        label = opt.get('label_fa', 'بدون نام')
        price = opt.get('price_modifier', 0)
        text = label
        if price:
            text += f" (+{price:,})"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"opt_{opt['id']}")
        ])
    keyboard.append([InlineKeyboardButton("گزینه جدید", callback_data=f"opt_create_{attribute_id}")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data=f"attr_{attribute_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_plan_list_keyboard(plans: list, category_id: str) -> InlineKeyboardMarkup:
    """Get keyboard with list of design plans."""
    keyboard = []
    for plan in plans:
        name = plan.get('name_fa', 'بدون نام')
        price = plan.get('price', 0)
        text = name
        if price:
            text += f" ({price:,} تومان)"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"plan_{plan['id']}")
        ])
    keyboard.append([InlineKeyboardButton("پلن جدید", callback_data=f"plan_create_{category_id}")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data=f"cat_{category_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_plan_actions_keyboard(plan_id: str, category_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for plan actions."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("سوالات پرسشنامه", callback_data=f"plan_questions_{plan_id}")],
        [InlineKeyboardButton("قالب ها", callback_data=f"plan_templates_{plan_id}")],
        [InlineKeyboardButton("بازگشت", callback_data=f"cat_plans_{category_id}")],
    ])


def get_input_type_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting attribute input type."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("انتخابی", callback_data="input_SELECT")],
        [InlineKeyboardButton("چند انتخابی", callback_data="input_MULTI_SELECT")],
        [InlineKeyboardButton("عددی", callback_data="input_NUMBER")],
        [InlineKeyboardButton("متنی", callback_data="input_TEXT")],
        [InlineKeyboardButton("انصراف", callback_data="cancel")],
    ])


def get_plan_type_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting design plan type."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("عمومی (قالب آماده)", callback_data="ptype_PUBLIC")],
        [InlineKeyboardButton("نیمه خصوصی (پرسشنامه)", callback_data="ptype_SEMI_PRIVATE")],
        [InlineKeyboardButton("خصوصی (آپلود فایل)", callback_data="ptype_PRIVATE")],
        [InlineKeyboardButton("انصراف", callback_data="cancel")],
    ])


def get_question_type_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting question input type."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("متنی", callback_data="qtype_TEXT")],
        [InlineKeyboardButton("تک انتخابی", callback_data="qtype_SINGLE_CHOICE")],
        [InlineKeyboardButton("چند انتخابی", callback_data="qtype_MULTI_CHOICE")],
        [InlineKeyboardButton("آپلود تصویر", callback_data="qtype_IMAGE_UPLOAD")],
        [InlineKeyboardButton("انتخاب رنگ", callback_data="qtype_COLOR_PICKER")],
        [InlineKeyboardButton("انصراف", callback_data="cancel")],
    ])


# ============== Order Keyboards ==============

def get_orders_menu_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for orders menu."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("سفارشات فعال", callback_data="orders_active")],
        [InlineKeyboardButton("سفارشات تکمیل شده", callback_data="orders_completed")],
        [InlineKeyboardButton("همه سفارشات", callback_data="orders_all")],
    ])


def get_order_actions_keyboard(order_id: str, can_cancel: bool = True, can_pay: bool = False) -> InlineKeyboardMarkup:
    """Get keyboard for order actions."""
    keyboard = []
    if can_pay:
        keyboard.append([InlineKeyboardButton("پرداخت", callback_data=f"order_pay_{order_id}")])
    if can_cancel:
        keyboard.append([InlineKeyboardButton("لغو سفارش", callback_data=f"order_cancel_{order_id}")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="orders_list")])
    return InlineKeyboardMarkup(keyboard)


# ============== Payment Keyboards ==============

def get_payment_keyboard(amount: int) -> InlineKeyboardMarkup:
    """Get keyboard for payment."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"پرداخت {amount:,} تومان", callback_data="pay_confirm")],
        [InlineKeyboardButton("انصراف", callback_data="pay_cancel")],
    ])


def get_receipt_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for receipt upload."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("انصراف", callback_data="receipt_cancel")],
    ])


# ============== Admin Payment Keyboards ==============

def get_pending_payments_keyboard(payments: list) -> InlineKeyboardMarkup:
    """Get keyboard with list of pending payments."""
    keyboard = []
    for payment in payments:
        amount = int(float(payment.get('amount', 0)))
        payment_id = payment.get('id', '')[:8]
        keyboard.append([
            InlineKeyboardButton(
                f"#{payment_id} - {amount:,} تومان",
                callback_data=f"payment_{payment.get('id')}"
            )
        ])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="back_to_admin")])
    return InlineKeyboardMarkup(keyboard)


def get_payment_review_keyboard(payment_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for reviewing a payment."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تایید", callback_data=f"approve_{payment_id}")],
        [InlineKeyboardButton("رد", callback_data=f"reject_{payment_id}")],
        [InlineKeyboardButton("بازگشت", callback_data="pending_list")],
    ])

