"""Order service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from decimal import Decimal

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderAssign,
    OrderOut, OrderListResponse, PrintShopOrderOut
)
from app.models.enums import OrderStatus, DesignPlan, UserRole
from app.utils.logger import log_event


# Pricing constants (in Tomans)
VALIDATION_PRICE = Decimal('50000')
DESIGN_PRICES = {
    DesignPlan.PUBLIC: Decimal('0'),
    DesignPlan.SEMI_PRIVATE: Decimal('600000'),  # Base price
    DesignPlan.PRIVATE: Decimal('5000000'),
    DesignPlan.OWN_DESIGN: Decimal('0'),
}


class OrderService:
    """Service layer for order business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.user_repo = UserRepository(db)
    
    def _calculate_prices(
        self,
        product_base_price: Decimal,
        quantity: int,
        design_plan: DesignPlan,
        validation_requested: bool,
    ) -> dict:
        """Calculate order prices."""
        design_price = DESIGN_PRICES.get(design_plan, Decimal('0'))
        validation_price = VALIDATION_PRICE if validation_requested else Decimal('0')
        print_price = product_base_price * quantity
        
        total_price = design_price + validation_price + print_price
        
        # Set max revisions based on plan
        max_revisions = None
        if design_plan == DesignPlan.SEMI_PRIVATE:
            max_revisions = 3
        elif design_plan == DesignPlan.PUBLIC:
            max_revisions = 0
        # Private plan has unlimited (None)
        
        return {
            'design_price': design_price,
            'validation_price': validation_price,
            'print_price': print_price,
            'total_price': total_price,
            'max_revisions': max_revisions,
        }
    
    async def create_order(self, user_id: UUID, order_data: OrderCreate) -> OrderOut:
        """Create a new order."""
        # Validate product exists
        product = await self.product_repo.get_by_id(order_data.product_id)
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_active:
            raise ValueError("Product is not available")
        
        # Validate design file for OWN_DESIGN
        if order_data.design_plan == DesignPlan.OWN_DESIGN and not order_data.design_file_url:
            raise ValueError("Design file is required for OWN_DESIGN plan")
        
        # Calculate prices
        prices = self._calculate_prices(
            product_base_price=product.base_price,
            quantity=order_data.quantity,
            design_plan=order_data.design_plan,
            validation_requested=order_data.validation_requested,
        )
        
        # Determine initial status
        initial_status = OrderStatus.PENDING
        if order_data.validation_requested:
            initial_status = OrderStatus.AWAITING_VALIDATION
        elif order_data.design_plan in [DesignPlan.SEMI_PRIVATE, DesignPlan.PRIVATE]:
            initial_status = OrderStatus.DESIGNING
        
        prices['status'] = initial_status
        
        # Create order
        order = await self.repository.create(user_id, order_data, prices)
        
        log_event(
            event_type="order.create",
            order_id=str(order.id),
            user_id=str(user_id),
            product_id=str(order_data.product_id),
            design_plan=order_data.design_plan.value,
            total_price=str(order.total_price),
        )
        
        return OrderOut.model_validate(order)
    
    async def get_order_by_id(self, order_id: UUID, user_id: Optional[UUID] = None) -> Optional[OrderOut]:
        """Get order by ID, optionally filtering by user."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        
        # If user_id provided, verify ownership
        if user_id and order.user_id != user_id:
            return None
        
        return OrderOut.model_validate(order)
    
    async def get_user_orders(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> OrderListResponse:
        """Get orders for a user."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        orders, total = await self.repository.get_by_user(
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        
        return OrderListResponse(
            items=[OrderOut.model_validate(o) for o in orders],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def get_printshop_queue(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> OrderListResponse:
        """Get orders ready for print shop."""
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        orders, total = await self.repository.get_ready_for_print(
            page=page,
            page_size=page_size,
        )
        
        # Convert to PrintShopOrderOut with customer info
        items = []
        for order in orders:
            order_out = PrintShopOrderOut.model_validate(order)
            if order.user:
                order_out.customer_name = f"{order.user.first_name} {order.user.last_name or ''}".strip()
                order_out.customer_phone = order.user.phone_number
                order_out.customer_city = order.user.city
            items.append(order_out)
        
        return OrderListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def update_order(
        self,
        order_id: UUID,
        order_data: OrderUpdate,
        user_id: Optional[UUID] = None,
    ) -> Optional[OrderOut]:
        """Update order."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        
        # Verify ownership if user_id provided
        if user_id and order.user_id != user_id:
            return None
        
        # Can only update pending orders
        if order.status not in [OrderStatus.PENDING, OrderStatus.NEEDS_ACTION]:
            raise ValueError("Cannot update order in current status")
        
        updated_order = await self.repository.update(order_id, order_data)
        if updated_order:
            return OrderOut.model_validate(updated_order)
        return None
    
    async def update_order_status(
        self,
        order_id: UUID,
        status_data: OrderStatusUpdate,
    ) -> Optional[OrderOut]:
        """Update order status (admin/staff only)."""
        order = await self.repository.update_status(order_id, status_data)
        
        if order:
            log_event(
                event_type="order.status_change",
                order_id=str(order_id),
                new_status=status_data.status.value,
            )
            return OrderOut.model_validate(order)
        return None
    
    async def accept_order_by_printshop(
        self,
        order_id: UUID,
        printshop_id: UUID,
    ) -> Optional[OrderOut]:
        """Accept order by print shop."""
        # Verify print shop role
        printshop = await self.user_repo.get_by_id(printshop_id)
        if not printshop or printshop.role != UserRole.PRINT_SHOP:
            raise ValueError("User is not a print shop")
        
        order = await self.repository.accept_by_printshop(order_id, printshop_id)
        
        if order:
            log_event(
                event_type="order.accepted_by_printshop",
                order_id=str(order_id),
                printshop_id=str(printshop_id),
            )
            return OrderOut.model_validate(order)
        return None
    
    async def cancel_order(
        self,
        order_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Optional[OrderOut]:
        """Cancel order."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        
        # Verify ownership if user_id provided
        if user_id and order.user_id != user_id:
            return None
        
        # Can only cancel before printing starts
        if order.status in [OrderStatus.PRINTING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("Cannot cancel order after printing has started")
        
        status_update = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        updated_order = await self.repository.update_status(order_id, status_update)
        
        if updated_order:
            log_event(
                event_type="order.cancelled",
                order_id=str(order_id),
                user_id=str(user_id) if user_id else None,
            )
            return OrderOut.model_validate(updated_order)
        return None



