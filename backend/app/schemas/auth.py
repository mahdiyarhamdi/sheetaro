"""Auth schemas for web authentication."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
import re


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    
    phone: str = Field(..., description="Phone number in format 09XXXXXXXXX")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize Iranian phone number."""
        # Remove any non-digit characters
        cleaned = re.sub(r"\D", "", v)
        
        # Handle different formats
        if cleaned.startswith("98"):
            cleaned = "0" + cleaned[2:]
        elif cleaned.startswith("9") and len(cleaned) == 10:
            cleaned = "0" + cleaned
        
        # Validate format
        if not re.match(r"^09\d{9}$", cleaned):
            raise ValueError("شماره موبایل نامعتبر است. فرمت صحیح: 09123456789")
        
        return cleaned


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        cleaned = re.sub(r"\D", "", v)
        if cleaned.startswith("98"):
            cleaned = "0" + cleaned[2:]
        elif cleaned.startswith("9") and len(cleaned) == 10:
            cleaned = "0" + cleaned
        return cleaned


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    
    refresh_token: str = Field(..., description="Refresh token")


class TelegramLinkResponse(BaseModel):
    """Response schema for telegram link OTP generation."""
    
    otp: str = Field(..., description="6-digit OTP code")
    expires_at: datetime = Field(..., description="OTP expiration time")
    message: str = Field(default="کد تایید را در ربات تلگرام وارد کنید")


class TelegramVerifyRequest(BaseModel):
    """Request schema for verifying telegram link."""
    
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class TelegramVerifyResponse(BaseModel):
    """Response schema for telegram verification."""
    
    success: bool
    telegram_id: int | None = None
    message: str


class UserResponse(BaseModel):
    """Response schema for user data."""
    
    id: UUID
    phone: str | None = Field(None, alias="phone_number")
    full_name: str | None
    first_name: str
    last_name: str | None
    telegram_id: int | None
    is_admin: bool
    role: str | None = None
    phone_verified: bool
    web_linked: bool
    city: str | None = None
    address: str | None = None
    postal_code: str | None = None
    bio: str | None = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response schema for authentication."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload."""
    
    sub: str  # user_id
    type: str  # "access" or "refresh"
    exp: datetime

