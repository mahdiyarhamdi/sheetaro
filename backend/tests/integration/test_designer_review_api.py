"""Integration tests for designer review functionality."""

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal

from tests.conftest import (
    create_test_web_user,
    create_test_category,
    create_test_order,
    create_admin_token,
)
from app.models.enums import UserRole, OrderStatus


# ==================== Fixtures ====================


@pytest_asyncio.fixture
async def designer_user(db_session):
    """Create a designer user."""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        phone_number="09126660001",
        password_hash=get_password_hash("designer123"),
        first_name="Designer",
        last_name="Review",
        full_name="Designer Review",
        role=UserRole.DESIGNER,
        phone_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def customer_user(db_session):
    """Create a customer user."""
    return await create_test_web_user(db_session, {
        "phone_number": "09126660002",
        "password_hash": "hashed",
        "first_name": "Review",
        "last_name": "Customer",
        "full_name": "Review Customer",
        "role": UserRole.CUSTOMER,
        "phone_verified": True,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def customer_headers(customer_user):
    """Auth headers for customer."""
    token = create_admin_token(str(customer_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def printshop_user(db_session):
    """Create a printshop user."""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        phone_number="09126660003",
        password_hash=get_password_hash("printshop123"),
        first_name="PrintShop",
        last_name="Review",
        full_name="PrintShop Review",
        role=UserRole.PRINT_SHOP,
        phone_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def category(db_session):
    """Create a test category."""
    return await create_test_category(db_session, {
        "slug": "review-test-cat",
        "name_fa": "دسته تست نظر",
        "base_price": 50000,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def delivered_order_with_designer(db_session, customer_user, category, printshop_user, designer_user):
    """Create a DELIVERED order with both printshop and designer assigned."""
    return await create_test_order(db_session, customer_user, category, {
        "status": OrderStatus.DELIVERED,
        "assigned_printshop_id": printshop_user.id,
        "assigned_designer_id": designer_user.id,
    })


@pytest_asyncio.fixture
async def delivered_order_no_designer(db_session, customer_user, category, printshop_user):
    """Create a DELIVERED order with only printshop assigned."""
    return await create_test_order(db_session, customer_user, category, {
        "status": OrderStatus.DELIVERED,
        "assigned_printshop_id": printshop_user.id,
    })


# ==================== Tests ====================


@pytest.mark.asyncio
async def test_submit_printshop_review(client, customer_headers, delivered_order_with_designer):
    """Customer can submit a printshop review."""
    resp = await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 4, "comment": "خوب بود", "review_type": "PRINTSHOP"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 4
    assert data["review_type"] == "PRINTSHOP"


@pytest.mark.asyncio
async def test_submit_designer_review(client, customer_headers, delivered_order_with_designer):
    """Customer can submit a designer review."""
    resp = await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 5, "comment": "طراحی عالی", "review_type": "DESIGNER"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 5
    assert data["review_type"] == "DESIGNER"


@pytest.mark.asyncio
async def test_submit_both_reviews_for_same_order(client, customer_headers, delivered_order_with_designer):
    """Customer can submit both printshop and designer reviews for same order."""
    # Printshop review
    resp1 = await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 4, "review_type": "PRINTSHOP"},
    )
    assert resp1.status_code == 201

    # Designer review
    resp2 = await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 5, "review_type": "DESIGNER"},
    )
    assert resp2.status_code == 201


@pytest.mark.asyncio
async def test_cannot_submit_duplicate_review_type(client, customer_headers, delivered_order_with_designer):
    """Cannot submit two reviews of the same type for one order."""
    await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 4, "review_type": "PRINTSHOP"},
    )

    resp = await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 3, "review_type": "PRINTSHOP"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_cannot_submit_designer_review_without_designer(client, customer_headers, delivered_order_no_designer):
    """Cannot submit designer review if order has no designer."""
    resp = await client.post(
        f"/api/v1/orders/{delivered_order_no_designer.id}/review",
        headers=customer_headers,
        json={"rating": 5, "review_type": "DESIGNER"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_all_reviews_for_order(client, customer_headers, delivered_order_with_designer):
    """Get all reviews (printshop + designer) for an order."""
    # Submit both
    await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 4, "review_type": "PRINTSHOP"},
    )
    await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 5, "review_type": "DESIGNER"},
    )

    resp = await client.get(
        f"/api/v1/orders/{delivered_order_with_designer.id}/reviews",
        headers=customer_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    types = {r["review_type"] for r in data}
    assert types == {"PRINTSHOP", "DESIGNER"}


@pytest.mark.asyncio
async def test_get_review_by_type(client, customer_headers, delivered_order_with_designer):
    """Get a specific review by type."""
    await client.post(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review",
        headers=customer_headers,
        json={"rating": 4, "review_type": "PRINTSHOP"},
    )

    resp = await client.get(
        f"/api/v1/orders/{delivered_order_with_designer.id}/review?review_type=PRINTSHOP",
        headers=customer_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["review_type"] == "PRINTSHOP"
    assert data["rating"] == 4
