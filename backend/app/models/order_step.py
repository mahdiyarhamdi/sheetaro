"""Order Step models for dynamic order flow."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum as PyEnum

from app.core.database import Base


class StepType(str, PyEnum):
    """Types of order steps."""
    SELECT_ATTRIBUTE = "SELECT_ATTRIBUTE"  # Select attribute option
    ENTER_VALUE = "ENTER_VALUE"  # Enter numeric/text value
    UPLOAD_FILE = "UPLOAD_FILE"  # Upload design file
    SELECT_PLAN = "SELECT_PLAN"  # Select design plan
    SELECT_TEMPLATE = "SELECT_TEMPLATE"  # Select template (public plan)
    UPLOAD_LOGO = "UPLOAD_LOGO"  # Upload logo for template
    QUESTIONNAIRE = "QUESTIONNAIRE"  # Fill questionnaire (semi-private)
    VALIDATION = "VALIDATION"  # Request validation
    PAYMENT = "PAYMENT"  # Make payment
    CONFIRMATION = "CONFIRMATION"  # Confirm order


class OrderStepTemplate(Base):
    """Template for order steps in a category."""
    
    __tablename__ = "order_step_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = Column(String(50), nullable=False)  # e.g., "select_size", "payment"
    name_fa = Column(String(100), nullable=False)  # Persian name
    step_type = Column(ENUM(StepType, name='steptype', create_type=False), nullable=False)
    
    # Configuration (JSON for flexible settings)
    config = Column(JSONB, nullable=True)
    # Example configs:
    # SELECT_ATTRIBUTE: {"attribute_slug": "size"}
    # PAYMENT: {"payment_type": "PRINT"}
    # VALIDATION: {"is_optional": true, "price": 50000}
    
    # Conditional logic (JSON)
    conditions = Column(JSONB, nullable=True)
    # Example: {"plan_slug": "public"} - only show for public plan
    
    is_required = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="step_templates")
    
    def __repr__(self) -> str:
        return f"<OrderStepTemplate(id={self.id}, slug={self.slug}, step_type={self.step_type})>"


class OrderStep(Base):
    """Actual step in an order's flow."""
    
    __tablename__ = "order_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('order_step_templates.id'), nullable=True)
    step_type = Column(ENUM(StepType, name='steptype', create_type=False), nullable=False)
    
    # Step data
    status = Column(String(50), default='pending', nullable=False)  # pending, completed, skipped
    value = Column(Text, nullable=True)  # Selected value or input
    file_url = Column(String(500), nullable=True)  # Uploaded file URL
    
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template = relationship("OrderStepTemplate")
    
    def __repr__(self) -> str:
        return f"<OrderStep(id={self.id}, order_id={self.order_id}, status={self.status})>"

