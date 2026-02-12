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
    # Payment statuses
    PENDING_PAYMENT = "PENDING_PAYMENT"  # Waiting for receipt upload
    PAYMENT_UPLOADED = "PAYMENT_UPLOADED"  # Receipt uploaded, awaiting admin approval
    PAYMENT_APPROVED = "PAYMENT_APPROVED"  # Payment approved by admin
    PAYMENT_REJECTED = "PAYMENT_REJECTED"  # Payment rejected by admin
    # Order processing statuses
    PENDING = "PENDING"
    AWAITING_VALIDATION = "AWAITING_VALIDATION"
    NEEDS_ACTION = "NEEDS_ACTION"
    PENDING_DESIGNER = "PENDING_DESIGNER"  # Waiting for a designer to accept (queue)
    DESIGNING = "DESIGNING"  # Designer accepted and is working on it
    READY_FOR_PRINT = "READY_FOR_PRINT"
    PRINTING = "PRINTING"
    PRINTED = "PRINTED"  # Print completed, awaiting shipment
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class SettlementStatus(str, Enum):
    """Settlement status values."""
    PENDING = "PENDING"
    PAID = "PAID"


class ValidationStatus(str, Enum):
    """Validation status values."""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    FIXED = "FIXED"


class PaymentType(str, Enum):
    """Payment types."""
    FULL = "FULL"  # Full order payment
    VALIDATION = "VALIDATION"
    DESIGN = "DESIGN"
    FIX = "FIX"
    PRINT = "PRINT"
    SUBSCRIPTION = "SUBSCRIPTION"


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "PENDING"  # Created, waiting for receipt upload
    AWAITING_APPROVAL = "AWAITING_APPROVAL"  # Receipt uploaded, waiting for admin approval
    SUCCESS = "SUCCESS"  # Approved by admin
    FAILED = "FAILED"  # Rejected by admin


class RevisionStatus(str, Enum):
    """Design revision review status."""
    PENDING_REVIEW = "PENDING_REVIEW"  # Designer uploaded, waiting for customer review
    APPROVED = "APPROVED"              # Customer approved the design
    REJECTED = "REJECTED"              # Customer rejected and requested changes


class ReviewType(str, Enum):
    """Target type for a customer review."""
    PRINTSHOP = "PRINTSHOP"
    DESIGNER = "DESIGNER"


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    ADVANCED_SEARCH = "ADVANCED_SEARCH"

