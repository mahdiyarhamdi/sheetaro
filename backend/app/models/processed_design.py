"""Processed Design model for customer-generated designs from templates."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ProcessedDesign(Base):
    """Model for designs generated from templates with customer logos."""
    
    __tablename__ = "processed_designs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=True, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('design_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    logo_url = Column(String(500), nullable=False)  # Customer's uploaded logo
    preview_url = Column(String(500), nullable=False)  # Generated preview with logo
    final_url = Column(String(500), nullable=False)  # Final high-res file
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    template = relationship("DesignTemplate", back_populates="processed_designs")
    
    def __repr__(self) -> str:
        return f"<ProcessedDesign(id={self.id}, template_id={self.template_id})>"

