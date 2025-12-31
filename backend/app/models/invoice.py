"""Invoice model."""

from sqlalchemy import Column, String, DateTime, Numeric, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Invoice(Base):
    """Invoice model for post-purchase invoice generation."""
    
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Order relationship
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer info on invoice
    customer_name = Column(String(255), nullable=False)
    customer_code = Column(String(50), nullable=True)
    customer_address = Column(Text, nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_national_id = Column(String(20), nullable=True)
    
    # Line items (JSONB array)
    # Format: [{"description": "...", "quantity": 1, "unit_price": 100000, "total": 100000}]
    items = Column(JSONB, nullable=False, default=list)
    
    # Totals
    subtotal = Column(Numeric(12, 0), nullable=False)
    tax_amount = Column(Numeric(12, 0), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 0), default=0, nullable=False)
    total_amount = Column(Numeric(12, 0), nullable=False)
    
    # Invoice date
    issue_date = Column(Date, nullable=False)
    
    # Generated PDF
    pdf_file_url = Column(String(500), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", backref="invoices")
    user = relationship("User", backref="invoices")
    
    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number})>"



