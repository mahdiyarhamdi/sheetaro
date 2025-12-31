"""Repository for category and related models."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.attribute import CategoryAttribute, AttributeOption
from app.models.design_plan import CategoryDesignPlan
from app.models.design_question import DesignQuestion, QuestionOption
from app.models.design_template import DesignTemplate
from app.models.order_step import OrderStepTemplate
from app.schemas.category import (
    CategoryCreate, CategoryUpdate,
    AttributeCreate, AttributeUpdate,
    AttributeOptionCreate, AttributeOptionUpdate,
    DesignPlanCreate, DesignPlanUpdate,
    QuestionCreate, QuestionUpdate,
    QuestionOptionCreate, QuestionOptionUpdate,
    TemplateCreate, TemplateUpdate,
    StepTemplateCreate, StepTemplateUpdate,
)


class CategoryRepository:
    """Repository for Category CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== Category ==============
    
    async def get_all_categories(self, active_only: bool = True) -> List[Category]:
        """Get all categories."""
        query = select(Category)
        if active_only:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.sort_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID."""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_category_with_details(self, category_id: UUID) -> Optional[Category]:
        """Get category with all related data."""
        result = await self.db.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.attributes).selectinload(CategoryAttribute.options),
                selectinload(Category.design_plans),
                selectinload(Category.step_templates),
            )
        )
        return result.scalar_one_or_none()
    
    async def create_category(self, data: CategoryCreate) -> Category:
        """Create a new category."""
        category = Category(**data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
    
    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> Optional[Category]:
        """Update a category."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_category_by_id(category_id)
        
        await self.db.execute(
            update(Category).where(Category.id == category_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_category_by_id(category_id)
    
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category."""
        result = await self.db.execute(
            delete(Category).where(Category.id == category_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Attributes ==============
    
    async def get_attributes_by_category(self, category_id: UUID, active_only: bool = True) -> List[CategoryAttribute]:
        """Get all attributes for a category."""
        query = select(CategoryAttribute).where(CategoryAttribute.category_id == category_id)
        if active_only:
            query = query.where(CategoryAttribute.is_active == True)
        query = query.order_by(CategoryAttribute.sort_order).options(selectinload(CategoryAttribute.options))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_attribute_by_id(self, attribute_id: UUID) -> Optional[CategoryAttribute]:
        """Get attribute by ID."""
        result = await self.db.execute(
            select(CategoryAttribute)
            .where(CategoryAttribute.id == attribute_id)
            .options(selectinload(CategoryAttribute.options))
        )
        return result.scalar_one_or_none()
    
    async def create_attribute(self, category_id: UUID, data: AttributeCreate) -> CategoryAttribute:
        """Create a new attribute."""
        attribute = CategoryAttribute(category_id=category_id, **data.model_dump())
        self.db.add(attribute)
        await self.db.commit()
        await self.db.refresh(attribute)
        return attribute
    
    async def update_attribute(self, attribute_id: UUID, data: AttributeUpdate) -> Optional[CategoryAttribute]:
        """Update an attribute."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_attribute_by_id(attribute_id)
        
        await self.db.execute(
            update(CategoryAttribute).where(CategoryAttribute.id == attribute_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_attribute_by_id(attribute_id)
    
    async def delete_attribute(self, attribute_id: UUID) -> bool:
        """Delete an attribute."""
        result = await self.db.execute(
            delete(CategoryAttribute).where(CategoryAttribute.id == attribute_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Attribute Options ==============
    
    async def get_option_by_id(self, option_id: UUID) -> Optional[AttributeOption]:
        """Get attribute option by ID."""
        result = await self.db.execute(
            select(AttributeOption).where(AttributeOption.id == option_id)
        )
        return result.scalar_one_or_none()
    
    async def create_attribute_option(self, attribute_id: UUID, data: AttributeOptionCreate) -> AttributeOption:
        """Create a new attribute option."""
        option = AttributeOption(attribute_id=attribute_id, **data.model_dump())
        self.db.add(option)
        await self.db.commit()
        await self.db.refresh(option)
        return option
    
    async def update_attribute_option(self, option_id: UUID, data: AttributeOptionUpdate) -> Optional[AttributeOption]:
        """Update an attribute option."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_option_by_id(option_id)
        
        await self.db.execute(
            update(AttributeOption).where(AttributeOption.id == option_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_option_by_id(option_id)
    
    async def delete_attribute_option(self, option_id: UUID) -> bool:
        """Delete an attribute option."""
        result = await self.db.execute(
            delete(AttributeOption).where(AttributeOption.id == option_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Design Plans ==============
    
    async def get_plans_by_category(self, category_id: UUID, active_only: bool = True) -> List[CategoryDesignPlan]:
        """Get all design plans for a category."""
        query = select(CategoryDesignPlan).where(CategoryDesignPlan.category_id == category_id)
        if active_only:
            query = query.where(CategoryDesignPlan.is_active == True)
        query = query.order_by(CategoryDesignPlan.sort_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_plan_by_id(self, plan_id: UUID) -> Optional[CategoryDesignPlan]:
        """Get design plan by ID."""
        result = await self.db.execute(
            select(CategoryDesignPlan).where(CategoryDesignPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def get_plan_with_details(self, plan_id: UUID) -> Optional[CategoryDesignPlan]:
        """Get design plan with questions and templates."""
        result = await self.db.execute(
            select(CategoryDesignPlan)
            .where(CategoryDesignPlan.id == plan_id)
            .options(
                selectinload(CategoryDesignPlan.questions).selectinload(DesignQuestion.options),
                selectinload(CategoryDesignPlan.templates),
            )
        )
        return result.scalar_one_or_none()
    
    async def create_plan(self, category_id: UUID, data: DesignPlanCreate) -> CategoryDesignPlan:
        """Create a new design plan."""
        plan = CategoryDesignPlan(category_id=category_id, **data.model_dump())
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan
    
    async def update_plan(self, plan_id: UUID, data: DesignPlanUpdate) -> Optional[CategoryDesignPlan]:
        """Update a design plan."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_plan_by_id(plan_id)
        
        await self.db.execute(
            update(CategoryDesignPlan).where(CategoryDesignPlan.id == plan_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_plan_by_id(plan_id)
    
    async def delete_plan(self, plan_id: UUID) -> bool:
        """Delete a design plan."""
        result = await self.db.execute(
            delete(CategoryDesignPlan).where(CategoryDesignPlan.id == plan_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Questions ==============
    
    async def get_questions_by_plan(self, plan_id: UUID, active_only: bool = True) -> List[DesignQuestion]:
        """Get all questions for a plan."""
        query = select(DesignQuestion).where(DesignQuestion.plan_id == plan_id)
        if active_only:
            query = query.where(DesignQuestion.is_active == True)
        query = query.order_by(DesignQuestion.sort_order).options(selectinload(DesignQuestion.options))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_question_by_id(self, question_id: UUID) -> Optional[DesignQuestion]:
        """Get question by ID."""
        result = await self.db.execute(
            select(DesignQuestion)
            .where(DesignQuestion.id == question_id)
            .options(selectinload(DesignQuestion.options))
        )
        return result.scalar_one_or_none()
    
    async def create_question(self, plan_id: UUID, data: QuestionCreate) -> DesignQuestion:
        """Create a new question with options."""
        options_data = data.options or []
        question_data = data.model_dump(exclude={'options'})
        question = DesignQuestion(plan_id=plan_id, **question_data)
        self.db.add(question)
        await self.db.flush()
        
        for opt_data in options_data:
            option = QuestionOption(question_id=question.id, **opt_data.model_dump())
            self.db.add(option)
        
        await self.db.commit()
        await self.db.refresh(question)
        return await self.get_question_by_id(question.id)
    
    async def update_question(self, question_id: UUID, data: QuestionUpdate) -> Optional[DesignQuestion]:
        """Update a question."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_question_by_id(question_id)
        
        await self.db.execute(
            update(DesignQuestion).where(DesignQuestion.id == question_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_question_by_id(question_id)
    
    async def delete_question(self, question_id: UUID) -> bool:
        """Delete a question."""
        result = await self.db.execute(
            delete(DesignQuestion).where(DesignQuestion.id == question_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Question Options ==============
    
    async def get_question_option_by_id(self, option_id: UUID) -> Optional[QuestionOption]:
        """Get question option by ID."""
        result = await self.db.execute(
            select(QuestionOption).where(QuestionOption.id == option_id)
        )
        return result.scalar_one_or_none()
    
    async def create_question_option(self, question_id: UUID, data: QuestionOptionCreate) -> QuestionOption:
        """Create a new question option."""
        option = QuestionOption(question_id=question_id, **data.model_dump())
        self.db.add(option)
        await self.db.commit()
        await self.db.refresh(option)
        return option
    
    async def update_question_option(self, option_id: UUID, data: QuestionOptionUpdate) -> Optional[QuestionOption]:
        """Update a question option."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_question_option_by_id(option_id)
        
        await self.db.execute(
            update(QuestionOption).where(QuestionOption.id == option_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_question_option_by_id(option_id)
    
    async def delete_question_option(self, option_id: UUID) -> bool:
        """Delete a question option."""
        result = await self.db.execute(
            delete(QuestionOption).where(QuestionOption.id == option_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Templates ==============
    
    async def get_templates_by_plan(self, plan_id: UUID, active_only: bool = True) -> List[DesignTemplate]:
        """Get all templates for a plan."""
        query = select(DesignTemplate).where(DesignTemplate.plan_id == plan_id)
        if active_only:
            query = query.where(DesignTemplate.is_active == True)
        query = query.order_by(DesignTemplate.sort_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_template_by_id(self, template_id: UUID) -> Optional[DesignTemplate]:
        """Get template by ID."""
        result = await self.db.execute(
            select(DesignTemplate).where(DesignTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def create_template(self, plan_id: UUID, data: TemplateCreate) -> DesignTemplate:
        """Create a new template."""
        template = DesignTemplate(plan_id=plan_id, **data.model_dump())
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def update_template(self, template_id: UUID, data: TemplateUpdate) -> Optional[DesignTemplate]:
        """Update a template."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_template_by_id(template_id)
        
        await self.db.execute(
            update(DesignTemplate).where(DesignTemplate.id == template_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_template_by_id(template_id)
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Delete a template."""
        result = await self.db.execute(
            delete(DesignTemplate).where(DesignTemplate.id == template_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ============== Step Templates ==============
    
    async def get_step_templates_by_category(self, category_id: UUID, active_only: bool = True) -> List[OrderStepTemplate]:
        """Get all step templates for a category."""
        query = select(OrderStepTemplate).where(OrderStepTemplate.category_id == category_id)
        if active_only:
            query = query.where(OrderStepTemplate.is_active == True)
        query = query.order_by(OrderStepTemplate.sort_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_step_template_by_id(self, template_id: UUID) -> Optional[OrderStepTemplate]:
        """Get step template by ID."""
        result = await self.db.execute(
            select(OrderStepTemplate).where(OrderStepTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def create_step_template(self, category_id: UUID, data: StepTemplateCreate) -> OrderStepTemplate:
        """Create a new step template."""
        template = OrderStepTemplate(category_id=category_id, **data.model_dump())
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def update_step_template(self, template_id: UUID, data: StepTemplateUpdate) -> Optional[OrderStepTemplate]:
        """Update a step template."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_step_template_by_id(template_id)
        
        await self.db.execute(
            update(OrderStepTemplate).where(OrderStepTemplate.id == template_id).values(**update_data)
        )
        await self.db.commit()
        return await self.get_step_template_by_id(template_id)
    
    async def delete_step_template(self, template_id: UUID) -> bool:
        """Delete a step template."""
        result = await self.db.execute(
            delete(OrderStepTemplate).where(OrderStepTemplate.id == template_id)
        )
        await self.db.commit()
        return result.rowcount > 0

