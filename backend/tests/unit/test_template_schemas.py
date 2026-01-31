"""Unit tests for Template Placeholder and System Font schemas."""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.category import (
    PlaceholderCreate,
    PlaceholderUpdate,
    PlaceholderOut,
    PlaceholderBase,
    PlaceholderReorderItem,
    PlaceholderReorderRequest,
    SystemFontCreate,
    SystemFontUpdate,
    SystemFontOut,
    SystemFontBase,
    FontVariant,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    PlaceholderPreviewData,
)
from app.models.design_template import PlaceholderType, TextAlign


class TestPlaceholderCreateSchema:
    """Test PlaceholderCreate schema validation."""
    
    def test_create_image_placeholder_minimal(self):
        """Test creating IMAGE placeholder with minimal fields."""
        data = PlaceholderCreate(
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
        )
        
        assert data.type == PlaceholderType.IMAGE
        assert data.name == "logo"
        assert data.label_fa == "لوگو"
        # Check defaults
        assert data.x == 0
        assert data.y == 0
        assert data.width == 100
        assert data.height == 100
        assert data.rotation == 0
        assert data.is_required is True
    
    def test_create_text_placeholder_full(self):
        """Test creating TEXT placeholder with all fields."""
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="company_name",
            label_fa="نام شرکت",
            x=100,
            y=200,
            width=300,
            height=50,
            rotation=90,
            is_required=False,
            sort_order=1,
            font_family="IRANSans",
            font_size=28,
            font_weight=700,
            font_color="#333333",
            text_align=TextAlign.CENTER,
            max_length=100,
            default_value="متن پیش‌فرض",
        )
        
        assert data.type == PlaceholderType.TEXT
        assert data.font_family == "IRANSans"
        assert data.font_size == 28
        assert data.font_weight == 700
        assert data.font_color == "#333333"
        assert data.text_align == TextAlign.CENTER
        assert data.max_length == 100
        assert data.default_value == "متن پیش‌فرض"
    
    def test_create_placeholder_requires_type(self):
        """Test that type is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderCreate(
                name="test",
                label_fa="تست",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "type" for e in errors)
    
    def test_create_placeholder_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderCreate(
                type=PlaceholderType.IMAGE,
                label_fa="تست",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "name" for e in errors)
    
    def test_create_placeholder_requires_label_fa(self):
        """Test that label_fa is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderCreate(
                type=PlaceholderType.IMAGE,
                name="test",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "label_fa" for e in errors)
    
    def test_create_placeholder_name_max_length(self):
        """Test name max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderCreate(
                type=PlaceholderType.IMAGE,
                name="a" * 51,  # Max is 50
                label_fa="تست",
            )
        
        errors = exc_info.value.errors()
        assert any("string_too_long" in str(e).lower() or "max_length" in str(e).lower() for e in errors)
    
    def test_create_placeholder_label_fa_max_length(self):
        """Test label_fa max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderCreate(
                type=PlaceholderType.IMAGE,
                name="test",
                label_fa="ت" * 101,  # Max is 100
            )
        
        errors = exc_info.value.errors()
        assert any("string_too_long" in str(e).lower() or "max_length" in str(e).lower() for e in errors)
    
    def test_create_placeholder_invalid_type(self):
        """Test invalid placeholder type is rejected."""
        with pytest.raises(ValidationError):
            PlaceholderCreate(
                type="INVALID_TYPE",
                name="test",
                label_fa="تست",
            )
    
    def test_create_placeholder_invalid_text_align(self):
        """Test invalid text_align is rejected."""
        with pytest.raises(ValidationError):
            PlaceholderCreate(
                type=PlaceholderType.TEXT,
                name="test",
                label_fa="تست",
                text_align="justify",  # Invalid
            )
    
    def test_create_placeholder_font_color_max_length(self):
        """Test font_color max length (9 chars for #RRGGBBAA)."""
        # Valid 9-char color with alpha
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="test",
            label_fa="تست",
            font_color="#12345678",
        )
        assert data.font_color == "#12345678"
        
        # Too long
        with pytest.raises(ValidationError):
            PlaceholderCreate(
                type=PlaceholderType.TEXT,
                name="test",
                label_fa="تست",
                font_color="#1234567890",  # 10 chars
            )


class TestPlaceholderUpdateSchema:
    """Test PlaceholderUpdate schema validation."""
    
    def test_update_placeholder_partial(self):
        """Test updating with partial fields."""
        data = PlaceholderUpdate(
            x=150,
            y=250,
        )
        
        assert data.x == 150
        assert data.y == 250
        assert data.type is None
        assert data.name is None
    
    def test_update_placeholder_text_fields(self):
        """Test updating text-specific fields."""
        data = PlaceholderUpdate(
            font_family="Vazir",
            font_size=32,
            font_weight=400,
            font_color="#FF0000",
            text_align=TextAlign.RIGHT,
        )
        
        assert data.font_family == "Vazir"
        assert data.font_size == 32
        assert data.font_color == "#FF0000"
        assert data.text_align == TextAlign.RIGHT
    
    def test_update_placeholder_empty_is_valid(self):
        """Test that empty update is valid."""
        data = PlaceholderUpdate()
        assert data.type is None
        assert data.name is None
        assert data.x is None


class TestPlaceholderOutSchema:
    """Test PlaceholderOut schema."""
    
    def test_placeholder_out_from_orm(self):
        """Test creating PlaceholderOut from attributes."""
        from datetime import datetime, timezone
        
        data = PlaceholderOut(
            id=uuid4(),
            template_id=uuid4(),
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
            x=100,
            y=100,
            width=200,
            height=200,
            rotation=0,
            is_required=True,
            sort_order=0,
            font_family=None,
            font_size=24,
            font_weight=400,
            font_color="#000000",
            text_align=TextAlign.RIGHT,
            max_length=None,
            default_value=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        assert data.id is not None
        assert data.template_id is not None
        assert data.type == PlaceholderType.IMAGE


class TestPlaceholderReorderSchema:
    """Test PlaceholderReorder schemas."""
    
    def test_reorder_item_valid(self):
        """Test valid reorder item."""
        data = PlaceholderReorderItem(
            id=uuid4(),
            sort_order=5,
        )
        assert data.sort_order == 5
    
    def test_reorder_request_with_items(self):
        """Test reorder request with multiple items."""
        items = [
            PlaceholderReorderItem(id=uuid4(), sort_order=0),
            PlaceholderReorderItem(id=uuid4(), sort_order=1),
            PlaceholderReorderItem(id=uuid4(), sort_order=2),
        ]
        
        data = PlaceholderReorderRequest(items=items)
        assert len(data.items) == 3


class TestFontVariantSchema:
    """Test FontVariant schema."""
    
    def test_font_variant_valid(self):
        """Test valid font variant."""
        data = FontVariant(
            weight=400,
            style="normal",
            file_url="/fonts/Font-Regular.ttf",
        )
        
        assert data.weight == 400
        assert data.style == "normal"
        assert data.file_url == "/fonts/Font-Regular.ttf"
    
    def test_font_variant_weight_min(self):
        """Test font weight minimum (100)."""
        data = FontVariant(
            weight=100,
            style="normal",
            file_url="/fonts/Font.ttf",
        )
        assert data.weight == 100
        
        with pytest.raises(ValidationError):
            FontVariant(
                weight=99,  # Below minimum
                style="normal",
                file_url="/fonts/Font.ttf",
            )
    
    def test_font_variant_weight_max(self):
        """Test font weight maximum (900)."""
        data = FontVariant(
            weight=900,
            style="normal",
            file_url="/fonts/Font.ttf",
        )
        assert data.weight == 900
        
        with pytest.raises(ValidationError):
            FontVariant(
                weight=901,  # Above maximum
                style="normal",
                file_url="/fonts/Font.ttf",
            )
    
    def test_font_variant_default_style(self):
        """Test default style is 'normal'."""
        data = FontVariant(
            weight=400,
            file_url="/fonts/Font.ttf",
        )
        assert data.style == "normal"


class TestSystemFontCreateSchema:
    """Test SystemFontCreate schema."""
    
    def test_create_font_minimal(self):
        """Test creating font with minimal fields."""
        data = SystemFontCreate(
            name="IRANSans",
            name_fa="ایران سنس",
        )
        
        assert data.name == "IRANSans"
        assert data.name_fa == "ایران سنس"
        assert data.variants == []
    
    def test_create_font_full(self):
        """Test creating font with all fields."""
        data = SystemFontCreate(
            name="Vazir",
            name_fa="وزیر",
            file_url="/fonts/Vazir.ttf",
            variants=[
                FontVariant(weight=400, style="normal", file_url="/fonts/Vazir-Regular.ttf"),
                FontVariant(weight=700, style="normal", file_url="/fonts/Vazir-Bold.ttf"),
            ],
            sample_text="نمونه متن سفارشی",
        )
        
        assert len(data.variants) == 2
        assert data.sample_text == "نمونه متن سفارشی"
    
    def test_create_font_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            SystemFontCreate(
                name_fa="فونت",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "name" for e in errors)
    
    def test_create_font_requires_name_fa(self):
        """Test that name_fa is required."""
        with pytest.raises(ValidationError) as exc_info:
            SystemFontCreate(
                name="Font",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "name_fa" for e in errors)
    
    def test_create_font_name_max_length(self):
        """Test name max length validation."""
        with pytest.raises(ValidationError):
            SystemFontCreate(
                name="a" * 101,  # Max is 100
                name_fa="فونت",
            )


class TestSystemFontUpdateSchema:
    """Test SystemFontUpdate schema."""
    
    def test_update_font_partial(self):
        """Test updating with partial fields."""
        data = SystemFontUpdate(
            name_fa="نام جدید",
            is_active=False,
        )
        
        assert data.name_fa == "نام جدید"
        assert data.is_active is False
        assert data.name is None
    
    def test_update_font_variants(self):
        """Test updating variants."""
        data = SystemFontUpdate(
            variants=[
                FontVariant(weight=300, style="normal", file_url="/fonts/Light.ttf"),
            ],
        )
        
        assert len(data.variants) == 1
        assert data.variants[0].weight == 300
    
    def test_update_font_empty_is_valid(self):
        """Test that empty update is valid."""
        data = SystemFontUpdate()
        assert data.name is None
        assert data.variants is None


class TestSystemFontOutSchema:
    """Test SystemFontOut schema."""
    
    def test_font_out_from_orm(self):
        """Test creating SystemFontOut from attributes."""
        from datetime import datetime, timezone
        
        data = SystemFontOut(
            id=uuid4(),
            name="TestFont",
            name_fa="فونت تست",
            file_url="/fonts/Test.ttf",
            variants=[],
            sample_text="نمونه",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        assert data.id is not None
        assert data.name == "TestFont"


class TestPlaceholderPreviewDataSchema:
    """Test PlaceholderPreviewData schema."""
    
    def test_preview_data_image(self):
        """Test preview data for image placeholder."""
        data = PlaceholderPreviewData(
            placeholder_id=uuid4(),
            image_url="https://example.com/logo.png",
        )
        
        assert data.image_url == "https://example.com/logo.png"
        assert data.text_value is None
    
    def test_preview_data_text(self):
        """Test preview data for text placeholder."""
        data = PlaceholderPreviewData(
            placeholder_id=uuid4(),
            text_value="نام شرکت",
        )
        
        assert data.text_value == "نام شرکت"
        assert data.image_url is None
    
    def test_preview_data_requires_placeholder_id(self):
        """Test that placeholder_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlaceholderPreviewData(
                image_url="https://example.com/logo.png",
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "placeholder_id" for e in errors)


class TestTemplatePreviewRequestSchema:
    """Test TemplatePreviewRequest schema."""
    
    def test_preview_request_valid(self):
        """Test valid preview request."""
        data = TemplatePreviewRequest(
            placeholders=[
                PlaceholderPreviewData(placeholder_id=uuid4(), image_url="https://example.com/logo.png"),
                PlaceholderPreviewData(placeholder_id=uuid4(), text_value="متن نمونه"),
            ]
        )
        
        assert len(data.placeholders) == 2
    
    def test_preview_request_empty_placeholders(self):
        """Test preview request with empty placeholders list."""
        data = TemplatePreviewRequest(placeholders=[])
        assert len(data.placeholders) == 0


class TestTemplatePreviewResponseSchema:
    """Test TemplatePreviewResponse schema."""
    
    def test_preview_response_valid(self):
        """Test valid preview response."""
        data = TemplatePreviewResponse(
            preview_url="https://example.com/preview.png",
            width=1000,
            height=800,
        )
        
        assert data.preview_url == "https://example.com/preview.png"
        assert data.width == 1000
        assert data.height == 800


class TestTextPlaceholderFieldsOptionalForImage:
    """Test that text-specific fields are optional for IMAGE type."""
    
    def test_image_placeholder_without_text_fields(self):
        """Test IMAGE placeholder doesn't require text fields."""
        data = PlaceholderCreate(
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        # Text fields should have defaults or be None
        assert data.font_family is None
        # font_size, font_weight, etc. have defaults
    
    def test_image_placeholder_with_text_fields_is_valid(self):
        """Test IMAGE placeholder can have text fields (though unused)."""
        data = PlaceholderCreate(
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
            font_family="SomeFont",  # Unusual but valid
            font_size=20,
        )
        
        assert data.font_family == "SomeFont"
        assert data.font_size == 20


class TestHexColorFormatValidation:
    """Test hex color format validation."""
    
    def test_hex_color_6_chars(self):
        """Test 6-character hex color (#RRGGBB)."""
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="test",
            label_fa="تست",
            font_color="#FF5500",
        )
        assert data.font_color == "#FF5500"
    
    def test_hex_color_with_alpha(self):
        """Test 8-character hex color with alpha (#RRGGBBAA)."""
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="test",
            label_fa="تست",
            font_color="#FF5500CC",
        )
        assert data.font_color == "#FF5500CC"
    
    def test_hex_color_lowercase(self):
        """Test lowercase hex color."""
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="test",
            label_fa="تست",
            font_color="#ff5500",
        )
        assert data.font_color == "#ff5500"
    
    def test_default_font_color(self):
        """Test default font color."""
        data = PlaceholderCreate(
            type=PlaceholderType.TEXT,
            name="test",
            label_fa="تست",
        )
        assert data.font_color == "#000000"

