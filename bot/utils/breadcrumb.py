"""Breadcrumb navigation system for admin menus.

This module provides a unified breadcrumb system that tracks the user's navigation path
and displays it at the end of each admin message for better UX.

Usage:
    from utils.breadcrumb import Breadcrumb, BreadcrumbPath

    # Initialize or update breadcrumb
    bc = Breadcrumb(context)
    bc.set_path(BreadcrumbPath.CATALOG_CATEGORIES)
    
    # Add dynamic item (like category name)
    bc.push("لیبل")
    
    # Get formatted message with breadcrumb
    message = bc.format_message("📂 لیست ویژگی‌ها:")
    
    # Go back one level
    bc.pop()
"""

from enum import Enum
from typing import Optional, List
from telegram.ext import ContextTypes


class BreadcrumbPath(Enum):
    """Predefined breadcrumb paths for admin menus."""
    
    # Root paths
    ADMIN_MENU = ("🔧 پنل مدیریت",)
    
    # Payment paths
    PAYMENTS_PENDING = ("🔧 پنل مدیریت", "💳 پرداخت‌ها")
    PAYMENT_REVIEW = ("🔧 پنل مدیریت", "💳 پرداخت‌ها", "بررسی پرداخت")
    
    # Admin management paths
    ADMIN_MANAGEMENT = ("🔧 پنل مدیریت", "👥 مدیران")
    ADMIN_INFO = ("🔧 پنل مدیریت", "👥 مدیران", "اطلاعات مدیر")
    ADMIN_ADD = ("🔧 پنل مدیریت", "👥 مدیران", "افزودن مدیر")
    
    # Settings paths
    SETTINGS = ("🔧 پنل مدیریت", "⚙️ تنظیمات کارت")
    SETTINGS_CARD_NUMBER = ("🔧 پنل مدیریت", "⚙️ تنظیمات کارت", "شماره کارت")
    SETTINGS_CARD_HOLDER = ("🔧 پنل مدیریت", "⚙️ تنظیمات کارت", "نام صاحب کارت")
    
    # Catalog paths
    CATALOG_MENU = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ")
    CATALOG_CATEGORIES = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")
    CATALOG_CATEGORY_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها", "➕ دسته جدید")
    
    # Category actions
    CATEGORY_VIEW = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category name
    CATEGORY_ATTRIBUTES = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category name + "ویژگی‌ها"
    CATEGORY_PLANS = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category name + "پلن‌ها"
    
    # Attribute paths (dynamic - add category and attribute names)
    ATTRIBUTE_VIEW = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "ویژگی‌ها" + attr
    ATTRIBUTE_OPTIONS = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "ویژگی‌ها" + attr + "گزینه‌ها"
    ATTRIBUTE_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "ویژگی‌ها" + "➕ ویژگی جدید"
    
    # Option paths (dynamic)
    OPTION_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + ... + "➕ گزینه جدید"
    
    # Plan paths (dynamic - add category and plan names)
    PLAN_VIEW = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "پلن‌ها" + plan
    PLAN_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "پلن‌ها" + "➕ پلن جدید"
    PLAN_QUESTIONNAIRE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "پلن‌ها" + plan + "پرسشنامه"
    PLAN_TEMPLATES = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + category + "پلن‌ها" + plan + "قالب‌ها"
    
    # Section paths (dynamic)
    SECTION_LIST = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "پرسشنامه" + "بخش‌ها"
    SECTION_VIEW = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "بخش‌ها" + section
    SECTION_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "➕ بخش جدید"
    
    # Question paths (dynamic)
    QUESTION_LIST = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "سوالات"
    QUESTION_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "➕ سوال جدید"
    
    # Template paths (dynamic)
    TEMPLATE_LIST = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "قالب‌ها"
    TEMPLATE_VIEW = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "قالب‌ها" + template
    TEMPLATE_CREATE = ("🔧 پنل مدیریت", "📂 مدیریت کاتالوگ", "دسته‌بندی‌ها")  # + ... + "➕ قالب جدید"


class Breadcrumb:
    """Breadcrumb navigation manager.
    
    Stores the navigation path in context.user_data['breadcrumb'] as a list of strings.
    """
    
    STORAGE_KEY = 'breadcrumb'
    SEPARATOR = " › "
    PREFIX = "\n\n📍 "
    
    def __init__(self, context: ContextTypes.DEFAULT_TYPE):
        """Initialize breadcrumb with context."""
        self.context = context
        if self.STORAGE_KEY not in context.user_data:
            context.user_data[self.STORAGE_KEY] = []
    
    @property
    def path(self) -> List[str]:
        """Get the current breadcrumb path."""
        return self.context.user_data.get(self.STORAGE_KEY, [])
    
    @path.setter
    def path(self, value: List[str]) -> None:
        """Set the breadcrumb path."""
        self.context.user_data[self.STORAGE_KEY] = value
    
    def clear(self) -> None:
        """Clear the breadcrumb path."""
        self.path = []
    
    def set_path(self, base: BreadcrumbPath, *extras: str) -> None:
        """Set the breadcrumb to a predefined path with optional extra items.
        
        Args:
            base: A predefined BreadcrumbPath
            extras: Additional path items to append
        """
        self.path = list(base.value) + list(extras)
    
    def push(self, item: str) -> None:
        """Add an item to the end of the breadcrumb path.
        
        Args:
            item: The item to add
        """
        path = self.path
        path.append(item)
        self.path = path
    
    def pop(self) -> Optional[str]:
        """Remove and return the last item from the breadcrumb path.
        
        Returns:
            The removed item, or None if path is empty
        """
        path = self.path
        if path:
            item = path.pop()
            self.path = path
            return item
        return None
    
    def go_back_to(self, item: str) -> bool:
        """Go back to a specific item in the path, removing everything after it.
        
        Args:
            item: The item to go back to
            
        Returns:
            True if the item was found and path was trimmed, False otherwise
        """
        path = self.path
        try:
            index = path.index(item)
            self.path = path[:index + 1]
            return True
        except ValueError:
            return False
    
    def replace_last(self, item: str) -> None:
        """Replace the last item in the breadcrumb path.
        
        Args:
            item: The new item to replace with
        """
        path = self.path
        if path:
            path[-1] = item
        else:
            path.append(item)
        self.path = path
    
    def get_display(self) -> str:
        """Get the formatted breadcrumb string for display.
        
        Returns:
            Formatted breadcrumb string like "📍 پنل مدیریت › کاتالوگ › دسته‌ها"
        """
        if not self.path:
            return ""
        return f"{self.PREFIX}{self.SEPARATOR.join(self.path)}"
    
    def format_message(self, message: str, include_breadcrumb: bool = True) -> str:
        """Format a message with the breadcrumb appended.
        
        Args:
            message: The main message text
            include_breadcrumb: Whether to include the breadcrumb
            
        Returns:
            Message with breadcrumb appended
        """
        if not include_breadcrumb:
            return message
        
        breadcrumb_display = self.get_display()
        if breadcrumb_display:
            return f"{message}{breadcrumb_display}"
        return message
    
    def __len__(self) -> int:
        """Return the length of the breadcrumb path."""
        return len(self.path)
    
    def __bool__(self) -> bool:
        """Return True if breadcrumb has any items."""
        return bool(self.path)
    
    def __str__(self) -> str:
        """Return the formatted breadcrumb display."""
        return self.get_display()
    
    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"Breadcrumb({self.path})"


def get_breadcrumb(context: ContextTypes.DEFAULT_TYPE) -> Breadcrumb:
    """Get or create a Breadcrumb instance for the context.
    
    Args:
        context: The telegram context
        
    Returns:
        Breadcrumb instance
    """
    return Breadcrumb(context)


def format_admin_message(
    context: ContextTypes.DEFAULT_TYPE,
    message: str,
    path: Optional[BreadcrumbPath] = None,
    *extras: str
) -> str:
    """Helper function to format an admin message with breadcrumb.
    
    Args:
        context: The telegram context
        message: The main message text
        path: Optional BreadcrumbPath to set
        extras: Additional path items to append
        
    Returns:
        Formatted message with breadcrumb
    """
    bc = get_breadcrumb(context)
    if path:
        bc.set_path(path, *extras)
    return bc.format_message(message)

