"""Designer API router -- endpoints for designer workflow."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
import os
import uuid as uuid_mod
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
from app.models.enums import OrderStatus

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
    from app.utils.logging import log_event

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

    file_url = f"/uploads/designs/{filename}"

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
