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


class TestCardToCardPayment:
    """Test cases for card-to-card payment flow."""
    
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
    async def test_admin(self, db_session):
        """Create a test admin user."""
        from app.models.enums import UserRole
        return await create_test_user(db_session, {
            "telegram_id": 888888888,
            "first_name": "Admin",
            "role": UserRole.ADMIN,
        })
    
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
    
    @pytest_asyncio.fixture
    async def initiated_payment(self, service, test_user, test_order):
        """Create an initiated payment."""
        payment_data = PaymentInitiate(
            order_id=test_order.id,
            type=PaymentType.PRINT,
            callback_url="https://example.com/callback",
        )
        return await service.initiate_payment(test_user.id, payment_data)
    
    @pytest.mark.asyncio
    async def test_upload_receipt(self, service, test_user, initiated_payment):
        """Test uploading a receipt image."""
        result = await service.upload_receipt(
            payment_id=initiated_payment.payment_id,
            user_id=test_user.id,
            receipt_image_url="https://example.com/receipt.jpg",
        )
        
        assert result is not None
        assert result.status == PaymentStatus.AWAITING_APPROVAL
        assert result.receipt_image_url == "https://example.com/receipt.jpg"
    
    @pytest.mark.asyncio
    async def test_upload_receipt_wrong_user_fails(self, service, initiated_payment, db_session):
        """Test that wrong user cannot upload receipt."""
        other_user = await create_test_user(db_session, {
            "telegram_id": 777777777,
            "first_name": "Other",
        })
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.upload_receipt(
                payment_id=initiated_payment.payment_id,
                user_id=other_user.id,
                receipt_image_url="https://example.com/receipt.jpg",
            )
    
    @pytest.mark.asyncio
    async def test_approve_payment(self, service, test_user, test_admin, initiated_payment):
        """Test approving a payment."""
        # First upload receipt
        await service.upload_receipt(
            payment_id=initiated_payment.payment_id,
            user_id=test_user.id,
            receipt_image_url="https://example.com/receipt.jpg",
        )
        
        # Approve
        result = await service.approve_payment(
            payment_id=initiated_payment.payment_id,
            admin_id=test_admin.id,
        )
        
        assert result is not None
        assert result.status == PaymentStatus.SUCCESS
        assert result.approved_by == test_admin.id
        assert result.approved_at is not None
    
    @pytest.mark.asyncio
    async def test_approve_payment_non_admin_fails(self, service, test_user, initiated_payment):
        """Test that non-admin cannot approve payment."""
        await service.upload_receipt(
            payment_id=initiated_payment.payment_id,
            user_id=test_user.id,
            receipt_image_url="https://example.com/receipt.jpg",
        )
        
        with pytest.raises(ValueError, match="Admin access required"):
            await service.approve_payment(
                payment_id=initiated_payment.payment_id,
                admin_id=test_user.id,
            )
    
    @pytest.mark.asyncio
    async def test_reject_payment(self, service, test_user, test_admin, initiated_payment):
        """Test rejecting a payment."""
        # First upload receipt
        await service.upload_receipt(
            payment_id=initiated_payment.payment_id,
            user_id=test_user.id,
            receipt_image_url="https://example.com/receipt.jpg",
        )
        
        # Reject
        result = await service.reject_payment(
            payment_id=initiated_payment.payment_id,
            admin_id=test_admin.id,
            reason="رسید نامعتبر است",
        )
        
        assert result is not None
        assert result.status == PaymentStatus.FAILED
        assert result.rejection_reason == "رسید نامعتبر است"
        assert result.approved_by == test_admin.id
    
    @pytest.mark.asyncio
    async def test_get_pending_approval_payments(self, service, test_user, test_admin, initiated_payment):
        """Test getting pending approval payments."""
        # Upload receipt
        await service.upload_receipt(
            payment_id=initiated_payment.payment_id,
            user_id=test_user.id,
            receipt_image_url="https://example.com/receipt.jpg",
        )
        
        # Get pending
        result = await service.get_pending_approval_payments(
            admin_id=test_admin.id,
        )
        
        assert result is not None
        assert result.total >= 1

