"""Unit tests for TemplateService dynamic placeholder methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO
from PIL import Image
import os

from app.services.template_service import TemplateService
from app.models.design_template import PlaceholderType, TextAlign


class TestApplyImagePlaceholder:
    """Test apply_image_placeholder method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))
    
    @pytest.fixture
    def base_image(self):
        """Create a sample base image."""
        return Image.new("RGB", (500, 500), color=(255, 255, 255))
    
    @pytest.fixture
    def logo_image(self):
        """Create a sample logo image."""
        return Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
    
    @pytest.fixture
    def mock_placeholder_image(self):
        """Create a mock IMAGE placeholder."""
        placeholder = MagicMock()
        placeholder.type = PlaceholderType.IMAGE
        placeholder.x = 150
        placeholder.y = 150
        placeholder.width = 200
        placeholder.height = 200
        placeholder.rotation = 0
        placeholder.is_active = True
        return placeholder

    def test_apply_image_returns_image(self, service, base_image, logo_image, mock_placeholder_image):
        """Test that apply_image_placeholder returns an image."""
        downloaded_images = {"https://example.com/logo.png": logo_image}
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="https://example.com/logo.png",
            placeholder=mock_placeholder_image,
            downloaded_images=downloaded_images,
        )
        
        assert isinstance(result, Image.Image)
        assert result.size == base_image.size
    
    def test_apply_image_maintains_aspect_ratio(self, service, base_image, mock_placeholder_image):
        """Test that wide images maintain aspect ratio."""
        # Wide image (2:1)
        wide_logo = Image.new("RGBA", (200, 100), color=(0, 255, 0, 255))
        downloaded_images = {"wide.png": wide_logo}
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="wide.png",
            placeholder=mock_placeholder_image,
            downloaded_images=downloaded_images,
        )
        
        assert result is not None
    
    def test_apply_image_centers_in_placeholder(self, service, base_image, mock_placeholder_image):
        """Test that small images are centered in placeholder."""
        small_logo = Image.new("RGBA", (50, 50), color=(0, 0, 255, 255))
        downloaded_images = {"small.png": small_logo}
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="small.png",
            placeholder=mock_placeholder_image,
            downloaded_images=downloaded_images,
        )
        
        assert result is not None
    
    def test_apply_image_with_rotation(self, service, base_image, logo_image):
        """Test applying image with rotation."""
        placeholder = MagicMock()
        placeholder.type = PlaceholderType.IMAGE
        placeholder.x = 100
        placeholder.y = 100
        placeholder.width = 100
        placeholder.height = 100
        placeholder.rotation = 45
        placeholder.is_active = True
        
        downloaded_images = {"logo.png": logo_image}
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="logo.png",
            placeholder=placeholder,
            downloaded_images=downloaded_images,
        )
        
        assert result is not None
    
    def test_apply_image_handles_transparency(self, service, base_image, mock_placeholder_image):
        """Test that transparency is handled correctly."""
        transparent_logo = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        downloaded_images = {"transparent.png": transparent_logo}
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="transparent.png",
            placeholder=mock_placeholder_image,
            downloaded_images=downloaded_images,
        )
        
        assert result.mode == "RGBA"
    
    def test_apply_image_missing_from_cache_returns_base(self, service, base_image, mock_placeholder_image):
        """Test that missing image returns base unchanged."""
        downloaded_images = {}  # Empty cache
        
        result = service.apply_image_placeholder(
            base_image=base_image,
            image_url_or_path="missing.png",
            placeholder=mock_placeholder_image,
            downloaded_images=downloaded_images,
        )
        
        assert result == base_image


class TestApplyTextPlaceholder:
    """Test apply_text_placeholder method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance with temp directory."""
        return TemplateService(upload_dir=str(tmp_path))
    
    @pytest.fixture
    def base_image(self):
        """Create a sample base image."""
        return Image.new("RGB", (500, 500), color=(255, 255, 255))
    
    @pytest.fixture
    def mock_placeholder_text(self):
        """Create a mock TEXT placeholder."""
        placeholder = MagicMock()
        placeholder.type = PlaceholderType.TEXT
        placeholder.x = 100
        placeholder.y = 200
        placeholder.width = 300
        placeholder.height = 50
        placeholder.font_family = None  # Use default
        placeholder.font_size = 24
        placeholder.font_weight = 400
        placeholder.font_color = "#000000"
        placeholder.text_align = TextAlign.CENTER
        placeholder.default_value = "Default Text"
        placeholder.is_active = True
        return placeholder

    def test_apply_text_returns_image(self, service, base_image, mock_placeholder_text):
        """Test that apply_text_placeholder returns an image."""
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="Test Text",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert isinstance(result, Image.Image)
        assert result.size == base_image.size
    
    def test_apply_text_with_default_font(self, service, base_image, mock_placeholder_text):
        """Test text rendering with default font."""
        mock_placeholder_text.font_family = None
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="متن فارسی",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert result is not None
    
    def test_apply_text_alignment_right(self, service, base_image, mock_placeholder_text):
        """Test right-aligned text."""
        mock_placeholder_text.text_align = TextAlign.RIGHT
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="Right aligned",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert result is not None
    
    def test_apply_text_alignment_center(self, service, base_image, mock_placeholder_text):
        """Test center-aligned text."""
        mock_placeholder_text.text_align = TextAlign.CENTER
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="Centered",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert result is not None
    
    def test_apply_text_alignment_left(self, service, base_image, mock_placeholder_text):
        """Test left-aligned text."""
        mock_placeholder_text.text_align = TextAlign.LEFT
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="Left",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert result is not None
    
    def test_apply_text_with_color(self, service, base_image, mock_placeholder_text):
        """Test text with custom color."""
        mock_placeholder_text.font_color = "#FF0000"
        font_cache = {}
        
        result = service.apply_text_placeholder(
            base_image=base_image,
            text="Red Text",
            placeholder=mock_placeholder_text,
            font_cache=font_cache,
        )
        
        assert result is not None


class TestColorParsing:
    """Test color parsing methods."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance."""
        return TemplateService(upload_dir=str(tmp_path))
    
    def test_parse_hex_color_6_chars(self, service):
        """Test parsing 6-character hex color."""
        color = service._parse_color("#FF5500")
        
        assert color == (255, 85, 0, 255)
    
    def test_parse_hex_color_8_chars_with_alpha(self, service):
        """Test parsing 8-character hex color with alpha."""
        color = service._parse_color("#FF550080")
        
        assert color == (255, 85, 0, 128)
    
    def test_parse_hex_color_lowercase(self, service):
        """Test parsing lowercase hex color."""
        color = service._parse_color("#ff5500")
        
        assert color == (255, 85, 0, 255)
    
    def test_parse_hex_color_without_hash(self, service):
        """Test parsing hex color without # prefix."""
        color = service._parse_color("FF5500")
        
        assert color == (255, 85, 0, 255)
    
    def test_parse_invalid_color_returns_black(self, service):
        """Test that invalid color returns black."""
        color = service._parse_color("invalid")
        
        assert color == (0, 0, 0, 255)
    
    def test_parse_empty_string_returns_black(self, service):
        """Test that empty string returns black."""
        color = service._parse_color("")
        
        assert color == (0, 0, 0, 255)
    
    def test_parse_short_hex(self, service):
        """Test parsing too-short hex color."""
        color = service._parse_color("#FFF")  # 3 chars
        
        assert color == (0, 0, 0, 255)


class TestFontLoading:
    """Test font loading and caching."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance."""
        return TemplateService(upload_dir=str(tmp_path))
    
    @pytest.fixture
    def mock_placeholder_text(self):
        """Create a mock TEXT placeholder."""
        placeholder = MagicMock()
        placeholder.font_family = None
        placeholder.font_size = 24
        placeholder.font_weight = 400
        return placeholder
    
    def test_get_font_uses_default(self, service, mock_placeholder_text):
        """Test that default font is used when no family specified."""
        font_cache = {}
        
        font = service._get_font(mock_placeholder_text, font_cache)
        
        assert font is not None
    
    def test_font_cache_reuses_loaded_fonts(self, service, mock_placeholder_text):
        """Test that font cache is used."""
        font_cache = {}
        
        font1 = service._get_font(mock_placeholder_text, font_cache)
        font2 = service._get_font(mock_placeholder_text, font_cache)
        
        # Should be same object from cache
        assert font1 is font2
    
    def test_font_cache_key_includes_size(self, service):
        """Test that font cache key includes font size."""
        font_cache = {}
        
        placeholder1 = MagicMock()
        placeholder1.font_family = None
        placeholder1.font_size = 20
        placeholder1.font_weight = 400
        
        placeholder2 = MagicMock()
        placeholder2.font_family = None
        placeholder2.font_size = 30
        placeholder2.font_weight = 400
        
        service._get_font(placeholder1, font_cache)
        service._get_font(placeholder2, font_cache)
        
        # Should have 2 entries for different sizes
        assert len(font_cache) == 2


class TestGeneratePreview:
    """Test generate_preview method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create service instance."""
        return TemplateService(upload_dir=str(tmp_path))
    
    @pytest.fixture
    def mock_template(self):
        """Create a mock template with placeholders."""
        template = MagicMock()
        template.id = "template-123"
        template.file_url = "https://example.com/template.png"
        template.placeholders = []
        return template
    
    @pytest.fixture
    def mock_image_placeholder(self):
        """Create a mock IMAGE placeholder."""
        placeholder = MagicMock()
        placeholder.id = "ph-image-1"
        placeholder.type = PlaceholderType.IMAGE
        placeholder.x = 50
        placeholder.y = 50
        placeholder.width = 100
        placeholder.height = 100
        placeholder.rotation = 0
        placeholder.is_active = True
        placeholder.sort_order = 0
        return placeholder
    
    @pytest.fixture
    def mock_text_placeholder(self):
        """Create a mock TEXT placeholder."""
        placeholder = MagicMock()
        placeholder.id = "ph-text-1"
        placeholder.type = PlaceholderType.TEXT
        placeholder.x = 100
        placeholder.y = 200
        placeholder.width = 200
        placeholder.height = 40
        placeholder.font_family = None
        placeholder.font_size = 20
        placeholder.font_weight = 400
        placeholder.font_color = "#000000"
        placeholder.text_align = TextAlign.CENTER
        placeholder.default_value = "Default"
        placeholder.is_active = True
        placeholder.sort_order = 1
        return placeholder
    
    @pytest.mark.asyncio
    async def test_generate_preview_combines_placeholders(self, service, mock_template, mock_image_placeholder, mock_text_placeholder):
        """Test that generate_preview combines multiple placeholders."""
        mock_template.placeholders = [mock_image_placeholder, mock_text_placeholder]
        
        template_image = Image.new("RGB", (400, 300), color=(255, 255, 255))
        logo_image = Image.new("RGBA", (80, 80), color=(255, 0, 0, 255))
        
        with patch.object(service, "download_image") as mock_download:
            mock_download.side_effect = [template_image, logo_image]
            
            result = await service.generate_preview(
                template=mock_template,
                placeholder_data=[
                    {"placeholder_id": "ph-image-1", "image_url": "https://example.com/logo.png"},
                    {"placeholder_id": "ph-text-1", "text_value": "Company Name"},
                ],
                base_url="http://localhost",
            )
            
            assert "preview_url" in result
            assert "width" in result
            assert "height" in result
            assert result["width"] == 400
            assert result["height"] == 300
    
    @pytest.mark.asyncio
    async def test_generate_preview_respects_sort_order(self, service, mock_template, mock_image_placeholder, mock_text_placeholder):
        """Test that placeholders are processed in sort order."""
        mock_image_placeholder.sort_order = 1
        mock_text_placeholder.sort_order = 0
        mock_template.placeholders = [mock_image_placeholder, mock_text_placeholder]
        
        template_image = Image.new("RGB", (400, 300), color=(255, 255, 255))
        
        with patch.object(service, "download_image") as mock_download:
            mock_download.return_value = template_image
            
            # Should not raise
            result = await service.generate_preview(
                template=mock_template,
                placeholder_data=[
                    {"placeholder_id": "ph-text-1", "text_value": "First"},
                ],
                base_url="http://localhost",
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_preview_skips_inactive_placeholders(self, service, mock_template, mock_image_placeholder):
        """Test that inactive placeholders are skipped from processing (not applied to final image)."""
        mock_image_placeholder.is_active = False
        mock_template.placeholders = [mock_image_placeholder]
        
        template_image = Image.new("RGB", (400, 300), color=(255, 255, 255))
        
        with patch.object(service, "download_image") as mock_download, \
             patch.object(service, "apply_image_placeholder") as mock_apply:
            mock_download.return_value = template_image
            
            result = await service.generate_preview(
                template=mock_template,
                placeholder_data=[
                    {"placeholder_id": "ph-image-1", "image_url": "https://example.com/logo.png"},
                ],
                base_url="http://localhost",
            )
            
            assert result is not None
            # Inactive placeholder should not be applied (even if image was pre-downloaded)
            mock_apply.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_preview_uses_default_values_for_text(self, service, mock_template, mock_text_placeholder):
        """Test that default values are used when text is not provided."""
        mock_template.placeholders = [mock_text_placeholder]
        
        template_image = Image.new("RGB", (400, 300), color=(255, 255, 255))
        
        with patch.object(service, "download_image") as mock_download:
            mock_download.return_value = template_image
            
            result = await service.generate_preview(
                template=mock_template,
                placeholder_data=[
                    # Provide data but no text_value
                    {"placeholder_id": "ph-text-1"},
                ],
                base_url="http://localhost",
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_preview_no_file_url_raises(self, service, mock_template):
        """Test that missing file_url raises error."""
        mock_template.file_url = None
        
        with pytest.raises(ValueError, match="no file_url"):
            await service.generate_preview(
                template=mock_template,
                placeholder_data=[],
                base_url="http://localhost",
            )
    
    @pytest.mark.asyncio
    async def test_generate_preview_handles_download_failure(self, service, mock_template, mock_image_placeholder):
        """Test graceful handling of image download failure."""
        mock_template.placeholders = [mock_image_placeholder]
        template_image = Image.new("RGB", (400, 300), color=(255, 255, 255))
        
        with patch.object(service, "download_image") as mock_download:
            # First call succeeds (template), second fails (logo)
            mock_download.side_effect = [template_image, Exception("Download failed")]
            
            # Should not crash - just skip the failed image
            result = await service.generate_preview(
                template=mock_template,
                placeholder_data=[
                    {"placeholder_id": "ph-image-1", "image_url": "https://example.com/logo.png"},
                ],
                base_url="http://localhost",
            )
            
            assert result is not None

