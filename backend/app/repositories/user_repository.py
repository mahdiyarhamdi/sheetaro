"""User repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.model_dump())
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user by ID."""
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(user_id)
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(user_id)
    
    async def create_or_update(self, user_data: UserCreate) -> User:
        """Create user or update if exists."""
        existing_user = await self.get_by_telegram_id(user_data.telegram_id)
        
        if existing_user:
            # Update existing user
            update_data = UserUpdate(
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                city=user_data.city,
                address=user_data.address,
                profile_photo_url=user_data.profile_photo_url,
            )
            return await self.update(existing_user.id, update_data)
        else:
            # Create new user
            return await self.create(user_data)
    
    async def get_all_admins(self) -> list[User]:
        """Get all users with ADMIN role."""
        result = await self.db.execute(
            select(User).where(
                User.role == UserRole.ADMIN,
                User.is_active == True,
            )
        )
        return list(result.scalars().all())
    
    async def get_admin_telegram_ids(self) -> list[int]:
        """Get telegram IDs of all active admins."""
        result = await self.db.execute(
            select(User.telegram_id).where(
                User.role == UserRole.ADMIN,
                User.is_active == True,
            )
        )
        return list(result.scalars().all())
    
    async def update_role(self, user_id: UUID, new_role: UserRole) -> Optional[User]:
        """Update user role."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(role=new_role)
        )
        await self.db.flush()
        return await self.get_by_id(user_id)
    
    async def count_admins(self) -> int:
        """Count total admins."""
        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.role == UserRole.ADMIN,
                User.is_active == True,
            )
        )
        return result.scalar() or 0
