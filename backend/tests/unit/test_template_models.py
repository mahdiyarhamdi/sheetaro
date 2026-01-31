"""Unit tests for Template Placeholder and System Font models."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.design_template import (
    DesignTemplate, 
    TemplatePlaceholder, 
    PlaceholderType, 
    TextAlign
)
from app.models.system_font import SystemFont


class TestPlaceholderTypeEnum:
    """Test PlaceholderType enum values."""
    
    def test_placeholder_type_has_image(self):
        """Test IMAGE type exists."""
        assert PlaceholderType.IMAGE == "IMAGE"
    
    def test_placeholder_type_has_text(self):
        """Test TEXT type exists."""
        assert PlaceholderType.TEXT == "TEXT"
    
    def test_placeholder_type_only_two_values(self):
        """Test only IMAGE and TEXT types exist."""
        values = [e.value for e in PlaceholderType]
        assert len(values) == 2
        assert "IMAGE" in values
        assert "TEXT" in values


class TestTextAlignEnum:
    """Test TextAlign enum values."""
    
    def test_text_align_has_left(self):
        """Test left alignment exists."""
        assert TextAlign.LEFT == "left"
    
    def test_text_align_has_center(self):
        """Test center alignment exists."""
        assert TextAlign.CENTER == "center"
    
    def test_text_align_has_right(self):
        """Test right alignment exists."""
        assert TextAlign.RIGHT == "right"
    
    def test_text_align_only_three_values(self):
        """Test only left, center, right exist."""
        values = [e.value for e in TextAlign]
        assert len(values) == 3


class TestTemplatePlaceholderModel:
    """Test TemplatePlaceholder model."""
    
    @pytest_asyncio.fixture
    async def template(self, db_session: AsyncSession):
        """Create a test template for placeholder tests."""
        from tests.conftest import create_test_category, create_test_plan_with_templates
        
        category = await create_test_category(db_session)
        plan = await create_test_plan_with_templates(db_session, category)
        
        template = DesignTemplate(
            plan_id=plan.id,
            name_fa="قالب تست",
            preview_url="https://example.com/preview.png",
            file_url="https://example.com/template.png",
            image_width=1000,
            image_height=800,
        )
        db_session.add(template)
        await db_session.flush()
        await db_session.refresh(template)
        return template
    
    @pytest.mark.asyncio
    async def test_create_image_placeholder(self, db_session: AsyncSession, template):
        """Test creating an IMAGE type placeholder."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگوی شرکت",
            x=100,
            y=100,
            width=200,
            height=200,
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        assert placeholder.id is not None
        assert placeholder.type == PlaceholderType.IMAGE
        assert placeholder.name == "logo"
        assert placeholder.label_fa == "لوگوی شرکت"
        assert placeholder.x == 100
        assert placeholder.y == 100
        assert placeholder.width == 200
        assert placeholder.height == 200
    
    @pytest.mark.asyncio
    async def test_create_text_placeholder(self, db_session: AsyncSession, template):
        """Test creating a TEXT type placeholder."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.TEXT,
            name="company_name",
            label_fa="نام شرکت",
            x=300,
            y=500,
            width=400,
            height=50,
            font_family="IRANSans",
            font_size=28,
            font_weight=700,
            font_color="#333333",
            text_align=TextAlign.CENTER,
            max_length=100,
            default_value="نام شرکت",
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        assert placeholder.id is not None
        assert placeholder.type == PlaceholderType.TEXT
        assert placeholder.font_family == "IRANSans"
        assert placeholder.font_size == 28
        assert placeholder.font_weight == 700
        assert placeholder.font_color == "#333333"
        assert placeholder.text_align == TextAlign.CENTER
        assert placeholder.max_length == 100
        assert placeholder.default_value == "نام شرکت"
    
    @pytest.mark.asyncio
    async def test_placeholder_default_values(self, db_session: AsyncSession, template):
        """Test that placeholder has correct default values."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.IMAGE,
            name="test",
            label_fa="تست",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        assert placeholder.rotation == 0
        assert placeholder.is_required is True
        assert placeholder.sort_order == 0
        assert placeholder.is_active is True
        # Text-specific defaults for non-text placeholder
        assert placeholder.font_color == "#000000"
        assert placeholder.text_align == TextAlign.RIGHT
    
    @pytest.mark.asyncio
    async def test_placeholder_relationship_to_template(self, db_session: AsyncSession, template):
        """Test placeholder -> template relationship."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        # Load the relationship
        await db_session.refresh(placeholder, attribute_names=["template"])
        
        assert placeholder.template is not None
        assert placeholder.template.id == template.id
        assert placeholder.template.name_fa == "قالب تست"
    
    @pytest.mark.asyncio
    async def test_template_to_placeholders_relationship(self, db_session: AsyncSession, template):
        """Test template -> placeholders relationship."""
        # Create multiple placeholders
        for i in range(3):
            placeholder = TemplatePlaceholder(
                template_id=template.id,
                type=PlaceholderType.IMAGE if i == 0 else PlaceholderType.TEXT,
                name=f"placeholder_{i}",
                label_fa=f"جایگاه {i}",
                x=i * 100,
                y=i * 100,
                width=100,
                height=100,
                sort_order=i,
            )
            db_session.add(placeholder)
        
        await db_session.flush()
        await db_session.refresh(template, attribute_names=["placeholders"])
        
        assert len(template.placeholders) == 3
        # Should be ordered by sort_order
        assert template.placeholders[0].name == "placeholder_0"
        assert template.placeholders[1].name == "placeholder_1"
        assert template.placeholders[2].name == "placeholder_2"
    
    @pytest.mark.asyncio
    async def test_placeholder_cascade_delete_with_template(self, db_session: AsyncSession, template):
        """Test that placeholders are deleted when template is deleted."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.IMAGE,
            name="logo",
            label_fa="لوگو",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        db_session.add(placeholder)
        await db_session.flush()
        
        placeholder_id = placeholder.id
        template_id = template.id
        
        # Delete template
        await db_session.delete(template)
        await db_session.flush()
        
        # Verify placeholder is also deleted
        result = await db_session.execute(
            select(TemplatePlaceholder).where(TemplatePlaceholder.id == placeholder_id)
        )
        deleted_placeholder = result.scalar_one_or_none()
        assert deleted_placeholder is None
    
    @pytest.mark.asyncio
    async def test_placeholder_rotation(self, db_session: AsyncSession, template):
        """Test placeholder rotation value."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.IMAGE,
            name="rotated_logo",
            label_fa="لوگوی چرخیده",
            x=100,
            y=100,
            width=200,
            height=200,
            rotation=45,
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        assert placeholder.rotation == 45
    
    @pytest.mark.asyncio
    async def test_placeholder_repr(self, db_session: AsyncSession, template):
        """Test placeholder string representation."""
        placeholder = TemplatePlaceholder(
            template_id=template.id,
            type=PlaceholderType.TEXT,
            name="test_repr",
            label_fa="تست",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        db_session.add(placeholder)
        await db_session.flush()
        await db_session.refresh(placeholder)
        
        repr_str = repr(placeholder)
        assert "TemplatePlaceholder" in repr_str
        assert "test_repr" in repr_str
        assert "TEXT" in repr_str


class TestSystemFontModel:
    """Test SystemFont model."""
    
    @pytest.mark.asyncio
    async def test_create_system_font(self, db_session: AsyncSession):
        """Test creating a system font."""
        font = SystemFont(
            name="IRANSans",
            name_fa="ایران سنس",
            file_url="/fonts/IRANSans.ttf",
            variants=[
                {"weight": 400, "style": "normal", "file_url": "/fonts/IRANSans-Regular.ttf"},
                {"weight": 700, "style": "normal", "file_url": "/fonts/IRANSans-Bold.ttf"},
            ],
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        assert font.id is not None
        assert font.name == "IRANSans"
        assert font.name_fa == "ایران سنس"
        assert font.file_url == "/fonts/IRANSans.ttf"
    
    @pytest.mark.asyncio
    async def test_font_variants_jsonb(self, db_session: AsyncSession):
        """Test that variants are stored as JSONB correctly."""
        variants = [
            {"weight": 100, "style": "normal", "file_url": "/fonts/Font-Thin.ttf"},
            {"weight": 400, "style": "normal", "file_url": "/fonts/Font-Regular.ttf"},
            {"weight": 400, "style": "italic", "file_url": "/fonts/Font-Italic.ttf"},
            {"weight": 700, "style": "normal", "file_url": "/fonts/Font-Bold.ttf"},
            {"weight": 900, "style": "normal", "file_url": "/fonts/Font-Black.ttf"},
        ]
        
        font = SystemFont(
            name="TestFont",
            name_fa="فونت تست",
            file_url="/fonts/TestFont.ttf",
            variants=variants,
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        assert len(font.variants) == 5
        assert font.variants[0]["weight"] == 100
        assert font.variants[1]["style"] == "normal"
        assert font.variants[2]["style"] == "italic"
    
    @pytest.mark.asyncio
    async def test_font_default_values(self, db_session: AsyncSession):
        """Test font default values."""
        font = SystemFont(
            name="DefaultTest",
            name_fa="تست پیش‌فرض",
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        assert font.is_active is True
        assert font.variants == []
        assert font.sample_text == "نمونه متن فارسی - Sample Text 123"
    
    @pytest.mark.asyncio
    async def test_font_unique_name(self, db_session: AsyncSession):
        """Test that font name must be unique."""
        font1 = SystemFont(
            name="UniqueFont",
            name_fa="فونت یکتا",
        )
        db_session.add(font1)
        await db_session.flush()
        
        font2 = SystemFont(
            name="UniqueFont",  # Same name
            name_fa="فونت دیگر",
        )
        db_session.add(font2)
        
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            await db_session.flush()
    
    @pytest.mark.asyncio
    async def test_font_sample_text(self, db_session: AsyncSession):
        """Test custom sample text."""
        font = SystemFont(
            name="CustomSample",
            name_fa="نمونه سفارشی",
            sample_text="متن نمونه سفارشی ۱۲۳۴",
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        assert font.sample_text == "متن نمونه سفارشی ۱۲۳۴"
    
    @pytest.mark.asyncio
    async def test_font_repr(self, db_session: AsyncSession):
        """Test font string representation."""
        font = SystemFont(
            name="ReprTest",
            name_fa="تست نمایش",
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        repr_str = repr(font)
        assert "SystemFont" in repr_str
        assert "ReprTest" in repr_str
    
    @pytest.mark.asyncio
    async def test_font_timestamps(self, db_session: AsyncSession):
        """Test that created_at and updated_at are set."""
        font = SystemFont(
            name="TimestampTest",
            name_fa="تست زمان",
        )
        db_session.add(font)
        await db_session.flush()
        await db_session.refresh(font)
        
        assert font.created_at is not None
        assert font.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_font_active_toggle(self, db_session: AsyncSession):
        """Test toggling font active status."""
        font = SystemFont(
            name="ToggleTest",
            name_fa="تست تغییر",
            is_active=True,
        )
        db_session.add(font)
        await db_session.flush()
        
        assert font.is_active is True
        
        font.is_active = False
        await db_session.flush()
        await db_session.refresh(font)
        
        assert font.is_active is False

