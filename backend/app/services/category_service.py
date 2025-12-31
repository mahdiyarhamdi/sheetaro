"""Service for category and related operations."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryOut, CategoryWithDetails,
    AttributeCreate, AttributeUpdate, AttributeOut, AttributeWithOptions,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionOut,
    DesignPlanCreate, DesignPlanUpdate, DesignPlanOut, DesignPlanWithDetails,
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionWithOptions,
    QuestionOptionCreate, QuestionOptionUpdate, QuestionOptionOut,
    TemplateCreate, TemplateUpdate, TemplateOut,
    StepTemplateCreate, StepTemplateUpdate, StepTemplateOut,
)


class CategoryService:
    """Service for category operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)
    
    # ============== Category ==============
    
    async def get_all_categories(self, active_only: bool = True) -> List[CategoryOut]:
        """Get all categories."""
        categories = await self.repository.get_all_categories(active_only)
        return [CategoryOut.model_validate(c) for c in categories]
    
    async def get_category(self, category_id: UUID) -> Optional[CategoryOut]:
        """Get category by ID."""
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            return None
        return CategoryOut.model_validate(category)
    
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryOut]:
        """Get category by slug."""
        category = await self.repository.get_category_by_slug(slug)
        if not category:
            return None
        return CategoryOut.model_validate(category)
    
    async def get_category_with_details(self, category_id: UUID) -> Optional[CategoryWithDetails]:
        """Get category with all related data."""
        category = await self.repository.get_category_with_details(category_id)
        if not category:
            return None
        return CategoryWithDetails.model_validate(category)
    
    async def create_category(self, data: CategoryCreate) -> CategoryOut:
        """Create a new category."""
        # Check if slug already exists
        existing = await self.repository.get_category_by_slug(data.slug)
        if existing:
            raise ValueError(f"Category with slug '{data.slug}' already exists")
        
        category = await self.repository.create_category(data)
        return CategoryOut.model_validate(category)
    
    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> Optional[CategoryOut]:
        """Update a category."""
        # Check if category exists
        existing = await self.repository.get_category_by_id(category_id)
        if not existing:
            raise ValueError("Category not found")
        
        # Check slug uniqueness if changing
        if data.slug and data.slug != existing.slug:
            slug_exists = await self.repository.get_category_by_slug(data.slug)
            if slug_exists:
                raise ValueError(f"Category with slug '{data.slug}' already exists")
        
        category = await self.repository.update_category(category_id, data)
        return CategoryOut.model_validate(category) if category else None
    
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category."""
        return await self.repository.delete_category(category_id)
    
    # ============== Attributes ==============
    
    async def get_attributes(self, category_id: UUID, active_only: bool = True) -> List[AttributeWithOptions]:
        """Get all attributes for a category."""
        attributes = await self.repository.get_attributes_by_category(category_id, active_only)
        return [AttributeWithOptions.model_validate(a) for a in attributes]
    
    async def get_attribute(self, attribute_id: UUID) -> Optional[AttributeWithOptions]:
        """Get attribute by ID."""
        attribute = await self.repository.get_attribute_by_id(attribute_id)
        if not attribute:
            return None
        return AttributeWithOptions.model_validate(attribute)
    
    async def create_attribute(self, category_id: UUID, data: AttributeCreate) -> AttributeOut:
        """Create a new attribute."""
        attribute = await self.repository.create_attribute(category_id, data)
        return AttributeOut.model_validate(attribute)
    
    async def update_attribute(self, attribute_id: UUID, data: AttributeUpdate) -> Optional[AttributeOut]:
        """Update an attribute."""
        attribute = await self.repository.update_attribute(attribute_id, data)
        return AttributeOut.model_validate(attribute) if attribute else None
    
    async def delete_attribute(self, attribute_id: UUID) -> bool:
        """Delete an attribute."""
        return await self.repository.delete_attribute(attribute_id)
    
    # ============== Attribute Options ==============
    
    async def create_attribute_option(self, attribute_id: UUID, data: AttributeOptionCreate) -> AttributeOptionOut:
        """Create a new attribute option."""
        option = await self.repository.create_attribute_option(attribute_id, data)
        return AttributeOptionOut.model_validate(option)
    
    async def update_attribute_option(self, option_id: UUID, data: AttributeOptionUpdate) -> Optional[AttributeOptionOut]:
        """Update an attribute option."""
        option = await self.repository.update_attribute_option(option_id, data)
        return AttributeOptionOut.model_validate(option) if option else None
    
    async def delete_attribute_option(self, option_id: UUID) -> bool:
        """Delete an attribute option."""
        return await self.repository.delete_attribute_option(option_id)
    
    # ============== Design Plans ==============
    
    async def get_plans(self, category_id: UUID, active_only: bool = True) -> List[DesignPlanOut]:
        """Get all design plans for a category."""
        plans = await self.repository.get_plans_by_category(category_id, active_only)
        return [DesignPlanOut.model_validate(p) for p in plans]
    
    async def get_plan(self, plan_id: UUID) -> Optional[DesignPlanOut]:
        """Get design plan by ID."""
        plan = await self.repository.get_plan_by_id(plan_id)
        if not plan:
            return None
        return DesignPlanOut.model_validate(plan)
    
    async def get_plan_with_details(self, plan_id: UUID) -> Optional[DesignPlanWithDetails]:
        """Get design plan with questions and templates."""
        plan = await self.repository.get_plan_with_details(plan_id)
        if not plan:
            return None
        return DesignPlanWithDetails.model_validate(plan)
    
    async def create_plan(self, category_id: UUID, data: DesignPlanCreate) -> DesignPlanOut:
        """Create a new design plan."""
        plan = await self.repository.create_plan(category_id, data)
        return DesignPlanOut.model_validate(plan)
    
    async def update_plan(self, plan_id: UUID, data: DesignPlanUpdate) -> Optional[DesignPlanOut]:
        """Update a design plan."""
        plan = await self.repository.update_plan(plan_id, data)
        return DesignPlanOut.model_validate(plan) if plan else None
    
    async def delete_plan(self, plan_id: UUID) -> bool:
        """Delete a design plan."""
        return await self.repository.delete_plan(plan_id)
    
    # ============== Questions ==============
    
    async def get_questions(self, plan_id: UUID, active_only: bool = True) -> List[QuestionWithOptions]:
        """Get all questions for a plan."""
        questions = await self.repository.get_questions_by_plan(plan_id, active_only)
        return [QuestionWithOptions.model_validate(q) for q in questions]
    
    async def get_question(self, question_id: UUID) -> Optional[QuestionWithOptions]:
        """Get question by ID."""
        question = await self.repository.get_question_by_id(question_id)
        if not question:
            return None
        return QuestionWithOptions.model_validate(question)
    
    async def create_question(self, plan_id: UUID, data: QuestionCreate) -> QuestionWithOptions:
        """Create a new question."""
        question = await self.repository.create_question(plan_id, data)
        return QuestionWithOptions.model_validate(question)
    
    async def update_question(self, question_id: UUID, data: QuestionUpdate) -> Optional[QuestionOut]:
        """Update a question."""
        question = await self.repository.update_question(question_id, data)
        return QuestionOut.model_validate(question) if question else None
    
    async def delete_question(self, question_id: UUID) -> bool:
        """Delete a question."""
        return await self.repository.delete_question(question_id)
    
    # ============== Question Options ==============
    
    async def create_question_option(self, question_id: UUID, data: QuestionOptionCreate) -> QuestionOptionOut:
        """Create a new question option."""
        option = await self.repository.create_question_option(question_id, data)
        return QuestionOptionOut.model_validate(option)
    
    async def update_question_option(self, option_id: UUID, data: QuestionOptionUpdate) -> Optional[QuestionOptionOut]:
        """Update a question option."""
        option = await self.repository.update_question_option(option_id, data)
        return QuestionOptionOut.model_validate(option) if option else None
    
    async def delete_question_option(self, option_id: UUID) -> bool:
        """Delete a question option."""
        return await self.repository.delete_question_option(option_id)
    
    # ============== Templates ==============
    
    async def get_templates(self, plan_id: UUID, active_only: bool = True) -> List[TemplateOut]:
        """Get all templates for a plan."""
        templates = await self.repository.get_templates_by_plan(plan_id, active_only)
        return [TemplateOut.model_validate(t) for t in templates]
    
    async def get_template(self, template_id: UUID) -> Optional[TemplateOut]:
        """Get template by ID."""
        template = await self.repository.get_template_by_id(template_id)
        if not template:
            return None
        return TemplateOut.model_validate(template)
    
    async def create_template(self, plan_id: UUID, data: TemplateCreate) -> TemplateOut:
        """Create a new template."""
        template = await self.repository.create_template(plan_id, data)
        return TemplateOut.model_validate(template)
    
    async def update_template(self, template_id: UUID, data: TemplateUpdate) -> Optional[TemplateOut]:
        """Update a template."""
        template = await self.repository.update_template(template_id, data)
        return TemplateOut.model_validate(template) if template else None
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Delete a template."""
        return await self.repository.delete_template(template_id)
    
    # ============== Step Templates ==============
    
    async def get_step_templates(self, category_id: UUID, active_only: bool = True) -> List[StepTemplateOut]:
        """Get all step templates for a category."""
        templates = await self.repository.get_step_templates_by_category(category_id, active_only)
        return [StepTemplateOut.model_validate(t) for t in templates]
    
    async def get_step_template(self, template_id: UUID) -> Optional[StepTemplateOut]:
        """Get step template by ID."""
        template = await self.repository.get_step_template_by_id(template_id)
        if not template:
            return None
        return StepTemplateOut.model_validate(template)
    
    async def create_step_template(self, category_id: UUID, data: StepTemplateCreate) -> StepTemplateOut:
        """Create a new step template."""
        template = await self.repository.create_step_template(category_id, data)
        return StepTemplateOut.model_validate(template)
    
    async def update_step_template(self, template_id: UUID, data: StepTemplateUpdate) -> Optional[StepTemplateOut]:
        """Update a step template."""
        template = await self.repository.update_step_template(template_id, data)
        return StepTemplateOut.model_validate(template) if template else None
    
    async def delete_step_template(self, template_id: UUID) -> bool:
        """Delete a step template."""
        return await self.repository.delete_step_template(template_id)

