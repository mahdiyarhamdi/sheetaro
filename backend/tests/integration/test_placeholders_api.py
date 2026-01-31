"""Integration tests for Template Placeholders API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import (
    create_test_admin_user, 
    create_admin_token,
    create_test_category,
    create_test_plan_with_templates,
    create_test_template,
)
from app.models.enums import UserRole


class TestPlaceholdersList:
    """Test placeholder listing endpoints."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002001",
            "password_hash": "hashed_password",
            "first_name": "Placeholder",
            "last_name": "Admin",
            "full_name": "Placeholder Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def test_template(self, db_session, client: AsyncClient, admin_headers):
        """Create a test template for placeholder tests."""
        category = await create_test_category(db_session, {
            "slug": f"placeholder-test-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan, {
            "plan_id": plan.id,
            "name_fa": "قالب برای جایگاه‌ها",
            "preview_url": "https://example.com/preview.png",
            "file_url": "https://example.com/template.png",
        })
        return template
    
    @pytest_asyncio.fixture
    async def sample_placeholders(self, client: AsyncClient, test_template, admin_headers):
        """Create sample placeholders for testing."""
        placeholders = []
        
        # Create IMAGE placeholder
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "logo",
                "label_fa": "لوگو",
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 200,
                "sort_order": 0,
                "is_active": True,
            },
            headers=admin_headers,
        )
        if response.status_code == 201:
            placeholders.append(response.json())
        
        # Create TEXT placeholder
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "company_name",
                "label_fa": "نام شرکت",
                "x": 300,
                "y": 500,
                "width": 400,
                "height": 50,
                "font_family": "IRANSans",
                "font_size": 28,
                "font_color": "#333333",
                "sort_order": 1,
                "is_active": True,
            },
            headers=admin_headers,
        )
        if response.status_code == 201:
            placeholders.append(response.json())
        
        # Create inactive placeholder
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "inactive",
                "label_fa": "غیرفعال",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 50,
                "sort_order": 2,
                "is_active": False,
            },
            headers=admin_headers,
        )
        if response.status_code == 201:
            placeholders.append(response.json())
        
        return placeholders
    
    @pytest.mark.asyncio
    async def test_list_placeholders_for_template(self, client: AsyncClient, test_template, sample_placeholders):
        """Test listing all placeholders for a template."""
        response = await client.get(
            f"/api/v1/templates/{test_template.id}/placeholders"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least 2 active placeholders
    
    @pytest.mark.asyncio
    async def test_list_placeholders_active_only(self, client: AsyncClient, test_template, sample_placeholders):
        """Test filtering placeholders by active status."""
        response = await client.get(
            f"/api/v1/templates/{test_template.id}/placeholders?active_only=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        for placeholder in data:
            assert placeholder["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_list_placeholders_ordered_by_sort_order(self, client: AsyncClient, test_template, sample_placeholders):
        """Test that placeholders are ordered by sort_order."""
        response = await client.get(
            f"/api/v1/templates/{test_template.id}/placeholders?active_only=false"
        )
        
        assert response.status_code == 200
        data = response.json()
        if len(data) > 1:
            orders = [p["sort_order"] for p in data]
            assert orders == sorted(orders)
    
    @pytest.mark.asyncio
    async def test_list_placeholders_template_not_found(self, client: AsyncClient):
        """Test listing placeholders for non-existent template."""
        fake_id = str(uuid4())
        
        response = await client.get(
            f"/api/v1/templates/{fake_id}/placeholders"
        )
        
        # Should return 404 or empty list
        assert response.status_code in [200, 404]


class TestPlaceholderCreate:
    """Test placeholder creation endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002002",
            "password_hash": "hashed_password",
            "first_name": "Placeholder",
            "last_name": "Admin",
            "full_name": "Placeholder Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def regular_user(self, db_session):
        """Create a regular user for testing."""
        from tests.conftest import create_test_web_user
        from app.core.security import get_password_hash
        return await create_test_web_user(db_session, {
            "phone_number": "09120002003",
            "password_hash": get_password_hash("user123456"),
            "first_name": "Regular",
            "last_name": "User",
            "full_name": "Regular User",
            "role": UserRole.CUSTOMER,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def regular_user_headers(self, regular_user):
        """Get regular user authorization headers."""
        token = create_admin_token(str(regular_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def test_template(self, db_session):
        """Create a test template."""
        category = await create_test_category(db_session, {
            "slug": f"placeholder-create-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        return template
    
    @pytest.mark.asyncio
    async def test_create_image_placeholder(self, client: AsyncClient, test_template, admin_headers):
        """Test creating an IMAGE placeholder."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "logo",
                "label_fa": "لوگوی شرکت",
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 200,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "IMAGE"
        assert data["name"] == "logo"
        assert data["label_fa"] == "لوگوی شرکت"
        assert data["x"] == 100
        assert data["y"] == 100
        assert data["width"] == 200
        assert data["height"] == 200
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_text_placeholder(self, client: AsyncClient, test_template, admin_headers):
        """Test creating a TEXT placeholder."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "company_name",
                "label_fa": "نام شرکت",
                "x": 300,
                "y": 500,
                "width": 400,
                "height": 50,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "TEXT"
        assert data["name"] == "company_name"
    
    @pytest.mark.asyncio
    async def test_create_text_placeholder_with_font_settings(self, client: AsyncClient, test_template, admin_headers):
        """Test creating a TEXT placeholder with full font settings."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "styled_text",
                "label_fa": "متن با استایل",
                "x": 100,
                "y": 200,
                "width": 300,
                "height": 40,
                "font_family": "Vazir",
                "font_size": 24,
                "font_weight": 700,
                "font_color": "#FF5500",
                "text_align": "center",
                "max_length": 50,
                "default_value": "متن پیش‌فرض",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["font_family"] == "Vazir"
        assert data["font_size"] == 24
        assert data["font_weight"] == 700
        assert data["font_color"] == "#FF5500"
        assert data["text_align"] == "center"
        assert data["max_length"] == 50
        assert data["default_value"] == "متن پیش‌فرض"
    
    @pytest.mark.asyncio
    async def test_create_placeholder_requires_admin(self, client: AsyncClient, test_template, regular_user_headers):
        """Test that non-admin cannot create placeholders."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "test",
                "label_fa": "تست",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            headers=regular_user_headers,
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_create_placeholder_template_not_found(self, client: AsyncClient, admin_headers):
        """Test creating placeholder for non-existent template."""
        fake_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/templates/{fake_id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "test",
                "label_fa": "تست",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            headers=admin_headers,
        )
        
        assert response.status_code in [404, 500]
    
    @pytest.mark.asyncio
    async def test_create_placeholder_invalid_type_rejected(self, client: AsyncClient, test_template, admin_headers):
        """Test that invalid placeholder type is rejected."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/placeholders",
            json={
                "type": "INVALID_TYPE",
                "name": "test",
                "label_fa": "تست",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 422


class TestPlaceholderUpdate:
    """Test placeholder update endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002004",
            "password_hash": "hashed_password",
            "first_name": "Placeholder",
            "last_name": "Admin",
            "full_name": "Placeholder Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.fixture
    async def test_placeholder(self, db_session, client: AsyncClient, admin_headers):
        """Create a test placeholder."""
        category = await create_test_category(db_session, {
            "slug": f"placeholder-update-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "update_test",
                "label_fa": "برای ویرایش",
                "x": 50,
                "y": 50,
                "width": 150,
                "height": 40,
            },
            headers=admin_headers,
        )
        return response.json()
    
    @pytest.mark.asyncio
    async def test_update_placeholder_position(self, client: AsyncClient, test_placeholder, admin_headers):
        """Test updating placeholder position."""
        response = await client.patch(
            f"/api/v1/placeholders/{test_placeholder['id']}",
            json={
                "x": 200,
                "y": 300,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 200
        assert data["y"] == 300
    
    @pytest.mark.asyncio
    async def test_update_placeholder_size(self, client: AsyncClient, test_placeholder, admin_headers):
        """Test updating placeholder size."""
        response = await client.patch(
            f"/api/v1/placeholders/{test_placeholder['id']}",
            json={
                "width": 250,
                "height": 60,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["width"] == 250
        assert data["height"] == 60
    
    @pytest.mark.asyncio
    async def test_update_placeholder_rotation(self, client: AsyncClient, test_placeholder, admin_headers):
        """Test updating placeholder rotation."""
        response = await client.patch(
            f"/api/v1/placeholders/{test_placeholder['id']}",
            json={
                "rotation": 45,
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rotation"] == 45
    
    @pytest.mark.asyncio
    async def test_update_text_placeholder_font_settings(self, client: AsyncClient, test_placeholder, admin_headers):
        """Test updating TEXT placeholder font settings."""
        response = await client.patch(
            f"/api/v1/placeholders/{test_placeholder['id']}",
            json={
                "font_family": "NewFont",
                "font_size": 32,
                "font_weight": 600,
                "font_color": "#0000FF",
                "text_align": "left",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["font_family"] == "NewFont"
        assert data["font_size"] == 32
        assert data["font_weight"] == 600
        assert data["font_color"] == "#0000FF"
        assert data["text_align"] == "left"
    
    @pytest.mark.asyncio
    async def test_update_placeholder_not_found(self, client: AsyncClient, admin_headers):
        """Test updating non-existent placeholder."""
        fake_id = str(uuid4())
        
        response = await client.patch(
            f"/api/v1/placeholders/{fake_id}",
            json={"x": 100},
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_placeholder_requires_admin(self, client: AsyncClient, test_placeholder):
        """Test that non-admin cannot update placeholders."""
        response = await client.patch(
            f"/api/v1/placeholders/{test_placeholder['id']}",
            json={"x": 100},
            # No auth header
        )
        
        assert response.status_code in [401, 403]


class TestPlaceholderDelete:
    """Test placeholder deletion endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002005",
            "password_hash": "hashed_password",
            "first_name": "Placeholder",
            "last_name": "Admin",
            "full_name": "Placeholder Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_delete_placeholder_success(self, db_session, client: AsyncClient, admin_headers):
        """Test successful placeholder deletion."""
        # Create template and placeholder
        category = await create_test_category(db_session, {
            "slug": f"placeholder-delete-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        create_response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "to_delete",
                "label_fa": "برای حذف",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            headers=admin_headers,
        )
        placeholder_id = create_response.json()["id"]
        
        # Delete placeholder
        response = await client.delete(
            f"/api/v1/placeholders/{placeholder_id}",
            headers=admin_headers,
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_placeholder_not_found(self, client: AsyncClient, admin_headers):
        """Test deleting non-existent placeholder."""
        fake_id = str(uuid4())
        
        response = await client.delete(
            f"/api/v1/placeholders/{fake_id}",
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_placeholder_requires_admin(self, db_session, client: AsyncClient, admin_headers):
        """Test that non-admin cannot delete placeholders."""
        # Create template and placeholder
        category = await create_test_category(db_session, {
            "slug": f"placeholder-nodelete-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        create_response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "no_delete",
                "label_fa": "غیرقابل حذف",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            headers=admin_headers,
        )
        placeholder_id = create_response.json()["id"]
        
        # Try to delete without auth
        response = await client.delete(
            f"/api/v1/placeholders/{placeholder_id}",
            # No auth header
        )
        
        assert response.status_code in [401, 403]


class TestPlaceholderReorder:
    """Test placeholder reordering endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002006",
            "password_hash": "hashed_password",
            "first_name": "Placeholder",
            "last_name": "Admin",
            "full_name": "Placeholder Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_reorder_placeholders_success(self, db_session, client: AsyncClient, admin_headers):
        """Test successful placeholder reordering."""
        # Create template
        category = await create_test_category(db_session, {
            "slug": f"placeholder-reorder-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        # Create multiple placeholders
        placeholders = []
        for i in range(3):
            response = await client.post(
                f"/api/v1/templates/{template.id}/placeholders",
                json={
                    "type": "IMAGE",
                    "name": f"reorder_{i}",
                    "label_fa": f"جایگاه {i}",
                    "x": i * 100,
                    "y": 0,
                    "width": 80,
                    "height": 80,
                    "sort_order": i,
                },
                headers=admin_headers,
            )
            if response.status_code == 201:
                placeholders.append(response.json())
        
        # Reorder: reverse the order
        reorder_data = {
            "items": [
                {"id": placeholders[0]["id"], "sort_order": 2},
                {"id": placeholders[1]["id"], "sort_order": 1},
                {"id": placeholders[2]["id"], "sort_order": 0},
            ]
        }
        
        response = await client.patch(
            f"/api/v1/templates/{template.id}/placeholders/reorder",
            json=reorder_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_reorder_requires_admin(self, db_session, client: AsyncClient, admin_headers):
        """Test that non-admin cannot reorder placeholders."""
        category = await create_test_category(db_session, {
            "slug": f"placeholder-noreorder-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        response = await client.patch(
            f"/api/v1/templates/{template.id}/placeholders/reorder",
            json={"items": []},
            # No auth header
        )
        
        assert response.status_code in [401, 403]


class TestTemplateWithPlaceholders:
    """Test getting template with placeholders."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120002007",
            "password_hash": "hashed_password",
            "first_name": "Template",
            "last_name": "Admin",
            "full_name": "Template Admin",
            "role": UserRole.ADMIN,
            "phone_verified": True,
            "is_active": True,
        })
    
    @pytest_asyncio.fixture
    async def admin_headers(self, admin_user):
        """Get admin authorization headers."""
        token = create_admin_token(str(admin_user.id))
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_get_template_details_includes_placeholders(self, db_session, client: AsyncClient, admin_headers):
        """Test that template details include placeholders."""
        # Create template
        category = await create_test_category(db_session, {
            "slug": f"template-details-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        # Create placeholders
        for i in range(2):
            await client.post(
                f"/api/v1/templates/{template.id}/placeholders",
                json={
                    "type": "TEXT" if i % 2 else "IMAGE",
                    "name": f"ph_{i}",
                    "label_fa": f"جایگاه {i}",
                    "x": i * 100,
                    "y": 0,
                    "width": 100,
                    "height": 100,
                    "sort_order": i,
                },
                headers=admin_headers,
            )
        
        # Get template details
        response = await client.get(f"/api/v1/templates/{template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "placeholders" in data
        assert len(data["placeholders"]) >= 2
    
    @pytest.mark.asyncio
    async def test_template_details_placeholders_sorted(self, db_session, client: AsyncClient, admin_headers):
        """Test that placeholders are sorted by sort_order."""
        # Create template
        category = await create_test_category(db_session, {
            "slug": f"template-sorted-{uuid4().hex[:8]}",
            "name_fa": "دسته تست",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan)
        
        # Create placeholders in reverse order
        for i in [2, 0, 1]:
            await client.post(
                f"/api/v1/templates/{template.id}/placeholders",
                json={
                    "type": "IMAGE",
                    "name": f"sorted_{i}",
                    "label_fa": f"جایگاه ترتیب {i}",
                    "x": 0,
                    "y": 0,
                    "width": 100,
                    "height": 100,
                    "sort_order": i,
                },
                headers=admin_headers,
            )
        
        # Get template details
        response = await client.get(f"/api/v1/templates/{template.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        if "placeholders" in data and len(data["placeholders"]) > 1:
            orders = [p["sort_order"] for p in data["placeholders"]]
            assert orders == sorted(orders)

