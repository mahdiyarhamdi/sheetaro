# ARCHITECTURE.md - Sheetaro Backend Architecture

## Overview

Sheetaro backend is a FastAPI application for a **multi-role print ordering system** (labels and invoices) following clean architecture principles with a layered structure.

### Key Features
- Multi-role system: Customer, Designer, Validator, Print Shop, Admin
- Design plans: Public (free), Semi-private, Private
- File validation and processing
- Order workflow management
- Payment integration
- Invoice generation (post-purchase)

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | ~0.115 |
| ORM | SQLAlchemy | ~2.0 (async) |
| Migrations | Alembic | ~1.13 |
| Validation | Pydantic | v2.9 |
| Database | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Auth | python-jose | ~3.3 |
| HTTP Client | httpx | ~0.27 |
| File Storage | S3-Compatible | - |
| PDF Generation | (TBD) | - |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Telegram Bot                                │
│                    (python-telegram-bot)                            │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP (httpx)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    API Layer (Routers)                        │   │
│  │   • Input/output handling                                     │   │
│  │   • Request validation (Pydantic)                             │   │
│  │   • HTTP status codes                                         │   │
│  │   • No business logic                                         │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐   │
│  │                    Service Layer                              │   │
│  │   • Business logic                                            │   │
│  │   • Validation rules                                          │   │
│  │   • Event logging                                             │   │
│  │   • Orchestration                                             │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐   │
│  │                    Repository Layer                           │   │
│  │   • Database operations (CRUD)                                │   │
│  │   • Query building                                            │   │
│  │   • No business logic                                         │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐   │
│  │                    Data Layer (Models)                        │   │
│  │   • SQLAlchemy ORM models                                     │   │
│  │   • Table definitions                                         │   │
│  │   • Relationships                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Storage                                │
│   ┌─────────────────┐              ┌─────────────────┐              │
│   │   PostgreSQL    │              │     Redis       │              │
│   │   (Primary DB)  │              │   (Cache/Rate)  │              │
│   └─────────────────┘              └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration template
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Shared dependencies (DB session, auth)
│   │   └── routers/            # API route handlers
│   │       ├── health.py       # Health check
│   │       ├── users.py        # User CRUD
│   │       ├── products.py     # Product catalog
│   │       ├── orders.py       # Order management
│   │       ├── payments.py     # Payment processing
│   │       ├── validation.py   # Design validation
│   │       ├── invoices.py     # Invoice generation
│   │       ├── subscriptions.py # Subscription management
│   │       └── files.py        # File upload
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── database.py         # DB engine & session factory
│   │   └── security.py         # JWT, password hashing
│   ├── models/
│   │   ├── enums.py            # All enums (UserRole, OrderStatus, etc.)
│   │   ├── user.py             # User model
│   │   ├── product.py          # Product model
│   │   ├── order.py            # Order model
│   │   ├── payment.py          # Payment model
│   │   ├── validation.py       # ValidationReport model
│   │   ├── invoice.py          # Invoice model
│   │   └── subscription.py     # Subscription model
│   ├── repositories/           # Database CRUD operations
│   │   ├── user_repository.py
│   │   ├── product_repository.py
│   │   ├── order_repository.py
│   │   ├── payment_repository.py
│   │   ├── validation_repository.py
│   │   ├── invoice_repository.py
│   │   └── subscription_repository.py
│   ├── schemas/                # Pydantic schemas (Create/Update/Out)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── validation.py
│   │   ├── invoice.py
│   │   ├── subscription.py
│   │   └── file.py
│   ├── services/               # Business logic
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── validation_service.py
│   │   ├── invoice_service.py
│   │   ├── subscription_service.py
│   │   └── file_service.py
│   └── utils/
│       ├── logger.py           # Structured JSON logging
│       └── validators.py       # Shared validation functions
├── tests/
│   ├── conftest.py             # Test fixtures
│   ├── unit/                   # Unit tests for services
│   ├── integration/            # API endpoint tests
│   └── e2e/                    # End-to-end flow tests
├── alembic.ini
├── pytest.ini
├── Dockerfile
└── requirements.txt
```

---

## Request Flow

```
HTTP Request
    │
    ▼
┌─────────────────┐
│   Middleware    │ ← CORS, Exception handlers
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Router      │ ← Validate input (Pydantic schema)
│   (users.py)    │   Return HTTPException on error
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Service      │ ← Business logic, logging
│ (user_service)  │   Transform data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Repository    │ ← CRUD operations
│  (user_repo)    │   SQLAlchemy queries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │ ← PostgreSQL (async)
└─────────────────┘
```

---

## Layer Responsibilities

### API Layer (`api/routers/`)

- HTTP request/response handling
- Input validation via Pydantic schemas
- Status code management (201, 404, etc.)
- **NO** business logic

```python
# Good
@router.post("/users", status_code=201)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.create_user(user_data)

# Bad - business logic in router
@router.post("/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await db.query(User).filter(...).first():  # ❌ Don't do this
        raise HTTPException(409, "User exists")
```

### Service Layer (`services/`)

- Business logic and rules
- Data transformation
- Event logging
- Orchestration between repositories

```python
class UserService:
    async def create_or_update_user(self, user_data: UserCreate) -> UserOut:
        user = await self.repository.create_or_update(user_data)
        log_event("user.signup", telegram_id=user.telegram_id)  # Logging
        return UserOut.model_validate(user)  # Transformation
```

### Repository Layer (`repositories/`)

- Database CRUD operations
- Query building
- **NO** business logic

```python
class UserRepository:
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
```

### Model Layer (`models/`)

- SQLAlchemy ORM definitions
- Table columns and types
- Relationships (when needed)

---

## Coding Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Variables/Functions | snake_case | `get_user_by_id` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_SNAKE | `MAX_PAGE_SIZE` |
| Database Tables | singular | `user`, `order` |
| API Paths | plural, kebab-case | `/api/v1/users` |

### Type Hints

All functions MUST have type hints:

```python
# Good
async def get_user(telegram_id: int) -> Optional[UserOut]:
    ...

# Bad
async def get_user(telegram_id):
    ...
```

### Docstrings

One-line docstring for every public function:

```python
async def create_user(self, user_data: UserCreate) -> UserOut:
    """Create a new user or update existing by telegram_id."""
    ...
```

### Error Handling

- Exceptions raised in service layer
- Converted to HTTPException in router
- Standard HTTP status codes

```python
# Service
if not user:
    raise ValueError("User not found")

# Router
try:
    return await service.get_user(telegram_id)
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

---

## Database

### Connection

- Async engine with `asyncpg` driver
- Connection pooling (10 connections, 20 overflow)
- Session per request via dependency injection

```python
# database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
```

### Migrations

All schema changes require Alembic migration:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Logging

Structured JSON logging for all events:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "level": "INFO",
  "event_type": "user.signup",
  "telegram_id": 123456,
  "user_id": "uuid-here"
}
```

Required events to log:
- `user.signup` - New user registration
- `user.login` - User authenticated
- `user.update` - Profile updated
- `order.create` - New order
- `order.status_change` - Order status update

---

## Security

### Environment Variables

All secrets via environment:

```bash
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=<random-32-bytes>
TELEGRAM_BOT_TOKEN=<from-botfather>
```

### CORS

Restricted to allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # From env
    allow_credentials=True,
)
```

### Input Validation

All inputs validated via Pydantic:

```python
class UserCreate(BaseModel):
    telegram_id: int = Field(..., description="Telegram user ID")
    phone_number: str | None = Field(None, max_length=20)
    
    @field_validator('phone_number')
    def validate_phone(cls, v):
        return validate_iranian_phone(v)
```

---

## Testing (Future)

Test structure:

```
tests/
├── conftest.py          # Fixtures
├── test_api/
│   └── test_users.py    # API endpoint tests
├── test_services/
│   └── test_user_service.py
└── test_repositories/
    └── test_user_repo.py
```

---

## Deployment

### Docker Compose (Development)

```bash
docker-compose up --build
```

### Production Checklist

- [ ] Remove port exposures for DB/Redis
- [ ] Use production SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Configure proper CORS origins
- [ ] Set up log aggregation
- [ ] Configure health check monitoring

---

**Last Updated**: 2024-12-13


