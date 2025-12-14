"""Settings API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.schemas.settings import PaymentCardInfo, PaymentCardInfoOut, PaymentCardUpdate
from app.services.settings_service import SettingsService
from app.services.user_service import UserService
from app.models.enums import UserRole

router = APIRouter()


async def verify_admin(user_id: UUID, db: AsyncSession) -> bool:
    """Verify that user is an admin."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user or user.role != UserRole.ADMIN:
        return False
    return True


@router.get(
    "/settings/payment-card",
    response_model=PaymentCardInfoOut,
    summary="Get payment card info",
    description="Get the card number and holder name for card-to-card payments",
)
async def get_payment_card(
    db: AsyncSession = Depends(get_db),
) -> PaymentCardInfoOut:
    """Get payment card information."""
    service = SettingsService(db)
    card_info = await service.get_payment_card()
    if not card_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment card not configured"
        )
    return card_info


@router.put(
    "/settings/payment-card",
    response_model=PaymentCardInfoOut,
    summary="Set payment card info (admin)",
    description="Set the card number and holder name for card-to-card payments. Admin only.",
)
async def set_payment_card(
    card_info: PaymentCardInfo,
    admin_id: UUID = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db),
) -> PaymentCardInfoOut:
    """Set payment card information (admin only)."""
    if not await verify_admin(admin_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = SettingsService(db)
    return await service.set_payment_card(card_info, admin_id)


@router.patch(
    "/settings/payment-card",
    response_model=PaymentCardInfoOut,
    summary="Update payment card info (admin)",
    description="Partially update the card number or holder name. Admin only.",
)
async def update_payment_card(
    update_data: PaymentCardUpdate,
    admin_id: UUID = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db),
) -> PaymentCardInfoOut:
    """Update payment card information (admin only)."""
    if not await verify_admin(admin_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = SettingsService(db)
    result = await service.update_payment_card(update_data, admin_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment card not configured"
        )
    return result

