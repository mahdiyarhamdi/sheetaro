"""Order service for business logic.

This module contains the OrderService class which handles all business logic
related to order management, including:
- Order creation with automatic price calculation
- Order status management and transitions
- Print shop workflow (accept, print, ship)
- Order cancellation with state validation

Example usage:
    service = OrderService(db)
    order = await service.create_order(user_id, order_data)
    await service.update_order_status(order.id, status_data)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List
from decimal import Decimal

from app.repositories.order_repository import OrderRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderAssign,
    OrderOut, OrderListResponse, PrintShopOrderOut, PrintShopOrderListResponse,
    PrintShopShipRequest, PrintShopStats, SelectedAttributeItem,
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
    """Service layer for order business logic.
    
    Handles all order-related operations including creation, updates,
    status transitions, and print shop workflow.
    
    Attributes:
        db: Async database session.
        repository: Order repository for database operations.
        category_repo: Category repository for category lookups.
        user_repo: User repository for user lookups.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize OrderService with database session."""
        self.db = db
        self.repository = OrderRepository(db)
        self.category_repo = CategoryRepository(db)
        self.user_repo = UserRepository(db)
    
    async def _calculate_prices(
        self,
        category_base_price: Decimal,
        selected_attributes: List[SelectedAttributeItem],
        quantity: int,
        design_plan: DesignPlan,
        validation_requested: bool,
        plan_id: Optional[UUID] = None,
    ) -> dict:
        """Calculate order prices based on category and selected attributes.
        
        Args:
            category_base_price: Base price from category.
            selected_attributes: List of selected attributes with price modifiers.
            quantity: Number of units ordered.
            design_plan: Selected design plan type.
            validation_requested: Whether validation was requested.
            plan_id: Optional plan ID to fetch actual price from database.
        
        Returns:
            Dictionary with base_price, attributes_price, design_price, 
            validation_price, print_price, total_price, and max_revisions.
        """
        # Get design price from database if plan_id provided, otherwise use fallback
        design_price = Decimal('0')
        max_revisions_from_plan = None
        if plan_id:
            plan = await self.category_repo.get_plan_by_id(plan_id)
            if plan:
                design_price = Decimal(str(plan.price))
                max_revisions_from_plan = plan.max_revisions
        else:
            # Fallback to hardcoded prices if no plan_id
            design_price = DESIGN_PRICES.get(design_plan, Decimal('0'))
        
        validation_price = VALIDATION_PRICE if validation_requested else Decimal('0')
        
        # Calculate attributes prices - separate FIXED and MULTIPLIER types
        fixed_attributes_price = Decimal('0')
        multiplier = Decimal('1')
        
        for attr_item in selected_attributes:
            # Get attribute from database to check its price_type
            attribute = await self.category_repo.get_attribute_by_id(attr_item.attribute_id)
            if attribute and attr_item.option_id:
                # Get the ACTUAL price_modifier from database, not from request
                option = await self.category_repo.get_option_by_id(attr_item.option_id)
                if option:
                    modifier = Decimal(str(option.price_modifier))
                    if attribute.price_type.value == "MULTIPLIER":
                        # Multiplier is applied to base price (e.g., 1.5 = 150%)
                        multiplier *= modifier
                    else:
                        # FIXED: add to fixed price
                        fixed_attributes_price += modifier
        
        # Calculate unit price: (base_price × multiplier) + fixed_attributes
        base_price = category_base_price
        unit_price = (base_price * multiplier) + fixed_attributes_price
        
        # Total attributes price for record keeping
        attributes_price = int(unit_price - base_price)
        
        # Print price = unit price × quantity
        print_price = unit_price * quantity
        
        total_price = design_price + validation_price + print_price
        
        # Set max revisions - prefer value from database plan if available
        max_revisions = max_revisions_from_plan
        if max_revisions is None:
            # Fallback to enum-based defaults
            if design_plan == DesignPlan.SEMI_PRIVATE:
                max_revisions = 3
            elif design_plan == DesignPlan.PUBLIC:
                max_revisions = 0
            # Private plan has unlimited (None)
        
        return {
            'base_price': base_price,
            'attributes_price': attributes_price,
            'design_price': design_price,
            'validation_price': validation_price,
            'print_price': print_price,
            'total_price': total_price,
            'max_revisions': max_revisions,
        }
    
    async def create_order(self, user_id: UUID, order_data: OrderCreate) -> OrderOut:
        """Create a new order."""
        # Validate category exists
        category = await self.category_repo.get_category_by_id(order_data.category_id)
        if not category:
            raise ValueError("Category not found")
        
        if not category.is_active:
            raise ValueError("Category is not available")
        
        # Validate design file for OWN_DESIGN
        if order_data.design_plan == DesignPlan.OWN_DESIGN and not order_data.design_file_url:
            raise ValueError("Design file is required for OWN_DESIGN plan")
        
        # Calculate prices
        prices = await self._calculate_prices(
            category_base_price=Decimal(str(category.base_price)),
            selected_attributes=order_data.selected_attributes,
            quantity=order_data.quantity,
            design_plan=order_data.design_plan,
            validation_requested=order_data.validation_requested,
            plan_id=order_data.plan_id,
        )
        
        # All orders start with PENDING_PAYMENT status
        # After payment is approved, the order will transition to the appropriate next status
        # based on validation_requested and design_plan
        prices['status'] = OrderStatus.PENDING_PAYMENT
        
        # Create order
        order = await self.repository.create(user_id, order_data, prices)
        
        log_event(
            event_type="order.create",
            order_id=str(order.id),
            user_id=str(user_id),
            category_id=str(order_data.category_id),
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
    ) -> PrintShopOrderListResponse:
        """Get orders ready for print shop."""
        page_size = min(page_size, 100)
        page = max(page, 1)

        orders, total = await self.repository.get_ready_for_print(
            page=page,
            page_size=page_size,
        )

        items = [self._to_printshop_order_out(o) for o in orders]

        return PrintShopOrderListResponse(
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
        if order.status in [OrderStatus.PRINTING, OrderStatus.PRINTED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
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

    # ==================== Print Shop Methods ====================

    def _to_printshop_order_out(self, order) -> PrintShopOrderOut:
        """Convert an order with user relation to PrintShopOrderOut."""
        order_out = PrintShopOrderOut.model_validate(order)
        if order.user:
            order_out.customer_name = f"{order.user.first_name} {order.user.last_name or ''}".strip()
            order_out.customer_phone = order.user.phone_number
            order_out.customer_city = order.user.city
            order_out.customer_address = order.user.address
        return order_out

    async def get_printshop_my_orders(
        self,
        printshop_id: UUID,
        status_filter: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PrintShopOrderListResponse:
        """Get orders assigned to a print shop."""
        page_size = min(page_size, 100)
        page = max(page, 1)

        orders, total = await self.repository.get_printshop_my_orders(
            printshop_id=printshop_id,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
        )

        items = [self._to_printshop_order_out(o) for o in orders]

        return PrintShopOrderListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_printshop_order_detail(
        self,
        order_id: UUID,
        printshop_id: UUID,
    ) -> Optional[PrintShopOrderOut]:
        """Get a single order detail for print shop."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        if order.assigned_printshop_id != printshop_id:
            return None
        return self._to_printshop_order_out(order)

    async def complete_printing(
        self,
        order_id: UUID,
        printshop_id: UUID,
    ) -> Optional[OrderOut]:
        """Mark order as printed by print shop."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None

        if order.assigned_printshop_id != printshop_id:
            raise ValueError("Order is not assigned to this print shop")

        if order.status != OrderStatus.PRINTING:
            raise ValueError(f"Cannot complete printing: order status is {order.status.value}")

        updated = await self.repository.complete_printing(order_id)
        if updated:
            log_event(
                event_type="order.print_completed",
                order_id=str(order_id),
                printshop_id=str(printshop_id),
            )
            return OrderOut.model_validate(updated)
        return None

    async def ship_order(
        self,
        order_id: UUID,
        printshop_id: UUID,
        tracking_code: str,
    ) -> Optional[OrderOut]:
        """Ship order with tracking code."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None

        if order.assigned_printshop_id != printshop_id:
            raise ValueError("Order is not assigned to this print shop")

        if order.status != OrderStatus.PRINTED:
            raise ValueError(f"Cannot ship: order status is {order.status.value}, must be PRINTED")

        updated = await self.repository.ship_order(order_id, tracking_code)
        if updated:
            log_event(
                event_type="order.shipped",
                order_id=str(order_id),
                printshop_id=str(printshop_id),
                tracking_code=tracking_code,
            )
            return OrderOut.model_validate(updated)
        return None

    async def get_printshop_stats(self, printshop_id: UUID) -> PrintShopStats:
        """Get dashboard statistics for a print shop."""
        stats = await self.repository.get_printshop_stats(printshop_id)
        return PrintShopStats(**stats)




