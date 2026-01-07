"""Validation report model."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ValidationReport(Base):
    """Validation report model for design/file validation."""
    
    __tablename__ = "validation_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Order relationship
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    
    # Validator relationship
    validator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Issues found (JSONB array)
    # Format: [{"type": "resolution", "severity": "high", "description": "...", "suggestion": "..."}]
    issues = Column(JSONB, nullable=False, default=list)
    
    # Fix pricing
    fix_cost = Column(Numeric(12, 0), default=0, nullable=False)  # Suggested fix cost in Tomans
    
    # Summary
    summary = Column(Text, nullable=True)
    
    # Result
    passed = Column(String(20), nullable=False, default='PENDING')  # PENDING, PASSED, FAILED
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", backref="validation_reports")
    validator = relationship("User", backref="validation_reports")
    
    def __repr__(self) -> str:
        return f"<ValidationReport(id={self.id}, order_id={self.order_id}, passed={self.passed})>"





