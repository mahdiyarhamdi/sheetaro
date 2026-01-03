"""Design Question model for questionnaire in semi-private plans."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum as PyEnum

from app.core.database import Base


class QuestionInputType(str, PyEnum):
    """Input types for questionnaire questions."""
    TEXT = "TEXT"  # Free text input
    TEXTAREA = "TEXTAREA"  # Multi-line text
    NUMBER = "NUMBER"  # Numeric input
    SINGLE_CHOICE = "SINGLE_CHOICE"  # Single selection
    MULTI_CHOICE = "MULTI_CHOICE"  # Multiple selection
    IMAGE_UPLOAD = "IMAGE_UPLOAD"  # Upload image
    FILE_UPLOAD = "FILE_UPLOAD"  # Upload any file
    COLOR_PICKER = "COLOR_PICKER"  # Color selection
    DATE_PICKER = "DATE_PICKER"  # Date selection
    SCALE = "SCALE"  # Rating scale (1-5 or 1-10)


class DesignQuestion(Base):
    """Question model for design questionnaire (semi-private plans)."""
    
    __tablename__ = "design_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey('question_sections.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Question content
    question_fa = Column(Text, nullable=False)  # Persian question text
    input_type = Column(ENUM(QuestionInputType, name='questioninputtype', create_type=False), nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    placeholder_fa = Column(String(255), nullable=True)  # Placeholder text
    help_text_fa = Column(Text, nullable=True)  # Help text
    
    # Validation rules (JSON)
    # Example: {"min_length": 2, "max_length": 100, "regex": "^[a-z]+$", "error_message_fa": "..."}
    validation_rules = Column(JSONB, default={}, nullable=False)
    
    # Conditional logic - show question based on another answer
    depends_on_question_id = Column(UUID(as_uuid=True), ForeignKey('design_questions.id', ondelete='SET NULL'), nullable=True)
    depends_on_values = Column(JSONB, default=[], nullable=False)  # ["yes", "maybe"]
    
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    plan = relationship("CategoryDesignPlan", back_populates="questions")
    section = relationship("QuestionSection", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    depends_on = relationship("DesignQuestion", remote_side=[id], foreign_keys=[depends_on_question_id])
    answers = relationship("QuestionAnswer", back_populates="question")
    
    def __repr__(self) -> str:
        return f"<DesignQuestion(id={self.id}, input_type={self.input_type})>"


class QuestionOption(Base):
    """Option model for multiple choice questions."""
    
    __tablename__ = "question_options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey('design_questions.id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(String(100), nullable=False)  # Internal value
    label_fa = Column(String(200), nullable=False)  # Persian label for display
    image_url = Column(String(500), nullable=True)  # For visual options (image choices)
    price_modifier = Column(Integer, default=0, nullable=False)  # Price adjustment for this option
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    question = relationship("DesignQuestion", back_populates="options")
    
    def __repr__(self) -> str:
        return f"<QuestionOption(id={self.id}, label_fa={self.label_fa})>"

