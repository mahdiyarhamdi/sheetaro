"""Payment schemas."""

from pydantic import BaseModel, Field, ConfigDict
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
    type: PaymentType = Field(..., description="Payment type")
    callback_url: str = Field(..., description="Callback URL after payment")


class PaymentInitiateResponse(BaseModel):
    """Response schema for payment initiation."""
    payment_id: UUID
    authority: str
    redirect_url: str
    amount: Decimal


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


class ReceiptUpload(BaseModel):
    """Schema for uploading payment receipt."""
    receipt_image_url: str = Field(..., max_length=500, description="URL of uploaded receipt image")


class PaymentApprove(BaseModel):
    """Schema for approving a payment (admin)."""
    admin_id: UUID = Field(..., description="Admin user ID who approves")


class PaymentReject(BaseModel):
    """Schema for rejecting a payment (admin)."""
    admin_id: UUID = Field(..., description="Admin user ID who rejects")
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

