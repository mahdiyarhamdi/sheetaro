"""Question Section model for grouping questions in questionnaires."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class QuestionSection(Base):
    """Section model for grouping questions in questionnaires."""
    
    __tablename__ = "question_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    title_fa = Column(String(200), nullable=False)  # Persian section title
    description_fa = Column(Text, nullable=True)  # Persian description shown to customers
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    plan = relationship("CategoryDesignPlan", back_populates="sections")
    questions = relationship("DesignQuestion", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<QuestionSection(id={self.id}, title_fa={self.title_fa})>"

