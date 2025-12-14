from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, Field

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService

router = APIRouter()


class AdminPromote(BaseModel):
    """Schema for promoting user to admin."""
    target_telegram_id: int = Field(..., description="Telegram ID of user to promote")


class AdminDemote(BaseModel):
    """Schema for demoting admin to customer."""
    target_telegram_id: int = Field(..., description="Telegram ID of admin to demote")


class AdminListResponse(BaseModel):
    """Response schema for admin list."""
    items: list[UserOut]
    total: int


@router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update user",
    description="Create a new user or update existing user by telegram_id",
)
async def create_or_update_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Create new user or update existing."""
    service = UserService(db)
    return await service.create_or_update_user(user_data)


@router.get(
    "/users/{telegram_id}",
    response_model=UserOut,
    summary="Get user by telegram ID",
    description="Retrieve user information by telegram ID",
)
async def get_user(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Get user by telegram ID."""
    service = UserService(db)
    user = await service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return user


@router.patch(
    "/users/{telegram_id}",
    response_model=UserOut,
    summary="Update user",
    description="Update user information by telegram ID",
)
async def update_user(
    telegram_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Update user by telegram ID."""
    service = UserService(db)
    user = await service.update_user(telegram_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return user


# ==================== Admin Management Endpoints ====================


@router.get(
    "/users/admins/list",
    response_model=AdminListResponse,
    summary="Get all admins (admin)",
    description="Get list of all admin users",
)
async def get_admins(
    admin_id: UUID = Query(..., description="Admin user ID requesting the list"),
    db: AsyncSession = Depends(get_db),
) -> AdminListResponse:
    """Get all admin users (admin only)."""
    service = UserService(db)
    
    # Verify requester is admin
    admin = await service.get_user_by_id(admin_id)
    if not admin or admin.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    admins = await service.get_all_admins()
    return AdminListResponse(items=admins, total=len(admins))


@router.get(
    "/users/admins/telegram-ids",
    response_model=list[int],
    summary="Get admin telegram IDs",
    description="Get telegram IDs of all active admins (for notifications)",
)
async def get_admin_telegram_ids(
    db: AsyncSession = Depends(get_db),
) -> list[int]:
    """Get telegram IDs of all active admins."""
    service = UserService(db)
    return await service.get_admin_telegram_ids()


@router.post(
    "/users/admins/promote",
    response_model=UserOut,
    summary="Promote user to admin (admin)",
    description="Promote a user to admin role",
)
async def promote_to_admin(
    promote_data: AdminPromote,
    admin_id: UUID = Query(..., description="Admin user ID performing the action"),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Promote user to admin (admin only)."""
    service = UserService(db)
    try:
        result = await service.promote_to_admin(
            target_telegram_id=promote_data.target_telegram_id,
            admin_id=admin_id,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to promote user"
            )
        return result
    except ValueError as e:
        if "Admin access required" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/users/admins/demote",
    response_model=UserOut,
    summary="Demote admin to customer (admin)",
    description="Demote an admin to customer role",
)
async def demote_from_admin(
    demote_data: AdminDemote,
    admin_id: UUID = Query(..., description="Admin user ID performing the action"),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Demote admin to customer (admin only)."""
    service = UserService(db)
    try:
        result = await service.demote_from_admin(
            target_telegram_id=demote_data.target_telegram_id,
            admin_id=admin_id,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to demote admin"
            )
        return result
    except ValueError as e:
        if "Admin access required" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

