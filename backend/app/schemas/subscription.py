"""Subscription schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.models.enums import SubscriptionPlan


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan: SubscriptionPlan = Field(..., description="Subscription plan")


class SubscriptionOut(BaseModel):
    """Schema for subscription output."""
    id: UUID
    user_id: UUID
    plan: SubscriptionPlan
    price: Decimal
    start_date: date
    end_date: date
    is_active: bool
    payment_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionListResponse(BaseModel):
    """Response schema for subscription list."""
    items: list[SubscriptionOut]
    total: int
    page: int
    page_size: int


class SubscriptionStatus(BaseModel):
    """Current subscription status for a user."""
    has_active_subscription: bool
    current_subscription: Optional[SubscriptionOut] = None
    days_remaining: Optional[int] = None



