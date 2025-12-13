# SCOPE.md - Sheetaro MVP Scope Definition

## Overview

Sheetaro is a Telegram bot for ordering labels and business cards with a RESTful backend API.

---

## MVP Features

### Phase 1: Core Infrastructure (Completed)

- [x] FastAPI backend with layered architecture
- [x] PostgreSQL database with async SQLAlchemy 2.x
- [x] Alembic migrations
- [x] Docker Compose setup
- [x] Telegram bot with python-telegram-bot
- [x] User registration/sync via Telegram

### Phase 2: User Management (Completed)

- [x] User model with Telegram ID as primary identifier
- [x] Profile fields: name, username, phone, address, photo URL
- [x] Iranian phone number validation (09x / +98x formats)
- [x] Profile viewing and editing via bot
- [x] API endpoints: POST/GET/PATCH `/api/v1/users`

### Phase 3: Orders (Planned)

- [ ] Order model (label/business card types)
- [ ] Order status workflow (pending → processing → completed)
- [ ] File upload for designs
- [ ] Order history per user
- [ ] API endpoints: CRUD `/api/v1/orders`

### Phase 4: Payments (Planned)

- [ ] Payment integration (TBD: Zarinpal/etc)
- [ ] Payment status tracking
- [ ] Invoice generation

---

## Data Models

### User

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| telegram_id | BigInteger | yes | Telegram user ID (unique) |
| username | String(255) | no | Telegram username |
| first_name | String(255) | yes | First name |
| last_name | String(255) | no | Last name |
| phone_number | String(20) | no | Iranian format |
| address | Text | no | Delivery address |
| bio | Text | no | User bio |
| profile_photo_url | String(500) | no | Telegram photo URL |
| is_active | Boolean | yes | Account status |
| created_at | DateTime | auto | Created timestamp |
| updated_at | DateTime | auto | Last update |

### Order (Future)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| user_id | UUID | yes | FK to users |
| type | Enum | yes | LABEL / BUSINESS_CARD |
| status | Enum | yes | PENDING / PROCESSING / COMPLETED / CANCELLED |
| quantity | Integer | yes | Number of items |
| design_file_url | String | no | Uploaded design |
| total_price | Decimal | yes | Total amount |
| created_at | DateTime | auto | Order date |

---

## API Endpoints

### Implemented

| Method | Path | Description | Status Code |
|--------|------|-------------|-------------|
| GET | `/health` | Health check | 200 |
| POST | `/api/v1/users` | Create/update user | 201 |
| GET | `/api/v1/users/{telegram_id}` | Get user by Telegram ID | 200/404 |
| PATCH | `/api/v1/users/{telegram_id}` | Update user | 200/404 |

### Planned

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/orders` | Create order |
| GET | `/api/v1/orders` | List user orders |
| GET | `/api/v1/orders/{id}` | Get order details |
| PATCH | `/api/v1/orders/{id}` | Update order status |
| DELETE | `/api/v1/orders/{id}` | Cancel order |

---

## Bot Commands

| Command | Description | Status |
|---------|-------------|--------|
| `/start` | Welcome + register user | Done |
| Menu: سفارش لیبل | Order label | Placeholder |
| Menu: سفارش کارت ویزیت | Order business card | Placeholder |
| Menu: سفارشات من | My orders | Placeholder |
| Menu: پروفایل من | View/edit profile | Done |
| Menu: راهنما | Help text | Done |
| Menu: پشتیبانی | Support contact | Done |

---

## Technical Constraints

### Stack

- **Backend**: Python 3.12, FastAPI 0.115, SQLAlchemy 2.x, Pydantic v2
- **Database**: PostgreSQL 16, Redis 7
- **Bot**: python-telegram-bot 21.x, httpx
- **Infra**: Docker, Docker Compose

### Architecture Rules

1. **Layered Architecture**: Router → Service → Repository → DB
2. **No business logic in routers** - only input/output handling
3. **All async** - use async/await for DB and HTTP calls
4. **Type hints required** - all functions must be typed
5. **Pydantic for validation** - all inputs validated via schemas
6. **Structured JSON logging** - no print statements

### Security Rules

1. Environment variables for all secrets
2. No hardcoded credentials
3. CORS restricted to allowed origins
4. Input validation on all endpoints
5. DB ports not exposed in production

---

## Out of Scope (Do NOT implement without approval)

- Admin panel / web dashboard
- SMS notifications
- Multiple payment gateways
- Multi-language support
- Analytics/reporting
- Email marketing
- Social login (Google/etc)
- Product catalog management
- Inventory tracking
- Shipping integration

---

## Change Management

Any changes to this scope require:

1. Written approval from project owner
2. ADR document in `docs/` explaining the decision
3. Update to this SCOPE.md file

**Last Updated**: 2024-12-13

