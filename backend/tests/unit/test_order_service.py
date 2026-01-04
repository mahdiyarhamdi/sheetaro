"""Unit tests for OrderService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate
from app.models.enums import DesignPlan, OrderStatus, UserRole
from tests.conftest import create_test_user, create_test_product


class TestOrderService:
    """Test cases for OrderService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create OrderService instance."""
        return OrderService(db_session)
    
    @pytest_asyncio.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        return await create_test_user(db_session)
    
    @pytest_asyncio.fixture
    async def test_product(self, db_session):
        """Create a test product."""
        return await create_test_product(db_session)
    
    @pytest.mark.asyncio
    async def test_create_order(self, service, test_user, test_product, sample_order_data):
        """Test creating a new order."""
        sample_order_data["product_id"] = str(test_product.id)
        order_create = OrderCreate(**sample_order_data)
        
        result = await service.create_order(test_user.id, order_create)
        
        assert result is not None
        assert result.user_id == test_user.id
        assert result.product_id == test_product.id
        assert result.design_plan == DesignPlan.PUBLIC
        assert result.quantity == 100
        assert result.total_price > 0
    
    @pytest.mark.asyncio
    async def test_create_order_with_validation(self, service, test_user, test_product, sample_order_data):
        """Test creating order with validation request."""
        sample_order_data["product_id"] = str(test_product.id)
        sample_order_data["validation_requested"] = True
        order_create = OrderCreate(**sample_order_data)
        
        result = await service.create_order(test_user.id, order_create)
        
        assert result.validation_requested is True
        assert result.validation_price == Decimal("50000")
        assert result.status == OrderStatus.AWAITING_VALIDATION
    
    @pytest.mark.asyncio
    async def test_create_order_own_design_without_file_fails(self, service, test_user, test_product, sample_order_data):
        """Test that OWN_DESIGN without file raises error."""
        sample_order_data["product_id"] = str(test_product.id)
        sample_order_data["design_plan"] = DesignPlan.OWN_DESIGN.value
        order_create = OrderCreate(**sample_order_data)
        
        with pytest.raises(ValueError, match="Design file is required"):
            await service.create_order(test_user.id, order_create)
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, service, test_user, test_product, sample_order_data):
        """Test getting order by ID."""
        sample_order_data["product_id"] = str(test_product.id)
        order_create = OrderCreate(**sample_order_data)
        created = await service.create_order(test_user.id, order_create)
        
        result = await service.get_order_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_with_user_check(self, service, test_user, test_product, sample_order_data, db_session):
        """Test getting order with user ownership check."""
        sample_order_data["product_id"] = str(test_product.id)
        order_create = OrderCreate(**sample_order_data)
        created = await service.create_order(test_user.id, order_create)
        
        # Correct user should get the order
        result = await service.get_order_by_id(created.id, test_user.id)
        assert result is not None
        
        # Different user should not get the order
        other_user = await create_test_user(db_session, {
            "telegram_id": 999999999,
            "first_name": "Other",
            "role": UserRole.CUSTOMER,
        })
        result2 = await service.get_order_by_id(created.id, other_user.id)
        assert result2 is None
    
    @pytest.mark.asyncio
    async def test_get_user_orders(self, service, test_user, test_product, sample_order_data):
        """Test getting orders for a user."""
        sample_order_data["product_id"] = str(test_product.id)
        
        # Create multiple orders
        for _ in range(3):
            order_create = OrderCreate(**sample_order_data)
            await service.create_order(test_user.id, order_create)
        
        result = await service.get_user_orders(test_user.id)
        
        assert result.total == 3
        assert len(result.items) == 3
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, service, test_user, test_product, sample_order_data):
        """Test cancelling an order."""
        sample_order_data["product_id"] = str(test_product.id)
        order_create = OrderCreate(**sample_order_data)
        created = await service.create_order(test_user.id, order_create)
        
        result = await service.cancel_order(created.id, test_user.id)
        
        assert result is not None
        assert result.status == OrderStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_order_after_printing_fails(self, service, test_user, test_product, sample_order_data):
        """Test that cancelling order after printing fails."""
        sample_order_data["product_id"] = str(test_product.id)
        order_create = OrderCreate(**sample_order_data)
        created = await service.create_order(test_user.id, order_create)
        
        # Update status to PRINTING
        status_update = OrderStatusUpdate(status=OrderStatus.PRINTING)
        await service.update_order_status(created.id, status_update)
        
        with pytest.raises(ValueError, match="Cannot cancel order"):
            await service.cancel_order(created.id, test_user.id)




