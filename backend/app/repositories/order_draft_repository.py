"""Repository for order draft CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from uuid import UUID, uuid4

from app.models.order_draft import OrderDraft


class OrderDraftRepository:
    """CRUD operations for order drafts (one active draft per user)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: UUID) -> Optional[OrderDraft]:
        """Get the active draft for a user."""
        result = await self.db.execute(
            select(OrderDraft).where(OrderDraft.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: UUID, current_step: str, data: dict) -> OrderDraft:
        """Create or update the user's draft (one per user)."""
        existing = await self.get_by_user(user_id)
        if existing:
            existing.current_step = current_step
            existing.data = data
            await self.db.flush()
            await self.db.refresh(existing)
            return existing

        draft = OrderDraft(
            id=uuid4(),
            user_id=user_id,
            current_step=current_step,
            data=data,
        )
        self.db.add(draft)
        await self.db.flush()
        await self.db.refresh(draft)
        return draft

    async def delete_by_user(self, user_id: UUID) -> bool:
        """Delete the user's draft. Returns True if a row was deleted."""
        result = await self.db.execute(
            delete(OrderDraft).where(OrderDraft.user_id == user_id)
        )
        return result.rowcount > 0
