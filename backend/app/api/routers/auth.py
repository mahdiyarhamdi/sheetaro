"""Authentication router for web users."""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TelegramLinkResponse,
    TelegramVerifyRequest,
    TelegramVerifyResponse,
    AuthResponse,
    UserResponse,
)
from app.exceptions import UnauthorizedException
from app.utils.logger import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_redis() -> Optional[aioredis.Redis]:
    """Get Redis connection."""
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        return redis
    except Exception:
        return None


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: Optional[aioredis.Redis] = Depends(get_redis),
) -> AuthService:
    """Get auth service instance."""
    return AuthService(db, redis)


def get_token_from_header(authorization: str = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization:
        raise UnauthorizedException("توکن احراز هویت ارسال نشده است")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("فرمت توکن نامعتبر است")
    
    return parts[1]


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new web user.
    
    - **phone**: Iranian phone number (e.g., 09123456789)
    - **password**: At least 6 characters
    - **full_name**: User's full name
    """
    user = await auth_service.register(data)
    access_token, refresh_token = auth_service.create_tokens(user)
    
    log_event(
        "user_registered",
        user_id=str(user.id),
        phone=data.phone,
        method="web",
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Login with phone and password.
    
    - **phone**: Registered phone number
    - **password**: User's password
    """
    user = await auth_service.login(data)
    access_token, refresh_token = auth_service.create_tokens(user)
    
    log_event(
        "user_login",
        user_id=str(user.id),
        phone=data.phone,
        method="web",
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token from previous login
    """
    access_token, new_refresh_token, user = await auth_service.refresh_tokens(
        data.refresh_token
    )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get current authenticated user.
    
    Requires Bearer token in Authorization header.
    """
    user = await auth_service.get_current_user(token)
    return UserResponse.model_validate(user)


@router.post("/telegram-link", response_model=TelegramLinkResponse)
async def generate_telegram_link(
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Generate OTP code for linking Telegram account.
    
    The OTP code should be entered in the Telegram bot using /linkweb command.
    The code expires in 5 minutes.
    """
    user = await auth_service.get_current_user(token)
    otp, expires_at = await auth_service.generate_telegram_link_otp(user)
    
    log_event(
        "telegram_link_requested",
        user_id=str(user.id),
    )
    
    return TelegramLinkResponse(
        otp=otp,
        expires_at=expires_at,
        message="این کد را در ربات تلگرام با دستور /linkweb وارد کنید",
    )


@router.post("/telegram-verify", response_model=TelegramVerifyResponse)
async def verify_telegram_link(
    data: TelegramVerifyRequest,
    telegram_id: int = Header(..., alias="X-Telegram-ID"),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Verify OTP and link Telegram account.
    
    This endpoint is called by the Telegram bot when user enters the OTP.
    
    - **otp**: 6-digit OTP code
    - **X-Telegram-ID**: Telegram user ID (sent by bot)
    """
    user = await auth_service.verify_telegram_link(data.otp, telegram_id)
    
    log_event(
        "telegram_linked",
        user_id=str(user.id),
        telegram_id=telegram_id,
    )
    
    return TelegramVerifyResponse(
        success=True,
        telegram_id=telegram_id,
        message="حساب تلگرام با موفقیت متصل شد",
    )

