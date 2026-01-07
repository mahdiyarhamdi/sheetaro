"""Tests for keyboard consistency and emoji presence.

This module tests that all keyboards are properly consolidated
and have consistent emoji styling.
"""

import pytest
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton

# Import from the single source of truth
from keyboards.manager import (
    get_main_menu_keyboard,
    get_admin_menu_keyboard,
    get_back_keyboard,
    get_catalog_menu_keyboard,
    get_category_list_keyboard,
)


def get_button_texts(keyboard: ReplyKeyboardMarkup) -> list[str]:
    """Extract text from all buttons in a ReplyKeyboardMarkup."""
    texts = []
    for row in keyboard.keyboard:
        for btn in row:
            if isinstance(btn, KeyboardButton):
                texts.append(btn.text)
            elif isinstance(btn, str):
                texts.append(btn)
    return texts


class TestMainMenuKeyboard:
    """Tests for the main menu keyboard."""

    def test_main_menu_has_emojis(self):
        """Test that main menu buttons have emojis."""
        keyboard = get_main_menu_keyboard(is_admin=False)
        buttons = get_button_texts(keyboard)
        
        # Check that key buttons have emojis
        assert any("🛒" in btn for btn in buttons), "Should have order emoji"
        assert any("📦" in btn for btn in buttons), "Should have orders emoji"
        assert any("👤" in btn for btn in buttons), "Should have profile emoji"
        assert any("🔍" in btn for btn in buttons), "Should have tracking emoji"
        assert any("📞" in btn for btn in buttons), "Should have support emoji"
        assert any("ℹ️" in btn for btn in buttons), "Should have help emoji"

    def test_main_menu_customer_no_admin_button(self):
        """Test that non-admin users don't see admin panel button."""
        keyboard = get_main_menu_keyboard(is_admin=False)
        buttons = get_button_texts(keyboard)
        
        assert not any("پنل مدیریت" in btn for btn in buttons), \
            "Non-admin should not see admin panel button"

    def test_main_menu_admin_has_admin_button(self):
        """Test that admin users see admin panel button with emoji."""
        keyboard = get_main_menu_keyboard(is_admin=True)
        buttons = get_button_texts(keyboard)
        
        admin_button = [btn for btn in buttons if "پنل مدیریت" in btn]
        assert len(admin_button) == 1, "Admin should see admin panel button"
        assert "🔧" in admin_button[0], "Admin button should have emoji"

    def test_main_menu_returns_reply_keyboard(self):
        """Test that main menu returns ReplyKeyboardMarkup."""
        keyboard = get_main_menu_keyboard()
        assert isinstance(keyboard, ReplyKeyboardMarkup)

    def test_main_menu_resize_keyboard_enabled(self):
        """Test that resize_keyboard is enabled."""
        keyboard = get_main_menu_keyboard()
        assert keyboard.resize_keyboard is True


class TestAdminMenuKeyboard:
    """Tests for the admin menu keyboard."""

    def test_admin_menu_has_emojis(self):
        """Test that admin menu buttons have emojis."""
        keyboard = get_admin_menu_keyboard()
        buttons = get_button_texts(keyboard)
        
        # Check that all admin buttons have emojis
        assert any("💳" in btn for btn in buttons), "Should have payment emoji"
        assert any("📂" in btn for btn in buttons), "Should have catalog emoji"
        assert any("⚙️" in btn for btn in buttons), "Should have settings emoji"
        assert any("👥" in btn for btn in buttons), "Should have admins emoji"
        assert any("🔙" in btn for btn in buttons), "Should have back emoji"

    def test_admin_menu_has_back_button(self):
        """Test that admin menu has back button."""
        keyboard = get_admin_menu_keyboard()
        buttons = get_button_texts(keyboard)
        
        back_button = [btn for btn in buttons if "بازگشت" in btn]
        assert len(back_button) == 1, "Should have exactly one back button"

    def test_admin_menu_returns_reply_keyboard(self):
        """Test that admin menu returns ReplyKeyboardMarkup."""
        keyboard = get_admin_menu_keyboard()
        assert isinstance(keyboard, ReplyKeyboardMarkup)

    def test_admin_menu_button_count(self):
        """Test that admin menu has correct number of buttons."""
        keyboard = get_admin_menu_keyboard()
        buttons = get_button_texts(keyboard)
        assert len(buttons) == 5, "Admin menu should have 5 buttons"


class TestKeyboardConsistency:
    """Tests for keyboard consistency across the application."""

    def test_main_menu_buttons_contain_expected_text(self):
        """Test that main menu contains expected Persian text."""
        keyboard = get_main_menu_keyboard(is_admin=True)
        buttons = get_button_texts(keyboard)
        
        # Expected Persian texts (without emojis for flexibility)
        expected_texts = [
            "ثبت سفارش",
            "سفارشات من",
            "پروفایل",
            "رهگیری سفارش",
            "پشتیبانی",
            "راهنما",
            "پنل مدیریت"
        ]
        
        for text in expected_texts:
            assert any(text in btn for btn in buttons), \
                f"Main menu should contain '{text}'"

    def test_admin_menu_buttons_contain_expected_text(self):
        """Test that admin menu contains expected Persian text."""
        keyboard = get_admin_menu_keyboard()
        buttons = get_button_texts(keyboard)
        
        # Expected Persian texts
        expected_texts = [
            "پرداخت",
            "کاتالوگ",
            "تنظیمات",
            "مدیران",
            "بازگشت"
        ]
        
        for text in expected_texts:
            assert any(text in btn for btn in buttons), \
                f"Admin menu should contain '{text}'"

    def test_back_keyboard_has_text(self):
        """Test that back keyboard has proper text."""
        keyboard = get_back_keyboard()
        buttons = get_button_texts(keyboard)
        
        assert len(buttons) == 1, "Back keyboard should have 1 button"
        assert "بازگشت" in buttons[0], "Back button should contain 'بازگشت'"

    def test_catalog_menu_is_inline(self):
        """Test that catalog menu is inline keyboard."""
        keyboard = get_catalog_menu_keyboard()
        assert isinstance(keyboard, InlineKeyboardMarkup)


class TestNoLegacyImports:
    """Tests to ensure legacy keyboard files are not used."""

    def test_main_menu_import_path(self):
        """Test that get_main_menu_keyboard is imported from manager."""
        from keyboards import manager
        assert hasattr(manager, 'get_main_menu_keyboard')

    def test_admin_menu_import_path(self):
        """Test that get_admin_menu_keyboard is imported from manager."""
        from keyboards import manager
        assert hasattr(manager, 'get_admin_menu_keyboard')

    def test_main_menu_py_deleted(self):
        """Test that main_menu.py doesn't exist as a module with the function."""
        try:
            from keyboards import main_menu
            # If import works, check if get_main_menu_keyboard exists
            # It should not, as the file was deleted
            assert not hasattr(main_menu, 'get_main_menu_keyboard'), \
                "main_menu.py should be deleted or not have get_main_menu_keyboard"
        except ImportError:
            # This is expected - the file should be deleted
            pass


class TestCategoryListKeyboard:
    """Tests for category list keyboard."""

    def test_category_list_with_categories(self):
        """Test category list with sample categories."""
        categories = [
            {"id": "cat1", "name_fa": "برچسب", "icon": "🏷️", "base_price": 10000},
            {"id": "cat2", "name_fa": "کارت ویزیت", "icon": "💼", "base_price": 50000},
        ]
        
        keyboard = get_category_list_keyboard(categories)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Check that categories are in the keyboard
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                all_buttons.append(btn.text)
        
        assert any("برچسب" in btn for btn in all_buttons)
        assert any("کارت ویزیت" in btn for btn in all_buttons)

    def test_category_list_empty(self):
        """Test category list with no categories."""
        keyboard = get_category_list_keyboard([])
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Should still have create and back buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                all_buttons.append(btn.text)
        
        assert any("ایجاد" in btn for btn in all_buttons)
        assert any("بازگشت" in btn for btn in all_buttons)

