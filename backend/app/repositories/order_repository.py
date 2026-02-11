"""Order repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, extract, case
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.models.order import Order
from app.models.enums import OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate, OrderAssign


class OrderRepository:
    """Repository for order database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_id: UUID, order_data: OrderCreate, prices: dict) -> Order:
        """Create a new order."""
        order_dict = order_data.model_dump()
        order_dict['user_id'] = user_id
        order_dict.update(prices)
        
        # Remove plan_id as it's not a field in the Order model (used only for price calculation)
        order_dict.pop('plan_id', None)
        
        # Convert UUID objects in selected_attributes to strings for JSONB serialization
        if 'selected_attributes' in order_dict and order_dict['selected_attributes']:
            order_dict['selected_attributes'] = [
                {
                    key: str(value) if isinstance(value, UUID) else value
                    for key, value in attr.items()
                }
                for attr in order_dict['selected_attributes']
            ]
        
        order = Order(**order_dict)
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID with relationships."""
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.category),
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """Get orders for a user with pagination."""
        query = select(Order).where(Order.user_id == user_id)
        count_query = select(func.count(Order.id)).where(Order.user_id == user_id)
        
        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc())
        
        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        orders = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return orders, total
    
    async def get_ready_for_print(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """Get orders ready for print shop."""
        query = select(Order).where(Order.status == OrderStatus.READY_FOR_PRINT)
        count_query = select(func.count(Order.id)).where(Order.status == OrderStatus.READY_FOR_PRINT)
        
        query = query.order_by(Order.created_at.asc())  # FIFO
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.options(selectinload(Order.user), selectinload(Order.category))
        
        result = await self.db.execute(query)
        orders = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return orders, total
    
    async def get_printshop_orders(
        self,
        printshop_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """Get orders assigned to a print shop."""
        query = select(Order).where(Order.assigned_printshop_id == printshop_id)
        count_query = select(func.count(Order.id)).where(Order.assigned_printshop_id == printshop_id)
        
        query = query.order_by(Order.accepted_at.desc())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.options(selectinload(Order.user), selectinload(Order.category))
        
        result = await self.db.execute(query)
        orders = list(result.scalars().all())
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        return orders, total
    
    async def update(self, order_id: UUID, order_data: OrderUpdate) -> Optional[Order]:
        """Update order."""
        update_data = order_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(order_id)
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(order_id)
    
    async def update_status(self, order_id: UUID, status_data: OrderStatusUpdate) -> Optional[Order]:
        """Update order status with timestamps."""
        update_data = status_data.model_dump(exclude_unset=True)
        now = datetime.now(timezone.utc)
        
        # Set appropriate timestamp based on status
        if status_data.status == OrderStatus.PRINTING:
            update_data['accepted_at'] = now
        elif status_data.status == OrderStatus.PRINTED:
            update_data['printed_at'] = now
        elif status_data.status == OrderStatus.SHIPPED:
            update_data['shipped_at'] = now
        elif status_data.status == OrderStatus.DELIVERED:
            update_data['delivered_at'] = now
        elif status_data.status == OrderStatus.CANCELLED:
            update_data['cancelled_at'] = now
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(order_id)
    
    async def assign_staff(self, order_id: UUID, assign_data: OrderAssign) -> Optional[Order]:
        """Assign staff to order."""
        update_data = assign_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(order_id)
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(order_id)
    
    async def accept_by_printshop(self, order_id: UUID, printshop_id: UUID) -> Optional[Order]:
        """Accept order by print shop."""
        order = await self.get_by_id(order_id)
        if not order or order.status != OrderStatus.READY_FOR_PRINT:
            return None
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                assigned_printshop_id=printshop_id,
                status=OrderStatus.PRINTING,
                accepted_at=datetime.now(timezone.utc),
            )
        )
        await self.db.flush()
        return await self.get_by_id(order_id)
    
    async def increment_revision(self, order_id: UUID) -> Optional[Order]:
        """Increment revision count."""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(revision_count=order.revision_count + 1)
        )
        await self.db.flush()
        return await self.get_by_id(order_id)

    # ==================== Print Shop Methods ====================

    async def get_printshop_my_orders(
        self,
        printshop_id: UUID,
        status_filter: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """Get orders assigned to a specific print shop with optional status filter."""
        base_condition = Order.assigned_printshop_id == printshop_id
        query = select(Order).where(base_condition)
        count_query = select(func.count(Order.id)).where(base_condition)

        if status_filter:
            query = query.where(Order.status == status_filter)
            count_query = count_query.where(Order.status == status_filter)

        query = query.order_by(Order.accepted_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.options(selectinload(Order.user), selectinload(Order.category))

        result = await self.db.execute(query)
        orders = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return orders, total

    async def complete_printing(self, order_id: UUID) -> Optional[Order]:
        """Mark order as printed."""
        order = await self.get_by_id(order_id)
        if not order or order.status != OrderStatus.PRINTING:
            return None

        now = datetime.now(timezone.utc)
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                status=OrderStatus.PRINTED,
                printed_at=now,
            )
        )
        await self.db.flush()
        return await self.get_by_id(order_id)

    async def ship_order(self, order_id: UUID, tracking_code: str) -> Optional[Order]:
        """Mark order as shipped with tracking code."""
        order = await self.get_by_id(order_id)
        if not order or order.status != OrderStatus.PRINTED:
            return None

        now = datetime.now(timezone.utc)
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                status=OrderStatus.SHIPPED,
                shipped_at=now,
                tracking_code=tracking_code,
            )
        )
        await self.db.flush()
        return await self.get_by_id(order_id)

    async def get_printshop_stats(self, printshop_id: UUID) -> dict:
        """Get aggregated stats for a print shop."""
        base_condition = Order.assigned_printshop_id == printshop_id

        # Count by status
        status_counts = {}
        for s in [OrderStatus.PRINTING, OrderStatus.PRINTED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            result = await self.db.execute(
                select(func.count(Order.id)).where(
                    and_(base_condition, Order.status == s)
                )
            )
            status_counts[s.value] = result.scalar() or 0

        # Total assigned
        total_result = await self.db.execute(
            select(func.count(Order.id)).where(base_condition)
        )
        total = total_result.scalar() or 0

        # Queue count (READY_FOR_PRINT, not assigned)
        queue_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.status == OrderStatus.READY_FOR_PRINT)
        )
        pending = queue_result.scalar() or 0

        # Average print time (accepted_at -> printed_at)
        avg_print = await self.db.execute(
            select(
                func.avg(
                    extract('epoch', Order.printed_at) - extract('epoch', Order.accepted_at)
                )
            ).where(
                and_(
                    base_condition,
                    Order.printed_at.isnot(None),
                    Order.accepted_at.isnot(None),
                )
            )
        )
        avg_print_seconds = avg_print.scalar()
        avg_print_hours = round(avg_print_seconds / 3600, 1) if avg_print_seconds else None

        # Average ship time (printed_at -> shipped_at)
        avg_ship = await self.db.execute(
            select(
                func.avg(
                    extract('epoch', Order.shipped_at) - extract('epoch', Order.printed_at)
                )
            ).where(
                and_(
                    base_condition,
                    Order.shipped_at.isnot(None),
                    Order.printed_at.isnot(None),
                )
            )
        )
        avg_ship_seconds = avg_ship.scalar()
        avg_ship_hours = round(avg_ship_seconds / 3600, 1) if avg_ship_seconds else None

        # SLA compliance: shipped within 48h of accepted_at
        sla_total = await self.db.execute(
            select(func.count(Order.id)).where(
                and_(base_condition, Order.shipped_at.isnot(None))
            )
        )
        sla_total_count = sla_total.scalar() or 0

        sla_passed = await self.db.execute(
            select(func.count(Order.id)).where(
                and_(
                    base_condition,
                    Order.shipped_at.isnot(None),
                    Order.accepted_at.isnot(None),
                    (extract('epoch', Order.shipped_at) - extract('epoch', Order.accepted_at)) <= 48 * 3600,
                )
            )
        )
        sla_passed_count = sla_passed.scalar() or 0
        sla_compliance = round((sla_passed_count / sla_total_count) * 100, 1) if sla_total_count > 0 else None

        return {
            'total_orders': total,
            'pending_orders': pending,
            'in_progress_orders': status_counts.get(OrderStatus.PRINTING.value, 0),
            'printed_orders': status_counts.get(OrderStatus.PRINTED.value, 0),
            'shipped_orders': status_counts.get(OrderStatus.SHIPPED.value, 0),
            'delivered_orders': status_counts.get(OrderStatus.DELIVERED.value, 0),
            'avg_print_time_hours': avg_print_hours,
            'avg_ship_time_hours': avg_ship_hours,
            'sla_compliance_percent': sla_compliance,
        }

    async def get_stale_ready_orders(self, threshold_minutes: int = 30) -> list[Order]:
        """Get READY_FOR_PRINT orders older than threshold."""
        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=threshold_minutes)
        query = (
            select(Order)
            .where(
                and_(
                    Order.status == OrderStatus.READY_FOR_PRINT,
                    Order.assigned_printshop_id.is_(None),
                    Order.created_at <= threshold_time,
                )
            )
            .options(selectinload(Order.user))
            .order_by(Order.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())










