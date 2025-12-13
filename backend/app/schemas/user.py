from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID

from app.utils.validators import validate_iranian_phone


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, max_length=255, description="Telegram username")
    first_name: str = Field(..., max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    address: str | None = Field(None, description="User address")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Validate Iranian phone number format."""
        return validate_iranian_phone(v)


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: str | None = Field(None, max_length=255, description="Telegram username")
    first_name: str | None = Field(None, max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    address: str | None = Field(None, description="User address")
    bio: str | None = Field(None, description="User bio")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Validate Iranian phone number format."""
        return validate_iranian_phone(v)


class UserOut(UserBase):
    """Schema for user output."""
    id: UUID
    address: str | None = None
    bio: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

