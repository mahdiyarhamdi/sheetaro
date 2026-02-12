"""Order schemas."""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional, List

from app.models.enums import DesignPlan, OrderStatus, ValidationStatus


class SelectedAttributeItem(BaseModel):
    """Schema for a selected attribute with its option."""
    attribute_id: UUID = Field(..., description="Attribute ID")
    option_id: Optional[UUID] = Field(None, description="Selected option ID (for SELECT/MULTI_SELECT)")
    value: Optional[str] = Field(None, description="Value (for TEXT/NUMBER types)")
    price_modifier: int = Field(default=0, description="Price modifier from this selection")


class OrderBase(BaseModel):
    """Base order schema."""
    category_id: UUID = Field(..., description="Category ID")
    selected_attributes: List[SelectedAttributeItem] = Field(default_factory=list, description="Selected attributes with options")
    design_plan: DesignPlan = Field(..., description="Design plan type")
    quantity: int = Field(..., ge=1, description="Order quantity")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    customer_notes: Optional[str] = Field(None, max_length=1000, description="Customer notes")


class OrderCreate(OrderBase):
    """Schema for creating an order."""
    plan_id: Optional[UUID] = Field(None, description="Design plan ID from database")
    design_file_url: Optional[str] = Field(None, max_length=500, description="Design file URL (for OWN_DESIGN)")
    validation_requested: bool = Field(default=False, description="Request design validation")
    
    @field_validator('design_file_url')
    @classmethod
    def validate_design_file(cls, v: Optional[str], info) -> Optional[str]:
        """Validate design file is provided for OWN_DESIGN plan."""
        # Note: Full validation happens in service layer
        return v


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    quantity: Optional[int] = Field(None, ge=1, description="Order quantity")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    customer_notes: Optional[str] = Field(None, max_length=1000, description="Customer notes")
    design_file_url: Optional[str] = Field(None, max_length=500, description="Design file URL")


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus = Field(..., description="New order status")
    tracking_code: Optional[str] = Field(None, max_length=100, description="Shipping tracking code")
    admin_notes: Optional[str] = Field(None, description="Admin notes")


class OrderAssign(BaseModel):
    """Schema for assigning staff to order."""
    assigned_designer_id: Optional[UUID] = Field(None, description="Designer ID")
    assigned_validator_id: Optional[UUID] = Field(None, description="Validator ID")
    assigned_printshop_id: Optional[UUID] = Field(None, description="Print shop ID")


class OrderOut(BaseModel):
    """Schema for order output."""
    id: UUID
    user_id: UUID
    category_id: Optional[UUID] = None
    product_id: Optional[UUID] = None  # Legacy field - kept for backwards compatibility
    selected_attributes: List[SelectedAttributeItem] = Field(default_factory=list)
    design_plan: DesignPlan
    status: OrderStatus
    quantity: int
    design_file_url: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    validation_requested: bool
    assigned_designer_id: Optional[UUID] = None
    assigned_validator_id: Optional[UUID] = None
    assigned_printshop_id: Optional[UUID] = None
    revision_count: int
    max_revisions: Optional[int] = None
    base_price: Decimal = Decimal(0)  # Category base price at order time
    attributes_price: Decimal = Decimal(0)  # Sum of selected attribute price modifiers
    design_price: Decimal
    validation_price: Decimal
    fix_price: Decimal
    print_price: Decimal
    total_price: Decimal
    tracking_code: Optional[str] = None
    shipping_address: Optional[str] = None
    customer_notes: Optional[str] = None
    accepted_at: Optional[datetime] = None
    printed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EnrichedAttributeItem(BaseModel):
    """Human-readable attribute for display."""
    attribute_name: str = Field(..., description="Persian attribute name (e.g. اندازه)")
    value_name: str = Field(..., description="Persian option label (e.g. A4)")
    price: int = Field(default=0, description="Price modifier for this selection")


class CustomerOrderDetailOut(OrderOut):
    """Enriched order detail for the customer view (category name, attributes, design plan, etc.)."""
    design_plan_id: Optional[UUID] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    design_plan_label: Optional[str] = None
    template_name: Optional[str] = None
    enriched_attributes: List[EnrichedAttributeItem] = Field(default_factory=list)
    design_preview_url: Optional[str] = None
    design_final_url: Optional[str] = None
    payment_status: Optional[str] = None
    payment_paid_at: Optional[datetime] = None


class DesignerOrderOut(OrderOut):
    """Enriched order detail for designer view."""
    design_plan_id: Optional[UUID] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    design_plan_label: Optional[str] = None
    template_name: Optional[str] = None
    enriched_attributes: List[EnrichedAttributeItem] = Field(default_factory=list)
    design_preview_url: Optional[str] = None
    design_final_url: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None


class DesignerOrderListResponse(BaseModel):
    """Response for designer order list."""
    items: list[DesignerOrderOut]
    total: int
    page: int
    page_size: int


class DesignerStats(BaseModel):
    """Designer dashboard statistics."""
    total_assigned: int = 0
    in_progress: int = 0
    pending_upload: int = 0
    completed: int = 0
    queue_count: int = 0  # Orders waiting in PENDING_DESIGNER queue


class OrderListResponse(BaseModel):
    """Response schema for order list."""
    items: list[OrderOut]
    total: int
    page: int
    page_size: int


class PrintShopOrderOut(OrderOut):
    """Order output for print shop view (includes customer info + design preview + enriched data)."""
    # Customer info (joined from User)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_city: Optional[str] = None
    customer_address: Optional[str] = None
    # Design preview (from ProcessedDesign or design_file_url)
    design_preview_url: Optional[str] = None
    design_final_url: Optional[str] = None
    # Enriched product/category info
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    design_plan_label: Optional[str] = None
    template_name: Optional[str] = None
    # Enriched attributes (human-readable names resolved from IDs)
    enriched_attributes: List[EnrichedAttributeItem] = Field(default_factory=list)
    # Admin notes (not in base OrderOut for security)
    admin_notes: Optional[str] = None
    # Payment status
    payment_status: Optional[str] = None
    payment_paid_at: Optional[datetime] = None


class PrintShopOrderListResponse(BaseModel):
    """Response schema for print shop order list."""
    items: list[PrintShopOrderOut]
    total: int
    page: int
    page_size: int


class PrintShopShipRequest(BaseModel):
    """Schema for shipping an order with tracking code."""
    tracking_code: str = Field(..., min_length=5, max_length=100, description="Shipping tracking code")
    shipping_notes: Optional[str] = Field(None, max_length=500, description="Shipping notes")


class PrintShopStats(BaseModel):
    """Print shop dashboard statistics."""
    total_orders: int = 0
    pending_orders: int = 0         # READY_FOR_PRINT in queue
    in_progress_orders: int = 0     # PRINTING
    printed_orders: int = 0         # PRINTED
    shipped_orders: int = 0         # SHIPPED
    delivered_orders: int = 0       # DELIVERED
    avg_print_time_hours: Optional[float] = None
    avg_ship_time_hours: Optional[float] = None
    sla_compliance_percent: Optional[float] = None


class SettlementOut(BaseModel):
    """Settlement output schema."""
    id: UUID
    printshop_id: UUID
    period_start: str
    period_end: str
    total_orders: int
    total_revenue: Decimal
    platform_commission: Decimal
    net_amount: Decimal
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SettlementListResponse(BaseModel):
    """Response schema for settlement list."""
    items: list[SettlementOut]
    total: int
    page: int
    page_size: int










