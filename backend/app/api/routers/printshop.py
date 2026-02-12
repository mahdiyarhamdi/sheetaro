"""Print Shop API router -- endpoints for print shop workflow."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from typing import Optional

from app.api.deps import (
    get_db,
    AuthenticatedUser,
    require_print_shop,
    require_print_shop_hybrid,
)
from app.schemas.order import (
    OrderOut,
    PrintShopOrderOut,
    PrintShopOrderListResponse,
    PrintShopShipRequest,
    PrintShopStats,
    SettlementOut,
    SettlementListResponse,
)
from app.services.order_service import OrderService
from app.models.enums import OrderStatus
from app.models.settlement import Settlement

router = APIRouter(prefix="/api/v1/printshop", tags=["Print Shop"])


@router.get(
    "/orders",
    response_model=PrintShopOrderListResponse,
    summary="Get print shop queue",
    description="Get orders ready for printing (READY_FOR_PRINT).",
)
async def get_printshop_queue(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> PrintShopOrderListResponse:
    """Get queue of orders ready for print shop."""
    service = OrderService(db)
    return await service.get_printshop_queue(page=page, page_size=page_size)


@router.get(
    "/my-orders",
    response_model=PrintShopOrderListResponse,
    summary="Get my assigned orders",
    description="Get orders assigned to the current print shop.",
)
async def get_my_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> PrintShopOrderListResponse:
    """Get print shop's own assigned orders."""
    service = OrderService(db)
    return await service.get_printshop_my_orders(
        printshop_id=user.user_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/my-orders/{order_id}",
    response_model=PrintShopOrderOut,
    summary="Get order detail",
    description="Get a single order detail assigned to this print shop.",
)
async def get_order_detail(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> PrintShopOrderOut:
    """Get order detail for print shop."""
    service = OrderService(db)
    order = await service.get_printshop_order_detail(order_id, user.user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or not assigned to this print shop",
        )
    return order


@router.post(
    "/accept/{order_id}",
    response_model=OrderOut,
    summary="Accept order",
    description="Accept an order from the queue for printing.",
)
async def accept_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> OrderOut:
    """Accept order by print shop."""
    service = OrderService(db)
    try:
        order = await service.accept_order_by_printshop(order_id, user.user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not available for acceptance",
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/orders/{order_id}/complete",
    response_model=OrderOut,
    summary="Mark as printed",
    description="Mark an order as printing completed.",
)
async def complete_printing(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> OrderOut:
    """Mark order as printed."""
    service = OrderService(db)
    try:
        order = await service.complete_printing(order_id, user.user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/orders/{order_id}/ship",
    response_model=OrderOut,
    summary="Ship order",
    description="Mark order as shipped with tracking code.",
)
async def ship_order(
    order_id: UUID,
    ship_data: PrintShopShipRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> OrderOut:
    """Ship order with tracking code."""
    service = OrderService(db)
    try:
        order = await service.ship_order(
            order_id=order_id,
            printshop_id=user.user_id,
            tracking_code=ship_data.tracking_code,
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/stats",
    response_model=PrintShopStats,
    summary="Get print shop stats",
    description="Get dashboard statistics for the print shop.",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> PrintShopStats:
    """Get print shop dashboard statistics."""
    service = OrderService(db)
    return await service.get_printshop_stats(user.user_id)


@router.get(
    "/settlements",
    response_model=SettlementListResponse,
    summary="Get settlements",
    description="Get settlement/commission history for the print shop.",
)
async def get_settlements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_print_shop_hybrid),
) -> SettlementListResponse:
    """Get print shop settlement history."""
    query = select(Settlement).where(Settlement.printshop_id == user.user_id)
    count_query = select(func.count(Settlement.id)).where(Settlement.printshop_id == user.user_id)

    query = query.order_by(Settlement.period_end.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    settlements = list(result.scalars().all())

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    items = [
        SettlementOut(
            id=s.id,
            printshop_id=s.printshop_id,
            period_start=s.period_start.isoformat(),
            period_end=s.period_end.isoformat(),
            total_orders=s.total_orders,
            total_revenue=s.total_revenue,
            platform_commission=s.platform_commission,
            net_amount=s.net_amount,
            status=s.status.value,
            paid_at=s.paid_at,
            created_at=s.created_at,
        )
        for s in settlements
    ]

    return SettlementListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
