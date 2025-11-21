from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from uuid import UUID

from app.models.user import User
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
                address=user_data.address,
                profile_photo_url=user_data.profile_photo_url,
            )
            return await self.update(existing_user.id, update_data)
        else:
            # Create new user
            return await self.create(user_data)

