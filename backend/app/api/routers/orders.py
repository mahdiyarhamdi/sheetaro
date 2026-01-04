"""Order API router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.api.deps import (
    get_db,
    AuthenticatedUser,
    get_current_user,
    require_admin,
    require_staff,
    require_print_shop_by_query,
)
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate,
    OrderOut, OrderListResponse
)
from app.services.order_service import OrderService
from app.models.enums import OrderStatus

router = APIRouter()


@router.post(
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Create a new print order",
)
async def create_order(
    order_data: OrderCreate,
    user_id: UUID = Query(..., description="User ID (from bot)"),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Create a new order."""
    service = OrderService(db)
    try:
        return await service.create_order(user_id, order_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/orders",
    response_model=OrderListResponse,
    summary="List user orders",
    description="Get list of orders for a user",
)
async def list_orders(
    user_id: UUID = Query(..., description="User ID"),
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
    """List orders for a user."""
    service = OrderService(db)
    return await service.get_user_orders(
        user_id=user_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/orders/{order_id}",
    response_model=OrderOut,
    summary="Get order details",
    description="Get order details by ID",
)
async def get_order(
    order_id: UUID,
    user_id: Optional[UUID] = Query(None, description="User ID for ownership check"),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Get order by ID."""
    service = OrderService(db)
    order = await service.get_order_by_id(order_id, user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return order


@router.patch(
    "/orders/{order_id}",
    response_model=OrderOut,
    summary="Update order",
    description="Update order details",
)
async def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    user_id: Optional[UUID] = Query(None, description="User ID for ownership check"),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Update order."""
    service = OrderService(db)
    try:
        order = await service.update_order(order_id, order_data, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderOut,
    summary="Update order status",
    description="Update order status (Admin/Staff only)",
)
async def update_order_status(
    order_id: UUID,
    status_data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    staff_user: AuthenticatedUser = Depends(require_staff),
) -> OrderOut:
    """Update order status (staff only)."""
    service = OrderService(db)
    order = await service.update_order_status(order_id, status_data)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return order


@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrderOut,
    summary="Cancel order",
    description="Cancel an order (before printing)",
)
async def cancel_order(
    order_id: UUID,
    user_id: Optional[UUID] = Query(None, description="User ID for ownership check"),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Cancel order."""
    service = OrderService(db)
    try:
        order = await service.cancel_order(order_id, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Print shop endpoints
@router.get(
    "/printshop/orders",
    response_model=OrderListResponse,
    summary="Get print shop queue",
    description="Get orders ready for printing (Print shop/Staff only)",
)
async def get_printshop_queue(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    staff_user: AuthenticatedUser = Depends(require_staff),
) -> OrderListResponse:
    """Get orders ready for print shop (staff only)."""
    service = OrderService(db)
    return await service.get_printshop_queue(page=page, page_size=page_size)


@router.post(
    "/printshop/accept/{order_id}",
    response_model=OrderOut,
    summary="Accept order",
    description="Accept order by print shop (Print shop only)",
)
async def accept_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    printshop_user: AuthenticatedUser = Depends(require_print_shop_by_query),
) -> OrderOut:
    """Accept order by print shop (print shop only)."""
    service = OrderService(db)
    try:
        order = await service.accept_order_by_printshop(order_id, printshop_user.user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found or not available"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )




