"""Review model for customer order reviews and ratings."""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Review(Base):
    """Review model for customer ratings and feedback on orders."""

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Relationships
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    printshop_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)

    # Review content
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)

    # Moderation
    is_approved = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ORM relationships
    order = relationship("Order", foreign_keys=[order_id])
    user = relationship("User", foreign_keys=[user_id])
    printshop = relationship("User", foreign_keys=[printshop_id])

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, order_id={self.order_id}, rating={self.rating})>"
