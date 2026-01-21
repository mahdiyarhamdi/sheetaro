"""User model."""

from sqlalchemy import Column, String, BigInteger, Boolean, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    """User model supporting both Telegram and Web registration."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Telegram fields
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    username = Column(String(255), nullable=True)
    
    # Web auth fields
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)  # For web users
    phone_verified = Column(Boolean, default=False, nullable=False)
    web_linked = Column(Boolean, default=False, nullable=False)  # True if web account linked to telegram
    
    # Profile fields
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    full_name = Column(String(511), nullable=True)  # Computed or set on update
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    
    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, phone={self.phone_number}, role={self.role})>"
