"""Order repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

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
                selectinload(Order.product),
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
        query = query.options(selectinload(Order.user), selectinload(Order.product))
        
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
        query = query.options(selectinload(Order.user), selectinload(Order.product))
        
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




