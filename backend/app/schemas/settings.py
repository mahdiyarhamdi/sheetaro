"""Settings schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class SettingBase(BaseModel):
    """Base setting schema."""
    key: str = Field(..., max_length=100, description="Setting key")
    value: str = Field(..., max_length=1000, description="Setting value")


class SettingUpdate(BaseModel):
    """Schema for updating a setting."""
    value: str = Field(..., max_length=1000, description="New setting value")


class SettingOut(SettingBase):
    """Schema for setting output."""
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaymentCardInfo(BaseModel):
    """Schema for payment card information."""
    card_number: str = Field(..., min_length=16, max_length=16, description="Card number (16 digits)")
    card_holder: str = Field(..., min_length=2, max_length=100, description="Card holder name")


class PaymentCardInfoOut(BaseModel):
    """Schema for payment card information output."""
    card_number: str
    card_holder: str
    updated_at: Optional[datetime] = None


class PaymentCardUpdate(BaseModel):
    """Schema for updating payment card information."""
    card_number: Optional[str] = Field(None, min_length=16, max_length=16, description="Card number (16 digits)")
    card_holder: Optional[str] = Field(None, min_length=2, max_length=100, description="Card holder name")

