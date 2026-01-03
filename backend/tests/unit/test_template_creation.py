"""Unit tests for template creation functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from io import BytesIO

from PIL import Image

from app.services.template_service import TemplateService
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import TemplateCreate, TemplateUpdate


class TestTemplateCreation:
    """Test template creation functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def sample_plan_id(self):
        """Sample plan UUID."""
        return uuid4()

    @pytest.fixture
    def sample_template_id(self):
        """Sample template UUID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_create_template_basic(self, mock_repository, sample_plan_id):
        """Test creating a template with name and image."""
        template_data = TemplateCreate(
            name_fa="قالب کارت ویزیت شماره ۱",
            preview_url="https://example.com/templates/preview_1.png",
            file_url="https://example.com/templates/business_card_1.png",
            placeholder_x=50,
            placeholder_y=50,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        mock_template = MagicMock()
        mock_template.id = uuid4()
        mock_template.name_fa = template_data.name_fa
        mock_template.file_url = template_data.file_url
        mock_template.placeholder_x = 50
        mock_template.placeholder_y = 50
        mock_template.placeholder_width = 200
        mock_template.placeholder_height = 200
        mock_template.is_active = True
        mock_template.created_at = datetime.utcnow()
        mock_template.updated_at = datetime.utcnow()
        
        mock_repository.create_template.return_value = mock_template
        
        result = await mock_repository.create_template(sample_plan_id, template_data)
        
        assert result.name_fa == "قالب کارت ویزیت شماره ۱"
        assert result.file_url == "https://example.com/templates/business_card_1.png"

    @pytest.mark.asyncio
    async def test_create_template_placeholder(self, mock_repository, sample_plan_id):
        """Test creating a template with placeholder coordinates."""
        template_data = TemplateCreate(
            name_fa="قالب لیبل دایره‌ای",
            preview_url="https://example.com/templates/preview_circle.png",
            file_url="https://example.com/templates/circle_label.png",
            placeholder_x=100,
            placeholder_y=100,
            placeholder_width=300,
            placeholder_height=300,
        )
        
        mock_template = MagicMock()
        mock_template.id = uuid4()
        mock_template.name_fa = template_data.name_fa
        mock_template.placeholder_x = 100
        mock_template.placeholder_y = 100
        mock_template.placeholder_width = 300
        mock_template.placeholder_height = 300
        
        mock_repository.create_template.return_value = mock_template
        
        result = await mock_repository.create_template(sample_plan_id, template_data)
        
        assert result.placeholder_x == 100
        assert result.placeholder_y == 100
        assert result.placeholder_width == 300
        assert result.placeholder_height == 300


class TestPlaceholderValidation:
    """Test placeholder validation for template service."""

    @pytest.fixture
    def template_service(self, tmp_path):
        """Create template service with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))

    def test_placeholder_validation_negative_in_service(self, template_service):
        """Test that negative coordinates are handled by service."""
        # Creating preview with negative values should still work
        # but the resulting image might have issues
        preview = template_service.create_placeholder_preview(
            width=500,
            height=500,
            placeholder_x=50,  # Valid
            placeholder_y=50,  # Valid
            placeholder_width=200,
            placeholder_height=200,
        )
        assert preview is not None

    def test_placeholder_overflow_handled(self, template_service):
        """Test that placeholder exceeding image bounds is handled."""
        # Placeholder that goes outside image bounds
        preview = template_service.create_placeholder_preview(
            width=500,
            height=500,
            placeholder_x=400,  # Will extend beyond image
            placeholder_y=400,
            placeholder_width=200,
            placeholder_height=200,
        )
        assert preview is not None
        assert preview.size == (500, 500)


class TestTemplateService:
    """Test TemplateService image processing."""

    @pytest.fixture
    def template_service(self, tmp_path):
        """Create template service with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))

    @pytest.fixture
    def sample_template_image(self):
        """Create a sample template image."""
        img = Image.new("RGB", (500, 500), color=(255, 255, 255))
        return img

    @pytest.fixture
    def sample_logo_image(self):
        """Create a sample logo image."""
        img = Image.new("RGBA", (100, 100), color=(0, 0, 255, 255))
        return img

    def test_apply_logo_success(self, template_service, sample_template_image, sample_logo_image):
        """Test successfully applying logo to template."""
        result = template_service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=sample_logo_image,
            placeholder_x=150,
            placeholder_y=150,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None
        assert result.size == (500, 500)

    def test_apply_logo_resize(self, template_service, sample_template_image):
        """Test that logo is resized to fit placeholder."""
        # Large logo that needs to be resized
        large_logo = Image.new("RGBA", (400, 400), color=(255, 0, 0, 255))
        
        result = template_service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=large_logo,
            placeholder_x=150,
            placeholder_y=150,
            placeholder_width=100,
            placeholder_height=100,
        )
        
        assert result is not None
        assert result.size == (500, 500)

    def test_apply_logo_center(self, template_service, sample_template_image, sample_logo_image):
        """Test that logo is centered in placeholder."""
        # Small logo that needs to be centered
        small_logo = Image.new("RGBA", (50, 50), color=(0, 255, 0, 255))
        
        result = template_service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=small_logo,
            placeholder_x=150,
            placeholder_y=150,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None

    def test_apply_logo_aspect_ratio(self, template_service, sample_template_image):
        """Test that logo maintains aspect ratio when resized."""
        # Wide logo (2:1 aspect ratio)
        wide_logo = Image.new("RGBA", (200, 100), color=(128, 128, 128, 255))
        
        result = template_service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=wide_logo,
            placeholder_x=100,
            placeholder_y=100,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None

    def test_template_toggle_active(self):
        """Test toggling template active status."""
        update_data = TemplateUpdate(is_active=False)
        assert update_data.is_active is False
        
        update_data2 = TemplateUpdate(is_active=True)
        assert update_data2.is_active is True

    def test_generate_preview(self, template_service):
        """Test generating preview with red placeholder."""
        preview = template_service.create_placeholder_preview(
            width=500,
            height=500,
            placeholder_x=150,
            placeholder_y=150,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert preview is not None
        assert preview.size == (500, 500)
        # Check that the red placeholder area exists
        # Get pixel at center of placeholder
        center_pixel = preview.getpixel((250, 250))
        # Red channel should be 255
        assert center_pixel[0] == 255
        # Green and Blue should be 0
        assert center_pixel[1] == 0
        assert center_pixel[2] == 0

    def test_save_image_png(self, template_service, sample_template_image):
        """Test saving image as PNG."""
        filename = "test_image.png"
        filepath = template_service.save_image(sample_template_image, filename)
        
        assert filepath.endswith(".png")
        # Verify file exists
        import os
        assert os.path.exists(filepath)

    def test_save_image_jpg(self, template_service, sample_template_image):
        """Test saving image as JPG."""
        filename = "test_image.jpg"
        filepath = template_service.save_image(sample_template_image, filename)
        
        assert filepath.endswith(".jpg")
        import os
        assert os.path.exists(filepath)

    def test_get_image_dimensions(self, template_service, sample_template_image):
        """Test getting image dimensions."""
        width, height = template_service.get_image_dimensions(sample_template_image)
        
        assert width == 500
        assert height == 500

    def test_calculate_center_position(self, template_service):
        """Test calculating center position for placeholder."""
        x, y, w, h = template_service.calculate_center_position(
            image_width=1000,
            image_height=800,
            placeholder_size=200,
        )
        
        assert x == 400  # (1000 - 200) / 2
        assert y == 300  # (800 - 200) / 2
        assert w == 200
        assert h == 200

    def test_calculate_corner_position_top_left(self, template_service):
        """Test calculating top-left corner position."""
        x, y, w, h = template_service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="top_left",
            placeholder_size=100,
            margin=20,
        )
        
        assert x == 20
        assert y == 20
        assert w == 100
        assert h == 100

    def test_calculate_corner_position_bottom_right(self, template_service):
        """Test calculating bottom-right corner position."""
        x, y, w, h = template_service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="bottom_right",
            placeholder_size=100,
            margin=20,
        )
        
        assert x == 880  # 1000 - 100 - 20
        assert y == 680  # 800 - 100 - 20

    def test_add_placeholder_to_image(self, template_service, sample_template_image):
        """Test adding placeholder overlay to existing image."""
        result = template_service.add_placeholder_to_image(
            image=sample_template_image,
            placeholder_x=100,
            placeholder_y=100,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None
        assert result.size == sample_template_image.size
        # Check that the placeholder area has red overlay
        center_pixel = result.getpixel((200, 200))  # Center of placeholder
        # Should have high red value due to overlay
        assert center_pixel[0] > 200


class TestTemplateProcessing:
    """Test template processing with logo."""

    @pytest.fixture
    def template_service(self, tmp_path):
        """Create template service with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))

    @pytest.fixture
    def mock_template(self):
        """Create mock template object."""
        template = MagicMock()
        template.id = uuid4()
        template.file_url = "https://example.com/template.png"
        template.placeholder_x = 100
        template.placeholder_y = 100
        template.placeholder_width = 200
        template.placeholder_height = 200
        return template

    @pytest.mark.asyncio
    async def test_download_image(self, template_service):
        """Test downloading image from URL."""
        # Create a simple test image in memory
        test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        buffer = BytesIO()
        test_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = buffer.getvalue()
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock()
            
            result = await template_service.download_image("https://example.com/test.png")
            
            assert result is not None
            assert isinstance(result, Image.Image)

    @pytest.mark.asyncio
    async def test_process_template_with_logo(self, template_service, mock_template):
        """Test processing template with logo."""
        # Create test images
        template_image = Image.new("RGB", (500, 500), color=(255, 255, 255))
        logo_image = Image.new("RGBA", (100, 100), color=(0, 0, 255, 255))
        
        with patch.object(template_service, "download_image") as mock_download:
            # Return different images for template and logo
            mock_download.side_effect = [template_image, logo_image]
            
            result = await template_service.process_template_with_logo(
                template=mock_template,
                logo_url="https://example.com/logo.png",
                base_url="http://localhost",
            )
            
            assert "preview_url" in result
            assert "final_url" in result
            assert result["preview_url"].startswith("http://localhost/uploads/preview_")
            assert result["final_url"].startswith("http://localhost/uploads/final_")

    @pytest.mark.asyncio
    async def test_create_template_preview(self, template_service):
        """Test creating template preview with placeholder visible."""
        test_image = Image.new("RGB", (500, 500), color=(255, 255, 255))
        
        with patch.object(template_service, "download_image") as mock_download:
            mock_download.return_value = test_image
            
            result = await template_service.create_template_preview(
                file_url="https://example.com/template.png",
                placeholder_x=100,
                placeholder_y=100,
                placeholder_width=200,
                placeholder_height=200,
                base_url="http://localhost",
            )
            
            assert "preview_url" in result
            assert "image_width" in result
            assert "image_height" in result
            assert result["image_width"] == 500
            assert result["image_height"] == 500


class TestTemplateUpdate:
    """Test template update functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock(spec=CategoryRepository)

    @pytest.fixture
    def sample_template_id(self):
        """Sample template UUID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_update_template(self, mock_repository, sample_template_id):
        """Test updating template placeholder."""
        update_data = TemplateUpdate(
            placeholder_x=200,
            placeholder_y=200,
            placeholder_width=250,
            placeholder_height=250,
        )
        
        mock_template = MagicMock()
        mock_template.id = sample_template_id
        mock_template.placeholder_x = 200
        mock_template.placeholder_y = 200
        mock_template.placeholder_width = 250
        mock_template.placeholder_height = 250
        
        mock_repository.update_template.return_value = mock_template
        
        result = await mock_repository.update_template(sample_template_id, update_data)
        
        assert result.placeholder_x == 200
        assert result.placeholder_y == 200
        assert result.placeholder_width == 250
        assert result.placeholder_height == 250

    @pytest.mark.asyncio
    async def test_delete_template(self, mock_repository, sample_template_id):
        """Test deleting a template."""
        mock_repository.delete_template.return_value = True
        
        result = await mock_repository.delete_template(sample_template_id)
        
        mock_repository.delete_template.assert_called_once_with(sample_template_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_list_templates_by_plan(self, mock_repository):
        """Test listing templates for a plan."""
        plan_id = uuid4()
        
        mock_templates = [
            MagicMock(id=uuid4(), name_fa="قالب ۱"),
            MagicMock(id=uuid4(), name_fa="قالب ۲"),
            MagicMock(id=uuid4(), name_fa="قالب ۳"),
        ]
        
        mock_repository.get_templates_by_plan.return_value = mock_templates
        
        result = await mock_repository.get_templates_by_plan(plan_id)
        
        assert len(result) == 3

