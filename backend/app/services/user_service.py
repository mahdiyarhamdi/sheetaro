from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.models.user import User
from app.utils.logger import log_event


class UserService:
    """Service layer for user business logic."""
    
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
    
    async def create_or_update_user(self, user_data: UserCreate) -> UserOut:
        """Create new user or update existing."""
        user = await self.repository.create_or_update(user_data)
        
        # Log signup event
        log_event(
            event_type="user.signup",
            telegram_id=user.telegram_id,
            username=user.username,
            user_id=str(user.id),
        )
        
        return UserOut.model_validate(user)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserOut]:
        """Get user by telegram ID."""
        user = await self.repository.get_by_telegram_id(telegram_id)
        if user:
            return UserOut.model_validate(user)
        return None
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserOut]:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)
        if user:
            return UserOut.model_validate(user)
        return None
    
    async def update_user(self, telegram_id: int, user_data: UserUpdate) -> Optional[UserOut]:
        """Update user by telegram ID."""
        user = await self.repository.get_by_telegram_id(telegram_id)
        if not user:
            return None
        
        updated_user = await self.repository.update(user.id, user_data)
        if updated_user:
            return UserOut.model_validate(updated_user)
        return None

