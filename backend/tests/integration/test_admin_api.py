"""Integration tests for Admin API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole, OrderStatus, PaymentStatus
from tests.conftest import (
    create_test_admin_user,
    create_test_web_user,
    create_test_product,
    create_test_order,
    create_test_payment,
    create_admin_token,
)


# ==================== Dashboard Stats Tests ====================

class TestAdminStats:
    """Integration tests for GET /api/v1/admin/stats endpoint."""
    
    @pytest.mark.asyncio
    async def test_admin_stats_returns_all_fields(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I01: GET /admin/stats returns all expected fields."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all fields are present
        expected_fields = [
            "total_orders",
            "pending_payments",
            "total_revenue",
            "new_users_today",
            "active_users",
            "orders_today",
            "orders_this_week",
            "pending_orders",
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
    
    @pytest.mark.asyncio
    async def test_admin_stats_requires_admin_role(
        self, client: AsyncClient, regular_user_headers
    ):
        """ADMIN-I02: GET /admin/stats with non-admin user returns 403."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=regular_user_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_stats_without_auth_returns_401(
        self, client: AsyncClient
    ):
        """ADMIN-I03: GET /admin/stats without auth returns 401."""
        response = await client.get("/api/v1/admin/stats")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_admin_stats_with_invalid_token_returns_401(
        self, client: AsyncClient
    ):
        """ADMIN-I04: GET /admin/stats with invalid token returns 401."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


# ==================== Users Management Tests ====================

class TestAdminUsersList:
    """Integration tests for GET /api/v1/admin/users endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_users_returns_paginated_results(
        self, client: AsyncClient, admin_headers, db_session
    ):
        """ADMIN-I05: GET /admin/users returns paginated user list."""
        import random
        # Create some test users with unique phone numbers (11 digits)
        suffix = random.randint(1000, 9999)
        for i in range(5):
            await create_test_web_user(db_session, {
                "phone_number": f"0913{suffix}00{i}",
                "first_name": f"ListUser{i}",
                "last_name": "Test",
                "full_name": f"ListUser{i} Test",
                "role": UserRole.CUSTOMER,
            })
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/admin/users",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["page"] == 1
        assert len(data["items"]) <= data["page_size"]
    
    @pytest.mark.asyncio
    async def test_list_users_with_search_filter(
        self, client: AsyncClient, admin_headers, db_session
    ):
        """ADMIN-I06: GET /admin/users with search filter."""
        import random
        suffix = random.randint(1000, 9999)
        # Create user with specific name (11-digit phone number)
        await create_test_web_user(db_session, {
            "phone_number": f"09141{suffix}99",
            "first_name": f"SearchUser{suffix}",
            "last_name": "TestUser",
            "full_name": f"SearchUser{suffix} TestUser",
            "role": UserRole.CUSTOMER,
        })
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/admin/users",
            params={"search": f"SearchUser{suffix}"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find the user with matching name
        assert data["total"] >= 1
        assert any(f"SearchUser{suffix}" in u.get("first_name", "") for u in data["items"])
    
    @pytest.mark.asyncio
    async def test_list_users_with_role_filter(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I07: GET /admin/users with role filter."""
        response = await client.get(
            "/api/v1/admin/users",
            params={"role": "ADMIN"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned users should be ADMIN
        for user in data["items"]:
            assert user["role"] == "ADMIN"
    
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(
        self, client: AsyncClient, admin_headers
    ):
        """Test pagination for user list."""
        response = await client.get(
            "/api/v1/admin/users",
            params={"page": 1, "page_size": 5},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["items"]) <= 5


class TestAdminUserDetail:
    """Integration tests for GET /api/v1/admin/users/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_user(
        self, client: AsyncClient, admin_headers, regular_web_user
    ):
        """ADMIN-I08: GET /admin/users/{id} returns user details."""
        response = await client.get(
            f"/api/v1/admin/users/{regular_web_user.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(regular_web_user.id)
        assert "first_name" in data
        assert "phone_number" in data
    
    @pytest.mark.asyncio
    async def test_get_user_not_found_returns_404(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I09: GET /admin/users/{id} with invalid ID returns 404."""
        random_uuid = uuid4()
        response = await client.get(
            f"/api/v1/admin/users/{random_uuid}",
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestAdminUserRoleUpdate:
    """Integration tests for PATCH /api/v1/admin/users/{id}/role endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_user_role(
        self, client: AsyncClient, admin_headers, db_session
    ):
        """ADMIN-I10: PATCH /admin/users/{id}/role updates user role."""
        import random
        suffix = random.randint(1000, 9999)
        # Create a customer user (11-digit phone number)
        user = await create_test_web_user(db_session, {
            "phone_number": f"09151{suffix}88",
            "first_name": "RoleTest",
            "last_name": "User",
            "full_name": "RoleTest User",
            "role": UserRole.CUSTOMER,
        })
        await db_session.commit()
        
        response = await client.patch(
            f"/api/v1/admin/users/{user.id}/role",
            json={"role": "DESIGNER"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["role"] == "DESIGNER"
    
    @pytest.mark.asyncio
    async def test_update_role_invalid_role_returns_422(
        self, client: AsyncClient, admin_headers, regular_web_user
    ):
        """Test updating user with invalid role returns 422."""
        response = await client.patch(
            f"/api/v1/admin/users/{regular_web_user.id}/role",
            json={"role": "INVALID_ROLE"},
            headers=admin_headers
        )
        
        assert response.status_code == 422


class TestAdminUserBan:
    """Integration tests for POST /api/v1/admin/users/{id}/ban endpoint."""
    
    @pytest.mark.asyncio
    async def test_ban_user(
        self, client: AsyncClient, admin_headers, db_session
    ):
        """ADMIN-I11: POST /admin/users/{id}/ban deactivates user."""
        import random
        suffix = random.randint(1000, 9999)
        # Create user to ban (11-digit phone number)
        user = await create_test_web_user(db_session, {
            "phone_number": f"09161{suffix}77",
            "first_name": "ToBan",
            "last_name": "User",
            "full_name": "ToBan User",
            "role": UserRole.CUSTOMER,
            "is_active": True,
        })
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/admin/users/{user.id}/ban",
            json={"is_active": False, "reason": "Test ban"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_active"] == False
    
    @pytest.mark.asyncio
    async def test_unban_user(
        self, client: AsyncClient, admin_headers, db_session
    ):
        """ADMIN-I12: POST /admin/users/{id}/ban with is_active=true unbans user."""
        import random
        suffix = random.randint(1000, 9999)
        # Create banned user (11-digit phone number)
        user = await create_test_web_user(db_session, {
            "phone_number": f"09171{suffix}66",
            "first_name": "Banned",
            "last_name": "User",
            "full_name": "Banned User",
            "role": UserRole.CUSTOMER,
            "is_active": False,
        })
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/admin/users/{user.id}/ban",
            json={"is_active": True},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_cannot_ban_self(
        self, client: AsyncClient, admin_headers, admin_user
    ):
        """ADMIN-I13: Cannot ban yourself returns 400."""
        response = await client.post(
            f"/api/v1/admin/users/{admin_user.id}/ban",
            json={"is_active": False, "reason": "Self ban attempt"},
            headers=admin_headers
        )
        
        assert response.status_code == 400


# ==================== Orders Management Tests ====================

class TestAdminOrdersList:
    """Integration tests for GET /api/v1/admin/orders endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_admin_orders_returns_paginated(
        self, client: AsyncClient, admin_headers, test_order
    ):
        """ADMIN-I14: GET /admin/orders returns paginated order list."""
        response = await client.get(
            "/api/v1/admin/orders",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    @pytest.mark.asyncio
    async def test_list_orders_with_status_filter(
        self, client: AsyncClient, admin_headers, test_order
    ):
        """ADMIN-I15: GET /admin/orders with status filter."""
        response = await client.get(
            "/api/v1/admin/orders",
            params={"status": "PENDING"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for order in data["items"]:
            assert order["status"] == "PENDING"


class TestAdminOrderStatus:
    """Integration tests for PATCH /api/v1/admin/orders/{id}/status endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_order_status(
        self, client: AsyncClient, admin_headers, test_order
    ):
        """ADMIN-I16: PATCH /admin/orders/{id}/status updates order status."""
        response = await client.patch(
            f"/api/v1/admin/orders/{test_order.id}/status",
            params={"new_status": "DESIGNING"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["new_status"] == "DESIGNING"
    
    @pytest.mark.asyncio
    async def test_update_order_status_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """Test update order status with invalid ID returns 404."""
        random_uuid = uuid4()
        response = await client.patch(
            f"/api/v1/admin/orders/{random_uuid}/status",
            params={"new_status": "DESIGNING"},
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestAdminOrderAssignment:
    """Integration tests for POST /api/v1/admin/orders/{id}/assign endpoint."""
    
    @pytest.mark.asyncio
    async def test_assign_order(
        self, client: AsyncClient, admin_headers, test_order, db_session
    ):
        """ADMIN-I17: POST /admin/orders/{id}/assign assigns staff to order."""
        import random
        suffix = random.randint(1000, 9999)
        # Create a designer user (11-digit phone number)
        designer = await create_test_web_user(db_session, {
            "phone_number": f"09181{suffix}55",
            "first_name": "Designer",
            "last_name": "User",
            "full_name": "Designer User",
            "role": UserRole.DESIGNER,
        })
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/admin/orders/{test_order.id}/assign",
            params={"designer_id": str(designer.id)},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["assigned_designer_id"] == str(designer.id)


class TestAdminOrderStats:
    """Integration tests for GET /api/v1/admin/stats/orders endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_order_stats(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I18: GET /admin/stats/orders returns order statistics."""
        response = await client.get(
            "/api/v1/admin/stats/orders",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "by_status" in data
        assert "by_day" in data
        assert isinstance(data["by_status"], dict)
        assert isinstance(data["by_day"], list)


# ==================== Payments Management Tests ====================

class TestAdminPaymentsList:
    """Integration tests for GET /api/v1/admin/payments endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_admin_payments(
        self, client: AsyncClient, admin_headers, test_payment
    ):
        """ADMIN-I19: GET /admin/payments returns paginated payment list."""
        response = await client.get(
            "/api/v1/admin/payments",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    @pytest.mark.asyncio
    async def test_list_payments_with_status_filter(
        self, client: AsyncClient, admin_headers, test_payment
    ):
        """ADMIN-I20: GET /admin/payments with status filter."""
        response = await client.get(
            "/api/v1/admin/payments",
            params={"status": "PENDING"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for payment in data["items"]:
            assert payment["status"] == "PENDING"


class TestAdminPaymentVerification:
    """Integration tests for POST /api/v1/admin/payments/{id}/verify endpoint."""
    
    @pytest.mark.asyncio
    async def test_verify_payment_approve(
        self, client: AsyncClient, admin_headers, test_payment
    ):
        """ADMIN-I21: POST /admin/payments/{id}/verify?approved=true approves payment."""
        response = await client.post(
            f"/api/v1/admin/payments/{test_payment.id}/verify",
            params={"approved": True},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["status"] == "SUCCESS"
    
    @pytest.mark.asyncio
    async def test_verify_payment_reject(
        self, client: AsyncClient, admin_headers, db_session, test_order, regular_web_user
    ):
        """ADMIN-I22: POST /admin/payments/{id}/verify?approved=false rejects payment."""
        # Create a fresh payment for this test
        payment = await create_test_payment(db_session, test_order, regular_web_user)
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/admin/payments/{payment.id}/verify",
            params={"approved": False, "reason": "Invalid receipt"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["status"] == "FAILED"
    
    @pytest.mark.asyncio
    async def test_verify_already_processed_returns_400(
        self, client: AsyncClient, admin_headers, db_session, test_order, regular_web_user
    ):
        """ADMIN-I23: Verifying already processed payment returns 400."""
        # Create a payment that's already approved
        from app.models.enums import PaymentStatus
        payment = await create_test_payment(db_session, test_order, regular_web_user, {
            "status": PaymentStatus.SUCCESS,
        })
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/admin/payments/{payment.id}/verify",
            params={"approved": True},
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_verify_payment_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """Test verify payment with invalid ID returns 404."""
        random_uuid = uuid4()
        response = await client.post(
            f"/api/v1/admin/payments/{random_uuid}/verify",
            params={"approved": True},
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestAdminRevenueStats:
    """Integration tests for GET /api/v1/admin/stats/revenue endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_revenue_stats(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I24: GET /admin/stats/revenue returns revenue statistics."""
        response = await client.get(
            "/api/v1/admin/stats/revenue",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_revenue" in data
        assert "this_month" in data
        assert "last_month" in data
        assert "by_day" in data
        assert isinstance(data["by_day"], list)


class TestAdminUserStats:
    """Integration tests for GET /api/v1/admin/stats/users endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_user_stats(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN-I25: GET /admin/stats/users returns user statistics."""
        response = await client.get(
            "/api/v1/admin/stats/users",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "by_role" in data
        assert "daily_signups" in data
        assert isinstance(data["by_role"], dict)
        assert isinstance(data["daily_signups"], list)


# ==================== Access Control Tests ====================

class TestAdminAccessControl:
    """Tests for admin API access control."""
    
    @pytest.mark.asyncio
    async def test_all_admin_endpoints_require_auth(self, client: AsyncClient):
        """Verify all admin endpoints require authentication."""
        endpoints = [
            ("GET", "/api/v1/admin/stats"),
            ("GET", "/api/v1/admin/users"),
            ("GET", "/api/v1/admin/orders"),
            ("GET", "/api/v1/admin/payments"),
            ("GET", "/api/v1/admin/stats/orders"),
            ("GET", "/api/v1/admin/stats/revenue"),
            ("GET", "/api/v1/admin/stats/users"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            else:
                response = await client.post(endpoint)
            
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"
    
    @pytest.mark.asyncio
    async def test_all_admin_endpoints_require_admin_role(
        self, client: AsyncClient, regular_user_headers
    ):
        """Verify all admin endpoints require admin role."""
        endpoints = [
            ("GET", "/api/v1/admin/stats"),
            ("GET", "/api/v1/admin/users"),
            ("GET", "/api/v1/admin/orders"),
            ("GET", "/api/v1/admin/payments"),
            ("GET", "/api/v1/admin/stats/orders"),
            ("GET", "/api/v1/admin/stats/revenue"),
            ("GET", "/api/v1/admin/stats/users"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint, headers=regular_user_headers)
            else:
                response = await client.post(endpoint, headers=regular_user_headers)
            
            # Should get either 401 (invalid token) or 403 (not admin)
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require admin role, got {response.status_code}"

