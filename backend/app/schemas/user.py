from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, max_length=255, description="Telegram username")
    first_name: str = Field(..., max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: str | None = Field(None, max_length=255, description="Telegram username")
    first_name: str | None = Field(None, max_length=255, description="First name")
    last_name: str | None = Field(None, max_length=255, description="Last name")
    phone_number: str | None = Field(None, max_length=20, description="Phone number")
    bio: str | None = Field(None, description="User bio")
    profile_photo_url: str | None = Field(None, max_length=500, description="Profile photo URL")


class UserOut(UserBase):
    """Schema for user output."""
    id: UUID
    bio: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

