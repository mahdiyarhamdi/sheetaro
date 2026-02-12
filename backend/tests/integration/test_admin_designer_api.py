"""Integration tests for Admin Designer Management endpoints."""

import pytest
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash
from tests.conftest import create_admin_token


# ==================== Helpers ====================


async def _create_designer(db_session: AsyncSession, **overrides) -> User:
    """Create a designer user for testing."""
    defaults = {
        "id": uuid4(),
        "first_name": "تست",
        "last_name": "طراح",
        "full_name": "تست طراح",
        "phone_number": f"09{uuid4().hex[:9]}",
        "password_hash": get_password_hash("test123456"),
        "role": UserRole.DESIGNER,
        "is_active": True,
        "phone_verified": True,
    }
    defaults.update(overrides)
    user = User(**defaults)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ==================== Tests ====================


class TestDesignerManagement:
    """Integration tests for admin designer management endpoints."""

    @pytest.mark.asyncio
    async def test_list_designers_empty(
        self, client: AsyncClient, admin_headers
    ):
        """GET /admin/designers returns empty list when no designers exist."""
        response = await client.get(
            "/api/v1/admin/designers",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_designers(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """GET /admin/designers returns paginated designer list."""
        d1 = await _create_designer(db_session, first_name="علی", last_name="طراح")
        d2 = await _create_designer(db_session, first_name="سارا", last_name="گرافیست")

        response = await client.get(
            "/api/v1/admin/designers",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        ids = [item["id"] for item in data["items"]]
        assert str(d1.id) in ids
        assert str(d2.id) in ids

    @pytest.mark.asyncio
    async def test_list_designers_search(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """GET /admin/designers with search filters by name."""
        await _create_designer(db_session, first_name="جستجوطراح", last_name="ویژه", phone_number="09123456780")

        response = await client.get(
            "/api/v1/admin/designers?search=جستجوطراح",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any("جستجوطراح" in item["first_name"] for item in data["items"])

    @pytest.mark.asyncio
    async def test_list_designers_filter_active(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """GET /admin/designers with is_active filter."""
        await _create_designer(db_session, first_name="فعال", is_active=True, phone_number="09111111180")
        await _create_designer(db_session, first_name="غیرفعال", is_active=False, phone_number="09222222280")

        # Only active
        response = await client.get(
            "/api/v1/admin/designers?is_active=true",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_designer(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """POST /admin/designers creates user with DESIGNER role."""
        payload = {
            "first_name": "طراح جدید",
            "last_name": "تست",
            "phone_number": "09301234567",
            "password": "securePass123",
            "city": "تهران",
            "bio": "طراح گرافیک حرفه‌ای",
        }

        response = await client.post(
            "/api/v1/admin/designers",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "طراح جدید"
        assert data["role"] == "DESIGNER"
        assert data["phone_number"] == "09301234567"
        assert data["city"] == "تهران"
        assert "id" in data

        # Verify the user exists in DB with DESIGNER role
        result = await db_session.execute(
            select(User).where(User.phone_number == "09301234567")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.role == UserRole.DESIGNER
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_designer_duplicate_phone(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """POST /admin/designers with duplicate phone returns 409."""
        await _create_designer(db_session, phone_number="09399999999")

        payload = {
            "first_name": "دوباره",
            "phone_number": "09399999999",
            "password": "test123456",
        }

        response = await client.post(
            "/api/v1/admin/designers",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_designer_requires_admin(
        self, client: AsyncClient, regular_user_headers
    ):
        """POST /admin/designers with non-admin returns 403."""
        payload = {
            "first_name": "طراح",
            "phone_number": "09101010101",
            "password": "test123456",
        }

        response = await client.post(
            "/api/v1/admin/designers",
            json=payload,
            headers=regular_user_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_toggle_designer_active(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """POST /admin/designers/{id}/toggle-active toggles is_active."""
        designer = await _create_designer(db_session, is_active=True, phone_number="09441234567")
        assert designer.is_active is True

        # Toggle to inactive
        response = await client.post(
            f"/api/v1/admin/designers/{designer.id}/toggle-active",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

        # Toggle back to active
        response = await client.post(
            f"/api/v1/admin/designers/{designer.id}/toggle-active",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_designer(
        self, client: AsyncClient, admin_headers
    ):
        """POST /admin/designers/{id}/toggle-active for non-existent returns 404."""
        response = await client.post(
            f"/api/v1/admin/designers/{uuid4()}/toggle-active",
            headers=admin_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_designer_stats(
        self, client: AsyncClient, admin_headers, db_session: AsyncSession
    ):
        """GET /admin/designers/{id}/stats returns correct counts."""
        designer = await _create_designer(db_session, phone_number="09551234567")

        response = await client.get(
            f"/api/v1/admin/designers/{designer.id}/stats",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["designer_id"] == str(designer.id)
        assert "total_assigned" in data
        assert "in_progress" in data
        assert "completed" in data
        assert "queue_count" in data

    @pytest.mark.asyncio
    async def test_designer_stats_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """GET /admin/designers/{id}/stats for non-existent designer returns 404."""
        response = await client.get(
            f"/api/v1/admin/designers/{uuid4()}/stats",
            headers=admin_headers,
        )
        assert response.status_code == 404
