"""Product model."""

from sqlalchemy import Column, String, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import ProductType, MaterialType


class Product(Base):
    """Product model for labels and invoice templates."""
    
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(ENUM(ProductType, name='producttype', create_type=False), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_fa = Column(String(255), nullable=True)  # Persian name
    description = Column(String(1000), nullable=True)
    size = Column(String(50), nullable=False)  # e.g., "5x5cm", "A5"
    material = Column(ENUM(MaterialType, name='materialtype', create_type=False), nullable=True)  # Only for labels
    base_price = Column(Numeric(12, 0), nullable=False)  # Price in Tomans (no decimals)
    min_quantity = Column(Numeric(10, 0), default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Numeric(5, 0), default=0, nullable=False)  # For display ordering
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, type={self.type})>"




