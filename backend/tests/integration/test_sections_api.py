"""Integration tests for Sections API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import create_test_user
from app.models.enums import UserRole


class TestSectionsAPI:
    """Test section API endpoints."""

    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        user = await create_test_user(
            db_session,
            {
                "telegram_id": 999888777,
                "username": "testadmin",
                "first_name": "Admin",
                "last_name": "User",
                "role": UserRole.ADMIN,
            }
        )
        return user

    @pytest_asyncio.fixture
    async def test_category(self, client: AsyncClient, admin_user):
        """Create a test category."""
        import uuid
        unique_slug = f"test-label-{uuid.uuid4().hex[:8]}"
        response = await client.post(
            "/api/v1/categories",
            json={
                "slug": unique_slug,
                "name_fa": "لیبل تستی",
                "name_en": "Test Label",
                "description_fa": "توضیحات تست",
                "base_price": 10000,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        assert response.status_code == 201
        return response.json()

    @pytest_asyncio.fixture
    async def test_plan(self, client: AsyncClient, test_category, admin_user):
        """Create a test design plan."""
        import uuid
        unique_slug = f"semi-private-{uuid.uuid4().hex[:8]}"
        response = await client.post(
            f"/api/v1/categories/{test_category['id']}/plans",
            json={
                "slug": unique_slug,
                "name_fa": "پلن نیمه‌خصوصی",
                "name_en": "Semi-Private",
                "plan_type": "SEMI_PRIVATE",
                "has_questionnaire": True,
                "has_templates": False,
                "price": 50000,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        assert response.status_code == 201
        return response.json()

    @pytest.mark.asyncio
    async def test_create_section(self, client: AsyncClient, test_plan, admin_user):
        """Test creating a section for a plan."""
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/sections",
            json={
                "title_fa": "اطلاعات طراحی",
                "description_fa": "در این بخش اطلاعات طراحی را وارد کنید",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title_fa"] == "اطلاعات طراحی"
        assert data["sort_order"] == 1

    @pytest.mark.asyncio
    async def test_update_section(self, client: AsyncClient, test_plan, admin_user):
        """Test updating a section."""
        # Create section first
        create_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/sections",
            json={
                "title_fa": "اطلاعات اولیه",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        section_id = create_response.json()["id"]
        
        # Update section
        response = await client.patch(
            f"/api/v1/sections/{section_id}",
            json={
                "title_fa": "اطلاعات اولیه - ویرایش شده",
                "description_fa": "توضیحات جدید",
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title_fa"] == "اطلاعات اولیه - ویرایش شده"
        assert data["description_fa"] == "توضیحات جدید"

    @pytest.mark.asyncio
    async def test_delete_section(self, client: AsyncClient, test_plan, admin_user):
        """Test deleting a section."""
        # Create section first
        create_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/sections",
            json={
                "title_fa": "بخش موقت",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        section_id = create_response.json()["id"]
        
        # Delete section
        response = await client.delete(
            f"/api/v1/sections/{section_id}",
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 204
        
        # Verify section is deleted
        get_response = await client.get(
            f"/api/v1/sections/{section_id}",
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_sections_by_plan(self, client: AsyncClient, test_plan, admin_user):
        """Test listing sections for a plan."""
        # Create multiple sections
        for i in range(3):
            await client.post(
                f"/api/v1/plans/{test_plan['id']}/sections",
                json={
                    "title_fa": f"بخش {i + 1}",
                    "sort_order": i + 1,
                },
                headers={"X-Telegram-ID": str(admin_user.telegram_id)},
            )
        
        # List sections
        response = await client.get(
            f"/api/v1/plans/{test_plan['id']}/sections",
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_reorder_sections(self, client: AsyncClient, test_plan, admin_user):
        """Test reordering sections."""
        # Create sections
        section_ids = []
        for i in range(3):
            response = await client.post(
                f"/api/v1/plans/{test_plan['id']}/sections",
                json={
                    "title_fa": f"بخش {i + 1}",
                    "sort_order": i + 1,
                },
                headers={"X-Telegram-ID": str(admin_user.telegram_id)},
            )
            section_ids.append(response.json()["id"])
        
        # Reorder sections (reverse order)
        reorder_response = await client.patch(
            f"/api/v1/plans/{test_plan['id']}/sections/reorder",
            json={
                "section_ids": list(reversed(section_ids)),
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert reorder_response.status_code == 200

    @pytest.mark.asyncio
    async def test_section_with_questions(self, client: AsyncClient, test_plan, admin_user):
        """Test that section includes its questions."""
        # Create section
        section_response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/sections",
            json={
                "title_fa": "بخش با سوالات",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        section_id = section_response.json()["id"]
        
        # Add question to section
        await client.post(
            f"/api/v1/sections/{section_id}/questions",
            json={
                "question_fa": "نام برند شما چیست؟",
                "input_type": "TEXT",
                "is_required": True,
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        # Get section with questions
        response = await client.get(
            f"/api/v1/sections/{section_id}/questions",
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["question_fa"] == "نام برند شما چیست؟"

    @pytest.mark.asyncio
    async def test_create_section_without_auth(self, client: AsyncClient, test_plan):
        """Test section creation without explicit auth header.
        
        Note: In MVP mode, admin endpoints allow requests without auth.
        """
        response = await client.post(
            f"/api/v1/plans/{test_plan['id']}/sections",
            json={
                "title_fa": "بخش بدون احراز هویت",
                "sort_order": 1,
            },
            # No admin header - MVP mode allows this
        )
        
        # MVP mode allows creation without auth
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_section_invalid_plan(self, client: AsyncClient, admin_user):
        """Test creating section for non-existent plan."""
        fake_plan_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/plans/{fake_plan_id}/sections",
            json={
                "title_fa": "بخش تست",
                "sort_order": 1,
            },
            headers={"X-Telegram-ID": str(admin_user.telegram_id)},
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_section_sort_order_maintained(self, client: AsyncClient, test_plan, admin_user):
        """Test that sections maintain sort order."""
        # Create sections with specific sort orders
        sort_orders = [3, 1, 2]
        created_sections = []
        
        for order in sort_orders:
            response = await client.post(
                f"/api/v1/plans/{test_plan['id']}/sections",
                json={
                    "title_fa": f"بخش با ترتیب {order}",
                    "sort_order": order,
                },
                headers={"X-Telegram-ID": str(admin_user.telegram_id)},
            )
            created_sections.append(response.json())
        
        # List should return in sort_order
        list_response = await client.get(
            f"/api/v1/plans/{test_plan['id']}/sections",
        )
        
        assert list_response.status_code == 200
        data = list_response.json()
        
        # Verify ordering (should be sorted by sort_order)
        orders = [s["sort_order"] for s in data]
        assert orders == sorted(orders)

