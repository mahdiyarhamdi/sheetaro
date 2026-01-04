# ARCHITECTURE.md - Sheetaro Backend Architecture

## Overview

Sheetaro backend is a FastAPI application for a **multi-role print ordering system** (labels and invoices) following clean architecture principles with a layered structure.

### Key Features
- Multi-role system: Customer, Designer, Validator, Print Shop, Admin
- **Dynamic product catalog**: Admin can define categories, attributes, design plans
- Design plans: Public (free templates), Semi-private (questionnaire), Private
- Template system with auto logo placement for public plans
- Questionnaire system for semi-private plan design requirements
- File validation and processing
- Order workflow management
- Card-to-card payment with receipt upload and admin approval
- Admin management (promote via `/makeadmin` command)
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
| Rate Limiting | slowapi | ~0.1.9 |
| File Storage | S3-Compatible | - |
| Image Processing | Pillow | ~10.4 |
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
│   ├── exceptions.py           # Custom exceptions (SheetaroException hierarchy)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Shared dependencies (DB session, auth)
│   │   └── routers/            # API route handlers
│   │       ├── health.py       # Health check
│   │       ├── users.py        # User CRUD + Admin management
│   │       ├── products.py     # Product catalog (legacy)
│   │       ├── categories.py   # Dynamic catalog management
│   │       ├── attributes.py   # Category attributes
│   │       ├── design_plans.py # Design plans per category
│   │       ├── questions.py    # Questionnaire for semi-private
│   │       ├── templates.py    # Templates for public plans
│   │       ├── orders.py       # Order management
│   │       ├── payments.py     # Payment (card-to-card + approval)
│   │       ├── validation.py   # Design validation
│   │       ├── invoices.py     # Invoice generation
│   │       ├── subscriptions.py # Subscription management
│   │       ├── files.py        # File upload
│   │       └── settings.py     # System settings (payment card)
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── database.py         # DB engine, session factory, UnitOfWork
│   │   ├── security.py         # JWT, password hashing
│   │   └── rate_limit.py       # Rate limiting (slowapi + Redis)
│   ├── models/
│   │   ├── enums.py            # All enums (UserRole, OrderStatus, etc.)
│   │   ├── user.py             # User model
│   │   ├── product.py          # Product model (legacy)
│   │   ├── category.py         # Category model (dynamic catalog)
│   │   ├── attribute.py        # CategoryAttribute and AttributeOption
│   │   ├── design_plan.py      # CategoryDesignPlan model
│   │   ├── design_question.py  # DesignQuestion and QuestionOption
│   │   ├── design_template.py  # DesignTemplate with placeholder info
│   │   ├── order_step.py       # OrderStepTemplate model
│   │   ├── question_answer.py  # QuestionAnswer model
│   │   ├── order.py            # Order model
│   │   ├── payment.py          # Payment model (with card-to-card fields)
│   │   ├── validation.py       # ValidationReport model
│   │   ├── invoice.py          # Invoice model
│   │   ├── subscription.py     # Subscription model
│   │   └── settings.py         # SystemSettings model (key-value config)
│   ├── repositories/           # Database CRUD operations
│   │   ├── user_repository.py      # + admin management
│   │   ├── product_repository.py
│   │   ├── order_repository.py
│   │   ├── payment_repository.py   # + receipt upload, approve/reject
│   │   ├── validation_repository.py
│   │   ├── invoice_repository.py
│   │   ├── subscription_repository.py
│   │   └── settings_repository.py  # Key-value settings
│   ├── schemas/                # Pydantic schemas (Create/Update/Out)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py          # + receipt upload, approval schemas
│   │   ├── validation.py
│   │   ├── invoice.py
│   │   ├── subscription.py
│   │   ├── file.py
│   │   └── settings.py         # Payment card info schemas
│   ├── services/               # Business logic
│   │   ├── user_service.py         # + promote/demote admin
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py      # + card-to-card flow
│   │   ├── validation_service.py
│   │   ├── invoice_service.py
│   │   ├── subscription_service.py
│   │   ├── file_service.py
│   │   └── settings_service.py     # Payment card settings
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

## Card-to-Card Payment Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Customer   │     │   Backend    │     │    Admin     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1. Request Payment │                    │
       ├───────────────────>│                    │
       │                    │                    │
       │ 2. Get Card Info   │                    │
       │<───────────────────│                    │
       │   (card number,    │                    │
       │    holder name)    │                    │
       │                    │                    │
       │ 3. Upload Receipt  │                    │
       ├───────────────────>│                    │
       │                    │                    │
       │ Status: AWAITING   │ 4. Notify Admin   │
       │   _APPROVAL        ├───────────────────>│
       │                    │                    │
       │                    │ 5. Approve/Reject │
       │                    │<───────────────────│
       │                    │                    │
       │ 6. Notify Result   │                    │
       │<───────────────────│                    │
       │                    │                    │
```

### Payment Status Flow

```
PENDING ──(upload receipt)──> AWAITING_APPROVAL ──(approve)──> SUCCESS
                                    │
                                    └──(reject)──> FAILED
                                                     │
                                                     └──(re-upload)──> AWAITING_APPROVAL
```

---

## Admin Management

Any user can become admin by sending `/makeadmin` command in Telegram bot.

Once admin, they can:
- View list of all admins
- Demote other admins (except the last one)
- Manage dynamic product catalog (categories, attributes, plans)
- Manage design templates and questionnaires
- Approve/reject payments

Admin telegram IDs are stored in database (not environment variables).

---

## Dynamic Product Catalog

The system supports dynamic product catalog management:

### Entity Relationships

```
Category (e.g., "Label")
    │
    ├── CategoryAttribute (e.g., "Size", "Material")
    │   └── AttributeOption (e.g., "5x5cm", "10x10cm")
    │
    ├── CategoryDesignPlan (e.g., "Public", "Semi-Private")
    │   │
    │   ├── [if has_questionnaire] QuestionSection (e.g., "Brand Info", "Design Preferences")
    │   │   └── DesignQuestion (e.g., "Brand Name", "Preferred Colors")
    │   │       ├── validation_rules (min_length, max_value, pattern, etc.)
    │   │       ├── depends_on_question_id (conditional logic)
    │   │       └── QuestionOption (for SINGLE_CHOICE, MULTI_CHOICE)
    │   │
    │   └── [if has_templates] DesignTemplate
    │       ├── image_url, image_width, image_height
    │       ├── placeholder_x, placeholder_y, placeholder_width, placeholder_height
    │       └── preview_url (with red square showing placeholder)
    │
    ├── OrderStepTemplate (e.g., "validation", "payment")
    │
    └── Order
        ├── QuestionAnswer (stores questionnaire responses)
        └── ProcessedDesign (stores final design from template + logo)
```

### Design Plans

| Plan Type | has_questionnaire | has_templates | Description |
|-----------|-------------------|---------------|-------------|
| PUBLIC | ❌ | ✅ | Free, user selects from ready templates and uploads logo |
| SEMI_PRIVATE | ✅ | ❌ | Custom design, user fills questionnaire |
| PRIVATE | ❌ | ❌ | Full custom, direct communication |
| OWN_DESIGN | ❌ | ❌ | User uploads own ready design |

### Template Logo Placement

For public plan templates:
1. Admin uploads template with placeholder position (x, y, width, height)
2. Placeholder is visualized as red square in preview
3. When user selects template and uploads logo, system auto-places logo at placeholder position
4. Uses Pillow (PIL) for image processing

### Questionnaire System

For semi-private plans, admin creates questionnaires:

1. **Sections**: Group related questions (e.g., "Brand Info", "Design Preferences")
2. **Questions**: Various input types with validation

**Supported Input Types:**
| Type | Description | Validation Options |
|------|-------------|-------------------|
| `TEXT` | Short text input | min_length, max_length, pattern |
| `TEXTAREA` | Long text input | min_length, max_length |
| `NUMBER` | Numeric input | min_value, max_value |
| `SINGLE_CHOICE` | Single option select | From defined options |
| `MULTI_CHOICE` | Multiple options | min_selections, max_selections |
| `IMAGE_UPLOAD` | Image file | File size, dimensions |
| `FILE_UPLOAD` | Any file | File size, extensions |
| `COLOR_PICKER` | Hex color | Format validation |
| `DATE_PICKER` | Date input | Jalali format |
| `SCALE` | 1-5 or 1-10 scale | min_value, max_value |

**Conditional Logic:**
Questions can depend on previous answers:
```json
{
  "depends_on_question_id": "q-123",
  "depends_on_values": ["premium", "vip"]
}
```
The question only shows if the answer to q-123 is "premium" or "vip".

### Customer Flow

**Public Plan Flow:**
```
Select Category → Select Attributes → Select Plan → 
    → See Template Gallery → Select Template → 
    → Upload Logo → Preview Design → Confirm → 
    → Order Summary → Payment → Receipt Upload → Done
```

**Semi-Private Plan Flow:**
```
Select Category → Select Attributes → Select Plan →
    → Fill Questionnaire (section by section) →
    → Review Answers → Order Summary →
    → Payment → Receipt Upload → Done
```

---

## Logging

Structured JSON logging with request context:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "event_type": "user.signup",
  "telegram_id": 123456,
  "user_id": "uuid-here",
  "ip": "192.168.1.100",
  "ua": "Mozilla/5.0...",
  "request_id": "abc12345"
}
```

### Logging Features

- **Request Context**: IP address, user agent, request ID automatically captured
- **Context Variables**: Thread-safe storage via `contextvars`
- **Helper Functions**: `log_user_signup()`, `log_payment_approved()`, etc.

### Required Events to Log

| Event | Description | Fields |
|-------|-------------|--------|
| `user.signup` | New user registration | telegram_id, user_id, username |
| `user.login` | User authenticated | telegram_id, user_id |
| `user.update` | Profile updated | telegram_id, user_id |
| `user.promoted_to_admin` | User became admin | target_telegram_id, promoted_by |
| `user.demoted_from_admin` | Admin reverted to customer | target_telegram_id, demoted_by |
| `order.create` | New order | order_id, user_id, product_id, design_plan |
| `order.status_change` | Order status update | order_id, old_status, new_status |
| `payment.initiated` | Payment started | payment_id, order_id, amount |
| `payment.receipt_uploaded` | Receipt image uploaded | payment_id, user_id, receipt_url |
| `payment.approved` | Payment approved | payment_id, admin_id |
| `payment.rejected` | Payment rejected | payment_id, admin_id, reason |
| `file.uploaded` | File uploaded | user_id, filename, file_size |
| `validation.requested` | Validation requested | order_id, user_id |
| `validation.report_submitted` | Report submitted | order_id, validator_id, passed |

---

## Security

### Environment Variables

All secrets via environment:

```bash
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=<random-32-bytes>
TELEGRAM_BOT_TOKEN=<from-botfather>
REDIS_URL=redis://localhost:6379/0
```

### Authentication Dependencies

Role-based access control using FastAPI dependencies:

```python
from app.api.deps import require_admin, require_staff, require_print_shop

# Admin-only endpoint
@router.post("/products")
async def create_product(
    product_data: ProductCreate,
    admin_user: AuthenticatedUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ...

# Staff endpoint (admin, designer, validator, print_shop)
@router.patch("/orders/{order_id}/status")
async def update_status(
    staff_user: AuthenticatedUser = Depends(require_staff),
):
    ...
```

Available dependencies:
- `require_admin` - Admin only (403 if not admin)
- `require_staff` - Any staff role
- `require_designer` - Designer or admin
- `require_validator` - Validator or admin
- `require_print_shop` - Print shop or admin
- `get_current_user` - Any authenticated user

### Rate Limiting

Using slowapi with Redis backend:

```python
from app.core.rate_limit import limiter, RateLimits

@router.post("/payments/initiate")
@limiter.limit(RateLimits.PAYMENT_INITIATE)  # 10/minute
async def initiate_payment(request: Request, ...):
    ...
```

Rate limit presets:
| Preset | Limit | Use Case |
|--------|-------|----------|
| `LOGIN` | 5/min | Authentication |
| `PAYMENT_INITIATE` | 10/min | Payment start |
| `RECEIPT_UPLOAD` | 5/min | Receipt upload |
| `FILE_UPLOAD` | 20/min | File uploads |
| `READ` | 100/min | General reads |
| `WRITE` | 30/min | General writes |
| `MAKE_ADMIN` | 3/hour | Admin promotion |

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

### Custom Exceptions

Standardized error handling with custom exception hierarchy:

```python
from app.exceptions import (
    ResourceNotFoundException,
    AdminRequiredException,
    ValidationException,
)

# In service layer
if not user:
    raise ResourceNotFoundException("User", user_id)

if not current_user.is_admin:
    raise AdminRequiredException()
```

Exception classes:
- `SheetaroException` - Base exception
- `BusinessException` - Business logic errors (400)
- `ResourceNotFoundException` - Not found (404)
- `AuthorizationException` - Permission denied (403)
- `OrderException`, `PaymentException` - Domain-specific

---

## Testing

Test structure:

```
tests/
├── conftest.py                    # Test fixtures and configuration
├── unit/                          # Unit tests for services
│   ├── test_user_service.py
│   ├── test_product_service.py
│   ├── test_order_service.py
│   ├── test_payment_service.py    # Includes card-to-card tests
│   ├── test_invoice_service.py    # Invoice business logic
│   ├── test_validation_service.py # Design validation logic
│   ├── test_file_service.py       # File upload/delete logic
│   ├── test_subscription_service.py
│   └── test_settings_service.py
├── integration/                   # API endpoint tests
│   ├── test_users_api.py          # Includes admin management tests
│   ├── test_products_api.py
│   ├── test_orders_api.py
│   ├── test_payments_api.py       # Includes card-to-card flow tests
│   ├── test_invoices_api.py       # Invoice API tests
│   ├── test_validation_api.py     # Validation API tests
│   ├── test_files_api.py          # File upload API tests
│   └── test_subscriptions_api.py
└── e2e/                           # End-to-end flow tests
    ├── test_order_flow.py
    ├── test_payment_flow.py
    ├── test_semi_private_flow.py  # Semi-private design plan
    └── test_validation_flow.py    # Design validation with fixes
```

Run tests:

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_payment_service.py -v

# Run only unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run e2e tests
pytest tests/e2e/ -v
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

## Bot Architecture

The Telegram bot uses a **unified flow management** architecture:

### Flow Manager Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Telegram Bot Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Input (Text/Callback)                                         │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────┐                                │
│  │      text_router.py             │                                │
│  │  Routes based on flow_step      │                                │
│  └──────────┬──────────────────────┘                                │
│             │                                                        │
│  ┌──────────┴──────────────────────────────────────────┐            │
│  │                  flow_manager.py                      │            │
│  │  ┌─────────────────────────────────────────────┐     │            │
│  │  │ context.user_data = {                        │     │            │
│  │  │   'current_flow': 'catalog',                 │     │            │
│  │  │   'flow_step': 'category_create_name',       │     │            │
│  │  │   'flow_data': {...}                         │     │            │
│  │  │ }                                            │     │            │
│  │  └─────────────────────────────────────────────┘     │            │
│  └───────────────────────────────────────────────────────┘            │
│             │                                                        │
│      ┌──────┴──────┬──────────┬──────────┬──────────┐               │
│      ▼             ▼          ▼          ▼          ▼               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ catalog │ │  admin  │ │ orders  │ │products │ │ profile │        │
│  │  flow   │ │  flow   │ │  flow   │ │  flow   │ │  flow   │        │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │
│       │           │           │           │           │              │
│       └───────────┴───────────┴─────┬─────┴───────────┘              │
│                                     │                                │
│                                     ▼                                │
│                          ┌───────────────────┐                       │
│                          │   API Client      │                       │
│                          │   (httpx)         │                       │
│                          └─────────┬─────────┘                       │
│                                    │                                 │
└────────────────────────────────────┼─────────────────────────────────┘
                                     │ HTTP
                                     ▼
                            FastAPI Backend
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `flow_manager.py` | Centralized state management (current_flow, flow_step, flow_data) |
| `text_router.py` | Routes text input to appropriate flow handler |
| `flows/*.py` | Flow-specific text handlers |
| `admin_catalog.py` | Catalog management with callbacks |
| `api_client.py` | HTTP client for backend API |

### Advantages Over ConversationHandler

1. **No Handler Conflicts**: Single entry point for all text
2. **Explicit State**: Clear flow/step/data structure
3. **Easy Debugging**: Log current_flow and flow_step
4. **Flexible Navigation**: Can switch flows without ending handlers
5. **Callback Independence**: Callbacks work regardless of flow state

---

**Last Updated**: 2026-01-04


