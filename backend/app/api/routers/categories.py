"""API endpoints for categories and related resources."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_admin_user
from app.services.category_service import CategoryService
from app.services.template_service import TemplateService
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryOut, CategoryWithDetails,
    AttributeCreate, AttributeUpdate, AttributeOut, AttributeWithOptions,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionOut,
    DesignPlanCreate, DesignPlanUpdate, DesignPlanOut, DesignPlanWithDetails,
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionWithOptions,
    QuestionOptionCreate, QuestionOptionUpdate, QuestionOptionOut,
    TemplateCreate, TemplateUpdate, TemplateOut, ApplyLogoRequest, ApplyLogoResponse,
    StepTemplateCreate, StepTemplateUpdate, StepTemplateOut,
)

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


# ============== Category Endpoints ==============

@router.get("", response_model=List[CategoryOut])
async def list_categories(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all categories."""
    service = CategoryService(db)
    return await service.get_all_categories(active_only)


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a category by ID."""
    service = CategoryService(db)
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/details", response_model=CategoryWithDetails)
async def get_category_with_details(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a category with all related data."""
    service = CategoryService(db)
    category = await service.get_category_with_details(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new category. Admin only."""
    service = CategoryService(db)
    try:
        return await service.create_category(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a category. Admin only."""
    service = CategoryService(db)
    try:
        category = await service.update_category(category_id, data)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a category. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")


# ============== Attribute Endpoints ==============

@router.get("/{category_id}/attributes", response_model=List[AttributeWithOptions])
async def list_attributes(
    category_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all attributes for a category."""
    service = CategoryService(db)
    return await service.get_attributes(category_id, active_only)


@router.post("/{category_id}/attributes", response_model=AttributeOut, status_code=status.HTTP_201_CREATED)
async def create_attribute(
    category_id: UUID,
    data: AttributeCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new attribute. Admin only."""
    service = CategoryService(db)
    return await service.create_attribute(category_id, data)


# Attribute CRUD (outside category scope)
attributes_router = APIRouter(prefix="/api/v1/attributes", tags=["attributes"])


@attributes_router.get("/{attribute_id}", response_model=AttributeWithOptions)
async def get_attribute(
    attribute_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get an attribute by ID."""
    service = CategoryService(db)
    attribute = await service.get_attribute(attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute


@attributes_router.patch("/{attribute_id}", response_model=AttributeOut)
async def update_attribute(
    attribute_id: UUID,
    data: AttributeUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update an attribute. Admin only."""
    service = CategoryService(db)
    attribute = await service.update_attribute(attribute_id, data)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute


@attributes_router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attribute(
    attribute_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete an attribute. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_attribute(attribute_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attribute not found")


@attributes_router.post("/{attribute_id}/options", response_model=AttributeOptionOut, status_code=status.HTTP_201_CREATED)
async def create_attribute_option(
    attribute_id: UUID,
    data: AttributeOptionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new attribute option. Admin only."""
    service = CategoryService(db)
    return await service.create_attribute_option(attribute_id, data)


# Attribute Options CRUD
options_router = APIRouter(prefix="/api/v1/options", tags=["options"])


@options_router.patch("/{option_id}", response_model=AttributeOptionOut)
async def update_attribute_option(
    option_id: UUID,
    data: AttributeOptionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update an attribute option. Admin only."""
    service = CategoryService(db)
    option = await service.update_attribute_option(option_id, data)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    return option


@options_router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attribute_option(
    option_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete an attribute option. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_attribute_option(option_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Option not found")


# ============== Design Plan Endpoints ==============

@router.get("/{category_id}/plans", response_model=List[DesignPlanOut])
async def list_plans(
    category_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all design plans for a category."""
    service = CategoryService(db)
    return await service.get_plans(category_id, active_only)


@router.post("/{category_id}/plans", response_model=DesignPlanOut, status_code=status.HTTP_201_CREATED)
async def create_plan(
    category_id: UUID,
    data: DesignPlanCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new design plan. Admin only."""
    service = CategoryService(db)
    return await service.create_plan(category_id, data)


# Plans CRUD (outside category scope)
plans_router = APIRouter(prefix="/api/v1/plans", tags=["plans"])


@plans_router.get("/{plan_id}", response_model=DesignPlanOut)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a design plan by ID."""
    service = CategoryService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@plans_router.get("/{plan_id}/details", response_model=DesignPlanWithDetails)
async def get_plan_with_details(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a design plan with questions and templates."""
    service = CategoryService(db)
    plan = await service.get_plan_with_details(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@plans_router.patch("/{plan_id}", response_model=DesignPlanOut)
async def update_plan(
    plan_id: UUID,
    data: DesignPlanUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a design plan. Admin only."""
    service = CategoryService(db)
    plan = await service.update_plan(plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@plans_router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a design plan. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_plan(plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")


# ============== Question Endpoints ==============

@plans_router.get("/{plan_id}/questions", response_model=List[QuestionWithOptions])
async def list_questions(
    plan_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all questions for a plan."""
    service = CategoryService(db)
    return await service.get_questions(plan_id, active_only)


@plans_router.post("/{plan_id}/questions", response_model=QuestionWithOptions, status_code=status.HTTP_201_CREATED)
async def create_question(
    plan_id: UUID,
    data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new question. Admin only."""
    service = CategoryService(db)
    return await service.create_question(plan_id, data)


# Questions CRUD
questions_router = APIRouter(prefix="/api/v1/questions", tags=["questions"])


@questions_router.get("/{question_id}", response_model=QuestionWithOptions)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a question by ID."""
    service = CategoryService(db)
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@questions_router.patch("/{question_id}", response_model=QuestionOut)
async def update_question(
    question_id: UUID,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a question. Admin only."""
    service = CategoryService(db)
    question = await service.update_question(question_id, data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@questions_router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a question. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_question(question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")


@questions_router.post("/{question_id}/options", response_model=QuestionOptionOut, status_code=status.HTTP_201_CREATED)
async def create_question_option(
    question_id: UUID,
    data: QuestionOptionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new question option. Admin only."""
    service = CategoryService(db)
    return await service.create_question_option(question_id, data)


# Question Options CRUD
question_options_router = APIRouter(prefix="/api/v1/question-options", tags=["question-options"])


@question_options_router.patch("/{option_id}", response_model=QuestionOptionOut)
async def update_question_option(
    option_id: UUID,
    data: QuestionOptionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a question option. Admin only."""
    service = CategoryService(db)
    option = await service.update_question_option(option_id, data)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    return option


@question_options_router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_option(
    option_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a question option. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_question_option(option_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Option not found")


# ============== Template Endpoints ==============

@plans_router.get("/{plan_id}/templates", response_model=List[TemplateOut])
async def list_templates(
    plan_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all templates for a plan."""
    service = CategoryService(db)
    return await service.get_templates(plan_id, active_only)


@plans_router.post("/{plan_id}/templates", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
async def create_template(
    plan_id: UUID,
    data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new template. Admin only."""
    service = CategoryService(db)
    return await service.create_template(plan_id, data)


# Templates CRUD
templates_router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@templates_router.get("/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a template by ID."""
    service = CategoryService(db)
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@templates_router.patch("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a template. Admin only."""
    service = CategoryService(db)
    template = await service.update_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@templates_router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a template. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")


@templates_router.post("/{template_id}/apply-logo", response_model=ApplyLogoResponse)
async def apply_logo_to_template(
    template_id: UUID,
    data: ApplyLogoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Apply a logo to a template and get preview/final URLs."""
    service = CategoryService(db)
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get template model for processing
    from app.repositories.category_repository import CategoryRepository
    repo = CategoryRepository(db)
    template_model = await repo.get_template_by_id(template_id)
    
    # Process template with logo
    template_service = TemplateService()
    base_url = str(request.base_url).rstrip('/')
    
    try:
        result = await template_service.process_template_with_logo(
            template=template_model,
            logo_url=data.logo_file_url,
            base_url=base_url,
        )
        return ApplyLogoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Step Template Endpoints ==============

@router.get("/{category_id}/steps", response_model=List[StepTemplateOut])
async def list_step_templates(
    category_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all step templates for a category."""
    service = CategoryService(db)
    return await service.get_step_templates(category_id, active_only)


@router.post("/{category_id}/steps", response_model=StepTemplateOut, status_code=status.HTTP_201_CREATED)
async def create_step_template(
    category_id: UUID,
    data: StepTemplateCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new step template. Admin only."""
    service = CategoryService(db)
    return await service.create_step_template(category_id, data)


# Step Templates CRUD
step_templates_router = APIRouter(prefix="/api/v1/step-templates", tags=["step-templates"])


@step_templates_router.get("/{template_id}", response_model=StepTemplateOut)
async def get_step_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a step template by ID."""
    service = CategoryService(db)
    template = await service.get_step_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Step template not found")
    return template


@step_templates_router.patch("/{template_id}", response_model=StepTemplateOut)
async def update_step_template(
    template_id: UUID,
    data: StepTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a step template. Admin only."""
    service = CategoryService(db)
    template = await service.update_step_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Step template not found")
    return template


@step_templates_router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_step_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a step template. Admin only."""
    service = CategoryService(db)
    deleted = await service.delete_step_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Step template not found")

