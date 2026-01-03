"""Category schemas for API requests/responses."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.attribute import AttributeInputType
from app.models.design_question import QuestionInputType
from app.models.order_step import StepType


# ============== Category Schemas ==============

class CategoryBase(BaseModel):
    """Base category schema."""
    slug: str = Field(..., max_length=50)
    name_fa: str = Field(..., max_length=100)
    description_fa: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=10)
    base_price: int = 0  # Base price in Tomans
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    slug: Optional[str] = Field(None, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=100)
    description_fa: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=10)
    base_price: Optional[int] = None  # Base price in Tomans
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryOut(CategoryBase):
    """Schema for category response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryWithDetails(CategoryOut):
    """Category with attributes, plans, and steps."""
    attributes: List["AttributeOut"] = []
    design_plans: List["DesignPlanOut"] = []
    step_templates: List["StepTemplateOut"] = []


# ============== Attribute Schemas ==============

class AttributeOptionBase(BaseModel):
    """Base attribute option schema."""
    value: str = Field(..., max_length=100)
    label_fa: str = Field(..., max_length=100)
    price_modifier: int = 0
    sort_order: int = 0
    is_active: bool = True


class AttributeOptionCreate(AttributeOptionBase):
    """Schema for creating an attribute option."""
    pass


class AttributeOptionUpdate(BaseModel):
    """Schema for updating an attribute option."""
    value: Optional[str] = Field(None, max_length=100)
    label_fa: Optional[str] = Field(None, max_length=100)
    price_modifier: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class AttributeOptionOut(AttributeOptionBase):
    """Schema for attribute option response."""
    id: UUID
    attribute_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttributeBase(BaseModel):
    """Base attribute schema."""
    slug: str = Field(..., max_length=50)
    name_fa: str = Field(..., max_length=100)
    input_type: AttributeInputType
    is_required: bool = True
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default_value: Optional[str] = Field(None, max_length=255)
    sort_order: int = 0
    is_active: bool = True


class AttributeCreate(AttributeBase):
    """Schema for creating an attribute."""
    pass


class AttributeUpdate(BaseModel):
    """Schema for updating an attribute."""
    slug: Optional[str] = Field(None, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=100)
    input_type: Optional[AttributeInputType] = None
    is_required: Optional[bool] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default_value: Optional[str] = Field(None, max_length=255)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class AttributeOut(AttributeBase):
    """Schema for attribute response."""
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AttributeWithOptions(AttributeOut):
    """Attribute with its options."""
    options: List[AttributeOptionOut] = []


# ============== Design Plan Schemas ==============

class DesignPlanBase(BaseModel):
    """Base design plan schema."""
    slug: str = Field(..., max_length=50)
    name_fa: str = Field(..., max_length=100)
    description_fa: Optional[str] = None
    price: int = 0
    max_revisions: Optional[int] = None
    revision_price: int = 0
    has_questionnaire: bool = False
    has_templates: bool = False
    has_file_upload: bool = False
    sort_order: int = 0
    is_active: bool = True


class DesignPlanCreate(DesignPlanBase):
    """Schema for creating a design plan."""
    pass


class DesignPlanUpdate(BaseModel):
    """Schema for updating a design plan."""
    slug: Optional[str] = Field(None, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=100)
    description_fa: Optional[str] = None
    price: Optional[int] = None
    max_revisions: Optional[int] = None
    revision_price: Optional[int] = None
    has_questionnaire: Optional[bool] = None
    has_templates: Optional[bool] = None
    has_file_upload: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class DesignPlanOut(DesignPlanBase):
    """Schema for design plan response."""
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DesignPlanWithDetails(DesignPlanOut):
    """Design plan with sections, questions and templates."""
    sections: List["SectionOut"] = []
    questions: List["QuestionOut"] = []
    templates: List["TemplateOut"] = []


# ============== Question Section Schemas ==============

class SectionBase(BaseModel):
    """Base section schema for grouping questions."""
    title_fa: str = Field(..., max_length=200)
    description_fa: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class SectionCreate(SectionBase):
    """Schema for creating a section."""
    pass


class SectionUpdate(BaseModel):
    """Schema for updating a section."""
    title_fa: Optional[str] = Field(None, max_length=200)
    description_fa: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SectionOut(SectionBase):
    """Schema for section response."""
    id: UUID
    plan_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SectionWithQuestions(SectionOut):
    """Section with its questions."""
    questions: List["QuestionWithOptions"] = []


class SectionReorderItem(BaseModel):
    """Item for reordering sections."""
    id: UUID
    sort_order: int


class SectionReorderRequest(BaseModel):
    """Request to reorder sections."""
    items: List[SectionReorderItem]


# ============== Question Schemas ==============

class QuestionOptionBase(BaseModel):
    """Base question option schema."""
    value: str = Field(..., max_length=100)
    label_fa: str = Field(..., max_length=200)
    image_url: Optional[str] = Field(None, max_length=500)  # For visual options
    price_modifier: int = 0  # Price adjustment
    sort_order: int = 0
    is_active: bool = True


class QuestionOptionCreate(QuestionOptionBase):
    """Schema for creating a question option."""
    pass


class QuestionOptionUpdate(BaseModel):
    """Schema for updating a question option."""
    value: Optional[str] = Field(None, max_length=100)
    label_fa: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = Field(None, max_length=500)
    price_modifier: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class QuestionOptionOut(QuestionOptionBase):
    """Schema for question option response."""
    id: UUID
    question_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ValidationRules(BaseModel):
    """Validation rules for question answers."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    regex: Optional[str] = None
    error_message_fa: Optional[str] = None
    max_size_mb: Optional[int] = None  # For file uploads
    allowed_types: Optional[List[str]] = None  # ["jpg", "png", "pdf"]


class QuestionBase(BaseModel):
    """Base question schema."""
    question_fa: str
    input_type: QuestionInputType
    is_required: bool = True
    placeholder_fa: Optional[str] = Field(None, max_length=255)
    help_text_fa: Optional[str] = None
    validation_rules: Optional[ValidationRules] = None
    sort_order: int = 0
    is_active: bool = True


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    section_id: Optional[UUID] = None  # Optional section assignment
    depends_on_question_id: Optional[UUID] = None  # Conditional logic
    depends_on_values: Optional[List[str]] = None  # Show if answer is one of these
    options: Optional[List[QuestionOptionCreate]] = None


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""
    section_id: Optional[UUID] = None
    question_fa: Optional[str] = None
    input_type: Optional[QuestionInputType] = None
    is_required: Optional[bool] = None
    placeholder_fa: Optional[str] = Field(None, max_length=255)
    help_text_fa: Optional[str] = None
    validation_rules: Optional[ValidationRules] = None
    depends_on_question_id: Optional[UUID] = None
    depends_on_values: Optional[List[str]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class QuestionOut(QuestionBase):
    """Schema for question response."""
    id: UUID
    plan_id: UUID
    section_id: Optional[UUID] = None
    depends_on_question_id: Optional[UUID] = None
    depends_on_values: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QuestionWithOptions(QuestionOut):
    """Question with its options."""
    options: List[QuestionOptionOut] = []


class QuestionReorderItem(BaseModel):
    """Item for reordering questions."""
    id: UUID
    sort_order: int


class QuestionReorderRequest(BaseModel):
    """Request to reorder questions."""
    items: List[QuestionReorderItem]


class ValidateAnswerRequest(BaseModel):
    """Request to validate a single answer."""
    answer_text: Optional[str] = None
    answer_values: Optional[List[str]] = None
    answer_file_url: Optional[str] = None


class ValidateAnswerResponse(BaseModel):
    """Response for answer validation."""
    is_valid: bool
    error_message: Optional[str] = None


# ============== Template Schemas ==============

class TemplateBase(BaseModel):
    """Base template schema."""
    name_fa: str = Field(..., max_length=100)
    description_fa: Optional[str] = Field(None, max_length=500)
    preview_url: str = Field(..., max_length=500)
    file_url: str = Field(..., max_length=500)
    image_width: Optional[int] = None  # Original image width
    image_height: Optional[int] = None  # Original image height
    placeholder_x: int
    placeholder_y: int
    placeholder_width: int
    placeholder_height: int
    sort_order: int = 0
    is_active: bool = True


class TemplateCreate(TemplateBase):
    """Schema for creating a template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name_fa: Optional[str] = Field(None, max_length=100)
    description_fa: Optional[str] = Field(None, max_length=500)
    preview_url: Optional[str] = Field(None, max_length=500)
    file_url: Optional[str] = Field(None, max_length=500)
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    placeholder_x: Optional[int] = None
    placeholder_y: Optional[int] = None
    placeholder_width: Optional[int] = None
    placeholder_height: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class TemplateOut(TemplateBase):
    """Schema for template response."""
    id: UUID
    plan_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplyLogoRequest(BaseModel):
    """Request to apply logo to template."""
    logo_file_url: str = Field(..., max_length=500)


class ApplyLogoResponse(BaseModel):
    """Response after applying logo to template."""
    preview_url: str
    final_url: str


# ============== Processed Design Schemas ==============

class ProcessedDesignBase(BaseModel):
    """Base processed design schema."""
    template_id: UUID
    logo_url: str = Field(..., max_length=500)
    preview_url: str = Field(..., max_length=500)
    final_url: str = Field(..., max_length=500)


class ProcessedDesignCreate(BaseModel):
    """Schema for creating a processed design."""
    template_id: UUID
    logo_url: str = Field(..., max_length=500)


class ProcessedDesignOut(ProcessedDesignBase):
    """Schema for processed design response."""
    id: UUID
    order_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProcessedDesignWithTemplate(ProcessedDesignOut):
    """Processed design with template details."""
    template: TemplateOut


# ============== Step Template Schemas ==============

class StepTemplateBase(BaseModel):
    """Base step template schema."""
    slug: str = Field(..., max_length=50)
    name_fa: str = Field(..., max_length=100)
    step_type: StepType
    config: Optional[dict] = None
    conditions: Optional[dict] = None
    is_required: bool = True
    sort_order: int = 0
    is_active: bool = True


class StepTemplateCreate(StepTemplateBase):
    """Schema for creating a step template."""
    pass


class StepTemplateUpdate(BaseModel):
    """Schema for updating a step template."""
    slug: Optional[str] = Field(None, max_length=50)
    name_fa: Optional[str] = Field(None, max_length=100)
    step_type: Optional[StepType] = None
    config: Optional[dict] = None
    conditions: Optional[dict] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class StepTemplateOut(StepTemplateBase):
    """Schema for step template response."""
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Question Answer Schemas ==============

class QuestionAnswerBase(BaseModel):
    """Base question answer schema."""
    question_id: UUID
    answer_text: Optional[str] = None
    answer_values: Optional[List[str]] = None
    answer_file_url: Optional[str] = Field(None, max_length=500)


class QuestionAnswerCreate(QuestionAnswerBase):
    """Schema for creating a question answer."""
    pass


class QuestionAnswerOut(QuestionAnswerBase):
    """Schema for question answer response."""
    id: UUID
    order_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubmitAnswersRequest(BaseModel):
    """Request to submit all questionnaire answers."""
    answers: List[QuestionAnswerCreate]


# Update forward references
CategoryWithDetails.model_rebuild()
DesignPlanWithDetails.model_rebuild()
SectionWithQuestions.model_rebuild()
ProcessedDesignWithTemplate.model_rebuild()

