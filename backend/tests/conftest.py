"""Test fixtures and configuration."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.core.database import Base
from app.core.config import settings
from app.main import app
from app.api.deps import get_db
from app.models.enums import UserRole, ProductType, MaterialType, DesignPlan

# Test database URL (use a separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/sheetaro", "/sheetaro_test")


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

