"""Question Answer model for storing questionnaire responses."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class QuestionAnswer(Base):
    """Answer model for questionnaire questions in orders."""
    
    __tablename__ = "question_answers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey('design_questions.id'), nullable=False, index=True)
    
    # Answer data (one of these will be filled based on question type)
    answer_text = Column(Text, nullable=True)  # For TEXT, SINGLE_CHOICE, COLOR_PICKER
    answer_values = Column(ARRAY(String), nullable=True)  # For MULTI_CHOICE
    answer_file_url = Column(String(500), nullable=True)  # For IMAGE_UPLOAD
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    question = relationship("DesignQuestion", back_populates="answers")
    
    def __repr__(self) -> str:
        return f"<QuestionAnswer(id={self.id}, order_id={self.order_id}, question_id={self.question_id})>"

