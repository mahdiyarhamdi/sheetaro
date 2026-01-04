"""Product schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.models.enums import ProductType, MaterialType


class ProductBase(BaseModel):
    """Base product schema."""
    type: ProductType = Field(..., description="Product type (LABEL or INVOICE)")
    name: str = Field(..., max_length=255, description="Product name")
    name_fa: Optional[str] = Field(None, max_length=255, description="Persian product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    size: str = Field(..., max_length=50, description="Product size (e.g., '5x5cm', 'A5')")
    material: Optional[MaterialType] = Field(None, description="Material type (for labels only)")
    base_price: Decimal = Field(..., ge=0, description="Base price in Tomans")
    min_quantity: Decimal = Field(default=1, ge=1, description="Minimum order quantity")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    is_active: bool = Field(default=True, description="Product active status")
    sort_order: int = Field(default=0, ge=0, description="Display order")


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, max_length=255, description="Product name")
    name_fa: Optional[str] = Field(None, max_length=255, description="Persian product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    size: Optional[str] = Field(None, max_length=50, description="Product size")
    material: Optional[MaterialType] = Field(None, description="Material type")
    base_price: Optional[Decimal] = Field(None, ge=0, description="Base price in Tomans")
    min_quantity: Optional[Decimal] = Field(None, ge=1, description="Minimum order quantity")
    is_active: Optional[bool] = Field(None, description="Product active status")
    sort_order: Optional[int] = Field(None, ge=0, description="Display order")


class ProductOut(ProductBase):
    """Schema for product output."""
    id: UUID
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Response schema for product list."""
    items: list[ProductOut]
    total: int
    page: int
    page_size: int




