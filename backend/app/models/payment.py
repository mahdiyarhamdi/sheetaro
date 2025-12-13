"""Payment model."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import PaymentType, PaymentStatus


class Payment(Base):
    """Payment model for order payments."""
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Order relationship
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Payment details
    type = Column(ENUM(PaymentType, name='paymenttype', create_type=False), nullable=False)
    amount = Column(Numeric(12, 0), nullable=False)  # Amount in Tomans
    status = Column(ENUM(PaymentStatus, name='paymentstatus', create_type=False), nullable=False, default=PaymentStatus.PENDING)
    
    # PSP (Payment Service Provider) details
    transaction_id = Column(String(100), nullable=True, unique=True)  # From PSP
    authority = Column(String(100), nullable=True)  # PSP authority/token for redirect
    ref_id = Column(String(100), nullable=True)  # PSP reference ID after success
    card_pan = Column(String(20), nullable=True)  # Masked card number
    
    # Callback data
    callback_data = Column(String(1000), nullable=True)  # JSON string of callback response
    
    # Description
    description = Column(String(500), nullable=True)
    
    # Timestamps
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", backref="payments")
    user = relationship("User", backref="payments")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, order_id={self.order_id}, type={self.type}, amount={self.amount}, status={self.status})>"

