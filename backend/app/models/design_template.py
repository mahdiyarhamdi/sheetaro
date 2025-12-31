"""Design Template model for public plan templates with logo placeholder."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class DesignTemplate(Base):
    """Template model for public design plans (gallery with logo placeholder)."""
    
    __tablename__ = "design_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    name_fa = Column(String(100), nullable=False)  # Persian name
    description_fa = Column(String(500), nullable=True)  # Persian description
    preview_url = Column(String(500), nullable=False)  # Preview image URL (with red placeholder)
    file_url = Column(String(500), nullable=False)  # Original file URL for processing
    
    # Placeholder position (red square for logo)
    placeholder_x = Column(Integer, nullable=False)  # X position from top-left
    placeholder_y = Column(Integer, nullable=False)  # Y position from top-left
    placeholder_width = Column(Integer, nullable=False)  # Width of placeholder
    placeholder_height = Column(Integer, nullable=False)  # Height of placeholder
    
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    plan = relationship("CategoryDesignPlan", back_populates="templates")
    
    def __repr__(self) -> str:
        return f"<DesignTemplate(id={self.id}, name_fa={self.name_fa})>"

