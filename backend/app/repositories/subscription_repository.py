"""Subscription repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from typing import Optional
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal

from app.models.subscription import Subscription
from app.models.enums import SubscriptionPlan


# Subscription prices in Tomans
SUBSCRIPTION_PRICES = {
    SubscriptionPlan.ADVANCED_SEARCH: Decimal('250000'),
}

# Subscription duration in days
SUBSCRIPTION_DURATION = 30


class SubscriptionRepository:
    """Repository for subscription database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: UUID,
        plan: SubscriptionPlan,
        payment_id: Optional[UUID] = None,
    ) -> Subscription:
        """Create a new subscription."""
        today = date.today()
        end_date = today + timedelta(days=SUBSCRIPTION_DURATION)
        price = SUBSCRIPTION_PRICES.get(plan, Decimal('0'))
        
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            price=price,
            start_date=today,
            end_date=end_date,
            is_active=True,
            payment_id=payment_id,
        )
        self.db.add(subscription)
        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription
    
    async def get_by_id(self, subscription_id: UUID) -> Optional[Subscription]:
        """Get subscription by ID."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_by_user(self, user_id: UUID) -> Optional[Subscription]:
        """Get active subscription for a user."""
        today = date.today()
        result = await self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                    Subscription.end_date >= today,
                )
            ).order_by(Subscription.end_date.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Subscription], int]:
        """Get all subscriptions for a user."""
        query = select(Subscription).where(Subscription.user_id == user_id)
        count_query = select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        
        query = query.order_by(Subscription.created_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        subscriptions = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return subscriptions, total
    
    async def deactivate(self, subscription_id: UUID) -> Optional[Subscription]:
        """Deactivate a subscription."""
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(is_active=False)
        )
        await self.db.flush()
        return await self.get_by_id(subscription_id)
    
    async def extend(
        self,
        subscription_id: UUID,
        days: int = SUBSCRIPTION_DURATION,
    ) -> Optional[Subscription]:
        """Extend a subscription."""
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return None
        
        # Extend from end_date or today, whichever is later
        today = date.today()
        start_from = max(subscription.end_date, today)
        new_end_date = start_from + timedelta(days=days)
        
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(end_date=new_end_date, is_active=True)
        )
        await self.db.flush()
        return await self.get_by_id(subscription_id)
    
    async def set_payment_id(
        self,
        subscription_id: UUID,
        payment_id: UUID,
    ) -> Optional[Subscription]:
        """Set payment ID for subscription."""
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(payment_id=payment_id)
        )
        await self.db.flush()
        return await self.get_by_id(subscription_id)



