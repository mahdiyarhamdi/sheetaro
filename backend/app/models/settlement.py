"""Settlement model for print shop commission tracking."""

from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import SettlementStatus


class Settlement(Base):
    """Settlement model for tracking print shop commissions and payouts."""

    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Print shop relationship
    printshop_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)

    # Settlement period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Financial details
    total_orders = Column(Integer, nullable=False, default=0)
    total_revenue = Column(Numeric(12, 0), nullable=False, default=0)
    platform_commission = Column(Numeric(12, 0), nullable=False, default=0)  # 10%
    net_amount = Column(Numeric(12, 0), nullable=False, default=0)

    # Status
    status = Column(
        ENUM(SettlementStatus, name='settlementstatus', create_type=False),
        nullable=False,
        default=SettlementStatus.PENDING,
    )
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    printshop = relationship("User", foreign_keys=[printshop_id])

    def __repr__(self) -> str:
        return f"<Settlement(id={self.id}, printshop_id={self.printshop_id}, status={self.status})>"
