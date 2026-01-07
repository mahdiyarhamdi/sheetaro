"""Order schemas."""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.models.enums import DesignPlan, OrderStatus, ValidationStatus


class OrderBase(BaseModel):
    """Base order schema."""
    product_id: UUID = Field(..., description="Product ID")
    design_plan: DesignPlan = Field(..., description="Design plan type")
    quantity: int = Field(..., ge=1, description="Order quantity")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    customer_notes: Optional[str] = Field(None, max_length=1000, description="Customer notes")


class OrderCreate(OrderBase):
    """Schema for creating an order."""
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
    product_id: UUID
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


class OrderListResponse(BaseModel):
    """Response schema for order list."""
    items: list[OrderOut]
    total: int
    page: int
    page_size: int


class PrintShopOrderOut(OrderOut):
    """Order output for print shop view (includes customer info)."""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_city: Optional[str] = None





