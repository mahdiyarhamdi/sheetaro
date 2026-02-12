"""Integration tests for designer validation endpoints."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from tests.conftest import (
    create_test_admin_user,
    create_test_web_user,
    create_test_category,
    create_test_order,
    create_admin_token,
)
from app.models.enums import UserRole, OrderStatus, ValidationStatus


# ==================== Fixtures ====================


@pytest_asyncio.fixture
async def designer_user(db_session):
    """Create a designer user."""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        phone_number="09125550001",
        password_hash=get_password_hash("designer123"),
        first_name="Designer",
        last_name="User",
        full_name="Designer User",
        role=UserRole.DESIGNER,
        phone_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def designer_headers(designer_user):
    """Auth headers for designer."""
    token = create_admin_token(str(designer_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def customer_user(db_session):
    """Create a customer user."""
    return await create_test_web_user(db_session, {
        "phone_number": "09125550002",
        "password_hash": "hashed",
        "first_name": "Customer",
        "last_name": "One",
        "full_name": "Customer One",
        "role": UserRole.CUSTOMER,
        "phone_verified": True,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def category(db_session):
    """Create a test category."""
    return await create_test_category(db_session, {
        "slug": "val-test-cat",
        "name_fa": "دسته تست ولیدیشن",
        "base_price": 50000,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def validation_order(db_session, customer_user, category):
    """Create an order with validation_requested=True in AWAITING_VALIDATION."""
    return await create_test_order(db_session, customer_user, category, {
        "status": OrderStatus.AWAITING_VALIDATION,
        "validation_requested": True,
        "validation_price": Decimal("30000"),
    })


# ==================== Tests ====================


@pytest.mark.asyncio
async def test_designer_list_validations(client, designer_headers, validation_order):
    """Designer can list validation requests."""
    resp = await client.get("/api/v1/designer/validations", headers=designer_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(item["id"] == str(validation_order.id) for item in data["items"])


@pytest.mark.asyncio
async def test_designer_list_validations_with_filter(client, designer_headers, validation_order):
    """Designer can filter validation requests by status."""
    resp = await client.get(
        "/api/v1/designer/validations?status=PENDING",
        headers=designer_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_designer_approve_validation(client, designer_headers, validation_order, designer_user):
    """Designer can approve a validation request."""
    resp = await client.post(
        f"/api/v1/designer/validations/{validation_order.id}/approve",
        headers=designer_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["validation_status"] == "PASSED"


@pytest.mark.asyncio
async def test_designer_reject_validation(client, designer_headers, validation_order, designer_user):
    """Designer can reject a validation request with comment."""
    resp = await client.post(
        f"/api/v1/designer/validations/{validation_order.id}/reject",
        headers=designer_headers,
        json={"comment": "لطفا رزولوشن را افزایش دهید"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["validation_status"] == "FAILED"
    assert data["comment"] == "لطفا رزولوشن را افزایش دهید"


@pytest.mark.asyncio
async def test_designer_approve_nonexistent_order(client, designer_headers):
    """Approving a non-existent order returns 404."""
    fake_id = uuid4()
    resp = await client.post(
        f"/api/v1/designer/validations/{fake_id}/approve",
        headers=designer_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_non_designer_cannot_access_validations(client, db_session):
    """Non-designer user gets 403 when accessing designer validation endpoints."""
    customer = await create_test_web_user(db_session, {
        "phone_number": "09125550099",
        "password_hash": "hashed",
        "first_name": "Cust",
        "last_name": "User",
        "full_name": "Cust User",
        "role": UserRole.CUSTOMER,
        "phone_verified": True,
        "is_active": True,
    })
    token = create_admin_token(str(customer.id))
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/designer/validations", headers=headers)
    assert resp.status_code == 403
