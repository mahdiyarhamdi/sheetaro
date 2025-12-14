"""System settings model."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SystemSettings(Base):
    """System settings key-value store for application configuration."""
    
    __tablename__ = "system_settings"
    
    key = Column(String(100), primary_key=True, index=True)
    value = Column(String(1000), nullable=False)
    
    # Audit fields
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    updater = relationship("User", backref="updated_settings")
    
    def __repr__(self) -> str:
        return f"<SystemSettings(key={self.key}, value={self.value})>"


# Predefined setting keys
class SettingKeys:
    """Predefined keys for system settings."""
    PAYMENT_CARD_NUMBER = "payment_card_number"
    PAYMENT_CARD_HOLDER = "payment_card_holder"

