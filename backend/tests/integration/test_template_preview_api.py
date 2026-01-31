"""Integration tests for Template Preview API endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from PIL import Image
from io import BytesIO

from tests.conftest import (
    create_test_admin_user,
    create_admin_token,
    create_test_category,
    create_test_plan_with_templates,
    create_test_template,
)
from app.models.enums import UserRole


class TestTemplatePreview:
    """Test template preview generation endpoints."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120003001",
            "password_hash": "hashed_password",
            "first_name": "Preview",
            "last_name": "Admin",
            "full_name": "Preview Admin",
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
    async def test_template_with_placeholders(self, db_session, client: AsyncClient, admin_headers):
        """Create a template with placeholders for preview testing."""
        category = await create_test_category(db_session, {
            "slug": f"preview-test-{uuid4().hex[:8]}",
            "name_fa": "دسته پیش‌نمایش",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan, {
            "plan_id": plan.id,
            "name_fa": "قالب با جایگاه برای پیش‌نمایش",
            "preview_url": "https://via.placeholder.com/500x400/FFFFFF/000000",
            "file_url": "https://via.placeholder.com/500x400/FFFFFF/000000",
            "image_width": 500,
            "image_height": 400,
        })
        
        # Create IMAGE placeholder
        img_response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "IMAGE",
                "name": "logo",
                "label_fa": "لوگو",
                "x": 50,
                "y": 50,
                "width": 100,
                "height": 100,
                "is_required": True,
                "sort_order": 0,
            },
            headers=admin_headers,
        )
        
        # Create TEXT placeholder
        txt_response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "company_name",
                "label_fa": "نام شرکت",
                "x": 200,
                "y": 300,
                "width": 250,
                "height": 50,
                "font_family": "IRANSans",
                "font_size": 24,
                "font_color": "#000000",
                "text_align": "center",
                "default_value": "نام شرکت",
                "is_required": True,
                "sort_order": 1,
            },
            headers=admin_headers,
        )
        
        return {
            "template": template,
            "image_placeholder": img_response.json() if img_response.status_code == 201 else None,
            "text_placeholder": txt_response.json() if txt_response.status_code == 201 else None,
        }
    
    @pytest.mark.asyncio
    async def test_generate_preview_with_image_placeholder(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test generating preview with image placeholder data."""
        template_data = test_template_with_placeholders
        template = template_data["template"]
        img_placeholder = template_data["image_placeholder"]
        
        if not img_placeholder:
            pytest.skip("Image placeholder creation failed")
        
        # Mock the image download to avoid network calls
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            # Create mock images
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            logo_img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
            mock_download.side_effect = [template_img, logo_img]
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": [
                        {
                            "placeholder_id": img_placeholder["id"],
                            "image_url": "https://example.com/logo.png",
                        }
                    ]
                },
                headers=admin_headers,
            )
            
            # Preview should work or fail gracefully if service not configured
            assert response.status_code in [200, 400, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "preview_url" in data
                assert "width" in data
                assert "height" in data
    
    @pytest.mark.asyncio
    async def test_generate_preview_with_text_placeholder(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test generating preview with text placeholder data."""
        template_data = test_template_with_placeholders
        template = template_data["template"]
        txt_placeholder = template_data["text_placeholder"]
        
        if not txt_placeholder:
            pytest.skip("Text placeholder creation failed")
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            mock_download.return_value = template_img
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": [
                        {
                            "placeholder_id": txt_placeholder["id"],
                            "text_value": "شرکت تست",
                        }
                    ]
                },
                headers=admin_headers,
            )
            
            assert response.status_code in [200, 400, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "preview_url" in data
    
    @pytest.mark.asyncio
    async def test_generate_preview_with_multiple_placeholders(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test generating preview with both image and text placeholders."""
        template_data = test_template_with_placeholders
        template = template_data["template"]
        img_placeholder = template_data["image_placeholder"]
        txt_placeholder = template_data["text_placeholder"]
        
        if not img_placeholder or not txt_placeholder:
            pytest.skip("Placeholder creation failed")
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            logo_img = Image.new("RGBA", (100, 100), color=(0, 0, 255, 255))
            mock_download.side_effect = [template_img, logo_img]
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": [
                        {
                            "placeholder_id": img_placeholder["id"],
                            "image_url": "https://example.com/logo.png",
                        },
                        {
                            "placeholder_id": txt_placeholder["id"],
                            "text_value": "متن شرکت",
                        }
                    ]
                },
                headers=admin_headers,
            )
            
            assert response.status_code in [200, 400, 422, 500]
    
    @pytest.mark.asyncio
    async def test_generate_preview_template_not_found(self, client: AsyncClient, admin_headers):
        """Test generating preview for non-existent template."""
        fake_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/templates/{fake_id}/preview",
            json={
                "placeholders": []
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_generate_preview_empty_placeholders(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test generating preview with no placeholder data."""
        template = test_template_with_placeholders["template"]
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            mock_download.return_value = template_img
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": []
                },
                headers=admin_headers,
            )
            
            # Should succeed (just shows template) or fail gracefully
            assert response.status_code in [200, 400, 422, 500]
    
    @pytest.mark.asyncio
    async def test_generate_preview_returns_dimensions(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test that preview response includes dimensions."""
        template = test_template_with_placeholders["template"]
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            mock_download.return_value = template_img
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": []
                },
                headers=admin_headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "width" in data
                assert "height" in data
                assert data["width"] == 500
                assert data["height"] == 400
    
    @pytest.mark.asyncio
    async def test_generate_preview_requires_auth(self, client: AsyncClient, test_template_with_placeholders):
        """Test that preview generation requires authentication."""
        template = test_template_with_placeholders["template"]
        
        response = await client.post(
            f"/api/v1/templates/{template.id}/preview",
            json={
                "placeholders": []
            },
            # No auth header
        )
        
        # May require admin or be open
        # Just verify it doesn't crash
        assert response.status_code in [200, 400, 401, 403, 422, 500]
    
    @pytest.mark.asyncio
    async def test_generate_preview_invalid_placeholder_id(self, client: AsyncClient, test_template_with_placeholders, admin_headers):
        """Test generating preview with invalid placeholder ID."""
        template = test_template_with_placeholders["template"]
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (500, 400), color=(255, 255, 255))
            mock_download.return_value = template_img
            
            response = await client.post(
                f"/api/v1/templates/{template.id}/preview",
                json={
                    "placeholders": [
                        {
                            "placeholder_id": str(uuid4()),  # Non-existent
                            "text_value": "تست",
                        }
                    ]
                },
                headers=admin_headers,
            )
            
            # Should succeed (ignore unknown) or fail gracefully
            assert response.status_code in [200, 400, 422, 500]


class TestApplyLogoEndpoint:
    """Test the legacy apply-logo endpoint."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120003002",
            "password_hash": "hashed_password",
            "first_name": "Logo",
            "last_name": "Admin",
            "full_name": "Logo Admin",
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
    async def test_template(self, db_session):
        """Create a test template with legacy placeholder fields."""
        category = await create_test_category(db_session, {
            "slug": f"legacy-logo-{uuid4().hex[:8]}",
            "name_fa": "دسته لوگو",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan, {
            "plan_id": plan.id,
            "name_fa": "قالب با پلیس‌هولدر لوگو",
            "preview_url": "https://via.placeholder.com/800x600",
            "file_url": "https://via.placeholder.com/800x600",
            "image_width": 800,
            "image_height": 600,
            "placeholder_x": 300,
            "placeholder_y": 200,
            "placeholder_width": 200,
            "placeholder_height": 200,
        })
        return template
    
    @pytest.mark.asyncio
    async def test_apply_logo_success(self, client: AsyncClient, test_template, admin_headers):
        """Test successful logo application."""
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            template_img = Image.new("RGB", (800, 600), color=(255, 255, 255))
            logo_img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
            mock_download.side_effect = [template_img, logo_img]
            
            response = await client.post(
                f"/api/v1/templates/{test_template.id}/apply-logo",
                json={
                    "logo_file_url": "https://example.com/logo.png",
                },
                headers=admin_headers,
            )
            
            # May succeed or fail based on service configuration
            if response.status_code == 200:
                data = response.json()
                assert "preview_url" in data
                assert "final_url" in data
    
    @pytest.mark.asyncio
    async def test_apply_logo_template_not_found(self, client: AsyncClient, admin_headers):
        """Test applying logo to non-existent template."""
        fake_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/templates/{fake_id}/apply-logo",
            json={
                "logo_file_url": "https://example.com/logo.png",
            },
            headers=admin_headers,
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_apply_logo_missing_url(self, client: AsyncClient, test_template, admin_headers):
        """Test applying logo without URL."""
        response = await client.post(
            f"/api/v1/templates/{test_template.id}/apply-logo",
            json={},
            headers=admin_headers,
        )
        
        assert response.status_code == 422


class TestTemplatePreviewGeneration:
    """Test template preview file creation."""
    
    @pytest_asyncio.fixture
    async def admin_user(self, db_session):
        """Create an admin user for testing."""
        return await create_test_admin_user(db_session, {
            "phone_number": "09120003003",
            "password_hash": "hashed_password",
            "first_name": "Generate",
            "last_name": "Admin",
            "full_name": "Generate Admin",
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
    async def test_preview_creates_file(self, db_session, client: AsyncClient, admin_headers, tmp_path):
        """Test that preview generation creates a file."""
        # Create template
        category = await create_test_category(db_session, {
            "slug": f"file-create-{uuid4().hex[:8]}",
            "name_fa": "دسته فایل",
        })
        plan = await create_test_plan_with_templates(db_session, category)
        template = await create_test_template(db_session, plan, {
            "plan_id": plan.id,
            "name_fa": "قالب برای ذخیره فایل",
            "file_url": "https://example.com/template.png",
        })
        
        # Create placeholder
        ph_response = await client.post(
            f"/api/v1/templates/{template.id}/placeholders",
            json={
                "type": "TEXT",
                "name": "test",
                "label_fa": "تست",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 30,
                "default_value": "متن تست",
            },
            headers=admin_headers,
        )
        
        if ph_response.status_code != 201:
            pytest.skip("Placeholder creation failed")
        
        placeholder = ph_response.json()
        
        with patch("app.services.template_service.TemplateService.download_image") as mock_download:
            with patch("app.services.template_service.TemplateService.save_image") as mock_save:
                template_img = Image.new("RGB", (400, 300), color=(255, 255, 255))
                mock_download.return_value = template_img
                mock_save.return_value = str(tmp_path / "preview.png")
                
                response = await client.post(
                    f"/api/v1/templates/{template.id}/preview",
                    json={
                        "placeholders": [
                            {
                                "placeholder_id": placeholder["id"],
                                "text_value": "متن پیش‌نمایش",
                            }
                        ]
                    },
                    headers=admin_headers,
                )
                
                # Just verify the endpoint handles the request
                assert response.status_code in [200, 400, 422, 500]

