"""Attribute models for dynamic category attributes."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum as PyEnum

from app.core.database import Base


class AttributeInputType(str, PyEnum):
    """Input types for attributes."""
    SELECT = "SELECT"  # Single selection from options
    MULTI_SELECT = "MULTI_SELECT"  # Multiple selection from options
    NUMBER = "NUMBER"  # Numeric input (e.g., quantity)
    TEXT = "TEXT"  # Free text input
    

class CategoryAttribute(Base):
    """Attribute model for category-specific attributes (size, material, quantity, etc.)."""
    
    __tablename__ = "category_attributes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = Column(String(50), nullable=False)  # e.g., "size", "material"
    name_fa = Column(String(100), nullable=False)  # Persian name
    input_type = Column(ENUM(AttributeInputType, name='attributeinputtype', create_type=False), nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    min_value = Column(Integer, nullable=True)  # For NUMBER type
    max_value = Column(Integer, nullable=True)  # For NUMBER type
    default_value = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="attributes")
    options = relationship("AttributeOption", back_populates="attribute", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CategoryAttribute(id={self.id}, slug={self.slug}, name_fa={self.name_fa})>"


class AttributeOption(Base):
    """Option model for attribute choices (5x5, 10x10, Paper, PVC, etc.)."""
    
    __tablename__ = "attribute_options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey('category_attributes.id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(String(100), nullable=False)  # Internal value
    label_fa = Column(String(100), nullable=False)  # Persian label for display
    price_modifier = Column(Numeric(12, 0), default=0, nullable=False)  # Price adjustment in Tomans
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    attribute = relationship("CategoryAttribute", back_populates="options")
    
    def __repr__(self) -> str:
        return f"<AttributeOption(id={self.id}, value={self.value}, label_fa={self.label_fa})>"

