"""API dependencies for authentication and authorization."""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import Header, HTTPException, status, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.models.enums import UserRole
from app.models.user import User


class AuthenticatedUser:
    """Represents an authenticated user with role information."""
    
    def __init__(
        self,
        user_id: UUID,
        telegram_id: int,
        role: UserRole,
        username: Optional[str] = None,
    ):
        self.user_id = user_id
        self.telegram_id = telegram_id
        self.role = role
        self.username = username
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_designer(self) -> bool:
        """Check if user is designer."""
        return self.role == UserRole.DESIGNER
    
    @property
    def is_validator(self) -> bool:
        """Check if user is validator."""
        return self.role == UserRole.VALIDATOR
    
    @property
    def is_print_shop(self) -> bool:
        """Check if user is print shop."""
        return self.role == UserRole.PRINT_SHOP
    
    @property
    def is_staff(self) -> bool:
        """Check if user is any staff role (not customer)."""
        return self.role in [
            UserRole.ADMIN,
            UserRole.DESIGNER,
            UserRole.VALIDATOR,
            UserRole.PRINT_SHOP,
        ]


async def get_optional_user(
    user_id: Optional[UUID] = Query(None, description="User ID"),
    telegram_id: Optional[int] = Query(None, description="Telegram ID"),
    db: AsyncSession = Depends(get_db),
) -> Optional[AuthenticatedUser]:
    """
    Get optional authenticated user from query params.
    Returns None if no user info provided.
    """
    if not user_id and not telegram_id:
        return None
    
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    user = None
    if user_id:
        user = await repo.get_by_id(user_id)
    elif telegram_id:
        user = await repo.get_by_telegram_id(telegram_id)
    
    if not user:
        return None
    
    return AuthenticatedUser(
        user_id=user.id,
        telegram_id=user.telegram_id,
        role=user.role,
        username=user.username,
    )


async def get_current_user(
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Get current authenticated user. Raises 401 if not found.
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    
    return AuthenticatedUser(
        user_id=user.id,
        telegram_id=user.telegram_id,
        role=user.role,
        username=user.username,
    )


async def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Require admin role. Raises 403 if user is not admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_staff(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Require any staff role (admin, designer, validator, print_shop).
    Raises 403 if user is customer.
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )
    return current_user


async def require_designer(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Require designer or admin role. Raises 403 otherwise.
    """
    if not (current_user.is_designer or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Designer access required",
        )
    return current_user


async def require_validator(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Require validator or admin role. Raises 403 otherwise.
    """
    if not (current_user.is_validator or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Validator access required",
        )
    return current_user


async def require_print_shop(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Require print shop or admin role. Raises 403 otherwise.
    """
    if not (current_user.is_print_shop or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Print shop access required",
        )
    return current_user


async def require_designer_hybrid(
    authorization: Optional[str] = Header(None),
    designer_id: Optional[UUID] = Query(None, description="Designer user ID (for bot)"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Require designer or admin role using either JWT token or designer_id query param.
    Supports both web frontend (JWT) and bot (query param).
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)

    # 1. Try JWT token first
    if authorization and authorization.lower().startswith("bearer "):
        try:
            parts = authorization.split()
            if len(parts) == 2:
                token = parts[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                if payload.get("type") != "access":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                token_user_id = payload.get("sub")
                if not token_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن منقضی شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                user = await repo.get_by_id(UUID(token_user_id))
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="کاربر یافت نشد",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="حساب کاربری غیرفعال شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                if user.role not in [UserRole.DESIGNER, UserRole.ADMIN]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="دسترسی طراح یا ادمین لازم است",
                    )

                return AuthenticatedUser(
                    user_id=user.id,
                    telegram_id=user.telegram_id,
                    role=user.role,
                    username=user.username,
                )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Fall back to query param (for bot)
    if designer_id:
        user = await repo.get_by_id(designer_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="کاربر طراح یافت نشد",
            )

        if user.role not in [UserRole.DESIGNER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="دسترسی طراح لازم است",
            )

        return AuthenticatedUser(
            user_id=user.id,
            telegram_id=user.telegram_id,
            role=user.role,
            username=user.username,
        )

    # 3. Neither provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="احراز هویت لازم است. توکن یا designer_id ارسال کنید.",
    )


async def require_admin_by_query(
    admin_id: UUID = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Require admin role using admin_id query param.
    Legacy support for existing endpoints.
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    user = await repo.get_by_id(admin_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
        )
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return AuthenticatedUser(
        user_id=user.id,
        telegram_id=user.telegram_id,
        role=user.role,
        username=user.username,
    )


async def require_admin_hybrid(
    authorization: Optional[str] = Header(None),
    admin_id: Optional[UUID] = Query(None, description="Admin user ID (for bot)"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Require admin role using either JWT token or admin_id query param.
    Supports both web frontend (JWT) and bot (query param).
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    # 1. Try JWT token first if Authorization header exists
    if authorization and authorization.lower().startswith("bearer "):
        try:
            parts = authorization.split()
            if len(parts) == 2:
                token = parts[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                if payload.get("type") != "access":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                token_user_id = payload.get("sub")
                if not token_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Check expiration
                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن منقضی شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Get user and verify admin role
                user = await repo.get_by_id(UUID(token_user_id))
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="کاربر یافت نشد",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="حساب کاربری غیرفعال شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if user.role != UserRole.ADMIN:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="دسترسی ادمین لازم است",
                    )
                
                return AuthenticatedUser(
                    user_id=user.id,
                    telegram_id=user.telegram_id,
                    role=user.role,
                    username=user.username,
                )
                
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # 2. Fall back to query param (for bot)
    if admin_id:
        user = await repo.get_by_id(admin_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin user not found",
            )
        
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        
        return AuthenticatedUser(
            user_id=user.id,
            telegram_id=user.telegram_id,
            role=user.role,
            username=user.username,
        )
    
    # 3. Neither provided - error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="احراز هویت لازم است. توکن یا admin_id ارسال کنید.",
    )


async def require_print_shop_by_query(
    printshop_id: UUID = Query(..., description="Print shop user ID"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Require print shop role using printshop_id query param.
    Legacy support for existing endpoints.
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    user = await repo.get_by_id(printshop_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Print shop user not found",
        )
    
    if user.role not in [UserRole.PRINT_SHOP, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Print shop access required",
        )
    
    return AuthenticatedUser(
        user_id=user.id,
        telegram_id=user.telegram_id,
        role=user.role,
        username=user.username,
    )


async def require_print_shop_hybrid(
    authorization: Optional[str] = Header(None),
    printshop_id: Optional[UUID] = Query(None, description="Print shop user ID (for bot)"),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    Require print shop or admin role using either JWT token or printshop_id query param.
    Supports both web frontend (JWT) and bot (query param).
    """
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)

    # 1. Try JWT token first
    if authorization and authorization.lower().startswith("bearer "):
        try:
            parts = authorization.split()
            if len(parts) == 2:
                token = parts[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                if payload.get("type") != "access":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                token_user_id = payload.get("sub")
                if not token_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن منقضی شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                user = await repo.get_by_id(UUID(token_user_id))
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="کاربر یافت نشد",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="حساب کاربری غیرفعال شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                if user.role not in [UserRole.PRINT_SHOP, UserRole.ADMIN]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="دسترسی چاپخانه یا ادمین لازم است",
                    )

                return AuthenticatedUser(
                    user_id=user.id,
                    telegram_id=user.telegram_id,
                    role=user.role,
                    username=user.username,
                )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Fall back to query param (for bot)
    if printshop_id:
        user = await repo.get_by_id(printshop_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="کاربر چاپخانه یافت نشد",
            )

        if user.role not in [UserRole.PRINT_SHOP, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="دسترسی چاپخانه لازم است",
            )

        return AuthenticatedUser(
            user_id=user.id,
            telegram_id=user.telegram_id,
            role=user.role,
            username=user.username,
        )

    # 3. Neither provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="احراز هویت لازم است. توکن یا printshop_id ارسال کنید.",
    )


# Legacy compatibility
async def get_current_admin_user(x_admin_id: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Legacy: Get current admin user from header.
    Deprecated: Use require_admin dependency instead.
    """
    if not x_admin_id:
        return {"id": "system", "role": "ADMIN"}
    return {"id": x_admin_id, "role": "ADMIN"}


# ============== JWT Token-based Authentication ==============

def get_token_from_header(authorization: str = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن احراز هویت ارسال نشده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="فرمت توکن نامعتبر است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return parts[1]


async def get_current_user_from_token(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from JWT access token.
    
    Validates the token and returns the User model.
    Raises 401 if token is invalid or user not found.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن منقضی شده است",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر یافت نشد",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="حساب کاربری غیرفعال شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_admin_token(
    current_user: User = Depends(get_current_user_from_token),
) -> User:
    """
    Require admin role using JWT token authentication.
    Raises 403 if user is not admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی ادمین لازم است",
        )
    return current_user


# ============== Hybrid Authentication (JWT + Query Param) ==============

async def get_user_id_from_token_or_query(
    authorization: Optional[str] = Header(None),
    user_id: Optional[UUID] = Query(None, description="User ID (for bot)"),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """
    Get user ID from JWT token or query parameter.
    
    Supports both authentication methods:
    1. JWT Token (Authorization: Bearer ...) - for web frontend
    2. Query parameter (user_id=...) - for bot API
    
    Returns the user ID. Raises 401 if neither is provided or invalid.
    """
    # 1. Try JWT token first if Authorization header exists
    if authorization and authorization.lower().startswith("bearer "):
        try:
            parts = authorization.split()
            if len(parts) == 2:
                token = parts[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                if payload.get("type") != "access":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                token_user_id = payload.get("sub")
                if not token_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن نامعتبر است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Check expiration
                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="توکن منقضی شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Verify user exists and is active
                result = await db.execute(
                    select(User).where(User.id == UUID(token_user_id))
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="کاربر یافت نشد",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="حساب کاربری غیرفعال شده است",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                return user.id
                
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # 2. Fall back to query parameter (for bot)
    if user_id:
        return user_id
    
    # 3. Neither provided - error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="احراز هویت لازم است. توکن یا user_id ارسال کنید.",
    )


# Re-export get_db from database module
__all__ = [
    "get_db",
    "AuthenticatedUser",
    "get_optional_user",
    "get_current_user",
    "require_admin",
    "require_staff",
    "require_designer",
    "require_validator",
    "require_print_shop",
    "require_admin_by_query",
    "require_admin_hybrid",
    "require_print_shop_by_query",
    "require_print_shop_hybrid",
    "get_current_admin_user",
    # JWT token-based auth
    "get_token_from_header",
    "get_current_user_from_token",
    "require_admin_token",
    # Hybrid auth (JWT + query param)
    "get_user_id_from_token_or_query",
]

