"""Authentication service for web users."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from redis import asyncio as aioredis

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenPayload
from app.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ConflictException,
    NotFoundException,
)


class AuthService:
    """Service for handling web authentication."""
    
    def __init__(self, db: AsyncSession, redis: Optional[aioredis.Redis] = None):
        """Initialize auth service."""
        self.db = db
        self.redis = redis
    
    async def register(self, data: RegisterRequest) -> User:
        """Register a new web user.
        
        Args:
            data: Registration data with phone, password, and full_name
            
        Returns:
            Created user
            
        Raises:
            ConflictException: If phone number already exists
        """
        # Check if phone already exists
        existing = await self._get_user_by_phone(data.phone)
        if existing:
            raise ConflictException("این شماره موبایل قبلاً ثبت شده است")
        
        # Create user
        name_parts = data.full_name.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else None
        
        user = User(
            phone_number=data.phone,
            password_hash=get_password_hash(data.password),
            first_name=first_name,
            last_name=last_name,
            full_name=data.full_name.strip(),
            phone_verified=False,
            web_linked=False,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def login(self, data: LoginRequest) -> User:
        """Authenticate user with phone and password.
        
        Args:
            data: Login data with phone and password
            
        Returns:
            Authenticated user
            
        Raises:
            UnauthorizedException: If credentials are invalid
        """
        user = await self._get_user_by_phone(data.phone)
        
        if not user:
            raise UnauthorizedException("شماره موبایل یا رمز عبور اشتباه است")
        
        if not user.password_hash:
            raise UnauthorizedException("این حساب فاقد رمز عبور است. از طریق تلگرام وارد شوید")
        
        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("شماره موبایل یا رمز عبور اشتباه است")
        
        if not user.is_active:
            raise UnauthorizedException("حساب کاربری شما غیرفعال شده است")
        
        return user
    
    def create_tokens(self, user: User) -> tuple[str, str]:
        """Create access and refresh tokens for user.
        
        Args:
            user: User to create tokens for
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        access_token = self._create_token(
            user_id=str(user.id),
            token_type="access",
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        refresh_token = self._create_token(
            user_id=str(user.id),
            token_type="refresh",
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        
        return access_token, refresh_token
    
    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str, User]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token, user)
            
        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        payload = self._verify_token(refresh_token, expected_type="refresh")
        if not payload:
            raise UnauthorizedException("توکن نامعتبر یا منقضی شده است")
        
        user = await self._get_user_by_id(UUID(payload.sub))
        if not user or not user.is_active:
            raise UnauthorizedException("کاربر یافت نشد یا غیرفعال است")
        
        access_token, new_refresh_token = self.create_tokens(user)
        return access_token, new_refresh_token, user
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from access token.
        
        Args:
            token: Access token
            
        Returns:
            Current user
            
        Raises:
            UnauthorizedException: If token is invalid or user not found
        """
        payload = self._verify_token(token, expected_type="access")
        if not payload:
            raise UnauthorizedException("توکن نامعتبر یا منقضی شده است")
        
        user = await self._get_user_by_id(UUID(payload.sub))
        if not user or not user.is_active:
            raise UnauthorizedException("کاربر یافت نشد یا غیرفعال است")
        
        return user
    
    async def generate_telegram_link_otp(self, user: User) -> tuple[str, datetime]:
        """Generate OTP for linking web account to Telegram.
        
        Args:
            user: User to generate OTP for
            
        Returns:
            Tuple of (otp, expires_at)
        """
        if not self.redis:
            raise BadRequestException("سرویس OTP در دسترس نیست")
        
        # Generate 6-digit OTP
        otp = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
        
        # Store in Redis with user_id
        key = f"telegram_link_otp:{otp}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        await self.redis.setex(
            key,
            settings.OTP_EXPIRE_MINUTES * 60,
            str(user.id),
        )
        
        return otp, expires_at
    
    async def verify_telegram_link(self, otp: str, telegram_id: int) -> User:
        """Verify OTP and link Telegram account to web user.
        
        Args:
            otp: OTP code
            telegram_id: Telegram user ID
            
        Returns:
            Updated user with linked Telegram
            
        Raises:
            BadRequestException: If OTP is invalid or expired
            ConflictException: If Telegram account already linked
        """
        if not self.redis:
            raise BadRequestException("سرویس OTP در دسترس نیست")
        
        # Get user_id from Redis
        key = f"telegram_link_otp:{otp}"
        user_id_str = await self.redis.get(key)
        
        if not user_id_str:
            raise BadRequestException("کد تایید نامعتبر یا منقضی شده است")
        
        user_id = UUID(user_id_str.decode() if isinstance(user_id_str, bytes) else user_id_str)
        
        # Check if telegram_id already linked to another account
        existing = await self._get_user_by_telegram_id(telegram_id)
        if existing and existing.id != user_id:
            raise ConflictException("این حساب تلگرام قبلاً به کاربر دیگری متصل شده است")
        
        # Get user and update
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundException("کاربر یافت نشد")
        
        user.telegram_id = telegram_id
        user.web_linked = True
        
        await self.db.commit()
        await self.db.refresh(user)
        
        # Delete OTP
        await self.redis.delete(key)
        
        return user
    
    def _create_token(
        self,
        user_id: str,
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        """Create a JWT token."""
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        
        to_encode = {
            "sub": user_id,
            "type": token_type,
            "exp": expire,
            "iat": now,
        }
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    def _verify_token(self, token: str, expected_type: str) -> Optional[TokenPayload]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            if payload.get("type") != expected_type:
                return None
            
            return TokenPayload(
                sub=payload["sub"],
                type=payload["type"],
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
        except JWTError:
            return None
    
    async def _get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number."""
        result = await self.db.execute(
            select(User).where(User.phone_number == phone)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

