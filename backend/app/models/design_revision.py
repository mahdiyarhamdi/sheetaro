"""Design Revision model for tracking designer uploads and customer feedback."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import RevisionStatus


class DesignRevision(Base):
    """Tracks each design version uploaded by a designer for an order."""

    __tablename__ = "design_revisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    version = Column(Integer, nullable=False)  # 1, 2, 3 ...
    designer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    design_file_url = Column(String(500), nullable=False)

    # Customer feedback (filled when status changes to REJECTED)
    customer_feedback = Column(Text, nullable=True)

    status = Column(
        ENUM(RevisionStatus, name='revisionstatus', create_type=False),
        nullable=False,
        default=RevisionStatus.PENDING_REVIEW,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", backref="revisions")
    designer = relationship("User", foreign_keys=[designer_id])

    def __repr__(self) -> str:
        return f"<DesignRevision(id={self.id}, order_id={self.order_id}, v={self.version}, status={self.status})>"
