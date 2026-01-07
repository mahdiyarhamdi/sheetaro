"""Order model."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import DesignPlan, OrderStatus, ValidationStatus


class Order(Base):
    """Order model for print orders."""
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Product relationship
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    
    # Order details
    design_plan = Column(ENUM(DesignPlan, name='designplan', create_type=False), nullable=False)
    status = Column(ENUM(OrderStatus, name='orderstatus', create_type=False), nullable=False, default=OrderStatus.PENDING, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Design file
    design_file_url = Column(String(500), nullable=True)
    
    # Validation
    validation_status = Column(ENUM(ValidationStatus, name='validationstatus', create_type=False), nullable=True)
    validation_requested = Column(Boolean, default=False, nullable=False)
    
    # Assigned staff
    assigned_designer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_validator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_printshop_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Design revisions
    revision_count = Column(Integer, default=0, nullable=False)
    max_revisions = Column(Integer, nullable=True)  # NULL means unlimited (for private plan)
    
    # Pricing
    design_price = Column(Numeric(12, 0), default=0, nullable=False)
    validation_price = Column(Numeric(12, 0), default=0, nullable=False)
    fix_price = Column(Numeric(12, 0), default=0, nullable=False)
    print_price = Column(Numeric(12, 0), default=0, nullable=False)
    total_price = Column(Numeric(12, 0), nullable=False)
    
    # Shipping
    tracking_code = Column(String(100), nullable=True)
    shipping_address = Column(Text, nullable=True)
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    printed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="orders")
    product = relationship("Product", backref="orders")
    designer = relationship("User", foreign_keys=[assigned_designer_id])
    validator = relationship("User", foreign_keys=[assigned_validator_id])
    printshop = relationship("User", foreign_keys=[assigned_printshop_id])
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"





