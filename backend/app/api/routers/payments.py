"""Payment API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.schemas.payment import (
    PaymentInitiate, PaymentInitiateResponse, PaymentCallback,
    PaymentOut, PaymentListResponse, PaymentSummary
)
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post(
    "/payments/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate payment",
    description="Initiate a payment and get redirect URL",
)
async def initiate_payment(
    payment_data: PaymentInitiate,
    user_id: UUID = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> PaymentInitiateResponse:
    """Initiate a payment."""
    service = PaymentService(db)
    try:
        return await service.initiate_payment(user_id, payment_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/payments/callback",
    response_model=PaymentOut,
    summary="Payment callback",
    description="Handle payment callback from PSP",
)
async def payment_callback(
    callback_data: PaymentCallback,
    db: AsyncSession = Depends(get_db),
) -> PaymentOut:
    """Handle payment callback."""
    service = PaymentService(db)
    try:
        return await service.handle_callback(callback_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentOut,
    summary="Get payment details",
    description="Get payment details by ID",
)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PaymentOut:
    """Get payment by ID."""
    service = PaymentService(db)
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found"
        )
    return payment


@router.get(
    "/payments/order/{order_id}",
    response_model=PaymentListResponse,
    summary="Get order payments",
    description="Get all payments for an order",
)
async def get_order_payments(
    order_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> PaymentListResponse:
    """Get payments for an order."""
    service = PaymentService(db)
    return await service.get_order_payments(order_id, page, page_size)


@router.get(
    "/payments/order/{order_id}/summary",
    response_model=PaymentSummary,
    summary="Get payment summary",
    description="Get payment summary for an order",
)
async def get_payment_summary(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PaymentSummary:
    """Get payment summary for an order."""
    service = PaymentService(db)
    return await service.get_payment_summary(order_id)

