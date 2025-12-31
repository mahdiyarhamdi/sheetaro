"""Models package."""

from app.models.enums import (
    UserRole,
    ProductType,
    MaterialType,
    DesignPlan,
    OrderStatus,
    ValidationStatus,
    PaymentType,
    PaymentStatus,
    SubscriptionPlan,
)
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.payment import Payment
from app.models.validation import ValidationReport
from app.models.invoice import Invoice
from app.models.subscription import Subscription
from app.models.settings import SystemSettings, SettingKeys

# Dynamic category models
from app.models.category import Category
from app.models.attribute import CategoryAttribute, AttributeOption, AttributeInputType
from app.models.design_plan import CategoryDesignPlan
from app.models.design_question import DesignQuestion, QuestionOption, QuestionInputType
from app.models.design_template import DesignTemplate
from app.models.order_step import OrderStepTemplate, OrderStep, StepType
from app.models.question_answer import QuestionAnswer

__all__ = [
    "User",
    "Product",
    "Order",
    "Payment",
    "ValidationReport",
    "Invoice",
    "Subscription",
    "SystemSettings",
    "SettingKeys",
    "UserRole",
    "ProductType",
    "MaterialType",
    "DesignPlan",
    "OrderStatus",
    "ValidationStatus",
    "PaymentType",
    "PaymentStatus",
    "SubscriptionPlan",
    # Dynamic category models
    "Category",
    "CategoryAttribute",
    "AttributeOption",
    "AttributeInputType",
    "CategoryDesignPlan",
    "DesignQuestion",
    "QuestionOption",
    "QuestionInputType",
    "DesignTemplate",
    "OrderStepTemplate",
    "OrderStep",
    "StepType",
    "QuestionAnswer",
]

