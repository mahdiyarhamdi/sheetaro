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
    SectionCreate, SectionUpdate, SectionOut, SectionWithQuestions, SectionReorderRequest,
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionWithOptions,
    QuestionReorderRequest, ValidateAnswerRequest, ValidateAnswerResponse,
    QuestionOptionCreate, QuestionOptionUpdate, QuestionOptionOut,
    TemplateCreate, TemplateUpdate, TemplateOut, ApplyLogoRequest, ApplyLogoResponse,
    ProcessedDesignOut, ProcessedDesignCreate, ProcessedDesignWithTemplate,
    StepTemplateCreate, StepTemplateUpdate, StepTemplateOut,
    QuestionAnswerOut, QuestionAnswerCreate, SubmitAnswersRequest,
)
from app.services.questionnaire_service import QuestionnaireService
from app.repositories.category_repository import CategoryRepository

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


# ============== Section Endpoints ==============

@plans_router.get("/{plan_id}/sections", response_model=List[SectionWithQuestions])
async def list_sections(
    plan_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all sections for a plan with their questions."""
    repo = CategoryRepository(db)
    return await repo.get_sections_by_plan(plan_id, active_only)


@plans_router.post("/{plan_id}/sections", response_model=SectionOut, status_code=status.HTTP_201_CREATED)
async def create_section(
    plan_id: UUID,
    data: SectionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new section. Admin only."""
    repo = CategoryRepository(db)
    return await repo.create_section(plan_id, data)


# Sections CRUD
sections_router = APIRouter(prefix="/api/v1/sections", tags=["sections"])


@sections_router.get("/{section_id}", response_model=SectionWithQuestions)
async def get_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a section by ID with its questions."""
    repo = CategoryRepository(db)
    section = await repo.get_section_by_id(section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@sections_router.patch("/{section_id}", response_model=SectionOut)
async def update_section(
    section_id: UUID,
    data: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Update a section. Admin only."""
    repo = CategoryRepository(db)
    section = await repo.update_section(section_id, data)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@sections_router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Delete a section. Admin only."""
    repo = CategoryRepository(db)
    deleted = await repo.delete_section(section_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Section not found")


@sections_router.patch("/reorder", status_code=status.HTTP_200_OK)
async def reorder_sections(
    data: SectionReorderRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Reorder sections. Admin only."""
    repo = CategoryRepository(db)
    items = [{"id": item.id, "sort_order": item.sort_order} for item in data.items]
    await repo.reorder_sections(items)
    return {"success": True}


@sections_router.get("/{section_id}/questions", response_model=List[QuestionWithOptions])
async def list_section_questions(
    section_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all questions for a section."""
    repo = CategoryRepository(db)
    return await repo.get_questions_by_section(section_id, active_only)


@sections_router.post("/{section_id}/questions", response_model=QuestionWithOptions, status_code=status.HTTP_201_CREATED)
async def create_section_question(
    section_id: UUID,
    data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Create a new question in a section. Admin only."""
    repo = CategoryRepository(db)
    # Get section to find plan_id
    section = await repo.get_section_by_id(section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Create question with section_id
    data_dict = data.model_dump()
    data_dict['section_id'] = section_id
    question_data = QuestionCreate(**data_dict)
    return await repo.create_question(section.plan_id, question_data)


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


@questions_router.post("/{question_id}/validate", response_model=ValidateAnswerResponse)
async def validate_answer(
    question_id: UUID,
    data: ValidateAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validate an answer for a question."""
    repo = CategoryRepository(db)
    question = await repo.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    questionnaire_service = QuestionnaireService(repo)
    return questionnaire_service.validate_answer(question, data)


@questions_router.patch("/reorder", status_code=status.HTTP_200_OK)
async def reorder_questions(
    data: QuestionReorderRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    """Reorder questions. Admin only."""
    repo = CategoryRepository(db)
    items = [{"id": item.id, "sort_order": item.sort_order} for item in data.items]
    await repo.reorder_questions(items)
    return {"success": True}


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


# ============== Processed Design Endpoints ==============

processed_designs_router = APIRouter(prefix="/api/v1/processed-designs", tags=["processed-designs"])


@processed_designs_router.get("/{design_id}", response_model=ProcessedDesignWithTemplate)
async def get_processed_design(
    design_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a processed design by ID."""
    repo = CategoryRepository(db)
    design = await repo.get_processed_design_by_id(design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Processed design not found")
    return design


# ============== Questionnaire Answer Endpoints ==============

answers_router = APIRouter(prefix="/api/v1/orders", tags=["answers"])


@answers_router.get("/{order_id}/answers", response_model=List[QuestionAnswerOut])
async def list_order_answers(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all questionnaire answers for an order."""
    repo = CategoryRepository(db)
    return await repo.get_answers_by_order(order_id)


@answers_router.post("/{order_id}/answers", status_code=status.HTTP_201_CREATED)
async def submit_order_answers(
    order_id: UUID,
    data: SubmitAnswersRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit all questionnaire answers for an order."""
    repo = CategoryRepository(db)
    
    # Get the order to find the plan_id
    from app.repositories.order_repository import OrderRepository
    order_repo = OrderRepository(db)
    order = await order_repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # For now, we need to get plan_id from order or pass it
    # This assumes order has a design_plan_id field
    plan_id = getattr(order, 'design_plan_id', None)
    if not plan_id:
        # Submit without validation if no plan_id
        answers = await repo.submit_answers(order_id, data.answers)
        return {"success": True, "answer_count": len(answers)}
    
    questionnaire_service = QuestionnaireService(repo)
    result = await questionnaire_service.submit_questionnaire(order_id, plan_id, data.answers)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["errors"])
    
    return result


@answers_router.get("/{order_id}/answers/summary")
async def get_order_answers_summary(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a formatted summary of answers for an order."""
    repo = CategoryRepository(db)
    questionnaire_service = QuestionnaireService(repo)
    return await questionnaire_service.get_answers_summary(order_id)


@answers_router.get("/{order_id}/design", response_model=List[ProcessedDesignWithTemplate])
async def get_order_designs(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all processed designs for an order."""
    repo = CategoryRepository(db)
    return await repo.get_processed_designs_by_order(order_id)


@answers_router.post("/{order_id}/design", response_model=ProcessedDesignOut, status_code=status.HTTP_201_CREATED)
async def create_order_design(
    order_id: UUID,
    data: ProcessedDesignCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Process a template with logo and save as order design."""
    repo = CategoryRepository(db)
    
    # Get template
    template = await repo.get_template_by_id(data.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Process template with logo
    template_service = TemplateService(repository=repo)
    base_url = str(request.base_url).rstrip('/')
    
    try:
        result = await template_service.process_and_save_design(
            template=template,
            logo_url=data.logo_url,
            order_id=str(order_id),
            base_url=base_url,
        )
        
        # Get the created design
        from uuid import UUID as PyUUID
        design = await repo.get_processed_design_by_id(PyUUID(result["design_id"]))
        return design
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

