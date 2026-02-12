"""PrintShopProfile model for printshop-specific data."""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PrintShopProfile(Base):
    """Profile data specific to print shop users (capabilities, description, etc.)."""

    __tablename__ = "printshop_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # One profile per user
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True, index=True)

    # Profile content
    description = Column(Text, nullable=True)
    capabilities = Column(JSONB, nullable=False, default=[])
    max_daily_capacity = Column(Integer, nullable=True)
    service_areas = Column(JSONB, nullable=False, default=[])

    # Admin flags
    is_featured = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ORM relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<PrintShopProfile(id={self.id}, user_id={self.user_id})>"
