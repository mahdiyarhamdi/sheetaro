"""Schemas for print shop profiles and management."""

from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


# Predefined capabilities list
PRINTSHOP_CAPABILITIES = [
    "چاپ افست",
    "چاپ دیجیتال",
    "چاپ فلکسو",
    "چاپ سیلک",
    "لترپرس",
    "چاپ بزرگ (وایدفرمت)",
    "صحافی و بسته‌بندی",
    "لمینت و سلفون",
    "طلاکوب و نقره‌کوب",
    "برش و دایکات",
    "UV موضعی",
]


class PrintShopProfileCreate(BaseModel):
    """Schema for creating a printshop profile."""
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    max_daily_capacity: Optional[int] = Field(None, ge=1)
    service_areas: List[str] = Field(default_factory=list)


class PrintShopProfileUpdate(BaseModel):
    """Schema for updating a printshop profile."""
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    max_daily_capacity: Optional[int] = Field(None, ge=1)
    service_areas: Optional[List[str]] = None
    is_featured: Optional[bool] = None


class PrintShopProfileOut(BaseModel):
    """Schema for printshop profile output with user info."""
    id: UUID
    user_id: UUID
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    max_daily_capacity: Optional[int] = None
    service_areas: List[str] = Field(default_factory=list)
    is_featured: bool = False
    created_at: datetime
    updated_at: datetime
    # Joined user fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True
    user_created_at: Optional[datetime] = None
    # Computed fields
    avg_rating: Optional[float] = None
    review_count: int = 0
    total_orders: int = 0

    model_config = ConfigDict(from_attributes=True)


class PrintShopListItem(BaseModel):
    """Schema for printshop list item."""
    id: UUID  # user id
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    role: str
    is_active: bool = True
    created_at: datetime
    # Profile fields
    profile_id: Optional[UUID] = None
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    is_featured: bool = False
    # Computed
    avg_rating: Optional[float] = None
    review_count: int = 0
    total_orders: int = 0


class PrintShopListResponse(BaseModel):
    """Schema for paginated printshop list."""
    items: List[PrintShopListItem]
    total: int
    page: int
    page_size: int


class CreatePrintShopRequest(BaseModel):
    """Schema for admin to register a new printshop."""
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone_number: str = Field(..., min_length=11, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    city: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    max_daily_capacity: Optional[int] = Field(None, ge=1)
