"""User service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.models.enums import UserRole
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
            role=user.role.value if user.role else None,
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
            log_event(
                event_type="user.update",
                telegram_id=updated_user.telegram_id,
                user_id=str(updated_user.id),
            )
            return UserOut.model_validate(updated_user)
        return None
    
    async def get_all_admins(self) -> list[UserOut]:
        """Get all admin users."""
        admins = await self.repository.get_all_admins()
        return [UserOut.model_validate(admin) for admin in admins]
    
    async def get_admin_telegram_ids(self) -> list[int]:
        """Get telegram IDs of all active admins."""
        return await self.repository.get_admin_telegram_ids()
    
    async def promote_to_admin(
        self, 
        target_telegram_id: int, 
        admin_id: UUID
    ) -> Optional[UserOut]:
        """Promote a user to admin role."""
        # Verify the requesting user is an admin
        admin = await self.repository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Admin access required")
        
        # Get target user
        target = await self.repository.get_by_telegram_id(target_telegram_id)
        if not target:
            raise ValueError("User not found")
        
        if target.role == UserRole.ADMIN:
            raise ValueError("User is already an admin")
        
        # Promote to admin
        updated_user = await self.repository.update_role(target.id, UserRole.ADMIN)
        
        if updated_user:
            log_event(
                event_type="user.promoted_to_admin",
                target_telegram_id=target_telegram_id,
                target_user_id=str(target.id),
                promoted_by=str(admin_id),
            )
            return UserOut.model_validate(updated_user)
        return None
    
    async def demote_from_admin(
        self, 
        target_telegram_id: int, 
        admin_id: UUID
    ) -> Optional[UserOut]:
        """Demote an admin to customer role."""
        # Verify the requesting user is an admin
        admin = await self.repository.get_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Admin access required")
        
        # Get target user
        target = await self.repository.get_by_telegram_id(target_telegram_id)
        if not target:
            raise ValueError("User not found")
        
        if target.role != UserRole.ADMIN:
            raise ValueError("User is not an admin")
        
        # Cannot demote yourself if you're the last admin
        admin_count = await self.repository.count_admins()
        if target.id == admin.id and admin_count <= 1:
            raise ValueError("Cannot remove the last admin")
        
        # Demote to customer
        updated_user = await self.repository.update_role(target.id, UserRole.CUSTOMER)
        
        if updated_user:
            log_event(
                event_type="user.demoted_from_admin",
                target_telegram_id=target_telegram_id,
                target_user_id=str(target.id),
                demoted_by=str(admin_id),
            )
            return UserOut.model_validate(updated_user)
        return None
