"""Test fixtures and configuration."""

import os

# Set environment variables BEFORE any app imports
# This is critical to avoid pydantic validation errors
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://sheetaro:sheetaro@localhost:5432/sheetaro_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("DEBUG", "true")

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
import re

from app.core.database import Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.main import app
from app.api.deps import get_db
from app.models.enums import UserRole, ProductType, MaterialType, DesignPlan

# Test database URL (use a separate test database)
# Only replace the database name at the end of the URL, not the username
TEST_DATABASE_URL = re.sub(r'/sheetaro$', '/sheetaro_test', settings.DATABASE_URL)

# SQL to create enum types needed for tests
CREATE_ENUMS_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('CUSTOMER', 'DESIGNER', 'VALIDATOR', 'PRINT_SHOP', 'ADMIN');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'producttype') THEN
        CREATE TYPE producttype AS ENUM ('LABEL', 'INVOICE');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'materialtype') THEN
        CREATE TYPE materialtype AS ENUM ('PAPER', 'PVC', 'METALLIC');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'designplan') THEN
        CREATE TYPE designplan AS ENUM ('PUBLIC', 'SEMI_PRIVATE', 'PRIVATE', 'OWN_DESIGN');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus') THEN
        CREATE TYPE orderstatus AS ENUM ('PENDING', 'AWAITING_VALIDATION', 'NEEDS_ACTION', 'DESIGNING', 'READY_FOR_PRINT', 'PRINTING', 'SHIPPED', 'DELIVERED', 'CANCELLED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'validationstatus') THEN
        CREATE TYPE validationstatus AS ENUM ('PENDING', 'PASSED', 'FAILED', 'FIXED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymenttype') THEN
        CREATE TYPE paymenttype AS ENUM ('VALIDATION', 'DESIGN', 'FIX', 'PRINT', 'SUBSCRIPTION');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus') THEN
        CREATE TYPE paymentstatus AS ENUM ('PENDING', 'AWAITING_APPROVAL', 'SUCCESS', 'FAILED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscriptionplan') THEN
        CREATE TYPE subscriptionplan AS ENUM ('ADVANCED_SEARCH');
    END IF;
    -- Dynamic category system enums
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attributeinputtype') THEN
        CREATE TYPE attributeinputtype AS ENUM ('TEXT', 'SELECT', 'NUMBER', 'BOOLEAN');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'designplantype') THEN
        CREATE TYPE designplantype AS ENUM ('PUBLIC', 'SEMI_PRIVATE', 'PRIVATE', 'OWN_DESIGN');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'questioninputtype') THEN
        CREATE TYPE questioninputtype AS ENUM ('TEXT', 'TEXTAREA', 'NUMBER', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'IMAGE_UPLOAD', 'FILE_UPLOAD', 'COLOR_PICKER', 'DATE_PICKER', 'SCALE');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'steptype') THEN
        CREATE TYPE steptype AS ENUM ('VALIDATION', 'PAYMENT', 'DESIGN', 'PRINT', 'SHIPPING');
    END IF;
END
$$;
"""


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    
    async with engine.begin() as conn:
        # Create enum types first
        await conn.execute(text(CREATE_ENUMS_SQL))
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with transaction rollback."""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with overridden dependencies."""
    
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ==================== Sample Data Fixtures ====================

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "09121234567",
        "city": "Tehran",
        "address": "Test Address",
        "role": UserRole.CUSTOMER.value,
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "type": ProductType.LABEL.value,
        "name": "Test Label",
        "name_fa": "لیبل تست",
        "description": "A test label product",
        "size": "5x5cm",
        "material": MaterialType.PAPER.value,
        "base_price": 10000,
        "min_quantity": 100,
        "is_active": True,
        "sort_order": 1,
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "design_plan": DesignPlan.PUBLIC.value,
        "quantity": 100,
        "validation_requested": False,
        "shipping_address": "Test Shipping Address",
        "customer_notes": "Test notes",
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment initiation data for testing."""
    return {
        "type": "PRINT",
        "callback_url": "https://example.com/callback",
    }


@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    from datetime import date
    return {
        "customer_name": "Test Customer",
        "customer_code": "CUST001",
        "customer_address": "Test Address",
        "customer_phone": "09121234567",
        "items": [
            {
                "description": "Test Item",
                "quantity": 10,
                "unit_price": 10000,
                "total": 100000,
            }
        ],
        "tax_amount": 9000,
        "discount_amount": 0,
        "issue_date": date.today().isoformat(),
    }


@pytest.fixture
def sample_validation_report_data():
    """Sample validation report data for testing."""
    return {
        "issues": [
            {
                "type": "resolution",
                "severity": "high",
                "description": "Resolution too low",
                "suggestion": "Increase to 300 DPI",
            }
        ],
        "fix_cost": 150000,
        "summary": "File needs resolution fix",
        "passed": "FAILED",
    }


# ==================== Helper Functions ====================

async def create_test_user(db_session: AsyncSession, data: dict = None) -> dict:
    """Create a test user and return its data."""
    from app.models.user import User
    
    user_data = data or {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": UserRole.CUSTOMER,
    }
    
    if isinstance(user_data.get("role"), str):
        user_data["role"] = UserRole(user_data["role"])
    
    user = User(**user_data)
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


async def create_test_product(db_session: AsyncSession, data: dict = None) -> dict:
    """Create a test product and return its data."""
    from app.models.product import Product
    
    product_data = data or {
        "type": ProductType.LABEL,
        "name": "Test Label",
        "size": "5x5cm",
        "base_price": Decimal("10000"),
    }
    
    if isinstance(product_data.get("type"), str):
        product_data["type"] = ProductType(product_data["type"])
    if isinstance(product_data.get("material"), str):
        product_data["material"] = MaterialType(product_data["material"])
    
    product = Product(**product_data)
    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)
    return product


# ==================== Dynamic Category System Fixtures ====================

async def create_test_category(db_session: AsyncSession, data: dict = None):
    """Create a test category for dynamic product system."""
    from app.models.category import Category
    
    category_data = data or {
        "slug": "test-category",
        "name_fa": "دسته تست",
        "description_fa": "توضیحات تست",
        "sort_order": 1,
        "is_active": True,
    }
    
    category = Category(**category_data)
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


async def create_test_plan_with_questionnaire(db_session: AsyncSession, category, data: dict = None):
    """Create a plan configured for semi-private (has_questionnaire=True)."""
    from app.models.design_plan import CategoryDesignPlan
    from app.models.design_plan import DesignPlanType
    
    plan_data = data or {
        "category_id": category.id,
        "slug": "semi-private",
        "name_fa": "نیمه‌خصوصی",
        "has_questionnaire": True,
        "has_templates": False,
        "price": Decimal("600000"),
        "sort_order": 1,
        "is_active": True,
    }
    
    plan = CategoryDesignPlan(**plan_data)
    db_session.add(plan)
    await db_session.flush()
    await db_session.refresh(plan)
    return plan


async def create_test_plan_with_templates(db_session: AsyncSession, category, data: dict = None):
    """Create a plan configured for public (has_templates=True)."""
    from app.models.design_plan import CategoryDesignPlan
    
    plan_data = data or {
        "category_id": category.id,
        "slug": "public",
        "name_fa": "عمومی",
        "description_fa": "پلن عمومی با قالب",
        "has_questionnaire": False,
        "has_templates": True,
        "price": Decimal("0"),
        "sort_order": 1,
        "is_active": True,
    }
    
    plan = CategoryDesignPlan(**plan_data)
    db_session.add(plan)
    await db_session.flush()
    await db_session.refresh(plan)
    return plan


async def create_test_section(db_session: AsyncSession, plan, data: dict = None):
    """Create a question section for testing."""
    from app.models.question_section import QuestionSection
    
    section_data = data or {
        "plan_id": plan.id,
        "title_fa": "بخش تست",
        "description_fa": "توضیحات بخش تست",
        "sort_order": 1,
        "is_active": True,
    }
    
    section = QuestionSection(**section_data)
    db_session.add(section)
    await db_session.flush()
    await db_session.refresh(section)
    return section


async def create_test_questions(db_session: AsyncSession, plan, section=None, count: int = 3):
    """Create multiple questions of different types."""
    from app.models.design_question import DesignQuestion, QuestionOption, QuestionInputType
    
    questions = []
    question_types = [
        (QuestionInputType.TEXT, "نام برند خود را وارد کنید"),
        (QuestionInputType.SINGLE_CHOICE, "نوع جنس را انتخاب کنید"),
        (QuestionInputType.COLOR_PICKER, "رنگ پس‌زمینه را انتخاب کنید"),
    ]
    
    for i in range(min(count, len(question_types))):
        input_type, question_text = question_types[i]
        
        question = DesignQuestion(
            plan_id=plan.id,
            section_id=section.id if section else None,
            question_fa=question_text,
            input_type=input_type,
            is_required=True,
            sort_order=i + 1,
            is_active=True,
        )
        db_session.add(question)
        await db_session.flush()
        await db_session.refresh(question)
        
        # Add options for choice questions
        if input_type == QuestionInputType.SINGLE_CHOICE:
            for j, (value, label) in enumerate([("paper", "کاغذی"), ("pvc", "پی وی سی")]):
                option = QuestionOption(
                    question_id=question.id,
                    value=value,
                    label_fa=label,
                    sort_order=j + 1,
                    is_active=True,
                )
                db_session.add(option)
            await db_session.flush()
        
        questions.append(question)
    
    return questions


async def create_test_template(db_session: AsyncSession, plan, data: dict = None):
    """Create a template with placeholder coordinates."""
    from app.models.design_template import DesignTemplate
    
    template_data = data or {
        "plan_id": plan.id,
        "name_fa": "قالب تست",
        "preview_url": "https://example.com/preview.png",
        "file_url": "https://example.com/template.png",
        "image_width": 1000,
        "image_height": 800,
        "placeholder_x": 100,
        "placeholder_y": 100,
        "placeholder_width": 200,
        "placeholder_height": 200,
        "sort_order": 1,
        "is_active": True,
    }
    
    template = DesignTemplate(**template_data)
    db_session.add(template)
    await db_session.flush()
    await db_session.refresh(template)
    return template


# ==================== Pytest Fixtures ====================

@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "slug": "labels",
        "name_fa": "لیبل",
        "description_fa": "انواع لیبل چاپی",
        "sort_order": 1,
        "is_active": True,
    }


@pytest.fixture
def sample_plan_data():
    """Sample plan data for testing."""
    return {
        "slug": "semi-private",
        "name_fa": "نیمه‌خصوصی",
        "plan_type": "SEMI_PRIVATE",
        "has_questionnaire": True,
        "has_templates": False,
        "price": 600000,
        "sort_order": 1,
    }


@pytest.fixture
def sample_section_data():
    """Sample section data for testing."""
    return {
        "title_fa": "اطلاعات طراحی",
        "description_fa": "در این بخش اطلاعات طراحی را وارد کنید",
        "sort_order": 1,
    }


@pytest.fixture
def sample_question_data():
    """Sample question data for testing."""
    return {
        "question_fa": "نام برند خود را وارد کنید",
        "input_type": "TEXT",
        "is_required": True,
        "placeholder_fa": "مثال: برند من",
        "sort_order": 1,
    }


@pytest.fixture
def sample_template_data():
    """Sample template data for testing."""
    return {
        "name_fa": "قالب ساده",
        "preview_url": "https://example.com/preview.png",
        "file_url": "https://example.com/template.png",
        "placeholder_x": 100,
        "placeholder_y": 100,
        "placeholder_width": 200,
        "placeholder_height": 200,
        "sort_order": 1,
    }


# ==================== Web Auth Fixtures ====================

@pytest.fixture
def sample_web_user_data():
    """Sample web user registration data."""
    return {
        "phone": "09121234567",
        "password": "test123456",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_login_data():
    """Sample login data."""
    return {
        "phone": "09121234567",
        "password": "test123456"
    }


@pytest_asyncio.fixture
async def authenticated_user(client, db_session, sample_web_user_data):
    """Create and return authenticated user with tokens."""
    response = await client.post("/api/v1/auth/register", json=sample_web_user_data)
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(authenticated_user):
    """Get authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


async def create_test_web_user(db_session: AsyncSession, data: dict = None):
    """Create a test web user and return its data."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user_data = data or {
        "phone_number": "09121234567",
        "password_hash": get_password_hash("test123456"),
        "first_name": "Test",
        "last_name": "User",
        "full_name": "Test User",
        "role": UserRole.CUSTOMER,
        "phone_verified": False,
        "web_linked": False,
    }
    
    if isinstance(user_data.get("role"), str):
        user_data["role"] = UserRole(user_data["role"])
    
    user = User(**user_data)
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


# ==================== Admin Testing Fixtures ====================

async def create_test_admin_user(db_session: AsyncSession, data: dict = None):
    """Create a test admin user for admin API tests."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user_data = data or {
        "phone_number": "09120000000",
        "password_hash": get_password_hash("admin123456"),
        "first_name": "Admin",
        "last_name": "User",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "phone_verified": True,
        "web_linked": False,
        "is_active": True,
    }
    
    if isinstance(user_data.get("role"), str):
        user_data["role"] = UserRole(user_data["role"])
    
    user = User(**user_data)
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


async def create_test_order(db_session: AsyncSession, user, product, data: dict = None):
    """Create a test order for admin API tests."""
    from app.models.order import Order
    from app.models.enums import DesignPlan, OrderStatus
    
    order_data = {
        "user_id": user.id,
        "product_id": product.id,
        "design_plan": DesignPlan.PUBLIC,
        "status": OrderStatus.PENDING,
        "quantity": 100,
        "total_price": Decimal("50000"),
        "design_price": Decimal("0"),
        "validation_price": Decimal("0"),
        "fix_price": Decimal("0"),
        "print_price": Decimal("50000"),
        "validation_requested": False,
    }
    
    if data:
        order_data.update(data)
    
    if isinstance(order_data.get("design_plan"), str):
        order_data["design_plan"] = DesignPlan(order_data["design_plan"])
    if isinstance(order_data.get("status"), str):
        order_data["status"] = OrderStatus(order_data["status"])
    
    order = Order(**order_data)
    db_session.add(order)
    await db_session.flush()
    await db_session.refresh(order)
    return order


async def create_test_payment(db_session: AsyncSession, order, user, data: dict = None):
    """Create a test payment for admin API tests."""
    from app.models.payment import Payment
    from app.models.enums import PaymentType, PaymentStatus
    
    payment_data = {
        "order_id": order.id,
        "user_id": user.id,
        "type": PaymentType.PRINT,
        "amount": Decimal("50000"),
        "status": PaymentStatus.PENDING,
    }
    
    if data:
        payment_data.update(data)
    
    if isinstance(payment_data.get("type"), str):
        payment_data["type"] = PaymentType(payment_data["type"])
    if isinstance(payment_data.get("status"), str):
        payment_data["status"] = PaymentStatus(payment_data["status"])
    
    payment = Payment(**payment_data)
    db_session.add(payment)
    await db_session.flush()
    await db_session.refresh(payment)
    return payment


def create_admin_token(user_id: str) -> str:
    """Create a JWT access token for admin testing."""
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    from app.core.config import settings
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=30)
    
    to_encode = {
        "sub": user_id,
        "type": "access",
        "exp": expire,
        "iat": now,
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


@pytest_asyncio.fixture
async def admin_user(db_session):
    """Create an admin user for testing."""
    return await create_test_admin_user(db_session)


@pytest_asyncio.fixture
async def admin_token(admin_user):
    """Get access token for admin user."""
    return create_admin_token(str(admin_user.id))


@pytest_asyncio.fixture
async def admin_headers(admin_token):
    """Get authorization headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def regular_web_user(db_session):
    """Create a regular (non-admin) web user for testing."""
    return await create_test_web_user(db_session, {
        "phone_number": "09121111111",
        "password_hash": get_password_hash("user123456"),
        "first_name": "Regular",
        "last_name": "User",
        "full_name": "Regular User",
        "role": UserRole.CUSTOMER,
        "phone_verified": True,
        "web_linked": False,
        "is_active": True,
    })


@pytest_asyncio.fixture
async def regular_user_token(regular_web_user):
    """Get access token for regular user."""
    return create_admin_token(str(regular_web_user.id))


@pytest_asyncio.fixture
async def regular_user_headers(regular_user_token):
    """Get authorization headers for regular user requests."""
    return {"Authorization": f"Bearer {regular_user_token}"}


@pytest_asyncio.fixture
async def test_product(db_session):
    """Create a test product for order tests."""
    return await create_test_product(db_session)


@pytest_asyncio.fixture
async def test_order(db_session, regular_web_user, test_product):
    """Create a test order for admin tests."""
    return await create_test_order(db_session, regular_web_user, test_product)


@pytest_asyncio.fixture
async def test_payment(db_session, test_order, regular_web_user):
    """Create a test payment for admin tests."""
    return await create_test_payment(db_session, test_order, regular_web_user)

