"""Tests for DesignRevisionService."""

import pytest
import pytest_asyncio
from decimal import Decimal
from uuid import uuid4

from app.models.enums import (
    DesignPlan, OrderStatus, RevisionStatus, UserRole,
)
from app.services.design_revision_service import DesignRevisionService

from tests.conftest import (
    create_test_user,
    create_test_category,
    create_test_order,
)


@pytest_asyncio.fixture
async def customer(db_session):
    return await create_test_user(db_session, {
        "telegram_id": 111111,
        "username": "customer",
        "first_name": "Customer",
        "last_name": "User",
        "role": UserRole.CUSTOMER,
        "phone_number": "09121110000",
    })


@pytest_asyncio.fixture
async def designer(db_session):
    return await create_test_user(db_session, {
        "telegram_id": 222222,
        "username": "designer",
        "first_name": "Designer",
        "last_name": "User",
        "role": UserRole.DESIGNER,
        "phone_number": "09122220000",
    })


@pytest_asyncio.fixture
async def category(db_session):
    return await create_test_category(db_session, {
        "slug": "rev-test-cat",
        "name_fa": "دسته تست ریویژن",
        "base_price": 10000,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def designing_order(db_session, customer, designer, category):
    """An order in DESIGNING status with designer assigned, SEMI_PRIVATE plan, max 3 revisions."""
    return await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.SEMI_PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 0,
        "max_revisions": 3,
        "validation_requested": False,
    })


@pytest_asyncio.fixture
async def private_order(db_session, customer, designer, category):
    """An order in DESIGNING status with PRIVATE plan (unlimited revisions)."""
    return await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 0,
        "max_revisions": None,
        "validation_requested": False,
    })


@pytest.mark.asyncio
async def test_submit_revision(db_session, designing_order, designer):
    """Test designer submits a revision."""
    service = DesignRevisionService(db_session)
    rev = await service.submit_revision(
        order_id=designing_order.id,
        designer_id=designer.id,
        design_file_url="/uploads/designs/test.png",
    )

    assert rev.version == 1
    assert rev.status == RevisionStatus.PENDING_REVIEW
    assert rev.design_file_url == "/uploads/designs/test.png"
    assert rev.order_id == designing_order.id


@pytest.mark.asyncio
async def test_submit_multiple_revisions(db_session, designing_order, designer):
    """Submitting multiple revisions increments version."""
    service = DesignRevisionService(db_session)

    rev1 = await service.submit_revision(designing_order.id, designer.id, "/v1.png")
    assert rev1.version == 1

    # Reject to allow next submission (mark previous as reviewed first)
    await service.reject_design(designing_order.id, designing_order.user_id, "Change bg color")

    rev2 = await service.submit_revision(designing_order.id, designer.id, "/v2.png")
    assert rev2.version == 2


@pytest.mark.asyncio
async def test_approve_design(db_session, designing_order, designer, customer):
    """Customer approves the design -> order transitions to READY_FOR_PRINT."""
    service = DesignRevisionService(db_session)
    await service.submit_revision(designing_order.id, designer.id, "/design.png")

    result = await service.approve_design(designing_order.id, customer.id)
    assert result.status == RevisionStatus.APPROVED

    # Order should have moved to READY_FOR_PRINT
    await db_session.refresh(designing_order)
    assert designing_order.status == OrderStatus.READY_FOR_PRINT


@pytest.mark.asyncio
async def test_approve_design_with_validation(db_session, customer, designer, category):
    """Approval with validation_requested -> AWAITING_VALIDATION."""
    order = await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.SEMI_PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 0,
        "max_revisions": 3,
        "validation_requested": True,
    })

    service = DesignRevisionService(db_session)
    await service.submit_revision(order.id, designer.id, "/design.png")
    await service.approve_design(order.id, customer.id)

    await db_session.refresh(order)
    assert order.status == OrderStatus.AWAITING_VALIDATION


@pytest.mark.asyncio
async def test_reject_design_with_remaining(db_session, designing_order, designer, customer):
    """Rejecting design increments count, stays DESIGNING."""
    service = DesignRevisionService(db_session)
    await service.submit_revision(designing_order.id, designer.id, "/design.png")

    result = await service.reject_design(designing_order.id, customer.id, "Logo too small")
    assert result.status == RevisionStatus.REJECTED
    assert result.customer_feedback == "Logo too small"

    await db_session.refresh(designing_order)
    assert designing_order.revision_count == 1
    assert designing_order.status == OrderStatus.DESIGNING


@pytest.mark.asyncio
async def test_reject_design_auto_approve(db_session, customer, designer, category):
    """When max revisions reached, rejection triggers auto-approve."""
    order = await create_test_order(db_session, customer, category, {
        "design_plan": DesignPlan.SEMI_PRIVATE,
        "status": OrderStatus.DESIGNING,
        "assigned_designer_id": designer.id,
        "revision_count": 2,  # Already at 2, max is 3
        "max_revisions": 3,
        "validation_requested": False,
    })

    service = DesignRevisionService(db_session)
    await service.submit_revision(order.id, designer.id, "/design_v3.png")

    result = await service.reject_design(order.id, customer.id, "Still not right")
    # Should be auto-approved since revision_count (3) >= max_revisions (3)
    assert result.status == RevisionStatus.APPROVED

    await db_session.refresh(order)
    assert order.status == OrderStatus.READY_FOR_PRINT


@pytest.mark.asyncio
async def test_reject_design_unlimited(db_session, private_order, designer, customer):
    """PRIVATE plan: rejection never auto-approves (max_revisions is None)."""
    service = DesignRevisionService(db_session)
    await service.submit_revision(private_order.id, designer.id, "/design.png")

    result = await service.reject_design(private_order.id, customer.id, "Not what I want")
    assert result.status == RevisionStatus.REJECTED

    await db_session.refresh(private_order)
    assert private_order.revision_count == 1
    assert private_order.status == OrderStatus.DESIGNING  # Stays DESIGNING


@pytest.mark.asyncio
async def test_get_revision_history(db_session, designing_order, designer, customer):
    """Test fetching revision history."""
    service = DesignRevisionService(db_session)
    await service.submit_revision(designing_order.id, designer.id, "/v1.png")
    await service.reject_design(designing_order.id, customer.id, "First feedback")
    await service.submit_revision(designing_order.id, designer.id, "/v2.png")

    history = await service.get_revision_history(designing_order.id)
    assert history.total == 2
    assert history.items[0].version == 1
    assert history.items[1].version == 2


@pytest.mark.asyncio
async def test_only_owner_can_approve(db_session, designing_order, designer):
    """Non-owner cannot approve."""
    service = DesignRevisionService(db_session)
    await service.submit_revision(designing_order.id, designer.id, "/design.png")

    with pytest.raises(ValueError, match="Only the order owner"):
        await service.approve_design(designing_order.id, designer.id)
