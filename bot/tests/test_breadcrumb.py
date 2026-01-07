"""Tests for the breadcrumb navigation system."""

import pytest
from unittest.mock import MagicMock
from utils.breadcrumb import (
    Breadcrumb, BreadcrumbPath, get_breadcrumb, format_admin_message
)


class MockContext:
    """Mock Telegram context for testing."""
    
    def __init__(self):
        self.user_data = {}


class TestBreadcrumb:
    """Test Breadcrumb class functionality."""
    
    def test_init_creates_empty_path(self):
        """Test that initialization creates an empty breadcrumb path."""
        context = MockContext()
        bc = Breadcrumb(context)
        assert bc.path == []
        assert Breadcrumb.STORAGE_KEY in context.user_data
    
    def test_set_path_with_predefined_path(self):
        """Test setting a predefined breadcrumb path."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        assert bc.path == ["🔧 پنل مدیریت"]
    
    def test_set_path_with_extras(self):
        """Test setting a path with extra items."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل", "پلن‌ها")
        assert bc.path == ["🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها", "لیبل", "پلن‌ها"]
    
    def test_push_adds_item(self):
        """Test that push adds an item to the path."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        bc.push("مدیریت کاتالوگ")
        assert bc.path[-1] == "مدیریت کاتالوگ"
        assert len(bc) == 2
    
    def test_pop_removes_and_returns_last_item(self):
        """Test that pop removes and returns the last item."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
        item = bc.pop()
        assert item == "دسته‌بندی‌ها"
        assert "دسته‌بندی‌ها" not in bc.path
    
    def test_pop_on_empty_path_returns_none(self):
        """Test that pop on empty path returns None."""
        context = MockContext()
        bc = Breadcrumb(context)
        item = bc.pop()
        assert item is None
    
    def test_clear_removes_all_items(self):
        """Test that clear removes all items from path."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل")
        bc.clear()
        assert bc.path == []
    
    def test_go_back_to_existing_item(self):
        """Test going back to an existing item in path."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل", "پلن‌ها", "عمومی")
        result = bc.go_back_to("لیبل")
        assert result is True
        assert bc.path[-1] == "لیبل"
        assert "پلن‌ها" not in bc.path
    
    def test_go_back_to_nonexistent_item(self):
        """Test going back to a non-existent item returns False."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
        result = bc.go_back_to("non_existent")
        assert result is False
    
    def test_replace_last(self):
        """Test replacing the last item in path."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل")
        bc.replace_last("فاکتور")
        assert bc.path[-1] == "فاکتور"
    
    def test_replace_last_on_empty_adds_item(self):
        """Test replace_last on empty path adds the item."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.replace_last("test")
        assert bc.path == ["test"]
    
    def test_get_display_returns_formatted_string(self):
        """Test that get_display returns properly formatted breadcrumb."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل")
        display = bc.get_display()
        assert "📍" in display
        assert " › " in display
        assert "لیبل" in display
    
    def test_get_display_empty_path_returns_empty_string(self):
        """Test that get_display on empty path returns empty string."""
        context = MockContext()
        bc = Breadcrumb(context)
        assert bc.get_display() == ""
    
    def test_format_message_appends_breadcrumb(self):
        """Test that format_message appends breadcrumb to message."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        message = bc.format_message("سلام")
        assert "سلام" in message
        assert "📍" in message
        assert "پنل مدیریت" in message
    
    def test_format_message_without_breadcrumb(self):
        """Test format_message with include_breadcrumb=False."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        message = bc.format_message("سلام", include_breadcrumb=False)
        assert message == "سلام"
        assert "📍" not in message
    
    def test_len_returns_path_length(self):
        """Test that __len__ returns correct path length."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "item1", "item2")
        assert len(bc) == 5  # 3 from path + 2 extras
    
    def test_bool_true_when_has_items(self):
        """Test that __bool__ returns True when path has items."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.push("item")
        assert bool(bc) is True
    
    def test_bool_false_when_empty(self):
        """Test that __bool__ returns False when path is empty."""
        context = MockContext()
        bc = Breadcrumb(context)
        assert bool(bc) is False
    
    def test_str_returns_display(self):
        """Test that __str__ returns the display string."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        assert str(bc) == bc.get_display()
    
    def test_repr_shows_path(self):
        """Test that __repr__ shows the path for debugging."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.push("test")
        assert "Breadcrumb" in repr(bc)
        assert "test" in repr(bc)


class TestBreadcrumbPath:
    """Test BreadcrumbPath enum values."""
    
    def test_admin_menu_path(self):
        """Test ADMIN_MENU path value."""
        assert BreadcrumbPath.ADMIN_MENU.value == ("🔧 پنل مدیریت",)
    
    def test_catalog_menu_path(self):
        """Test CATALOG_MENU path value."""
        assert BreadcrumbPath.CATALOG_MENU.value == ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ")
    
    def test_catalog_categories_path(self):
        """Test CATALOG_CATEGORIES path value."""
        path = BreadcrumbPath.CATALOG_CATEGORIES.value
        assert "🔧 پنل مدیریت" in path
        assert "📂 مدیریت کاتالوگ" in path
        assert "دسته‌بندی‌ها" in path
    
    def test_payments_path(self):
        """Test PAYMENTS_PENDING path value."""
        path = BreadcrumbPath.PAYMENTS_PENDING.value
        assert "💳 پرداخت‌ها" in path
    
    def test_settings_path(self):
        """Test SETTINGS path value."""
        path = BreadcrumbPath.SETTINGS.value
        assert "⚙️ تنظیمات کارت" in path


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_get_breadcrumb_returns_instance(self):
        """Test that get_breadcrumb returns a Breadcrumb instance."""
        context = MockContext()
        bc = get_breadcrumb(context)
        assert isinstance(bc, Breadcrumb)
    
    def test_get_breadcrumb_same_context_same_data(self):
        """Test that multiple calls with same context share data."""
        context = MockContext()
        bc1 = get_breadcrumb(context)
        bc1.push("test")
        bc2 = get_breadcrumb(context)
        assert "test" in bc2.path
    
    def test_format_admin_message_basic(self):
        """Test format_admin_message basic usage."""
        context = MockContext()
        message = format_admin_message(
            context, 
            "سلام",
            BreadcrumbPath.ADMIN_MENU
        )
        assert "سلام" in message
        assert "پنل مدیریت" in message
    
    def test_format_admin_message_with_extras(self):
        """Test format_admin_message with extra path items."""
        context = MockContext()
        message = format_admin_message(
            context,
            "لیست دسته‌ها",
            BreadcrumbPath.CATALOG_CATEGORIES,
            "لیبل"
        )
        assert "لیست دسته‌ها" in message
        assert "لیبل" in message
    
    def test_format_admin_message_without_path(self):
        """Test format_admin_message without setting path."""
        context = MockContext()
        # First set a path
        bc = get_breadcrumb(context)
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        
        # Then format without specifying new path - should use existing
        message = format_admin_message(context, "test message")
        assert "test message" in message
        assert "پنل مدیریت" in message


class TestBreadcrumbNavigation:
    """Test breadcrumb for realistic navigation scenarios."""
    
    def test_catalog_navigation_flow(self):
        """Test a typical catalog navigation flow."""
        context = MockContext()
        bc = Breadcrumb(context)
        
        # Start at admin menu
        bc.set_path(BreadcrumbPath.ADMIN_MENU)
        assert len(bc) == 1
        
        # Go to catalog
        bc.set_path(BreadcrumbPath.CATALOG_MENU)
        assert any("مدیریت کاتالوگ" in item for item in bc.path)
        
        # Go to categories
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
        
        # Select a category
        bc.push("لیبل")
        assert bc.path[-1] == "لیبل"
        
        # Go to plans
        bc.push("پلن‌ها")
        
        # Select a plan
        bc.push("نیمه‌خصوصی")
        
        # Go to questionnaire
        bc.push("پرسشنامه")
        
        # Check full path
        display = bc.get_display()
        assert "پنل مدیریت" in display
        assert "لیبل" in display
        assert "پرسشنامه" in display
    
    def test_back_navigation(self):
        """Test navigating back through the breadcrumb."""
        context = MockContext()
        bc = Breadcrumb(context)
        
        # Build deep path
        bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES, "لیبل", "پلن‌ها", "عمومی", "قالب‌ها")
        
        # Go back one level
        bc.pop()
        assert bc.path[-1] == "عمومی"
        
        # Go back to specific item
        bc.go_back_to("لیبل")
        assert bc.path[-1] == "لیبل"
        assert "پلن‌ها" not in bc.path
    
    def test_payment_flow(self):
        """Test payment review flow breadcrumb."""
        context = MockContext()
        bc = Breadcrumb(context)
        
        # Go to pending payments
        bc.set_path(BreadcrumbPath.PAYMENTS_PENDING)
        
        # Select a payment
        bc.push("#abc123")
        
        display = bc.get_display()
        assert "پرداخت" in display
        assert "#abc123" in display
    
    def test_question_creation_flow(self):
        """Test question creation breadcrumb path."""
        context = MockContext()
        bc = Breadcrumb(context)
        
        # Navigate to question creation
        bc.set_path(
            BreadcrumbPath.CATALOG_CATEGORIES,
            "لیبل",  # category
            "پلن‌ها",
            "نیمه‌خصوصی",  # plan
            "پرسشنامه",
            "➕ سوال جدید"
        )
        
        display = bc.get_display()
        assert "سوال جدید" in display
        assert "نیمه‌خصوصی" in display
        
        # After creation, go back to questionnaire
        bc.pop()
        assert bc.path[-1] == "پرسشنامه"


class TestBreadcrumbEdgeCases:
    """Test edge cases and error handling."""
    
    def test_multiple_pops_on_short_path(self):
        """Test popping more times than path length."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.push("only_item")
        
        bc.pop()
        bc.pop()  # Should return None
        bc.pop()  # Should return None
        
        assert bc.path == []
    
    def test_unicode_in_path(self):
        """Test handling of Persian/Unicode characters."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.push("سلام 🎉")
        bc.push("تست ✅")
        
        assert "سلام 🎉" in bc.path
        assert "تست ✅" in bc.get_display()
    
    def test_empty_string_push(self):
        """Test pushing empty string."""
        context = MockContext()
        bc = Breadcrumb(context)
        bc.push("")
        assert "" in bc.path
        assert len(bc) == 1
    
    def test_very_long_path(self):
        """Test handling of very long paths."""
        context = MockContext()
        bc = Breadcrumb(context)
        
        for i in range(20):
            bc.push(f"level_{i}")
        
        assert len(bc) == 20
        display = bc.get_display()
        assert "level_19" in display

