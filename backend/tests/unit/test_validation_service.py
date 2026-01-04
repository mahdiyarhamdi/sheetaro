"""Unit tests for ValidationService."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from app.services.validation_service import ValidationService
from app.schemas.validation import ValidationRequestCreate, ValidationReportCreate
from app.models.enums import OrderStatus, DesignPlan, ValidationStatus, UserRole
from tests.conftest import create_test_user, create_test_product


class TestValidationService:
    """Test cases for ValidationService."""
    
    @pytest_asyncio.fixture
    async def service(self, db_session):
        """Create ValidationService instance."""
        return ValidationService(db_session)
    
    @pytest_asyncio.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        return await create_test_user(db_session)
    
    @pytest_asyncio.fixture
    async def test_validator(self, db_session):
        """Create a test validator user."""
        return await create_test_user(db_session, {
            "telegram_id": 777777777,
            "first_name": "Validator",
            "role": UserRole.VALIDATOR,
        })
    
    @pytest_asyncio.fixture
    async def test_product(self, db_session):
        """Create a test product."""
        return await create_test_product(db_session)
    
    @pytest_asyncio.fixture
    async def pending_order(self, db_session, test_user, test_product):
        """Create a pending order for validation tests."""
        from app.models.order import Order
        
        order = Order(
            user_id=test_user.id,
            product_id=test_product.id,
            design_plan=DesignPlan.OWN_DESIGN,
            status=OrderStatus.PENDING,
            quantity=100,
            total_price=Decimal("100000"),
            design_price=Decimal("0"),
            validation_price=Decimal("50000"),
            fix_price=Decimal("0"),
            print_price=Decimal("50000"),
            validation_requested=False,
            design_file_url="/files/test/design.pdf",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)
        return order
    
    @pytest_asyncio.fixture
    async def awaiting_validation_order(self, db_session, test_user, test_product):
        """Create an order awaiting validation."""
        from app.models.order import Order
        
        order = Order(
            user_id=test_user.id,
            product_id=test_product.id,
            design_plan=DesignPlan.OWN_DESIGN,
            status=OrderStatus.AWAITING_VALIDATION,
            quantity=100,
            total_price=Decimal("100000"),
            design_price=Decimal("0"),
            validation_price=Decimal("50000"),
            fix_price=Decimal("0"),
            print_price=Decimal("50000"),
            validation_requested=True,
            validation_status=ValidationStatus.PENDING,
            design_file_url="/files/test/design.pdf",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)
        return order
    
    @pytest.mark.asyncio
    async def test_request_validation(self, service, test_user, pending_order):
        """Test requesting validation for an order."""
        request_data = ValidationRequestCreate(order_id=pending_order.id)
        
        result = await service.request_validation(test_user.id, request_data)
        
        assert result is not None
        assert "message" in result
        assert str(pending_order.id) in result["order_id"]
    
    @pytest.mark.asyncio
    async def test_request_validation_wrong_user_fails(self, service, db_session, pending_order):
        """Test that requesting validation for another user's order fails."""
        other_user = await create_test_user(db_session, {
            "telegram_id": 888888888,
            "first_name": "Other",
        })
        
        request_data = ValidationRequestCreate(order_id=pending_order.id)
        
        with pytest.raises(ValueError, match="Access denied"):
            await service.request_validation(other_user.id, request_data)
    
    @pytest.mark.asyncio
    async def test_request_validation_already_requested_fails(self, service, test_user, awaiting_validation_order):
        """Test that requesting validation twice fails."""
        request_data = ValidationRequestCreate(order_id=awaiting_validation_order.id)
        
        with pytest.raises(ValueError, match="Validation already requested"):
            await service.request_validation(test_user.id, request_data)
    
    @pytest.mark.asyncio
    async def test_submit_report_passed(self, service, test_validator, awaiting_validation_order):
        """Test submitting a passing validation report."""
        report_data = ValidationReportCreate(
            order_id=awaiting_validation_order.id,
            issues=[],
            fix_cost=0,
            summary="Design looks good",
            passed="PASSED",
        )
        
        result = await service.submit_report(test_validator.id, report_data)
        
        assert result is not None
        assert result.passed == "PASSED"
        assert len(result.issues) == 0
    
    @pytest.mark.asyncio
    async def test_submit_report_failed(self, service, test_validator, awaiting_validation_order):
        """Test submitting a failing validation report with issues."""
        report_data = ValidationReportCreate(
            order_id=awaiting_validation_order.id,
            issues=[
                {
                    "type": "resolution",
                    "severity": "high",
                    "description": "Resolution too low",
                    "suggestion": "Increase to 300 DPI",
                }
            ],
            fix_cost=150000,
            summary="File needs resolution fix",
            passed="FAILED",
        )
        
        result = await service.submit_report(test_validator.id, report_data)
        
        assert result is not None
        assert result.passed == "FAILED"
        assert len(result.issues) == 1
        assert result.fix_cost == Decimal("150000")
    
    @pytest.mark.asyncio
    async def test_submit_report_non_validator_fails(self, service, test_user, awaiting_validation_order):
        """Test that non-validator cannot submit report."""
        report_data = ValidationReportCreate(
            order_id=awaiting_validation_order.id,
            issues=[],
            fix_cost=0,
            summary="Test",
            passed="PASSED",
        )
        
        with pytest.raises(ValueError, match="User is not a validator"):
            await service.submit_report(test_user.id, report_data)
    
    @pytest.mark.asyncio
    async def test_submit_report_wrong_order_status_fails(self, service, test_validator, pending_order):
        """Test that report submission fails for orders not awaiting validation."""
        report_data = ValidationReportCreate(
            order_id=pending_order.id,
            issues=[],
            fix_cost=0,
            summary="Test",
            passed="PASSED",
        )
        
        with pytest.raises(ValueError, match="Order is not awaiting validation"):
            await service.submit_report(test_validator.id, report_data)
    
    @pytest.mark.asyncio
    async def test_get_report_by_id(self, service, test_validator, awaiting_validation_order):
        """Test getting validation report by ID."""
        report_data = ValidationReportCreate(
            order_id=awaiting_validation_order.id,
            issues=[],
            fix_cost=0,
            summary="Good",
            passed="PASSED",
        )
        created = await service.submit_report(test_validator.id, report_data)
        
        result = await service.get_report_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    @pytest.mark.asyncio
    async def test_get_order_reports(self, service, test_validator, awaiting_validation_order):
        """Test getting validation reports for an order."""
        # Submit a report
        report_data = ValidationReportCreate(
            order_id=awaiting_validation_order.id,
            issues=[],
            fix_cost=0,
            summary="Good",
            passed="PASSED",
        )
        await service.submit_report(test_validator.id, report_data)
        
        result = await service.get_order_reports(awaiting_validation_order.id)
        
        assert result.total >= 1
        assert len(result.items) >= 1

