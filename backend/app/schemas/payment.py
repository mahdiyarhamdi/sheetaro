"""Payment schemas."""

from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.models.enums import PaymentType, PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema."""
    order_id: UUID = Field(..., description="Order ID")
    type: PaymentType = Field(..., description="Payment type")
    amount: Decimal = Field(..., ge=0, description="Payment amount in Tomans")
    description: Optional[str] = Field(None, max_length=500, description="Payment description")


class PaymentInitiate(BaseModel):
    """Schema for initiating a payment."""
    order_id: UUID = Field(..., description="Order ID")
    type: Optional[PaymentType] = Field(None, description="Payment type (optional, defaults to FULL order payment)")
    callback_url: Optional[str] = Field(None, description="Callback URL after payment (optional for card-to-card)")


class PaymentInitiateResponse(BaseModel):
    """Response schema for payment initiation."""
    id: UUID  # Changed from payment_id to match frontend Payment interface
    authority: str
    redirect_url: str
    amount: Decimal
    
    @field_serializer('amount')
    def serialize_amount(self, value: Decimal) -> int:
        """Serialize amount as integer."""
        return int(value)


class PaymentCallback(BaseModel):
    """Schema for payment callback."""
    authority: str = Field(..., description="PSP authority")
    status: str = Field(..., description="Payment status from PSP")
    ref_id: Optional[str] = Field(None, description="Reference ID from PSP")


class PaymentVerify(BaseModel):
    """Schema for payment verification."""
    authority: str = Field(..., description="PSP authority")
    status: PaymentStatus = Field(..., description="New payment status")
    ref_id: Optional[str] = Field(None, description="Reference ID")
    card_pan: Optional[str] = Field(None, description="Masked card number")


class PaymentOut(BaseModel):
    """Schema for payment output."""
    id: UUID
    order_id: UUID
    user_id: UUID
    type: PaymentType
    amount: Decimal
    status: PaymentStatus
    transaction_id: Optional[str] = None
    authority: Optional[str] = None
    ref_id: Optional[str] = None
    card_pan: Optional[str] = None
    description: Optional[str] = None
    receipt_image_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('amount')
    def serialize_amount(self, value: Decimal) -> int:
        """Serialize amount as integer (no decimals for Iranian currency)."""
        return int(value)


class ReceiptUpload(BaseModel):
    """Schema for uploading payment receipt."""
    receipt_image_url: str = Field(..., max_length=500, description="URL of uploaded receipt image")


class PaymentApprove(BaseModel):
    """Schema for approving a payment (admin). Deprecated - admin_id comes from JWT."""
    admin_id: Optional[UUID] = Field(None, description="Admin user ID who approves (deprecated, comes from JWT)")


class PaymentReject(BaseModel):
    """Schema for rejecting a payment (admin)."""
    admin_id: Optional[UUID] = Field(None, description="Admin user ID who rejects (deprecated, comes from JWT)")
    reason: str = Field(..., max_length=500, description="Reason for rejection")


class PendingPaymentOut(PaymentOut):
    """Schema for pending payment with order info."""
    order_short_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_telegram_id: Optional[int] = None


class PaymentListResponse(BaseModel):
    """Response schema for payment list."""
    items: list[PaymentOut]
    total: int
    page: int
    page_size: int


class PaymentSummary(BaseModel):
    """Summary of payments for an order."""
    order_id: UUID
    total_paid: Decimal
    total_pending: Decimal
    payments: list[PaymentOut]
    
    @field_serializer('total_paid', 'total_pending')
    def serialize_amounts(self, value: Decimal) -> int:
        """Serialize amounts as integers."""
        return int(value)

