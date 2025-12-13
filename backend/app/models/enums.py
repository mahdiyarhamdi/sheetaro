"""Central enums for Sheetaro application."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    CUSTOMER = "CUSTOMER"
    DESIGNER = "DESIGNER"
    VALIDATOR = "VALIDATOR"
    PRINT_SHOP = "PRINT_SHOP"
    ADMIN = "ADMIN"


class ProductType(str, Enum):
    """Product types."""
    LABEL = "LABEL"
    INVOICE = "INVOICE"


class MaterialType(str, Enum):
    """Material types for labels."""
    PAPER = "PAPER"
    PVC = "PVC"
    METALLIC = "METALLIC"


class DesignPlan(str, Enum):
    """Design plan types."""
    PUBLIC = "PUBLIC"
    SEMI_PRIVATE = "SEMI_PRIVATE"
    PRIVATE = "PRIVATE"
    OWN_DESIGN = "OWN_DESIGN"


class OrderStatus(str, Enum):
    """Order status values."""
    PENDING = "PENDING"
    AWAITING_VALIDATION = "AWAITING_VALIDATION"
    NEEDS_ACTION = "NEEDS_ACTION"
    DESIGNING = "DESIGNING"
    READY_FOR_PRINT = "READY_FOR_PRINT"
    PRINTING = "PRINTING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ValidationStatus(str, Enum):
    """Validation status values."""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    FIXED = "FIXED"


class PaymentType(str, Enum):
    """Payment types."""
    VALIDATION = "VALIDATION"
    DESIGN = "DESIGN"
    FIX = "FIX"
    PRINT = "PRINT"
    SUBSCRIPTION = "SUBSCRIPTION"


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    ADVANCED_SEARCH = "ADVANCED_SEARCH"

