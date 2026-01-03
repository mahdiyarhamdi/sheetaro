"""Category model for dynamic product categories."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Category(Base):
    """Category model for product categories (labels, invoices, business cards, etc.)."""
    
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "label", "invoice"
    name_fa = Column(String(100), nullable=False)  # Persian name
    description_fa = Column(String(500), nullable=True)  # Persian description
    icon = Column(String(10), nullable=True)  # Emoji icon
    base_price = Column(Numeric(12, 0), default=0, nullable=False)  # Base price in Tomans
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    attributes = relationship("CategoryAttribute", back_populates="category", cascade="all, delete-orphan")
    design_plans = relationship("CategoryDesignPlan", back_populates="category", cascade="all, delete-orphan")
    step_templates = relationship("OrderStepTemplate", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, slug={self.slug}, name_fa={self.name_fa})>"

