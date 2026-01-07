"""Subscription model."""

from sqlalchemy import Column, DateTime, Numeric, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import SubscriptionPlan


class Subscription(Base):
    """Subscription model for premium features."""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Subscription details
    plan = Column(ENUM(SubscriptionPlan, name='subscriptionplan', create_type=False), nullable=False)
    price = Column(Numeric(12, 0), nullable=False)  # Price in Tomans
    
    # Duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Payment reference
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="subscriptions")
    payment = relationship("Payment", backref="subscription")
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, is_active={self.is_active})>"





