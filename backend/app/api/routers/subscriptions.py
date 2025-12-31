"""Subscription API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.api.deps import get_db
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionOut, SubscriptionListResponse, SubscriptionStatus
)
from app.services.subscription_service import SubscriptionService
from app.models.enums import SubscriptionPlan

router = APIRouter()


@router.post(
    "/subscriptions",
    response_model=SubscriptionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription",
    description="Create a new subscription (requires payment)",
)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    user_id: UUID = Query(..., description="User ID"),
    payment_id: Optional[UUID] = Query(None, description="Payment ID"),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionOut:
    """Create a new subscription."""
    service = SubscriptionService(db)
    try:
        return await service.create_subscription(user_id, subscription_data, payment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/subscriptions/me",
    response_model=SubscriptionStatus,
    summary="Get subscription status",
    description="Get current subscription status for a user",
)
async def get_subscription_status(
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionStatus:
    """Get current subscription status."""
    service = SubscriptionService(db)
    return await service.get_user_status(user_id)


@router.get(
    "/subscriptions",
    response_model=SubscriptionListResponse,
    summary="List subscriptions",
    description="Get subscription history for a user",
)
async def list_subscriptions(
    user_id: UUID = Query(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionListResponse:
    """List subscriptions for a user."""
    service = SubscriptionService(db)
    return await service.get_user_subscriptions(user_id, page, page_size)


@router.get(
    "/subscriptions/{subscription_id}",
    response_model=SubscriptionOut,
    summary="Get subscription",
    description="Get subscription by ID",
)
async def get_subscription(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SubscriptionOut:
    """Get subscription by ID."""
    service = SubscriptionService(db)
    subscription = await service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with id {subscription_id} not found"
        )
    return subscription


@router.post(
    "/subscriptions/{subscription_id}/cancel",
    response_model=SubscriptionOut,
    summary="Cancel subscription",
    description="Cancel an active subscription",
)
async def cancel_subscription(
    subscription_id: UUID,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionOut:
    """Cancel subscription."""
    service = SubscriptionService(db)
    try:
        subscription = await service.cancel_subscription(subscription_id, user_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with id {subscription_id} not found"
            )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/subscriptions/plans/price",
    response_model=dict,
    summary="Get plan price",
    description="Get price for a subscription plan",
)
async def get_plan_price(
    plan: SubscriptionPlan = Query(..., description="Subscription plan"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get price for a subscription plan."""
    service = SubscriptionService(db)
    return service.get_price(plan)



