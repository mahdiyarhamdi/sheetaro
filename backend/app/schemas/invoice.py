"""Invoice schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from typing import Optional


class InvoiceItem(BaseModel):
    """Schema for an invoice line item."""
    description: str = Field(..., max_length=500, description="Item description")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price in Tomans")
    total: Decimal = Field(..., ge=0, description="Total price")


class InvoiceCreate(BaseModel):
    """Schema for creating an invoice."""
    order_id: UUID = Field(..., description="Order ID")
    customer_name: str = Field(..., max_length=255, description="Customer name on invoice")
    customer_code: Optional[str] = Field(None, max_length=50, description="Customer code")
    customer_address: Optional[str] = Field(None, description="Customer address")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_national_id: Optional[str] = Field(None, max_length=20, description="National ID")
    items: list[InvoiceItem] = Field(..., min_length=1, description="Invoice line items")
    tax_amount: Decimal = Field(default=0, ge=0, description="Tax amount")
    discount_amount: Decimal = Field(default=0, ge=0, description="Discount amount")
    issue_date: date = Field(..., description="Invoice issue date")
    notes: Optional[str] = Field(None, description="Invoice notes")


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    customer_name: Optional[str] = Field(None, max_length=255, description="Customer name")
    customer_code: Optional[str] = Field(None, max_length=50, description="Customer code")
    customer_address: Optional[str] = Field(None, description="Customer address")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_national_id: Optional[str] = Field(None, max_length=20, description="National ID")
    items: Optional[list[InvoiceItem]] = Field(None, description="Invoice line items")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Tax amount")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    notes: Optional[str] = Field(None, description="Invoice notes")


class InvoiceOut(BaseModel):
    """Schema for invoice output."""
    id: UUID
    order_id: UUID
    user_id: UUID
    invoice_number: str
    customer_name: str
    customer_code: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_national_id: Optional[str] = None
    items: list[InvoiceItem]
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    issue_date: date
    pdf_file_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    """Response schema for invoice list."""
    items: list[InvoiceOut]
    total: int
    page: int
    page_size: int


class InvoiceSearchParams(BaseModel):
    """Search parameters for invoices."""
    customer_name: Optional[str] = Field(None, description="Customer name")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    date_from: Optional[date] = Field(None, description="From date")
    date_to: Optional[date] = Field(None, description="To date")
    amount_min: Optional[Decimal] = Field(None, description="Minimum amount")
    amount_max: Optional[Decimal] = Field(None, description="Maximum amount")




