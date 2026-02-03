"""Admin API router - consolidated admin endpoints."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user_from_token, require_admin_token as require_admin
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.models.processed_design import ProcessedDesign
from app.models.enums import UserRole, OrderStatus, PaymentStatus, ValidationStatus
from app.services.user_service import UserService
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


# ============== Schemas ==============

class AdminStatsResponse(BaseModel):
    """Dashboard statistics."""
    total_orders: int
    pending_payments: int
    total_revenue: float
    new_users_today: int
    active_users: int
    orders_today: int
    orders_this_week: int
    pending_orders: int


class UserListResponse(BaseModel):
    """Paginated user list."""
    items: List[UserOut]
    total: int
    page: int
    page_size: int


class UserRoleUpdate(BaseModel):
    """Update user role."""
    role: UserRole


class UserStatusUpdate(BaseModel):
    """Update user status."""
    is_active: bool
    reason: Optional[str] = None


class OrderStatsResponse(BaseModel):
    """Order statistics."""
    total: int
    by_status: dict
    by_day: List[dict]


class RevenueStatsResponse(BaseModel):
    """Revenue statistics."""
    total_revenue: float
    this_month: float
    last_month: float
    by_day: List[dict]


# ============== Dashboard Stats ==============

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminStatsResponse:
    """Get dashboard statistics. Admin only."""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    # Total orders
    total_orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = total_orders_result.scalar() or 0
    
    # Pending payments
    pending_payments_result = await db.execute(
        select(func.count(Payment.id)).where(Payment.status == PaymentStatus.PENDING)
    )
    pending_payments = pending_payments_result.scalar() or 0
    
    # Total revenue (successful payments)
    revenue_result = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.SUCCESS)
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # New users today
    new_users_result = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )
    new_users_today = new_users_result.scalar() or 0
    
    # Active users
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0
    
    # Orders today
    orders_today_result = await db.execute(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
    )
    orders_today = orders_today_result.scalar() or 0
    
    # Orders this week
    orders_week_result = await db.execute(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) >= week_ago
        )
    )
    orders_this_week = orders_week_result.scalar() or 0
    
    # Pending orders
    pending_orders_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.AWAITING_VALIDATION])
        )
    )
    pending_orders = pending_orders_result.scalar() or 0
    
    return AdminStatsResponse(
        total_orders=total_orders,
        pending_payments=pending_payments,
        total_revenue=total_revenue,
        new_users_today=new_users_today,
        active_users=active_users,
        orders_today=orders_today,
        orders_this_week=orders_this_week,
        pending_orders=pending_orders,
    )


# ============== Users Management ==============

@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or phone"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserListResponse:
    """List all users with filters. Admin only."""
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Apply filters
    conditions = []
    
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern)) |
            (User.phone_number.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )
    
    if role:
        conditions.append(User.role == role)
    
    if is_active is not None:
        conditions.append(User.is_active == is_active)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        items=[UserOut.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserOut:
    """Get user details. Admin only."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    return UserOut.model_validate(user)


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserOut:
    """Update user role. Admin only."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    user.role = data.role
    await db.commit()
    await db.refresh(user)
    
    return UserOut.model_validate(user)


@router.post("/users/{user_id}/ban", response_model=UserOut)
async def ban_user(
    user_id: UUID,
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserOut:
    """Ban or unban a user. Admin only."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نمی‌توانید خودتان را مسدود کنید"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    user.is_active = data.is_active
    await db.commit()
    await db.refresh(user)
    
    return UserOut.model_validate(user)


@router.get("/stats/users")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Get user statistics. Admin only."""
    # By role
    role_stats = {}
    for role in UserRole:
        result = await db.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        role_stats[role.value] = result.scalar() or 0
    
    # New users by day (last 7 days)
    today = datetime.utcnow().date()
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        result = await db.execute(
            select(func.count(User.id)).where(
                func.date(User.created_at) == day
            )
        )
        daily_stats.append({
            "date": day.isoformat(),
            "count": result.scalar() or 0
        })
    
    return {
        "by_role": role_stats,
        "daily_signups": list(reversed(daily_stats)),
    }


# ============== Orders Management ==============

@router.get("/orders")
async def list_admin_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """List all orders with filters. Admin only."""
    query = select(Order)
    count_query = select(func.count(Order.id))
    
    conditions = []
    if status:
        conditions.append(Order.status == status)
    if user_id:
        conditions.append(Order.user_id == user_id)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(o.id),
                "user_id": str(o.user_id),
                "status": o.status.value,
                "total_price": float(o.total_price) if o.total_price else 0,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    new_status: OrderStatus = Query(..., description="New status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Force update order status. Admin only."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد"
        )
    
    old_status = order.status
    order.status = new_status
    await db.commit()
    
    return {
        "success": True,
        "order_id": str(order_id),
        "old_status": old_status.value,
        "new_status": new_status.value,
    }


@router.post("/orders/{order_id}/assign")
async def assign_order(
    order_id: UUID,
    designer_id: Optional[UUID] = Query(None),
    validator_id: Optional[UUID] = Query(None),
    printshop_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Assign order to staff members. Admin only."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد"
        )
    
    if designer_id:
        order.assigned_designer_id = designer_id
    if validator_id:
        order.assigned_validator_id = validator_id
    if printshop_id:
        order.assigned_printshop_id = printshop_id
    
    await db.commit()
    
    return {
        "success": True,
        "order_id": str(order_id),
        "assigned_designer_id": str(order.assigned_designer_id) if order.assigned_designer_id else None,
        "assigned_validator_id": str(order.assigned_validator_id) if order.assigned_validator_id else None,
        "assigned_printshop_id": str(order.assigned_printshop_id) if order.assigned_printshop_id else None,
    }


@router.get("/stats/orders", response_model=OrderStatsResponse)
async def get_order_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> OrderStatsResponse:
    """Get order statistics. Admin only."""
    # Total
    total_result = await db.execute(select(func.count(Order.id)))
    total = total_result.scalar() or 0
    
    # By status
    by_status = {}
    for s in OrderStatus:
        result = await db.execute(
            select(func.count(Order.id)).where(Order.status == s)
        )
        by_status[s.value] = result.scalar() or 0
    
    # By day (last 7 days)
    today = datetime.utcnow().date()
    by_day = []
    for i in range(7):
        day = today - timedelta(days=i)
        result = await db.execute(
            select(func.count(Order.id)).where(
                func.date(Order.created_at) == day
            )
        )
        by_day.append({
            "date": day.isoformat(),
            "count": result.scalar() or 0
        })
    
    return OrderStatsResponse(
        total=total,
        by_status=by_status,
        by_day=list(reversed(by_day)),
    )


# ============== Payments Management ==============

@router.get("/payments")
async def list_admin_payments(
    status: Optional[PaymentStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """List all payments with filters. Admin only."""
    query = select(Payment)
    count_query = select(func.count(Payment.id))
    
    if status:
        query = query.where(Payment.status == status)
        count_query = count_query.where(Payment.status == status)
    
    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Payment.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    payments = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(p.id),
                "order_id": str(p.order_id) if p.order_id else None,
                "user_id": str(p.user_id),
                "amount": float(p.amount),
                "type": p.type.value,
                "status": p.status.value,
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/payments/{payment_id}/verify")
async def verify_payment(
    payment_id: UUID,
    approved: bool = Query(..., description="Approve or reject"),
    reason: Optional[str] = Query(None, description="Rejection reason"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Verify or reject a payment. Admin only."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="پرداخت یافت نشد"
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این پرداخت قبلاً بررسی شده است"
        )
    
    payment.status = PaymentStatus.SUCCESS if approved else PaymentStatus.FAILED
    payment.approved_by = current_user.id
    payment.approved_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "payment_id": str(payment_id),
        "status": payment.status.value,
    }


@router.get("/stats/revenue", response_model=RevenueStatsResponse)
async def get_revenue_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RevenueStatsResponse:
    """Get revenue statistics. Admin only."""
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Total revenue
    total_result = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.SUCCESS)
    )
    total_revenue = float(total_result.scalar() or 0)
    
    # This month
    this_month_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                func.date(Payment.created_at) >= this_month_start
            )
        )
    )
    this_month = float(this_month_result.scalar() or 0)
    
    # Last month
    last_month_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.status == PaymentStatus.SUCCESS,
                func.date(Payment.created_at) >= last_month_start,
                func.date(Payment.created_at) < this_month_start
            )
        )
    )
    last_month = float(last_month_result.scalar() or 0)
    
    # By day (last 7 days)
    by_day = []
    for i in range(7):
        day = today - timedelta(days=i)
        result = await db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.status == PaymentStatus.SUCCESS,
                    func.date(Payment.created_at) == day
                )
            )
        )
        by_day.append({
            "date": day.isoformat(),
            "amount": float(result.scalar() or 0)
        })
    
    return RevenueStatsResponse(
        total_revenue=total_revenue,
        this_month=this_month,
        last_month=last_month,
        by_day=list(reversed(by_day)),
    )


# ============== Validation Management ==============

class ValidationRequestResponse(BaseModel):
    """Validation request item."""
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


class ValidationListResponse(BaseModel):
    """Paginated validation requests."""
    items: List[ValidationRequestResponse]
    total: int
    page: int
    page_size: int


class ValidationRejectRequest(BaseModel):
    """Reject validation with comment."""
    comment: str


@router.get("/validations", response_model=ValidationListResponse)
async def list_validation_requests(
    status: Optional[ValidationStatus] = Query(None, description="Filter by validation status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ValidationListResponse:
    """List orders with validation requested. Admin only."""
    from app.models.category import Category
    from sqlalchemy import or_
    
    query = select(Order).where(Order.validation_requested == True)
    count_query = select(func.count(Order.id)).where(Order.validation_requested == True)
    
    if status:
        # PENDING should include NULL validation_status (new requests)
        if status == ValidationStatus.PENDING:
            status_filter = or_(
                Order.validation_status == status,
                Order.validation_status.is_(None)
            )
        else:
            status_filter = Order.validation_status == status
        query = query.where(status_filter)
        count_query = count_query.where(status_filter)
    
    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    items = []
    for order in orders:
        # Get user info
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalar_one_or_none()
        
        # Get category info
        category_name = None
        if order.category_id:
            cat_result = await db.execute(select(Category).where(Category.id == order.category_id))
            cat = cat_result.scalar_one_or_none()
            if cat:
                category_name = cat.name_fa
        
        # Get plan name from enum
        plan_name = None
        if order.design_plan:
            plan_names = {
                "PUBLIC": "عمومی",
                "SEMI_PRIVATE": "نیمه خصوصی",
                "PRIVATE": "خصوصی",
                "OWN_DESIGN": "طرح اختصاصی",
            }
            plan_name = plan_names.get(order.design_plan.value, order.design_plan.value)
        
        # Get design preview URL - check order.design_file_url first (for OWN_DESIGN),
        # then check processed_designs table (for template-based orders)
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
                # Also get template name if available
                if processed.template:
                    template_name = processed.template.name_fa
        
        items.append(ValidationRequestResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            user_name=user.full_name if user else None,
            user_phone=user.phone_number if user else None,
            category_name=category_name,
            plan_name=plan_name,
            template_name=template_name,
            validation_status=order.validation_status.value if order.validation_status else None,
            total_price=float(order.total_price) if order.total_price else 0,
            validation_price=float(order.validation_price) if order.validation_price else 0,
            created_at=order.created_at.isoformat(),
            design_preview_url=design_preview_url,
        ))
    
    return ValidationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/validations/{order_id}/approve")
async def approve_validation(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Approve validation for an order. Admin only."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد"
        )
    
    if not order.validation_requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این سفارش درخواست اعتبارسنجی نداشته است"
        )
    
    order.validation_status = ValidationStatus.PASSED
    order.assigned_validator_id = current_user.id
    
    # If order was awaiting validation, move it forward to ready for print
    if order.status == OrderStatus.AWAITING_VALIDATION:
        order.status = OrderStatus.READY_FOR_PRINT
    
    await db.commit()
    
    return {
        "success": True,
        "order_id": str(order_id),
        "validation_status": order.validation_status.value,
        "message": "اعتبارسنجی با موفقیت تأیید شد"
    }


@router.post("/validations/{order_id}/reject")
async def reject_validation(
    order_id: UUID,
    data: ValidationRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Reject validation with correction comment. Admin only."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد"
        )
    
    if not order.validation_requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این سفارش درخواست اعتبارسنجی نداشته است"
        )
    
    order.validation_status = ValidationStatus.FAILED
    order.assigned_validator_id = current_user.id
    order.admin_notes = data.comment  # Store the correction comment
    
    # Set status to needs revision
    order.status = OrderStatus.NEEDS_ACTION
    
    await db.commit()
    
    return {
        "success": True,
        "order_id": str(order_id),
        "validation_status": order.validation_status.value,
        "comment": data.comment,
        "message": "درخواست اصلاح ثبت شد"
    }

