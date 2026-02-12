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
    get_user_id_from_token_or_query,
)
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate,
    OrderOut, OrderListResponse, CustomerOrderDetailOut,
)
from app.schemas.design_revision import (
    DesignRevisionOut, DesignRevisionListResponse, RejectDesignRequest,
)
from app.schemas.message import MessageCreate, MessageOut, MessageListResponse
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.order_service import OrderService
from app.services.design_revision_service import DesignRevisionService
from app.services.message_service import MessageService
from app.services.review_service import ReviewService
from app.models.enums import OrderStatus

router = APIRouter()


@router.post(
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Create a new print order. Supports JWT token (web) or user_id query param (bot).",
)
async def create_order(
    order_data: OrderCreate,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
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
    description="Get list of orders for a user. Supports JWT token (web) or user_id query param (bot).",
)
async def list_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: UUID = Depends(get_user_id_from_token_or_query),
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
    response_model=CustomerOrderDetailOut,
    summary="Get order details",
    description="Get enriched order details by ID (includes category name, attributes, design, payment)",
)
async def get_order(
    order_id: UUID,
    user_id: Optional[UUID] = Query(None, description="User ID for ownership check"),
    db: AsyncSession = Depends(get_db),
) -> CustomerOrderDetailOut:
    """Get order by ID with enriched details."""
    service = OrderService(db)
    order = await service.get_order_detail(order_id, user_id)
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

# ============== Design Approval / Rejection ==============


@router.post(
    "/orders/{order_id}/approve-design",
    response_model=DesignRevisionOut,
    summary="Approve design",
    description="Customer approves the latest design revision.",
)
async def approve_design(
    order_id: UUID,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> DesignRevisionOut:
    """Customer approves the latest design."""
    service = DesignRevisionService(db)
    try:
        return await service.approve_design(order_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/orders/{order_id}/reject-design",
    response_model=DesignRevisionOut,
    summary="Reject design",
    description="Customer rejects the design with feedback. Auto-approves if max revisions reached.",
)
async def reject_design(
    order_id: UUID,
    body: RejectDesignRequest,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> DesignRevisionOut:
    """Customer rejects the design with feedback."""
    service = DesignRevisionService(db)
    try:
        return await service.reject_design(order_id, user_id, body.feedback)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
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
) -> DesignRevisionListResponse:
    """Get design revision history for an order."""
    service = DesignRevisionService(db)
    return await service.get_revision_history(order_id)


# ============== Chat / Messages ==============


@router.get(
    "/orders/{order_id}/messages",
    response_model=MessageListResponse,
    summary="Get messages",
    description="Get paginated chat messages for an order (PRIVATE plan only).",
)
async def get_messages(
    order_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> MessageListResponse:
    """Get chat messages for an order."""
    service = MessageService(db)
    try:
        return await service.get_messages(order_id, user_id, page, page_size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/orders/{order_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    description="Send a chat message in an order context (PRIVATE plan, DESIGNING status only).",
)
async def send_message(
    order_id: UUID,
    body: MessageCreate,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> MessageOut:
    """Send a chat message."""
    service = MessageService(db)
    try:
        return await service.send_message(
            order_id=order_id,
            sender_id=user_id,
            content=body.content,
            file_url=body.file_url,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.patch(
    "/orders/{order_id}/messages/read",
    summary="Mark messages as read",
    description="Mark all unread messages as read for the current user.",
)
async def mark_messages_read(
    order_id: UUID,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark messages as read."""
    service = MessageService(db)
    try:
        count = await service.mark_read(order_id, user_id)
        return {"marked_read": count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ============== Delivery Confirmation & Reviews ==============


@router.post(
    "/orders/{order_id}/confirm-delivery",
    response_model=OrderOut,
    summary="Confirm delivery",
    description="Customer confirms that a shipped order has been received.",
)
async def confirm_delivery(
    order_id: UUID,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    """Customer confirms delivery of a shipped order."""
    service = ReviewService(db)
    try:
        result = await service.confirm_delivery(order_id, user_id)
        await db.commit()
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/orders/{order_id}/review",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit review",
    description="Customer submits a rating and review for a delivered order.",
)
async def submit_review(
    order_id: UUID,
    review_data: ReviewCreate,
    user_id: UUID = Depends(get_user_id_from_token_or_query),
    db: AsyncSession = Depends(get_db),
) -> ReviewOut:
    """Submit a review for a delivered order."""
    service = ReviewService(db)
    try:
        return await service.submit_review(order_id, user_id, review_data)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/orders/{order_id}/review",
    response_model=Optional[ReviewOut],
    summary="Get order review",
    description="Get the review for a specific order (if exists).",
)
async def get_order_review(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Optional[ReviewOut]:
    """Get review for an order."""
    service = ReviewService(db)
    return await service.get_review_for_order(order_id)


# NOTE: Print shop endpoints moved to app/api/routers/printshop.py


