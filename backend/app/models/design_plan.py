"""Design Plan model for category-specific design plans."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class CategoryDesignPlan(Base):
    """Design plan model for each category (Public, Semi-Private, Private, etc.)."""
    
    __tablename__ = "category_design_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = Column(String(50), nullable=False)  # e.g., "public", "semi_private", "private"
    name_fa = Column(String(100), nullable=False)  # Persian name
    description_fa = Column(Text, nullable=True)  # Persian description
    price = Column(Numeric(12, 0), default=0, nullable=False)  # Design price in Tomans
    max_revisions = Column(Integer, nullable=True)  # NULL = unlimited
    revision_price = Column(Numeric(12, 0), default=0, nullable=False)  # Price for extra revisions
    has_questionnaire = Column(Boolean, default=False, nullable=False)  # For semi-private
    has_templates = Column(Boolean, default=False, nullable=False)  # For public (gallery)
    has_file_upload = Column(Boolean, default=False, nullable=False)  # For own design
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="design_plans")
    sections = relationship("QuestionSection", back_populates="plan", cascade="all, delete-orphan")
    questions = relationship("DesignQuestion", back_populates="plan", cascade="all, delete-orphan")
    templates = relationship("DesignTemplate", back_populates="plan", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CategoryDesignPlan(id={self.id}, slug={self.slug}, name_fa={self.name_fa})>"

