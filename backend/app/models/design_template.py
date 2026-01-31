"""Design Template model for public plan templates with dynamic placeholders."""

from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PlaceholderType(str, PyEnum):
    """Type of placeholder in a template."""
    IMAGE = "IMAGE"
    TEXT = "TEXT"


class TextAlign(str, PyEnum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class DesignTemplate(Base):
    """Template model for public design plans (gallery with dynamic placeholders)."""
    
    __tablename__ = "design_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    name_fa = Column(String(100), nullable=False)  # Persian name
    description_fa = Column(String(500), nullable=True)  # Persian description
    preview_url = Column(String(500), nullable=True)  # Preview image URL
    file_url = Column(String(500), nullable=True)  # Original file URL for processing
    
    # Image dimensions
    image_width = Column(Integer, nullable=True)  # Original image width
    image_height = Column(Integer, nullable=True)  # Original image height
    
    # Legacy placeholder fields (kept for backward compatibility, now use placeholders relationship)
    placeholder_x = Column(Integer, nullable=True)
    placeholder_y = Column(Integer, nullable=True)
    placeholder_width = Column(Integer, nullable=True)
    placeholder_height = Column(Integer, nullable=True)
    placeholder_rotation = Column(Integer, nullable=True, default=0)
    
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    plan = relationship("CategoryDesignPlan", back_populates="templates")
    processed_designs = relationship("ProcessedDesign", back_populates="template", cascade="all, delete-orphan")
    placeholders = relationship("TemplatePlaceholder", back_populates="template", cascade="all, delete-orphan", order_by="TemplatePlaceholder.sort_order")
    
    def __repr__(self) -> str:
        return f"<DesignTemplate(id={self.id}, name_fa={self.name_fa})>"


class TemplatePlaceholder(Base):
    """Placeholder model for template dynamic areas (image or text)."""
    
    __tablename__ = "template_placeholders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('design_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Basic info
    type = Column(Enum(PlaceholderType, name='placeholdertype', create_type=False), nullable=False)
    name = Column(String(50), nullable=False)  # Slug-like identifier (e.g., "logo", "company_name")
    label_fa = Column(String(100), nullable=False)  # Persian label for user (e.g., "لوگوی شرکت")
    
    # Position and size
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)
    width = Column(Integer, nullable=False, default=100)
    height = Column(Integer, nullable=False, default=100)
    rotation = Column(Integer, nullable=False, default=0)  # Rotation in degrees
    
    # Constraints
    is_required = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Text-specific fields (only used when type=TEXT)
    font_family = Column(String(100), nullable=True)  # Font family name
    font_size = Column(Integer, nullable=True, default=24)  # Font size in pixels
    font_weight = Column(Integer, nullable=True, default=400)  # Font weight (100-900)
    font_color = Column(String(9), nullable=True, default="#000000")  # Hex color with optional alpha
    text_align = Column(String(10), nullable=True)  # 'left', 'center', 'right'
    max_length = Column(Integer, nullable=True)  # Maximum text length
    default_value = Column(Text, nullable=True)  # Default text value
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template = relationship("DesignTemplate", back_populates="placeholders")
    
    def __repr__(self) -> str:
        return f"<TemplatePlaceholder(id={self.id}, name={self.name}, type={self.type})>"

