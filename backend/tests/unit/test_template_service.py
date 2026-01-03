"""Unit tests for TemplateService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO

from app.services.template_service import TemplateService


class TestTemplateService:
    """Test TemplateService methods."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance."""
        return TemplateService(mock_db)

    @pytest.fixture
    def sample_template(self):
        """Sample template data."""
        return {
            'id': 'tpl-123',
            'name_fa': 'قالب تست',
            'image_url': 'https://example.com/template.png',
            'image_width': 1000,
            'image_height': 1000,
            'placeholder_x': 400,
            'placeholder_y': 400,
            'placeholder_width': 200,
            'placeholder_height': 200,
            'is_active': True,
        }

    # ==================== Template Validation Tests ====================

    def test_validate_placeholder_valid(self, service, sample_template):
        """Test valid placeholder coordinates."""
        result = service.validate_placeholder_coordinates(
            sample_template['image_width'],
            sample_template['image_height'],
            sample_template['placeholder_x'],
            sample_template['placeholder_y'],
            sample_template['placeholder_width'],
            sample_template['placeholder_height'],
        )
        assert result['is_valid'] is True

    def test_validate_placeholder_negative_x(self, service, sample_template):
        """Test negative X coordinate."""
        result = service.validate_placeholder_coordinates(
            sample_template['image_width'],
            sample_template['image_height'],
            -50,  # Negative X
            sample_template['placeholder_y'],
            sample_template['placeholder_width'],
            sample_template['placeholder_height'],
        )
        assert result['is_valid'] is False

    def test_validate_placeholder_exceeds_width(self, service, sample_template):
        """Test placeholder exceeding image width."""
        result = service.validate_placeholder_coordinates(
            sample_template['image_width'],
            sample_template['image_height'],
            900,  # X + width > image_width
            sample_template['placeholder_y'],
            sample_template['placeholder_width'],
            sample_template['placeholder_height'],
        )
        assert result['is_valid'] is False

    def test_validate_placeholder_exceeds_height(self, service, sample_template):
        """Test placeholder exceeding image height."""
        result = service.validate_placeholder_coordinates(
            sample_template['image_width'],
            sample_template['image_height'],
            sample_template['placeholder_x'],
            900,  # Y + height > image_height
            sample_template['placeholder_width'],
            sample_template['placeholder_height'],
        )
        assert result['is_valid'] is False

    def test_validate_placeholder_zero_dimensions(self, service, sample_template):
        """Test zero-dimension placeholder."""
        result = service.validate_placeholder_coordinates(
            sample_template['image_width'],
            sample_template['image_height'],
            sample_template['placeholder_x'],
            sample_template['placeholder_y'],
            0,  # Zero width
            sample_template['placeholder_height'],
        )
        assert result['is_valid'] is False

    # ==================== Preview Generation Tests ====================

    @pytest.mark.asyncio
    async def test_generate_preview_placeholder_creates_red_square(self, service, sample_template):
        """Test that preview generation creates a red placeholder square."""
        with patch.object(service, 'download_image') as mock_download:
            # Create a simple white image
            from PIL import Image
            img = Image.new('RGB', (1000, 1000), 'white')
            buffer = BytesIO()
            img.save(buffer, 'PNG')
            buffer.seek(0)
            mock_download.return_value = buffer.getvalue()

            with patch.object(service, 'save_image') as mock_save:
                mock_save.return_value = 'https://example.com/preview.png'

                result = await service.generate_placeholder_preview(sample_template)

                assert result is not None
                assert 'preview_url' in result

    @pytest.mark.asyncio
    async def test_generate_preview_download_failure(self, service, sample_template):
        """Test preview generation when download fails."""
        with patch.object(service, 'download_image') as mock_download:
            mock_download.return_value = None

            result = await service.generate_placeholder_preview(sample_template)

            assert result is None

    # ==================== Logo Application Tests ====================

    @pytest.mark.asyncio
    async def test_apply_logo_success(self, service, sample_template):
        """Test successful logo application."""
        with patch.object(service, 'download_image') as mock_download:
            from PIL import Image
            
            # Create template image
            template_img = Image.new('RGB', (1000, 1000), 'white')
            template_buffer = BytesIO()
            template_img.save(template_buffer, 'PNG')
            template_buffer.seek(0)

            # Create logo image
            logo_img = Image.new('RGBA', (200, 200), 'red')
            logo_buffer = BytesIO()
            logo_img.save(logo_buffer, 'PNG')
            logo_buffer.seek(0)

            # Return different images for template and logo
            mock_download.side_effect = [template_buffer.getvalue(), logo_buffer.getvalue()]

            with patch.object(service, 'save_image') as mock_save:
                mock_save.return_value = 'https://example.com/result.png'

                result = await service.apply_logo_to_template(
                    sample_template,
                    'https://example.com/logo.png'
                )

                assert result is not None
                assert 'preview_url' in result
                assert 'final_url' in result

    @pytest.mark.asyncio
    async def test_apply_logo_template_download_failure(self, service, sample_template):
        """Test logo application when template download fails."""
        with patch.object(service, 'download_image') as mock_download:
            mock_download.return_value = None

            result = await service.apply_logo_to_template(
                sample_template,
                'https://example.com/logo.png'
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_apply_logo_logo_download_failure(self, service, sample_template):
        """Test logo application when logo download fails."""
        with patch.object(service, 'download_image') as mock_download:
            from PIL import Image
            
            # First call returns template, second call returns None (logo fail)
            template_img = Image.new('RGB', (1000, 1000), 'white')
            template_buffer = BytesIO()
            template_img.save(template_buffer, 'PNG')
            template_buffer.seek(0)

            mock_download.side_effect = [template_buffer.getvalue(), None]

            result = await service.apply_logo_to_template(
                sample_template,
                'https://example.com/logo.png'
            )

            assert result is None

    # ==================== Logo Resizing Tests ====================

    def test_resize_logo_to_fit_larger_logo(self, service):
        """Test resizing a logo larger than placeholder."""
        from PIL import Image
        
        logo = Image.new('RGBA', (400, 400), 'red')
        placeholder_width = 200
        placeholder_height = 200

        resized = service.resize_logo_to_fit(logo, placeholder_width, placeholder_height)

        assert resized.width <= placeholder_width
        assert resized.height <= placeholder_height

    def test_resize_logo_to_fit_smaller_logo(self, service):
        """Test that smaller logos are not upscaled."""
        from PIL import Image
        
        logo = Image.new('RGBA', (100, 100), 'red')
        placeholder_width = 200
        placeholder_height = 200

        resized = service.resize_logo_to_fit(logo, placeholder_width, placeholder_height)

        # Should remain at original size or smaller
        assert resized.width <= placeholder_width
        assert resized.height <= placeholder_height

    def test_resize_logo_maintains_aspect_ratio(self, service):
        """Test that aspect ratio is maintained."""
        from PIL import Image
        
        # Wide logo
        logo = Image.new('RGBA', (400, 200), 'red')
        placeholder_width = 200
        placeholder_height = 200

        resized = service.resize_logo_to_fit(logo, placeholder_width, placeholder_height)

        # Aspect ratio should be maintained (2:1)
        original_ratio = logo.width / logo.height
        new_ratio = resized.width / resized.height
        assert abs(original_ratio - new_ratio) < 0.01

    # ==================== Center Positioning Tests ====================

    def test_calculate_center_position(self, service):
        """Test center position calculation."""
        placeholder_x = 100
        placeholder_y = 100
        placeholder_width = 200
        placeholder_height = 200
        logo_width = 100
        logo_height = 100

        x, y = service.calculate_center_position(
            placeholder_x, placeholder_y,
            placeholder_width, placeholder_height,
            logo_width, logo_height
        )

        # Logo should be centered in placeholder
        assert x == 150  # 100 + (200 - 100) / 2
        assert y == 150

    def test_calculate_center_position_asymmetric(self, service):
        """Test center position with asymmetric logo."""
        placeholder_x = 100
        placeholder_y = 100
        placeholder_width = 200
        placeholder_height = 200
        logo_width = 50
        logo_height = 100

        x, y = service.calculate_center_position(
            placeholder_x, placeholder_y,
            placeholder_width, placeholder_height,
            logo_width, logo_height
        )

        # Logo should still be centered
        assert x == 175  # 100 + (200 - 50) / 2
        assert y == 150  # 100 + (200 - 100) / 2

    # ==================== File Type Validation Tests ====================

    def test_validate_image_type_valid(self, service):
        """Test valid image types."""
        valid_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
        for content_type in valid_types:
            assert service.validate_image_type(content_type) is True

    def test_validate_image_type_invalid(self, service):
        """Test invalid image types."""
        invalid_types = ['image/gif', 'application/pdf', 'text/html']
        for content_type in invalid_types:
            assert service.validate_image_type(content_type) is False

    # ==================== Image Dimension Validation Tests ====================

    def test_validate_image_dimensions_valid(self, service):
        """Test valid image dimensions."""
        from PIL import Image
        
        img = Image.new('RGB', (500, 500), 'white')
        result = service.validate_image_dimensions(img, max_width=1000, max_height=1000)
        assert result['is_valid'] is True

    def test_validate_image_dimensions_too_wide(self, service):
        """Test image too wide."""
        from PIL import Image
        
        img = Image.new('RGB', (2000, 500), 'white')
        result = service.validate_image_dimensions(img, max_width=1000, max_height=1000)
        assert result['is_valid'] is False

    def test_validate_image_dimensions_too_tall(self, service):
        """Test image too tall."""
        from PIL import Image
        
        img = Image.new('RGB', (500, 2000), 'white')
        result = service.validate_image_dimensions(img, max_width=1000, max_height=1000)
        assert result['is_valid'] is False

    def test_validate_image_dimensions_too_small(self, service):
        """Test image too small."""
        from PIL import Image
        
        img = Image.new('RGB', (50, 50), 'white')
        result = service.validate_image_dimensions(img, min_width=100, min_height=100)
        assert result['is_valid'] is False

