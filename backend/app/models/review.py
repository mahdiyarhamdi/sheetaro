"""Review model for customer order reviews and ratings."""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import ReviewType


class Review(Base):
    """Review model for customer ratings and feedback on orders."""

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Relationships
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    printshop_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    designer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)

    # Review type (PRINTSHOP or DESIGNER)
    review_type = Column(
        ENUM(ReviewType, name='reviewtype', create_type=False),
        nullable=False,
        default=ReviewType.PRINTSHOP,
        server_default="PRINTSHOP",
    )

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
    designer = relationship("User", foreign_keys=[designer_id])

    # One printshop review + one designer review per order
    __table_args__ = (
        UniqueConstraint('order_id', 'review_type', name='uq_review_order_type'),
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, order_id={self.order_id}, type={self.review_type}, rating={self.rating})>"
