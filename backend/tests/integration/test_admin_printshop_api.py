"""Integration tests for Admin Print Shop Management API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from decimal import Decimal
from datetime import date

from tests.conftest import (
    create_test_printshop_user,
    create_test_admin_user,
    create_test_web_user,
    create_test_category,
    create_test_order,
    create_admin_token,
)
from app.models.enums import OrderStatus, UserRole
from app.models.settlement import Settlement
from app.models.enums import SettlementStatus


# ==================== Admin Print Shop List Tests ====================


class TestAdminPrintShopList:
    """Tests for GET /api/v1/admin/printshops."""

    @pytest.mark.asyncio
    async def test_list_printshops_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I01: Admin can list all print shops."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))

        await create_test_printshop_user(db_session)

        response = await client.get(
            "/api/v1/admin/printshops",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_printshops_forbidden_for_customer(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I02: Regular user cannot list print shops."""
        customer = await create_test_web_user(db_session, {
            "phone_number": "09121111111",
            "password_hash": "x",
            "first_name": "Customer",
            "last_name": "One",
            "full_name": "Customer One",
            "role": UserRole.CUSTOMER,
        })
        token = create_admin_token(str(customer.id))

        response = await client.get(
            "/api/v1/admin/printshops",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


# ==================== Admin Print Shop Stats Tests ====================


class TestAdminPrintShopStats:
    """Tests for GET /api/v1/admin/printshops/{printshop_id}/stats."""

    @pytest.mark.asyncio
    async def test_get_printshop_stats_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I03: Admin can view print shop stats."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))
        ps_user = await create_test_printshop_user(db_session)

        response = await client.get(
            f"/api/v1/admin/printshops/{ps_user.id}/stats",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data


# ==================== Admin Print Shop Orders Tests ====================


class TestAdminPrintShopOrders:
    """Tests for GET /api/v1/admin/printshops/{printshop_id}/orders."""

    @pytest.mark.asyncio
    async def test_get_printshop_orders_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I04: Admin can view print shop order history."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))
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
            f"/api/v1/admin/printshops/{ps_user.id}/orders",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1


# ==================== Admin Reassign Order Tests ====================


class TestAdminReassignOrder:
    """Tests for POST /api/v1/admin/orders/{order_id}/reassign-printshop."""

    @pytest.mark.asyncio
    async def test_reassign_order_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I05: Admin can reassign order to another print shop."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))
        ps_user1 = await create_test_printshop_user(db_session)
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
            "assigned_printshop_id": ps_user1.id,
        })

        response = await client.post(
            f"/api/v1/admin/orders/{order.id}/reassign-printshop",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"new_printshop_id": str(ps_user2.id)},
        )
        assert response.status_code == 200


# ==================== Admin Settlements Tests ====================


class TestAdminSettlements:
    """Tests for GET /api/v1/admin/settlements."""

    @pytest.mark.asyncio
    async def test_get_settlements_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I06: Admin can list all settlements."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))

        response = await client.get(
            "/api/v1/admin/settlements",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_mark_settlement_paid_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I07: Admin can mark a settlement as paid."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))
        ps_user = await create_test_printshop_user(db_session)

        # Create a settlement directly
        settlement = Settlement(
            printshop_id=ps_user.id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            total_orders=10,
            total_revenue=Decimal("1000000"),
            platform_commission=Decimal("100000"),
            net_amount=Decimal("900000"),
            status=SettlementStatus.PENDING,
        )
        db_session.add(settlement)
        await db_session.flush()
        await db_session.refresh(settlement)

        response = await client.post(
            f"/api/v1/admin/settlements/{settlement.id}/pay",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200


# ==================== Admin SLA Report Tests ====================


class TestAdminSlaReport:
    """Tests for GET /api/v1/admin/printshop-sla."""

    @pytest.mark.asyncio
    async def test_get_sla_report_returns_200(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ADMIN-PS-I08: Admin can view SLA compliance report."""
        admin = await create_test_admin_user(db_session)
        admin_token = create_admin_token(str(admin.id))

        response = await client.get(
            "/api/v1/admin/printshop-sla",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
