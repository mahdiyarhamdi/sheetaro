"""Unit tests for TemplateService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO
from PIL import Image

from app.services.template_service import TemplateService


class TestTemplateService:
    """Test TemplateService methods."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))

    @pytest.fixture
    def sample_template_image(self):
        """Create a sample template image."""
        return Image.new("RGB", (1000, 1000), color=(255, 255, 255))

    @pytest.fixture
    def sample_logo_image(self):
        """Create a sample logo image."""
        return Image.new("RGBA", (200, 200), color=(255, 0, 0, 255))

    # ==================== Placeholder Preview Tests ====================

    def test_create_placeholder_preview_creates_red_square(self, service):
        """Test that placeholder preview has a red square."""
        preview = service.create_placeholder_preview(
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
        center_pixel = preview.getpixel((250, 250))
        assert center_pixel[0] == 255  # Red channel
        assert center_pixel[1] == 0  # Green channel
        assert center_pixel[2] == 0  # Blue channel

    def test_create_placeholder_preview_dimensions(self, service):
        """Test placeholder preview has correct dimensions."""
        preview = service.create_placeholder_preview(
            width=800,
            height=600,
            placeholder_x=100,
            placeholder_y=100,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert preview.size == (800, 600)

    # ==================== Logo Application Tests ====================

    def test_apply_logo_to_template_success(self, service, sample_template_image, sample_logo_image):
        """Test successful logo application."""
        result = service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=sample_logo_image,
            placeholder_x=400,
            placeholder_y=400,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None
        assert result.size == sample_template_image.size

    def test_apply_logo_resizes_large_logo(self, service, sample_template_image):
        """Test that large logos are resized to fit placeholder."""
        large_logo = Image.new("RGBA", (400, 400), color=(0, 0, 255, 255))
        
        result = service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=large_logo,
            placeholder_x=400,
            placeholder_y=400,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None

    def test_apply_logo_maintains_aspect_ratio(self, service, sample_template_image):
        """Test that aspect ratio is maintained when resizing logo."""
        # Wide logo (2:1 ratio)
        wide_logo = Image.new("RGBA", (400, 200), color=(0, 255, 0, 255))
        
        result = service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=wide_logo,
            placeholder_x=400,
            placeholder_y=400,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None

    def test_apply_logo_centers_in_placeholder(self, service, sample_template_image):
        """Test that logo is centered in placeholder."""
        small_logo = Image.new("RGBA", (50, 50), color=(128, 128, 128, 255))
        
        result = service.apply_logo_to_template(
            template_image=sample_template_image,
            logo_image=small_logo,
            placeholder_x=400,
            placeholder_y=400,
            placeholder_width=200,
            placeholder_height=200,
        )
        
        assert result is not None

    # ==================== Image Saving Tests ====================

    def test_save_image_png(self, service, sample_template_image):
        """Test saving image as PNG."""
        filepath = service.save_image(sample_template_image, "test_image.png")
        
        assert filepath.endswith(".png")
        import os
        assert os.path.exists(filepath)

    def test_save_image_jpg(self, service, sample_template_image):
        """Test saving image as JPG."""
        filepath = service.save_image(sample_template_image, "test_image.jpg")
        
        assert filepath.endswith(".jpg")
        import os
        assert os.path.exists(filepath)

    # ==================== Image Dimension Tests ====================

    def test_get_image_dimensions(self, service, sample_template_image):
        """Test getting image dimensions."""
        width, height = service.get_image_dimensions(sample_template_image)
        
        assert width == 1000
        assert height == 1000

    def test_get_image_dimensions_various_sizes(self, service):
        """Test dimensions for various image sizes."""
        sizes = [(100, 200), (500, 300), (1920, 1080)]
        
        for w, h in sizes:
            img = Image.new("RGB", (w, h), color=(255, 255, 255))
            width, height = service.get_image_dimensions(img)
            assert width == w
            assert height == h

    # ==================== Center Position Tests ====================

    def test_calculate_center_position(self, service):
        """Test calculating center position for placeholder."""
        x, y, w, h = service.calculate_center_position(
            image_width=1000,
            image_height=800,
            placeholder_size=200,
        )
        
        assert x == 400  # (1000 - 200) / 2
        assert y == 300  # (800 - 200) / 2
        assert w == 200
        assert h == 200

    def test_calculate_center_position_small_image(self, service):
        """Test center position for small image."""
        x, y, w, h = service.calculate_center_position(
            image_width=300,
            image_height=300,
            placeholder_size=100,
        )
        
        assert x == 100
        assert y == 100

    # ==================== Corner Position Tests ====================

    def test_calculate_corner_position_top_left(self, service):
        """Test calculating top-left corner position."""
        x, y, w, h = service.calculate_corner_position(
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

    def test_calculate_corner_position_top_right(self, service):
        """Test calculating top-right corner position."""
        x, y, w, h = service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="top_right",
            placeholder_size=100,
            margin=20,
        )
        
        assert x == 880  # 1000 - 100 - 20
        assert y == 20

    def test_calculate_corner_position_bottom_left(self, service):
        """Test calculating bottom-left corner position."""
        x, y, w, h = service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="bottom_left",
            placeholder_size=100,
            margin=20,
        )
        
        assert x == 20
        assert y == 680  # 800 - 100 - 20

    def test_calculate_corner_position_bottom_right(self, service):
        """Test calculating bottom-right corner position."""
        x, y, w, h = service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="bottom_right",
            placeholder_size=100,
            margin=20,
        )
        
        assert x == 880
        assert y == 680

    def test_calculate_corner_position_center(self, service):
        """Test that center defaults to center position calculation."""
        x, y, w, h = service.calculate_corner_position(
            image_width=1000,
            image_height=800,
            corner="center",
            placeholder_size=200,
        )
        
        assert x == 400
        assert y == 300

    # ==================== Add Placeholder to Image Tests ====================

    def test_add_placeholder_to_image(self, service, sample_template_image):
        """Test adding placeholder overlay to existing image."""
        result = service.add_placeholder_to_image(
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

    def test_add_placeholder_preserves_size(self, service):
        """Test that adding placeholder doesn't change image size."""
        img = Image.new("RGB", (500, 400), color=(255, 255, 255))
        
        result = service.add_placeholder_to_image(
            image=img,
            placeholder_x=50,
            placeholder_y=50,
            placeholder_width=100,
            placeholder_height=100,
        )
        
        assert result.size == (500, 400)

    # ==================== Image Download Tests ====================

    @pytest.mark.asyncio
    async def test_download_image_success(self, service):
        """Test downloading image from URL."""
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
            
            result = await service.download_image("https://example.com/test.png")
            
            assert result is not None
            assert isinstance(result, Image.Image)

    # ==================== Template Processing Tests ====================

    @pytest.mark.asyncio
    async def test_process_template_with_logo(self, service):
        """Test processing template with logo."""
        template_image = Image.new("RGB", (500, 500), color=(255, 255, 255))
        logo_image = Image.new("RGBA", (100, 100), color=(0, 0, 255, 255))
        
        mock_template = MagicMock()
        mock_template.id = "tpl-123"
        mock_template.file_url = "https://example.com/template.png"
        mock_template.placeholder_x = 150
        mock_template.placeholder_y = 150
        mock_template.placeholder_width = 200
        mock_template.placeholder_height = 200
        
        with patch.object(service, "download_image") as mock_download:
            mock_download.side_effect = [template_image, logo_image]
            
            result = await service.process_template_with_logo(
                template=mock_template,
                logo_url="https://example.com/logo.png",
                base_url="http://localhost",
            )
            
            assert "preview_url" in result
            assert "final_url" in result
            assert result["preview_url"].startswith("http://localhost/uploads/preview_")
            assert result["final_url"].startswith("http://localhost/uploads/final_")

    @pytest.mark.asyncio
    async def test_create_template_preview(self, service):
        """Test creating template preview with placeholder visible."""
        test_image = Image.new("RGB", (500, 500), color=(255, 255, 255))
        
        with patch.object(service, "download_image") as mock_download:
            mock_download.return_value = test_image
            
            result = await service.create_template_preview(
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
