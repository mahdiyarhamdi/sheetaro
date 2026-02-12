"""Unit tests for Print Shop service methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.order_service import OrderService
from app.models.enums import OrderStatus, UserRole, DesignPlan, ValidationStatus


# ==================== Helpers ====================


def make_mock_user(role=UserRole.PRINT_SHOP, **kwargs):
    """Create a mock user object with real values for Pydantic."""
    defaults = {
        "id": uuid4(),
        "role": role,
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "09121234567",
        "city": "Tehran",
        "address": "Tehran, Main St",
        "username": "testuser",
        "is_active": True,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_mock_category(**kwargs):
    """Create a mock category object."""
    defaults = {
        "id": uuid4(),
        "slug": "label",
        "name_fa": "لیبل",
        "description_fa": "لیبل‌های مختلف",
        "icon": "🏷️",
        "base_price": Decimal("5000"),
        "sort_order": 0,
        "is_active": True,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


_SENTINEL = object()


def make_mock_order(user=None, printshop_user=None, status=OrderStatus.PRINTING, category=_SENTINEL, **kwargs):
    """Create a mock order object with real values compatible with Pydantic model_validate."""
    if user is None:
        user = make_mock_user(role=UserRole.CUSTOMER)
    if category is _SENTINEL:
        category = make_mock_category()
    defaults = {
        "id": uuid4(),
        "user_id": user.id,
        "category_id": category.id,
        "product_id": None,
        "selected_attributes": [],
        "design_plan": DesignPlan.PUBLIC,
        "status": status,
        "quantity": 100,
        "design_file_url": None,
        "validation_status": None,
        "validation_requested": False,
        "assigned_designer_id": None,
        "assigned_validator_id": None,
        "assigned_printshop_id": printshop_user.id if printshop_user else None,
        "revision_count": 0,
        "max_revisions": 3,
        "base_price": Decimal("50000"),
        "attributes_price": Decimal("0"),
        "design_price": Decimal("0"),
        "validation_price": Decimal("0"),
        "fix_price": Decimal("0"),
        "print_price": Decimal("50000"),
        "total_price": Decimal("50000"),
        "tracking_code": None,
        "shipping_address": "Tehran, Valiasr Street",
        "customer_notes": "Test notes",
        "admin_notes": "Admin internal note",
        "accepted_at": None,
        "printed_at": None,
        "shipped_at": None,
        "delivered_at": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "user": user,
        "category": category,
        "cancelled_at": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ==================== Fixtures ====================


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def order_service(mock_db_session):
    """Create an OrderService with mocked dependencies."""
    service = OrderService(mock_db_session)
    service.repository = AsyncMock()
    service.user_repo = AsyncMock()
    return service


@pytest.fixture
def ps_user():
    """Create a print shop user."""
    return make_mock_user(role=UserRole.PRINT_SHOP, first_name="PrintShop", last_name="Owner")


@pytest.fixture
def customer():
    """Create a customer user."""
    return make_mock_user(role=UserRole.CUSTOMER, first_name="Customer", last_name="One")


# ==================== Accept Order Tests ====================


class TestAcceptOrderByPrintshop:
    """Tests for OrderService.accept_order_by_printshop."""

    @pytest.mark.asyncio
    async def test_accept_order_success(self, order_service, ps_user, customer):
        """PS-U01: Print shop can accept an order."""
        order = make_mock_order(user=customer, status=OrderStatus.READY_FOR_PRINT)
        order_service.user_repo.get_by_id.return_value = ps_user
        order_service.repository.accept_by_printshop.return_value = order

        result = await order_service.accept_order_by_printshop(
            order_id=order.id, printshop_id=ps_user.id,
        )

        assert result is not None
        order_service.repository.accept_by_printshop.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_order_non_printshop_user_raises(self, order_service, customer):
        """PS-U02: Non-print-shop user cannot accept orders."""
        order_service.user_repo.get_by_id.return_value = customer

        with pytest.raises(ValueError, match="not a print shop"):
            await order_service.accept_order_by_printshop(
                order_id=uuid4(), printshop_id=customer.id,
            )

    @pytest.mark.asyncio
    async def test_accept_order_user_not_found_raises(self, order_service):
        """PS-U03: Non-existent user cannot accept orders."""
        order_service.user_repo.get_by_id.return_value = None

        with pytest.raises(ValueError):
            await order_service.accept_order_by_printshop(
                order_id=uuid4(), printshop_id=uuid4(),
            )


# ==================== Complete Printing Tests ====================


class TestCompletePrinting:
    """Tests for OrderService.complete_printing."""

    @pytest.mark.asyncio
    async def test_complete_printing_success(self, order_service, ps_user, customer):
        """PS-U04: Print shop can mark PRINTING order as PRINTED."""
        order = make_mock_order(user=customer, printshop_user=ps_user, status=OrderStatus.PRINTING)
        order_service.repository.get_by_id.return_value = order
        order_service.repository.complete_printing.return_value = order

        result = await order_service.complete_printing(
            order_id=order.id, printshop_id=ps_user.id,
        )

        assert result is not None
        order_service.repository.complete_printing.assert_called_once_with(order.id)

    @pytest.mark.asyncio
    async def test_complete_wrong_status_raises(self, order_service, ps_user, customer):
        """PS-U05: Cannot complete order that is not PRINTING."""
        order = make_mock_order(user=customer, printshop_user=ps_user, status=OrderStatus.SHIPPED)
        order_service.repository.get_by_id.return_value = order

        with pytest.raises(ValueError, match="Cannot complete printing"):
            await order_service.complete_printing(
                order_id=order.id, printshop_id=ps_user.id,
            )

    @pytest.mark.asyncio
    async def test_complete_wrong_printshop_raises(self, order_service, customer):
        """PS-U06: Cannot complete order assigned to another print shop."""
        other_ps = make_mock_user(role=UserRole.PRINT_SHOP)
        order = make_mock_order(user=customer, printshop_user=other_ps, status=OrderStatus.PRINTING)
        order_service.repository.get_by_id.return_value = order

        with pytest.raises(ValueError, match="not assigned"):
            await order_service.complete_printing(
                order_id=order.id, printshop_id=uuid4(),
            )

    @pytest.mark.asyncio
    async def test_complete_nonexistent_order_returns_none(self, order_service, ps_user):
        """PS-U07: Returns None for non-existent order."""
        order_service.repository.get_by_id.return_value = None
        result = await order_service.complete_printing(order_id=uuid4(), printshop_id=ps_user.id)
        assert result is None


# ==================== Ship Order Tests ====================


class TestShipOrder:
    """Tests for OrderService.ship_order."""

    @pytest.mark.asyncio
    async def test_ship_order_success(self, order_service, ps_user, customer):
        """PS-U08: Print shop can ship a PRINTED order."""
        order = make_mock_order(user=customer, printshop_user=ps_user, status=OrderStatus.PRINTED)
        order_service.repository.get_by_id.return_value = order
        order_service.repository.ship_order.return_value = order

        result = await order_service.ship_order(
            order_id=order.id, printshop_id=ps_user.id, tracking_code="POST-12345",
        )

        assert result is not None
        order_service.repository.ship_order.assert_called_once_with(order.id, "POST-12345")

    @pytest.mark.asyncio
    async def test_ship_wrong_status_raises(self, order_service, ps_user, customer):
        """PS-U09: Cannot ship order that is not PRINTED."""
        order = make_mock_order(user=customer, printshop_user=ps_user, status=OrderStatus.PRINTING)
        order_service.repository.get_by_id.return_value = order

        with pytest.raises(ValueError, match="Cannot ship"):
            await order_service.ship_order(
                order_id=order.id, printshop_id=ps_user.id, tracking_code="POST-12345",
            )

    @pytest.mark.asyncio
    async def test_ship_wrong_printshop_raises(self, order_service, customer):
        """PS-U10: Cannot ship order assigned to another print shop."""
        other_ps = make_mock_user(role=UserRole.PRINT_SHOP)
        order = make_mock_order(user=customer, printshop_user=other_ps, status=OrderStatus.PRINTED)
        order_service.repository.get_by_id.return_value = order

        with pytest.raises(ValueError, match="not assigned"):
            await order_service.ship_order(
                order_id=order.id, printshop_id=uuid4(), tracking_code="POST-12345",
            )

    @pytest.mark.asyncio
    async def test_ship_nonexistent_order_returns_none(self, order_service, ps_user):
        """PS-U11: Returns None for non-existent order."""
        order_service.repository.get_by_id.return_value = None
        result = await order_service.ship_order(
            order_id=uuid4(), printshop_id=ps_user.id, tracking_code="POST-12345",
        )
        assert result is None


# ==================== Get Print Shop Order Detail Tests ====================


class TestGetPrintshopOrderDetail:
    """Tests for OrderService.get_printshop_order_detail."""

    @pytest.mark.asyncio
    async def test_get_detail_success(self, order_service, ps_user, customer):
        """PS-U12: Print shop can get detail of its assigned order."""
        order = make_mock_order(user=customer, printshop_user=ps_user)
        order_service.repository.get_by_id.return_value = order
        # Mock db.execute for enrichment queries (ProcessedDesign, Payment)
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )

        result = await order_service.get_printshop_order_detail(
            order_id=order.id, printshop_id=ps_user.id,
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_detail_wrong_printshop_returns_none(self, order_service, ps_user, customer):
        """PS-U13: Returns None for order assigned to another print shop."""
        order = make_mock_order(user=customer, printshop_user=ps_user)
        order_service.repository.get_by_id.return_value = order

        result = await order_service.get_printshop_order_detail(
            order_id=order.id, printshop_id=uuid4(),
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_detail_nonexistent_returns_none(self, order_service, ps_user):
        """PS-U14: Returns None for non-existent order."""
        order_service.repository.get_by_id.return_value = None
        result = await order_service.get_printshop_order_detail(
            order_id=uuid4(), printshop_id=ps_user.id,
        )
        assert result is None


# ==================== Get Print Shop Stats Tests ====================


class TestGetPrintshopStats:
    """Tests for OrderService.get_printshop_stats."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self, order_service, ps_user):
        """PS-U15: Print shop can get its statistics."""
        order_service.repository.get_printshop_stats.return_value = {
            "total_orders": 10,
            "pending_orders": 5,
            "in_progress_orders": 2,
            "printed_orders": 3,
            "shipped_orders": 4,
            "delivered_orders": 1,
            "avg_print_time_hours": 4.5,
            "avg_ship_time_hours": 12.0,
            "sla_compliance_percent": 95.0,
        }

        result = await order_service.get_printshop_stats(ps_user.id)

        assert result.total_orders == 10
        assert result.in_progress_orders == 2
        assert result.avg_print_time_hours == 4.5

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, order_service, ps_user):
        """PS-U16: New print shop gets zero stats."""
        order_service.repository.get_printshop_stats.return_value = {
            "total_orders": 0,
            "pending_orders": 0,
            "in_progress_orders": 0,
            "printed_orders": 0,
            "shipped_orders": 0,
            "delivered_orders": 0,
            "avg_print_time_hours": None,
            "avg_ship_time_hours": None,
            "sla_compliance_percent": None,
        }

        result = await order_service.get_printshop_stats(ps_user.id)
        assert result.total_orders == 0
        assert result.avg_print_time_hours is None


# ==================== Get Print Shop Queue Tests ====================


class TestGetPrintshopQueue:
    """Tests for OrderService.get_printshop_queue."""

    @pytest.mark.asyncio
    async def test_get_queue_success(self, order_service, customer):
        """PS-U17: Queue returns paginated response."""
        order = make_mock_order(user=customer, status=OrderStatus.READY_FOR_PRINT)
        order_service.repository.get_ready_for_print.return_value = ([order], 1)
        # Mock db.execute for enrichment queries (ProcessedDesign, Payment)
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )

        result = await order_service.get_printshop_queue(page=1, page_size=20)

        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_get_queue_empty(self, order_service):
        """PS-U18: Empty queue returns empty list."""
        order_service.repository.get_ready_for_print.return_value = ([], 0)

        result = await order_service.get_printshop_queue(page=1, page_size=20)
        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_get_queue_caps_page_size(self, order_service):
        """PS-U19: Queue caps page_size to 100."""
        order_service.repository.get_ready_for_print.return_value = ([], 0)

        await order_service.get_printshop_queue(page=1, page_size=200)

        order_service.repository.get_ready_for_print.assert_called_once_with(
            page=1, page_size=100
        )


# ==================== Enriched PrintShopOrderOut Tests ====================


def _mock_scalar_one_or_none(value):
    """Create a mock execute result that returns value from scalar_one_or_none()."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = value
    return mock_result


class TestPrintShopOrderOutEnrichment:
    """Tests verifying _to_printshop_order_out populates enriched fields."""

    @pytest.mark.asyncio
    async def test_category_fields_populated(self, order_service, ps_user, customer):
        """PS-U20: category_name and category_icon come from order.category relation."""
        cat = make_mock_category(name_fa="فاکتور", icon="📄")
        order = make_mock_order(user=customer, printshop_user=ps_user, category=cat)

        # Mock db.execute calls for ProcessedDesign, DesignTemplate, Payment
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )

        result = await order_service._to_printshop_order_out(order)

        assert result.category_name == "فاکتور"
        assert result.category_icon == "📄"

    @pytest.mark.asyncio
    async def test_design_plan_label_populated(self, order_service, ps_user, customer):
        """PS-U21: design_plan_label is mapped from DesignPlan enum."""
        for plan, expected_label in [
            (DesignPlan.PUBLIC, "قالب آماده"),
            (DesignPlan.SEMI_PRIVATE, "نیمه اختصاصی"),
            (DesignPlan.PRIVATE, "اختصاصی"),
            (DesignPlan.OWN_DESIGN, "طرح مشتری"),
        ]:
            order = make_mock_order(
                user=customer, printshop_user=ps_user, design_plan=plan,
            )
            order_service.db.execute = AsyncMock(
                side_effect=[
                    _mock_scalar_one_or_none(None),  # ProcessedDesign
                    _mock_scalar_one_or_none(None),  # Payment
                ]
            )
            result = await order_service._to_printshop_order_out(order)
            assert result.design_plan_label == expected_label

    @pytest.mark.asyncio
    async def test_admin_notes_populated(self, order_service, ps_user, customer):
        """PS-U22: admin_notes is copied from the order model."""
        order = make_mock_order(
            user=customer, printshop_user=ps_user, admin_notes="Rush order",
        )
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.admin_notes == "Rush order"

    @pytest.mark.asyncio
    async def test_payment_status_populated(self, order_service, ps_user, customer):
        """PS-U23: payment_status is fetched from Payment table."""
        order = make_mock_order(user=customer, printshop_user=ps_user)
        mock_payment = SimpleNamespace(
            status=SimpleNamespace(value="SUCCESS"),
            paid_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            approved_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        )
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(mock_payment),  # Payment
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.payment_status == "SUCCESS"
        assert result.payment_paid_at is not None

    @pytest.mark.asyncio
    async def test_template_name_populated(self, order_service, ps_user, customer):
        """PS-U24: template_name fetched from DesignTemplate via ProcessedDesign."""
        order = make_mock_order(user=customer, printshop_user=ps_user)
        mock_processed = SimpleNamespace(
            preview_url="/files/preview.png",
            final_url="/files/final.png",
            template_id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(mock_processed),  # ProcessedDesign
                _mock_scalar_one_or_none("قالب شماره ۱"),  # DesignTemplate name_fa
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.template_name == "قالب شماره ۱"
        assert result.design_preview_url == "/files/preview.png"
        assert result.design_final_url == "/files/final.png"

    @pytest.mark.asyncio
    async def test_customer_info_populated(self, order_service, ps_user):
        """PS-U25: customer info comes from order.user relation."""
        cust = make_mock_user(
            role=UserRole.CUSTOMER, first_name="احمد", last_name="رضایی",
            phone_number="09121234567", city="تهران", address="ولیعصر",
        )
        order = make_mock_order(user=cust, printshop_user=ps_user)
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),
                _mock_scalar_one_or_none(None),
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.customer_name == "احمد رضایی"
        assert result.customer_phone == "09121234567"
        assert result.customer_city == "تهران"

    @pytest.mark.asyncio
    async def test_no_category_returns_none(self, order_service, ps_user, customer):
        """PS-U26: If category relation is None, category fields stay None."""
        order = make_mock_order(user=customer, printshop_user=ps_user)
        # Override the category relation to None (simulates missing join)
        order.category = None
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),
                _mock_scalar_one_or_none(None),
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.category_name is None
        assert result.category_icon is None

    @pytest.mark.asyncio
    async def test_enriched_attributes_populated(self, order_service, ps_user, customer):
        """PS-U27: enriched_attributes resolves IDs to human-readable names."""
        attr_id = str(uuid4())
        opt_id = str(uuid4())
        order = make_mock_order(
            user=customer,
            printshop_user=ps_user,
            selected_attributes=[
                {"attribute_id": attr_id, "option_id": opt_id, "value": None, "price_modifier": 5000},
            ],
        )
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none("اندازه"),    # CategoryAttribute.name_fa
                _mock_scalar_one_or_none("A4"),        # AttributeOption.label_fa
                _mock_scalar_one_or_none(None),        # ProcessedDesign
                _mock_scalar_one_or_none(None),        # Payment
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert len(result.enriched_attributes) == 1
        assert result.enriched_attributes[0].attribute_name == "اندازه"
        assert result.enriched_attributes[0].value_name == "A4"
        assert result.enriched_attributes[0].price == 5000

    @pytest.mark.asyncio
    async def test_enriched_attributes_empty_when_no_attrs(self, order_service, ps_user, customer):
        """PS-U28: enriched_attributes is empty when order has no selected_attributes."""
        order = make_mock_order(user=customer, printshop_user=ps_user, selected_attributes=[])
        order_service.db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_one_or_none(None),  # ProcessedDesign
                _mock_scalar_one_or_none(None),  # Payment
            ]
        )
        result = await order_service._to_printshop_order_out(order)
        assert result.enriched_attributes == []
