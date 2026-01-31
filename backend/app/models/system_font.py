"""System Font model for custom font management."""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class SystemFont(Base):
    """System font model for managing custom fonts."""
    
    __tablename__ = "system_fonts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Font family name (e.g., "IRANSans")
    name_fa = Column(String(100), nullable=False)  # Persian display name (e.g., "ایران سنس")
    file_url = Column(String(500), nullable=True)  # Primary font file URL (TTF/OTF/WOFF2)
    
    # Font variants (different weights and styles)
    # Format: [{"weight": 400, "style": "normal", "file_url": "..."}, {"weight": 700, "style": "normal", "file_url": "..."}]
    variants = Column(JSONB, nullable=False, default=[])
    
    # Preview settings
    sample_text = Column(String(200), nullable=True, default="نمونه متن فارسی - Sample Text 123")
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<SystemFont(id={self.id}, name={self.name})>"

