"""Unit tests for PaymentService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from app.services.payment_service import PaymentService
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate
from app.schemas.payment import PaymentInitiate, PaymentCallback
from app.models.enums import DesignPlan, PaymentType, PaymentStatus
from tests.conftest import create_test_user, create_test_product


class TestPaymentService:
    """Test cases for PaymentService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create PaymentService instance."""
        return PaymentService(db_session)
    
    @pytest_asyncio.fixture
    async def order_service(self, db_session):
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
    
    @pytest_asyncio.fixture
    async def test_order(self, order_service, test_user, test_product):
        """Create a test order."""
        order_data = OrderCreate(
            product_id=test_product.id,
            design_plan=DesignPlan.PUBLIC,
            quantity=100,
            validation_requested=False,
        )
        return await order_service.create_order(test_user.id, order_data)
    
    @pytest.mark.asyncio
    async def test_initiate_payment(self, service, test_user, test_order):
        """Test initiating a payment."""
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        
        result = await service.initiate_payment(test_user.id, payment_data)
        
        assert result is not None
        assert result.payment_id is not None
        assert result.authority is not None
        assert result.redirect_url is not None
        assert result.amount == test_order.print_price
    
    @pytest.mark.asyncio
    async def test_initiate_payment_wrong_user_fails(self, service, test_order, db_session):
        """Test that wrong user cannot initiate payment."""
        other_user = await create_test_user(db_session, {
            "telegram_id": 999999999,
            "first_name": "Other",
        })
        
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.initiate_payment(other_user.id, payment_data)
    
    @pytest.mark.asyncio
    async def test_handle_callback_success(self, service, test_user, test_order):
        """Test handling successful payment callback."""
        # First initiate payment
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        initiated = await service.initiate_payment(test_user.id, payment_data)
        
        # Handle callback
        callback_data = PaymentCallback(
            authority=initiated.authority,
            status="OK",
            ref_id="REF123456",
        )
        
        result = await service.handle_callback(callback_data)
        
        assert result is not None
        assert result.status == PaymentStatus.SUCCESS
        assert result.ref_id == "REF123456"
    
    @pytest.mark.asyncio
    async def test_handle_callback_failed(self, service, test_user, test_order):
        """Test handling failed payment callback."""
        # First initiate payment
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        initiated = await service.initiate_payment(test_user.id, payment_data)
        
        # Handle failed callback
        callback_data = PaymentCallback(
            authority=initiated.authority,
            status="NOK",
        )
        
        result = await service.handle_callback(callback_data)
        
        assert result is not None
        assert result.status == PaymentStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_get_payment_summary(self, service, test_user, test_order):
        """Test getting payment summary."""
        # Initiate and complete payment
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        initiated = await service.initiate_payment(test_user.id, payment_data)
        
        callback_data = PaymentCallback(
            authority=initiated.authority,
            status="OK",
            ref_id="REF123456",
        )
        await service.handle_callback(callback_data)
        
        # Get summary
        result = await service.get_payment_summary(test_order.id)
        
        assert result is not None
        assert result.total_paid == test_order.print_price
        assert len(result.payments) == 1

