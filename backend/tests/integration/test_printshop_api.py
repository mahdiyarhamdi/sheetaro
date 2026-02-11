"""Integration tests for Print Shop API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from tests.conftest import (
    create_test_printshop_user,
    create_test_web_user,
    create_test_category,
    create_test_order,
    create_admin_token,
)
from app.models.enums import OrderStatus, UserRole


# ==================== Print Shop Queue Tests ====================


class TestPrintShopQueue:
    """Tests for GET /api/v1/printshop/orders (print shop queue)."""

    @pytest.mark.asyncio
    async def test_get_queue_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I01: Print shop can view queue of READY_FOR_PRINT orders."""
        ps_user = await create_test_printshop_user(db_session)
        response = await client.get(
            "/api/v1/printshop/orders",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_queue_only_shows_ready_for_print(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I02: Queue only contains orders with READY_FOR_PRINT status."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)

        # Create orders with different statuses
        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.READY_FOR_PRINT,
        })
        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })
        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PENDING,
        })

        response = await client.get(
            "/api/v1/printshop/orders",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(
            item["status"] == "READY_FOR_PRINT" for item in data["items"]
        )

    @pytest.mark.asyncio
    async def test_queue_forbidden_for_customer(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I03: Regular customer cannot access print shop queue."""
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        response = await client.get(
            "/api/v1/printshop/orders",
            params={"printshop_id": str(customer.id)},
        )
        assert response.status_code == 403


# ==================== Accept Order Tests ====================


class TestAcceptOrder:
    """Tests for POST /api/v1/printshop/accept/{order_id}."""

    @pytest.mark.asyncio
    async def test_accept_order_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I04: Print shop can accept a READY_FOR_PRINT order."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.READY_FOR_PRINT,
        })

        response = await client.post(
            f"/api/v1/printshop/accept/{order.id}",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PRINTING"

    @pytest.mark.asyncio
    async def test_accept_non_ready_order_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I05: Cannot accept order that is not READY_FOR_PRINT."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.post(
            f"/api/v1/printshop/accept/{order.id}",
            params={"printshop_id": str(ps_user.id)},
        )
        # Should be 400 or 404 depending on implementation
        assert response.status_code in [400, 404]


# ==================== My Orders Tests ====================


class TestMyOrders:
    """Tests for GET /api/v1/printshop/my-orders."""

    @pytest.mark.asyncio
    async def test_get_my_orders_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I06: Print shop can view its assigned orders."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)

        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.get(
            "/api/v1/printshop/my-orders",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_my_orders_filter_by_status(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I07: Print shop can filter its orders by status."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)

        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })
        await create_test_order(db_session, customer, category, {
            "status": OrderStatus.SHIPPED,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.get(
            "/api/v1/printshop/my-orders",
            params={
                "printshop_id": str(ps_user.id),
                "status": "PRINTING",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert all(
            item["status"] == "PRINTING" for item in data["items"]
        )


# ==================== Complete Printing Tests ====================


class TestCompletePrinting:
    """Tests for POST /api/v1/printshop/orders/{order_id}/complete."""

    @pytest.mark.asyncio
    async def test_complete_printing_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I08: Print shop can mark a PRINTING order as PRINTED."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.post(
            f"/api/v1/printshop/orders/{order.id}/complete",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PRINTED"

    @pytest.mark.asyncio
    async def test_complete_non_printing_order_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I09: Cannot complete order that is not in PRINTING status."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.SHIPPED,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.post(
            f"/api/v1/printshop/orders/{order.id}/complete",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_complete_other_shops_order_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I10: Cannot complete order assigned to another print shop."""
        ps_user = await create_test_printshop_user(db_session)
        ps_user2 = await create_test_printshop_user(db_session, {
            "phone_number": "09128888888",
            "password_hash": "x",
            "first_name": "Other",
            "last_name": "PrintShop",
            "full_name": "Other PrintShop",
            "role": UserRole.PRINT_SHOP,
        })
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user2.id,
        })

        response = await client.post(
            f"/api/v1/printshop/orders/{order.id}/complete",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 400


# ==================== Ship Order Tests ====================


class TestShipOrder:
    """Tests for POST /api/v1/printshop/orders/{order_id}/ship."""

    @pytest.mark.asyncio
    async def test_ship_order_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I11: Print shop can ship a PRINTED order."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTED,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.post(
            f"/api/v1/printshop/orders/{order.id}/ship",
            params={"printshop_id": str(ps_user.id)},
            json={"tracking_code": "POST-12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SHIPPED"

    @pytest.mark.asyncio
    async def test_ship_non_printed_order_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I12: Cannot ship order that is not in PRINTED status."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.post(
            f"/api/v1/printshop/orders/{order.id}/ship",
            params={"printshop_id": str(ps_user.id)},
            json={"tracking_code": "POST-12345"},
        )
        assert response.status_code == 400


# ==================== Stats Tests ====================


class TestPrintShopStats:
    """Tests for GET /api/v1/printshop/stats."""

    @pytest.mark.asyncio
    async def test_get_stats_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I13: Print shop can view its stats."""
        ps_user = await create_test_printshop_user(db_session)
        response = await client.get(
            "/api/v1/printshop/stats",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data


# ==================== Settlements Tests ====================


class TestPrintShopSettlements:
    """Tests for GET /api/v1/printshop/settlements."""

    @pytest.mark.asyncio
    async def test_get_settlements_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I14: Print shop can view its settlements."""
        ps_user = await create_test_printshop_user(db_session)
        response = await client.get(
            "/api/v1/printshop/settlements",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_settlements_empty_for_new_printshop(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I15: New print shop has no settlements."""
        ps_user = await create_test_printshop_user(db_session)
        response = await client.get(
            "/api/v1/printshop/settlements",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


# ==================== Order Detail Tests ====================


class TestOrderDetail:
    """Tests for GET /api/v1/printshop/my-orders/{order_id}."""

    @pytest.mark.asyncio
    async def test_get_order_detail_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I16: Print shop can view detail of its assigned order."""
        ps_user = await create_test_printshop_user(db_session)
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user.id,
        })

        response = await client.get(
            f"/api/v1/printshop/my-orders/{order.id}",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_other_shops_order_returns_404(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I17: Cannot view detail of order assigned to another print shop."""
        ps_user = await create_test_printshop_user(db_session)
        ps_user2 = await create_test_printshop_user(db_session, {
            "phone_number": "09128888888",
            "password_hash": "x",
            "first_name": "Other",
            "last_name": "PrintShop",
            "full_name": "Other PrintShop",
            "role": UserRole.PRINT_SHOP,
        })
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        category = await create_test_category(db_session)
        order = await create_test_order(db_session, customer, category, {
            "status": OrderStatus.PRINTING,
            "assigned_printshop_id": ps_user2.id,
        })

        response = await client.get(
            f"/api/v1/printshop/my-orders/{order.id}",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_order_returns_404(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """PS-I18: Returns 404 for non-existent order."""
        ps_user = await create_test_printshop_user(db_session)
        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/printshop/my-orders/{fake_id}",
            params={"printshop_id": str(ps_user.id)},
        )
        assert response.status_code == 404
