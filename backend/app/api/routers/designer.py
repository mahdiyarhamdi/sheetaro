"""Designer API router -- endpoints for designer workflow."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
import os
import uuid as uuid_mod
import logging
from datetime import datetime

from app.api.deps import (
    get_db,
    AuthenticatedUser,
    require_designer_hybrid,
)
from app.schemas.order import (
    DesignerOrderOut,
    DesignerOrderListResponse,
    DesignerStats,
)
from app.schemas.design_revision import DesignRevisionOut, DesignRevisionListResponse
from app.services.order_service import OrderService
from app.services.design_revision_service import DesignRevisionService
from app.models.enums import OrderStatus, ValidationStatus
from app.models.order import Order
from app.models.user import User
from app.models.processed_design import ProcessedDesign

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/designer", tags=["Designer"])


@router.get(
    "/queue",
    response_model=DesignerOrderListResponse,
    summary="Get designer queue",
    description="Get unassigned orders waiting for a designer to accept (PENDING_DESIGNER).",
)
async def get_designer_queue(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerOrderListResponse:
    """Get queue of orders waiting for designer acceptance."""
    service = OrderService(db)
    return await service.get_designer_queue(page=page, page_size=page_size)


@router.get(
    "/orders",
    response_model=DesignerOrderListResponse,
    summary="Get designer orders",
    description="Get orders assigned to the current designer.",
)
async def get_designer_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerOrderListResponse:
    """Get designer's assigned orders."""
    service = OrderService(db)
    return await service.get_designer_orders(
        designer_id=user.user_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/orders/{order_id}",
    response_model=DesignerOrderOut,
    summary="Get order detail for designer",
    description="Get enriched order detail assigned to this designer.",
)
async def get_order_detail(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerOrderOut:
    """Get order detail for designer."""
    service = OrderService(db)
    order = await service.get_designer_order_detail(order_id, user.user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد یا به شما اختصاص داده نشده است",
        )
    return order


@router.post(
    "/orders/{order_id}/accept",
    response_model=DesignerOrderOut,
    summary="Accept order",
    description="Designer accepts an unassigned order for designing.",
)
async def accept_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerOrderOut:
    """Designer accepts an order from the queue."""
    from app.schemas.order import OrderStatusUpdate
    from app.utils.logger import log_event

    service = OrderService(db)
    order_obj = await service.repository.get_by_id(order_id)
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد",
        )
    if order_obj.status != OrderStatus.PENDING_DESIGNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این سفارش در صف طراحی نیست",
        )
    if order_obj.assigned_designer_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این سفارش قبلاً به طراح دیگری اختصاص یافته است",
        )

    # Assign designer and transition to DESIGNING
    order_obj.assigned_designer_id = user.user_id
    order_obj.status = OrderStatus.DESIGNING
    await db.flush()

    log_event(
        event_type="order.designer_accepted",
        order_id=str(order_id),
        designer_id=str(user.user_id),
    )

    result = await service.get_designer_order_detail(order_id, user.user_id)
    return result


@router.post(
    "/orders/{order_id}/upload-design",
    response_model=DesignRevisionOut,
    summary="Upload design",
    description="Designer uploads a new design revision.",
)
async def upload_design(
    order_id: UUID,
    file: UploadFile = File(..., description="Design file (image)"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignRevisionOut:
    """Upload a design revision for an order."""
    # Save file
    upload_dir = "/app/uploads/designs"
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "design.png")[1] or ".png"
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid_mod.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    file_url = f"/files/designs/{filename}"

    revision_service = DesignRevisionService(db)
    try:
        revision = await revision_service.submit_revision(
            order_id=order_id,
            designer_id=user.user_id,
            design_file_url=file_url,
        )
        return revision
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/orders/{order_id}/revisions",
    response_model=DesignRevisionListResponse,
    summary="Get revision history",
    description="Get all design revisions for an order.",
)
async def get_revisions(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignRevisionListResponse:
    """Get revision history for an order."""
    # Verify designer has access
    service = OrderService(db)
    order = await service.get_designer_order_detail(order_id, user.user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد",
        )

    revision_service = DesignRevisionService(db)
    return await revision_service.get_revision_history(order_id)


@router.get(
    "/stats",
    response_model=DesignerStats,
    summary="Get designer stats",
    description="Get dashboard statistics for the designer.",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerStats:
    """Get designer dashboard statistics."""
    service = OrderService(db)
    return await service.get_designer_stats(user.user_id)


# ============== Validation Management (Designer) ==============


class DesignerValidationRequestResponse(BaseModel):
    """Validation request item for designer view."""
    id: str
    user_id: str
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    category_name: Optional[str] = None
    plan_name: Optional[str] = None
    template_name: Optional[str] = None
    validation_status: Optional[str] = None
    total_price: float
    validation_price: float
    created_at: str
    design_preview_url: Optional[str] = None


class DesignerValidationListResponse(BaseModel):
    """Paginated validation requests for designer."""
    items: List[DesignerValidationRequestResponse]
    total: int
    page: int
    page_size: int


class DesignerValidationRejectRequest(BaseModel):
    """Reject validation with comment."""
    comment: str


@router.get("/validations", response_model=DesignerValidationListResponse)
async def list_designer_validations(
    status_filter: Optional[ValidationStatus] = Query(None, alias="status", description="Filter by validation status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> DesignerValidationListResponse:
    """List orders with validation requested. Designer access."""
    from app.models.category import Category

    query = select(Order).where(Order.validation_requested == True)
    count_query = select(func.count(Order.id)).where(Order.validation_requested == True)

    if status_filter:
        if status_filter == ValidationStatus.PENDING:
            sf = or_(
                Order.validation_status == status_filter,
                Order.validation_status.is_(None),
            )
        else:
            sf = Order.validation_status == status_filter
        query = query.where(sf)
        count_query = count_query.where(sf)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    orders = result.scalars().all()

    items = []
    for order in orders:
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        order_user = user_result.scalar_one_or_none()

        category_name = None
        if order.category_id:
            cat_result = await db.execute(select(Category).where(Category.id == order.category_id))
            cat = cat_result.scalar_one_or_none()
            if cat:
                category_name = cat.name_fa

        plan_name = None
        if order.design_plan:
            plan_names = {
                "PUBLIC": "عمومی",
                "SEMI_PRIVATE": "نیمه خصوصی",
                "PRIVATE": "خصوصی",
                "OWN_DESIGN": "طرح اختصاصی",
            }
            plan_name = plan_names.get(order.design_plan.value, order.design_plan.value)

        design_preview_url = order.design_file_url
        template_name = None
        if not design_preview_url:
            pd_result = await db.execute(
                select(ProcessedDesign)
                .where(ProcessedDesign.order_id == order.id)
                .options(selectinload(ProcessedDesign.template))
                .order_by(ProcessedDesign.created_at.desc())
                .limit(1)
            )
            processed = pd_result.scalar_one_or_none()
            if processed:
                design_preview_url = processed.preview_url
                if processed.template:
                    template_name = processed.template.name_fa

        items.append(DesignerValidationRequestResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            user_name=order_user.full_name if order_user else None,
            user_phone=order_user.phone_number if order_user else None,
            category_name=category_name,
            plan_name=plan_name,
            template_name=template_name,
            validation_status=order.validation_status.value if order.validation_status else None,
            total_price=float(order.total_price) if order.total_price else 0,
            validation_price=float(order.validation_price) if order.validation_price else 0,
            created_at=order.created_at.isoformat(),
            design_preview_url=design_preview_url,
        ))

    return DesignerValidationListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/validations/{order_id}/approve")
async def approve_designer_validation(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> dict:
    """Approve validation for an order. Designer access."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد")

    if not order.validation_requested:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="این سفارش درخواست اعتبارسنجی نداشته است")

    order.validation_status = ValidationStatus.PASSED
    order.assigned_validator_id = user.user_id

    if order.status == OrderStatus.AWAITING_VALIDATION:
        order.status = OrderStatus.READY_FOR_PRINT

    await db.commit()

    logger.info("Designer %s approved validation for order %s", user.user_id, order_id)

    return {
        "success": True,
        "order_id": str(order_id),
        "validation_status": order.validation_status.value,
        "message": "اعتبارسنجی با موفقیت تأیید شد",
    }


@router.post("/validations/{order_id}/reject")
async def reject_designer_validation(
    order_id: UUID,
    data: DesignerValidationRejectRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_designer_hybrid),
) -> dict:
    """Reject validation with correction comment. Designer access."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="سفارش یافت نشد")

    if not order.validation_requested:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="این سفارش درخواست اعتبارسنجی نداشته است")

    order.validation_status = ValidationStatus.FAILED
    order.assigned_validator_id = user.user_id
    order.admin_notes = data.comment
    order.status = OrderStatus.NEEDS_ACTION

    await db.commit()

    logger.info("Designer %s rejected validation for order %s", user.user_id, order_id)

    return {
        "success": True,
        "order_id": str(order_id),
        "validation_status": order.validation_status.value,
        "comment": data.comment,
        "message": "درخواست اصلاح ثبت شد",
    }
