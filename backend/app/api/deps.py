"""API dependencies for authentication and authorization."""

from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Header, HTTPException, status, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import UserRole


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


# Legacy compatibility
async def get_current_admin_user(x_admin_id: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Legacy: Get current admin user from header.
    Deprecated: Use require_admin dependency instead.
    """
    if not x_admin_id:
        return {"id": "system", "role": "ADMIN"}
    return {"id": x_admin_id, "role": "ADMIN"}


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
    "require_print_shop_by_query",
    "get_current_admin_user",
]

