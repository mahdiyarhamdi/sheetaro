from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService

router = APIRouter()


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

