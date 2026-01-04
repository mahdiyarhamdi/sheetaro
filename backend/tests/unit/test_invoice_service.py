"""Unit tests for InvoiceService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal
from datetime import date

from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceSearchParams
from app.models.enums import OrderStatus, DesignPlan
from tests.conftest import create_test_user, create_test_product


class TestInvoiceService:
    """Test cases for InvoiceService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create InvoiceService instance."""
        return InvoiceService(db_session)
    
    @pytest_asyncio.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        return await create_test_user(db_session)
    
    @pytest_asyncio.fixture
    async def test_product(self, db_session):
        """Create a test product."""
        return await create_test_product(db_session)
    
    @pytest_asyncio.fixture
    async def delivered_order(self, db_session, test_user, test_product):
        """Create a delivered order for invoice tests."""
        from app.models.order import Order
        from app.models.enums import OrderStatus, DesignPlan
        
        order = Order(
            user_id=test_user.id,
            product_id=test_product.id,
            design_plan=DesignPlan.PUBLIC,
            status=OrderStatus.DELIVERED,
            quantity=100,
            total_price=Decimal("100000"),
            design_price=Decimal("0"),
            validation_price=Decimal("0"),
            fix_price=Decimal("0"),
            print_price=Decimal("100000"),
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)
        return order
    
    @pytest.fixture
    def sample_invoice_data(self, delivered_order):
        """Sample invoice data for testing."""
        return {
            "order_id": str(delivered_order.id),
            "customer_name": "Test Customer",
            "customer_code": "CUST001",
            "customer_address": "Test Address",
            "customer_phone": "09121234567",
            "items": [
                {
                    "description": "Test Item",
                    "quantity": 10,
                    "unit_price": 10000,
                    "total": 100000,
                }
            ],
            "tax_amount": 9000,
            "discount_amount": 0,
            "issue_date": date.today().isoformat(),
        }
    
    @pytest.mark.asyncio
    async def test_create_invoice(self, service, test_user, delivered_order, sample_invoice_data):
        """Test creating a new invoice."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        
        result = await service.create_invoice(test_user.id, invoice_create)
        
        assert result is not None
        assert result.order_id == delivered_order.id
        assert result.customer_name == "Test Customer"
        assert result.invoice_number is not None  # Auto-generated
        assert len(result.items) == 1
    
    @pytest.mark.asyncio
    async def test_create_invoice_wrong_user_fails(self, service, db_session, delivered_order, sample_invoice_data):
        """Test that creating invoice for another user's order fails."""
        other_user = await create_test_user(db_session, {
            "telegram_id": 999999999,
            "first_name": "Other",
        })
        
        invoice_create = InvoiceCreate(**sample_invoice_data)
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.create_invoice(other_user.id, invoice_create)
    
    @pytest.mark.asyncio
    async def test_create_invoice_non_delivered_fails(self, service, db_session, test_user, test_product):
        """Test that invoice creation fails for non-delivered orders."""
        from app.models.order import Order
        
        order = Order(
            user_id=test_user.id,
            product_id=test_product.id,
            design_plan=DesignPlan.PUBLIC,
            status=OrderStatus.PENDING,  # Not delivered
            quantity=100,
            total_price=Decimal("100000"),
            design_price=Decimal("0"),
            validation_price=Decimal("0"),
            fix_price=Decimal("0"),
            print_price=Decimal("100000"),
        )
        db_session.add(order)
        await db_session.flush()
        
        invoice_data = {
            "order_id": str(order.id),
            "customer_name": "Test",
            "items": [{"description": "Item", "quantity": 1, "unit_price": 1000, "total": 1000}],
            "issue_date": date.today().isoformat(),
        }
        invoice_create = InvoiceCreate(**invoice_data)
        
        with pytest.raises(ValueError, match="Invoice can only be created for delivered orders"):
            await service.create_invoice(test_user.id, invoice_create)
    
    @pytest.mark.asyncio
    async def test_get_invoice_by_id(self, service, test_user, delivered_order, sample_invoice_data):
        """Test getting invoice by ID."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        created = await service.create_invoice(test_user.id, invoice_create)
        
        result = await service.get_invoice_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    @pytest.mark.asyncio
    async def test_get_invoice_by_number(self, service, test_user, delivered_order, sample_invoice_data):
        """Test getting invoice by invoice number."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        created = await service.create_invoice(test_user.id, invoice_create)
        
        result = await service.get_invoice_by_number(created.invoice_number)
        
        assert result is not None
        assert result.invoice_number == created.invoice_number
    
    @pytest.mark.asyncio
    async def test_get_user_invoices(self, service, test_user, delivered_order, sample_invoice_data):
        """Test getting invoices for a user."""
        # Create multiple invoices
        for i in range(3):
            invoice_data = sample_invoice_data.copy()
            invoice_data["customer_name"] = f"Customer {i}"
            invoice_create = InvoiceCreate(**invoice_data)
            await service.create_invoice(test_user.id, invoice_create)
        
        result = await service.get_user_invoices(test_user.id)
        
        assert result.total == 3
        assert len(result.items) == 3
    
    @pytest.mark.asyncio
    async def test_search_invoices_requires_subscription(self, service, test_user):
        """Test that search without subscription raises error."""
        search_params = InvoiceSearchParams(customer_name="Test")
        
        with pytest.raises(ValueError, match="Advanced search requires subscription"):
            await service.search_invoices(test_user.id, search_params, has_subscription=False)
    
    @pytest.mark.asyncio
    async def test_update_invoice(self, service, test_user, delivered_order, sample_invoice_data):
        """Test updating an invoice."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        created = await service.create_invoice(test_user.id, invoice_create)
        
        update_data = InvoiceUpdate(customer_name="Updated Customer")
        result = await service.update_invoice(created.id, update_data, test_user.id)
        
        assert result is not None
        assert result.customer_name == "Updated Customer"
    
    @pytest.mark.asyncio
    async def test_update_invoice_wrong_user_fails(self, service, db_session, test_user, delivered_order, sample_invoice_data):
        """Test that updating another user's invoice fails."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        created = await service.create_invoice(test_user.id, invoice_create)
        
        other_user = await create_test_user(db_session, {
            "telegram_id": 888888888,
            "first_name": "Other",
        })
        
        update_data = InvoiceUpdate(customer_name="Hacker")
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.update_invoice(created.id, update_data, other_user.id)
    
    @pytest.mark.asyncio
    async def test_generate_pdf(self, service, test_user, delivered_order, sample_invoice_data):
        """Test PDF generation (placeholder test)."""
        invoice_create = InvoiceCreate(**sample_invoice_data)
        created = await service.create_invoice(test_user.id, invoice_create)
        
        result = await service.generate_pdf(created.id, test_user.id)
        
        assert result is not None
        assert result.endswith(".pdf")

