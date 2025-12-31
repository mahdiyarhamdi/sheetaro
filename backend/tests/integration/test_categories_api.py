"""Integration tests for categories API endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestCategoriesAPI:
    """Test cases for categories endpoints."""

    @pytest.mark.asyncio
    async def test_list_categories_empty(self, client: AsyncClient):
        """Test listing categories when none exist."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient):
        """Test creating a new category."""
        data = {
            "slug": "labels",
            "name_fa": "لیبل",
            "description_fa": "انواع لیبل چاپی",
            "icon": "🏷️",
            "sort_order": 1,
            "is_active": True,
        }
        response = await client.post("/api/v1/categories", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["slug"] == "labels"
        assert result["name_fa"] == "لیبل"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, client: AsyncClient):
        """Test getting a category by ID."""
        # Create category first
        data = {
            "slug": "invoices",
            "name_fa": "فاکتور",
            "sort_order": 2,
        }
        create_response = await client.post("/api/v1/categories", json=data)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        # Get category
        response = await client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["slug"] == "invoices"

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, client: AsyncClient):
        """Test getting a non-existent category."""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/categories/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_category(self, client: AsyncClient):
        """Test updating a category."""
        # Create category first
        data = {
            "slug": "business-cards",
            "name_fa": "کارت ویزیت",
            "sort_order": 3,
        }
        create_response = await client.post("/api/v1/categories", json=data)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        # Update category
        update_data = {"name_fa": "کارت ویزیت حرفه‌ای"}
        response = await client.patch(
            f"/api/v1/categories/{category_id}", json=update_data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["name_fa"] == "کارت ویزیت حرفه‌ای"

    @pytest.mark.asyncio
    async def test_delete_category(self, client: AsyncClient):
        """Test deleting a category."""
        # Create category first
        data = {
            "slug": "stickers",
            "name_fa": "استیکر",
            "sort_order": 4,
        }
        create_response = await client.post("/api/v1/categories", json=data)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        # Delete category
        response = await client.delete(f"/api/v1/categories/{category_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(f"/api/v1/categories/{category_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_categories_with_items(self, client: AsyncClient):
        """Test listing categories after creating some."""
        # Create multiple categories
        for i, slug in enumerate(["cat1", "cat2", "cat3"]):
            data = {
                "slug": slug,
                "name_fa": f"دسته {i+1}",
                "sort_order": i + 1,
            }
            await client.post("/api/v1/categories", json=data)

        # List categories (active only by default)
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) >= 3


class TestAttributesAPI:
    """Test cases for category attributes endpoints."""

    @pytest.fixture
    async def category_id(self, client: AsyncClient) -> str:
        """Create a category and return its ID."""
        data = {
            "slug": "test-category",
            "name_fa": "دسته تست",
            "sort_order": 1,
        }
        response = await client.post("/api/v1/categories", json=data)
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_list_attributes_empty(self, client: AsyncClient, category_id: str):
        """Test listing attributes when none exist."""
        response = await client.get(f"/api/v1/categories/{category_id}/attributes")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_attribute(self, client: AsyncClient, category_id: str):
        """Test creating a new attribute."""
        data = {
            "slug": "size",
            "name_fa": "سایز",
            "input_type": "SELECT",
            "is_required": True,
            "sort_order": 1,
        }
        response = await client.post(
            f"/api/v1/categories/{category_id}/attributes", json=data
        )
        assert response.status_code == 201
        result = response.json()
        assert result["slug"] == "size"
        assert result["name_fa"] == "سایز"


class TestDesignPlansAPI:
    """Test cases for design plans endpoints."""

    @pytest.fixture
    async def category_id(self, client: AsyncClient) -> str:
        """Create a category and return its ID."""
        data = {
            "slug": "plan-test-category",
            "name_fa": "دسته تست پلن",
            "sort_order": 1,
        }
        response = await client.post("/api/v1/categories", json=data)
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_list_plans_empty(self, client: AsyncClient, category_id: str):
        """Test listing plans when none exist."""
        response = await client.get(f"/api/v1/categories/{category_id}/plans")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_public_plan(self, client: AsyncClient, category_id: str):
        """Test creating a public design plan."""
        data = {
            "slug": "public",
            "name_fa": "عمومی",
            "plan_type": "PUBLIC",
            "price": 0,
            "description_fa": "طرح‌های آماده رایگان",
            "has_templates": True,
            "has_questionnaire": False,
            "sort_order": 1,
        }
        response = await client.post(
            f"/api/v1/categories/{category_id}/plans", json=data
        )
        assert response.status_code == 201
        result = response.json()
        assert result["slug"] == "public"
        assert result["has_templates"] is True
        assert result["has_questionnaire"] is False

    @pytest.mark.asyncio
    async def test_create_semi_private_plan(self, client: AsyncClient, category_id: str):
        """Test creating a semi-private design plan."""
        data = {
            "slug": "semi-private",
            "name_fa": "نیمه‌خصوصی",
            "plan_type": "SEMI_PRIVATE",
            "price": 600000,
            "description_fa": "طراحی سفارشی با پرسشنامه",
            "has_templates": False,
            "has_questionnaire": True,
            "max_revisions": 3,
            "sort_order": 2,
        }
        response = await client.post(
            f"/api/v1/categories/{category_id}/plans", json=data
        )
        assert response.status_code == 201
        result = response.json()
        assert result["slug"] == "semi-private"
        assert result["has_questionnaire"] is True
        assert result["max_revisions"] == 3


class TestQuestionsAPI:
    """Test cases for design questions endpoints."""

    @pytest.fixture
    async def plan_id(self, client: AsyncClient) -> str:
        """Create a category and plan, return plan ID."""
        # Create category
        cat_data = {
            "slug": "question-test-cat",
            "name_fa": "دسته تست سوال",
            "sort_order": 1,
        }
        cat_response = await client.post("/api/v1/categories", json=cat_data)
        category_id = cat_response.json()["id"]

        # Create plan
        plan_data = {
            "slug": "semi-private-test",
            "name_fa": "نیمه‌خصوصی",
            "plan_type": "SEMI_PRIVATE",
            "price": 600000,
            "has_questionnaire": True,
            "sort_order": 1,
        }
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans", json=plan_data
        )
        return plan_response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_question(self, client: AsyncClient, plan_id: str):
        """Test creating a question for a plan."""
        data = {
            "question_fa": "رنگ اصلی طرح چه باشد؟",
            "input_type": "SINGLE_CHOICE",
            "is_required": True,
            "sort_order": 1,
            "options": [
                {"label_fa": "قرمز", "value": "red"},
                {"label_fa": "آبی", "value": "blue"},
                {"label_fa": "سبز", "value": "green"},
            ],
        }
        response = await client.post(f"/api/v1/plans/{plan_id}/questions", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["question_fa"] == "رنگ اصلی طرح چه باشد؟"


class TestTemplatesAPI:
    """Test cases for design templates endpoints."""

    @pytest.fixture
    async def plan_id(self, client: AsyncClient) -> str:
        """Create a category and public plan, return plan ID."""
        # Create category
        cat_data = {
            "slug": "template-test-cat",
            "name_fa": "دسته تست قالب",
            "sort_order": 1,
        }
        cat_response = await client.post("/api/v1/categories", json=cat_data)
        category_id = cat_response.json()["id"]

        # Create plan
        plan_data = {
            "slug": "public-test",
            "name_fa": "عمومی",
            "plan_type": "PUBLIC",
            "price": 0,
            "has_templates": True,
            "sort_order": 1,
        }
        plan_response = await client.post(
            f"/api/v1/categories/{category_id}/plans", json=plan_data
        )
        return plan_response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_template(self, client: AsyncClient, plan_id: str):
        """Test creating a template for a plan."""
        data = {
            "name_fa": "قالب ساده",
            "preview_url": "https://example.com/preview.jpg",
            "file_url": "https://example.com/template.png",
            "placeholder_x": 100,
            "placeholder_y": 100,
            "placeholder_width": 200,
            "placeholder_height": 200,
            "sort_order": 1,
        }
        response = await client.post(f"/api/v1/plans/{plan_id}/templates", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["name_fa"] == "قالب ساده"
        assert result["placeholder_x"] == 100

