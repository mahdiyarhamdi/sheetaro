"""Subscription service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from datetime import date

from app.repositories.subscription_repository import SubscriptionRepository, SUBSCRIPTION_PRICES
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionOut, SubscriptionListResponse, SubscriptionStatus
)
from app.models.enums import SubscriptionPlan
from app.utils.logger import log_event


class SubscriptionService:
    """Service layer for subscription business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SubscriptionRepository(db)
    
    async def create_subscription(
        self,
        user_id: UUID,
        subscription_data: SubscriptionCreate,
        payment_id: Optional[UUID] = None,
    ) -> SubscriptionOut:
        """Create a new subscription."""
        # Check if user already has active subscription
        existing = await self.repository.get_active_by_user(user_id)
        if existing:
            raise ValueError("User already has an active subscription")
        
        subscription = await self.repository.create(
            user_id=user_id,
            plan=subscription_data.plan,
            payment_id=payment_id,
        )
        
        log_event(
            event_type="subscription.created",
            subscription_id=str(subscription.id),
            user_id=str(user_id),
            plan=subscription_data.plan.value,
        )
        
        return SubscriptionOut.model_validate(subscription)
    
    async def get_subscription_by_id(self, subscription_id: UUID) -> Optional[SubscriptionOut]:
        """Get subscription by ID."""
        subscription = await self.repository.get_by_id(subscription_id)
        if subscription:
            return SubscriptionOut.model_validate(subscription)
        return None
    
    async def get_user_status(self, user_id: UUID) -> SubscriptionStatus:
        """Get current subscription status for a user."""
        subscription = await self.repository.get_active_by_user(user_id)
        
        if subscription:
            today = date.today()
            days_remaining = (subscription.end_date - today).days
            return SubscriptionStatus(
                has_active_subscription=True,
                current_subscription=SubscriptionOut.model_validate(subscription),
                days_remaining=max(0, days_remaining),
            )
        
        return SubscriptionStatus(
            has_active_subscription=False,
            current_subscription=None,
            days_remaining=None,
        )
    
    async def get_user_subscriptions(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> SubscriptionListResponse:
        """Get all subscriptions for a user."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        subscriptions, total = await self.repository.get_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )
        
        return SubscriptionListResponse(
            items=[SubscriptionOut.model_validate(s) for s in subscriptions],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def check_subscription(self, user_id: UUID) -> bool:
        """Check if user has active subscription."""
        subscription = await self.repository.get_active_by_user(user_id)
        return subscription is not None
    
    async def cancel_subscription(self, subscription_id: UUID, user_id: UUID) -> Optional[SubscriptionOut]:
        """Cancel a subscription."""
        subscription = await self.repository.get_by_id(subscription_id)
        if not subscription:
            return None
        
        if subscription.user_id != user_id:
            raise ValueError("Access denied")
        
        updated = await self.repository.deactivate(subscription_id)
        
        if updated:
            log_event(
                event_type="subscription.cancelled",
                subscription_id=str(subscription_id),
                user_id=str(user_id),
            )
            return SubscriptionOut.model_validate(updated)
        return None
    
    def get_price(self, plan: SubscriptionPlan) -> dict:
        """Get price for a subscription plan."""
        return {
            "plan": plan.value,
            "price": SUBSCRIPTION_PRICES.get(plan, 0),
            "duration_days": 30,
        }





