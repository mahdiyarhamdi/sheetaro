"""Settings repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.models.settings import SystemSettings


class SettingsRepository:
    """Repository for system settings database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get(self, key: str) -> Optional[SystemSettings]:
        """Get a setting by key."""
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        return result.scalar_one_or_none()
    
    async def set(self, key: str, value: str, updated_by: Optional[UUID] = None) -> SystemSettings:
        """Set a setting value (create or update)."""
        existing = await self.get(key)
        
        if existing:
            existing.value = value
            if updated_by:
                existing.updated_by = updated_by
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            setting = SystemSettings(
                key=key,
                value=value,
                updated_by=updated_by,
            )
            self.db.add(setting)
            await self.db.flush()
            await self.db.refresh(setting)
            return setting
    
    async def delete(self, key: str) -> bool:
        """Delete a setting by key."""
        setting = await self.get(key)
        if setting:
            await self.db.delete(setting)
            await self.db.flush()
            return True
        return False
    
    async def get_all(self) -> list[SystemSettings]:
        """Get all settings."""
        result = await self.db.execute(select(SystemSettings))
        return list(result.scalars().all())

