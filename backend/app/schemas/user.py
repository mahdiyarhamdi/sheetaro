"""User schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID

from app.models.enums import UserRole
from app.utils.validators import validate_iranian_phone


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: int | None = Field(None, description="Telegram user ID")
    username: str | None = Field(None, max_length=255, description="Telegram username")
    first_name: str | None = Field(None, max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    city: str | None = Field(None, max_length=100, description="City")
    address: str | None = Field(None, description="User address")
    postal_code: str | None = Field(None, max_length=20, description="Postal code")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Validate Iranian phone number format."""
        return validate_iranian_phone(v)


class UserCreate(UserBase):
    """Schema for creating a user."""
    role: UserRole = Field(default=UserRole.CUSTOMER, description="User role")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: str | None = Field(None, max_length=255, description="Telegram username")
    full_name: str | None = Field(None, max_length=511, description="Full name")
    first_name: str | None = Field(None, max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    city: str | None = Field(None, max_length=100, description="City")
    address: str | None = Field(None, description="User address")
    postal_code: str | None = Field(None, max_length=20, description="Postal code")
    bio: str | None = Field(None, description="User bio")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")
    role: UserRole | None = Field(None, description="User role")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Validate Iranian phone number format."""
        return validate_iranian_phone(v)


class UserOut(UserBase):
    """Schema for user output."""
    id: UUID
    role: UserRole
    bio: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    """Schema for authenticated user updating their own profile."""
    full_name: str | None = Field(None, min_length=2, max_length=511, description="Full name")
    city: str | None = Field(None, max_length=100, description="City")
    address: str | None = Field(None, description="Address")
    postal_code: str | None = Field(None, max_length=20, description="Postal code")
    bio: str | None = Field(None, max_length=500, description="Bio")


# ============ Designer Management Schemas ============


class CreateDesignerRequest(BaseModel):
    """Schema for admin to register a new designer."""
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone_number: str = Field(..., min_length=11, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    city: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate Iranian phone number format."""
        return validate_iranian_phone(v)


class DesignerListItem(BaseModel):
    """Single designer item in list response."""
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    total_orders: int = 0
    in_progress_orders: int = 0
    completed_orders: int = 0
    avg_rating: Optional[float] = None
    review_count: int = 0


class DesignerListResponse(BaseModel):
    """Paginated response for designer list."""
    items: List[DesignerListItem]
    total: int
    page: int
    page_size: int
