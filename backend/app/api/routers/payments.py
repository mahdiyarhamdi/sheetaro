"""Payment API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from pathlib import Path

from app.api.deps import (
    get_db, AuthenticatedUser, require_admin_by_query, require_admin_hybrid,
    get_user_id_from_token_or_query
)
from app.core.rate_limit import limiter, RateLimits
from app.schemas.payment import (
    PaymentInitiate, PaymentInitiateResponse, PaymentCallback,
    PaymentOut, PaymentListResponse, PaymentSummary,
    ReceiptUpload, PaymentReject
)
from app.services.payment_service import PaymentService
from app.services.file_service import UPLOAD_DIR

# Upload directory for receipts
RECEIPT_UPLOAD_DIR = UPLOAD_DIR / "receipts"
RECEIPT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_RECEIPT_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_RECEIPT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

router = APIRouter()


@router.post(
    "/payments/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate payment",
    description="Initiate a payment and get redirect URL",
)
@limiter.limit(RateLimits.PAYMENT_INITIATE)
async def initiate_payment(
    request: Request,
    payment_data: PaymentInitiate,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
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
    "/payments/pending-approval",
    response_model=PaymentListResponse,
    summary="Get pending approval payments (admin)",
    description="Get all payments awaiting admin approval",
)
async def get_pending_approval(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    admin_user: AuthenticatedUser = Depends(require_admin_hybrid),
) -> PaymentListResponse:
    """Get payments pending approval (admin only)."""
    service = PaymentService(db)
    return await service.get_pending_approval_payments(admin_user.user_id, page, page_size)


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


# ==================== Card-to-Card Payment Endpoints ====================


@router.post(
    "/payments/{payment_id}/upload-receipt",
    response_model=PaymentOut,
    summary="Upload payment receipt",
    description="Upload receipt image for card-to-card payment",
)
@limiter.limit(RateLimits.RECEIPT_UPLOAD)
async def upload_receipt(
    request: Request,
    payment_id: UUID,
    receipt: UploadFile = File(..., description="Receipt image file"),
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> PaymentOut:
    """Upload receipt for card-to-card payment."""
    # Validate file type
    if receipt.content_type not in ALLOWED_RECEIPT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فرمت فایل نامعتبر است. فقط JPEG، PNG و WebP مجاز هستند."
        )
    
    # Read and validate file size
    content = await receipt.read()
    if len(content) > MAX_RECEIPT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"حجم فایل بیش از {MAX_RECEIPT_SIZE / 1024 / 1024:.0f} مگابایت است."
        )
    
    # Generate unique filename
    ext = Path(receipt.filename or "receipt.jpg").suffix or ".jpg"
    filename = f"{uuid4().hex}{ext}"
    filepath = RECEIPT_UPLOAD_DIR / filename
    
    # Save file
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Generate URL
    receipt_image_url = f"/files/receipts/{filename}"
    
    service = PaymentService(db)
    try:
        return await service.upload_receipt(
            payment_id=payment_id,
            user_id=user_id,
            receipt_image_url=receipt_image_url,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/payments/{payment_id}/approve",
    response_model=PaymentOut,
    summary="Approve payment (admin)",
    description="Approve a payment receipt (admin only)",
)
async def approve_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: AuthenticatedUser = Depends(require_admin_hybrid),
) -> PaymentOut:
    """Approve payment (admin only)."""
    service = PaymentService(db)
    try:
        return await service.approve_payment(
            payment_id=payment_id,
            admin_id=admin_user.user_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/payments/{payment_id}/reject",
    response_model=PaymentOut,
    summary="Reject payment (admin)",
    description="Reject a payment receipt with reason (admin only)",
)
async def reject_payment(
    payment_id: UUID,
    reject_data: PaymentReject,
    db: AsyncSession = Depends(get_db),
    admin_user: AuthenticatedUser = Depends(require_admin_hybrid),
) -> PaymentOut:
    """Reject payment (admin only)."""
    service = PaymentService(db)
    try:
        return await service.reject_payment(
            payment_id=payment_id,
            admin_id=admin_user.user_id,
            reason=reject_data.reason,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

