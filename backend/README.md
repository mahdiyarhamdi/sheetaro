# Sheetaro Backend API

FastAPI backend for the Sheetaro print ordering system.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

## Docker

```bash
docker-compose up --build
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | No | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | No | `http://localhost:3000` |
| `DEBUG` | Enable debug mode | No | `false` |
| `APP_NAME` | Application name | No | `Sheetaro` |
| `APP_VERSION` | Application version | No | `1.0.0` |
| `SMTP_HOST` | SMTP server host | No | `mailhog` |
| `SMTP_PORT` | SMTP server port | No | `1025` |
| `EMAIL_FROM` | Sender email address | No | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | No | `1440` (24h) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token expiry | No | `30` |
| `OTP_EXPIRE_MINUTES` | OTP code expiry for Telegram linking | No | `5` |
| `OTP_LENGTH` | OTP code length | No | `6` |
| `UPLOAD_DIR` | File upload directory | No | `/app/uploads` |

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Authentication (`/api/v1/auth`) - Web Authentication
- `POST /auth/register` - Register new web user (phone + password)
- `POST /auth/login` - Login with phone + password
- `POST /auth/refresh` - Refresh JWT access token
- `GET /auth/me` - Get current authenticated user
- `POST /auth/telegram-link` - Generate OTP for Telegram account linking
- `POST /auth/telegram-verify` - Verify OTP and link Telegram account

### Users (`/api/v1/users`)
- `POST /users` - Create/update user
- `GET /users/{telegram_id}` - Get user by telegram ID
- `PATCH /users/{telegram_id}` - Update user
- `POST /users/{user_id}/promote` - Self-promote to admin (via `/makeadmin` command)
- `GET /users/admins/list` - Get all admin users (Admin)
- `GET /users/admins/telegram-ids` - Get admin telegram IDs (for notifications)
- `POST /users/admins/promote` - Promote user to admin (Admin)
- `POST /users/admins/demote` - Demote admin to customer (Admin)

### Products (`/api/v1/products`)
- `GET /products` - List products (filter by `type`, pagination)
- `GET /products/{id}` - Get product by ID
- `POST /products` - Create product (Admin)
- `PATCH /products/{id}` - Update product (Admin)
- `DELETE /products/{id}` - Soft delete product (Admin)

### Orders (`/api/v1/orders`)
- `POST /orders` - Create order
- `GET /orders` - List user orders (filter by `status`)
- `GET /orders/{id}` - Get order details
- `PATCH /orders/{id}` - Update order
- `PATCH /orders/{id}/status` - Update order status
- `POST /orders/{id}/cancel` - Cancel order
- `POST /orders/{id}/approve-design` - Customer approves the latest design revision
- `POST /orders/{id}/reject-design` - Customer rejects design with feedback (body: `{"feedback": "..."}`)
- `GET /orders/{id}/revisions` - List all design revisions for the order
- `GET /orders/{id}/messages` - Chat messages (PRIVATE plans only, paginated)
- `POST /orders/{id}/messages` - Send chat message (body: `{"content": "...", "file_url": "..."}`)
- `PATCH /orders/{id}/messages/read` - Mark chat messages as read

### Designer (`/api/v1/designer`)
- `GET /designer/orders` - List orders assigned to the designer (filter by `status`)
- `GET /designer/orders/{id}` - Get enriched order detail (includes customer info, questionnaire answers)
- `POST /designer/orders/{id}/accept` - Accept an assigned order
- `POST /designer/orders/{id}/upload-design` - Upload a new design revision (multipart/form-data)
- `GET /designer/orders/{id}/revisions` - List design revisions for the order
- `GET /designer/stats` - Get designer dashboard statistics

### Print Shop (`/api/v1/printshop`)
- `GET /printshop/orders` - Get queue of orders ready for printing (READY_FOR_PRINT). Response includes enriched `PrintShopOrderOut` with category info, design plan label, payment status, template name, and customer details.
- `GET /printshop/my-orders` - Get orders assigned to this print shop (filter by status). Enriched response with same data as queue.
- `GET /printshop/my-orders/{id}` - Get detail of an assigned order (full enriched `PrintShopOrderOut`)
- `POST /printshop/accept/{id}` - Accept order from queue (sets status to PRINTING)
- `POST /printshop/orders/{id}/complete` - Mark order as printed (PRINTING → PRINTED)
- `POST /printshop/orders/{id}/ship` - Ship order with tracking code (PRINTED → SHIPPED)
- `GET /printshop/stats` - Get print shop dashboard statistics
- `GET /printshop/settlements` - Get settlement/commission history

### Payments (`/api/v1/payments`)
- `POST /payments/initiate` - Initiate payment
- `POST /payments/callback` - Payment callback from PSP
- `GET /payments/{id}` - Get payment details
- `GET /payments/order/{order_id}` - Get order payments
- `GET /payments/order/{order_id}/summary` - Get payment summary
- `POST /payments/{id}/upload-receipt` - Upload receipt for card-to-card payment
- `GET /payments/pending-approval` - Get payments awaiting approval (Admin)
- `POST /payments/{id}/approve` - Approve payment (Admin)
- `POST /payments/{id}/reject` - Reject payment with reason (Admin)

### Validation (`/api/v1/validation`)
- `POST /validation/request` - Request design validation
- `POST /validation/{order_id}/report` - Submit validation report
- `GET /validation/{report_id}` - Get validation report
- `GET /validation/order/{order_id}` - Get order validation reports

### Invoices (`/api/v1/invoices`)
- `POST /invoices` - Create invoice
- `GET /invoices/{invoice_number}` - Get invoice by number
- `GET /invoices` - List user invoices
- `GET /invoices/search` - Advanced search (subscription required)
- `PATCH /invoices/{id}` - Update invoice
- `POST /invoices/{id}/pdf` - Generate PDF

### Subscriptions (`/api/v1/subscriptions`)
- `POST /subscriptions` - Create subscription
- `GET /subscriptions/me` - Get subscription status
- `GET /subscriptions` - List subscriptions
- `GET /subscriptions/{id}` - Get subscription
- `POST /subscriptions/{id}/cancel` - Cancel subscription
- `GET /subscriptions/plans/price` - Get plan price

### Files (`/api/v1`)
- `POST /files/upload` - Upload design file
- `GET /files/designs/{user_id}/{filename}` - Download design file
- `DELETE /files/designs/{user_id}/{filename}` - Delete design file
- `POST /templates/upload` - Upload template image (Admin, PNG/JPG/WEBP, max 20MB)
- `GET /files/templates/{filename}` - Download template image
- `POST /fonts/upload` - Upload font file (Admin, TTF/WOFF/WOFF2, max 10MB)
- `GET /files/fonts/{filename}` - Download font file
- `GET /files/thumbnail/{path}?max_size=400` - Get optimized WebP thumbnail (cached, 50-1200px)
- `GET /files/download/{path}` - Download original file with `Content-Disposition: attachment`

### Settings (`/api/v1/settings`)
- `GET /settings/payment-card` - Get payment card info
- `PUT /settings/payment-card` - Set payment card info (Admin)
- `PATCH /settings/payment-card` - Update payment card info (Admin)

### Admin (`/api/v1/admin`) - Admin Panel APIs
- `GET /admin/stats` - Dashboard statistics (orders, payments, revenue, users)
- `GET /admin/stats/orders` - Order statistics with daily breakdown
- `GET /admin/stats/revenue` - Revenue statistics (this month, last month, daily)
- `GET /admin/stats/users` - User statistics (by role, daily signups)
- `GET /admin/users` - List users with filters (search, role, active status)
- `GET /admin/users/{id}` - Get user details
- `PATCH /admin/users/{id}/role` - Update user role
- `POST /admin/users/{id}/ban` - Ban/unban user
- `GET /admin/orders` - List all orders with filters
- `PATCH /admin/orders/{id}/status` - Force update order status
- `POST /admin/orders/{id}/assign` - Assign order to designer/validator/printshop
- `GET /admin/payments` - List all payments with filters
- `POST /admin/payments/{id}/verify` - Verify or reject payment
- `GET /admin/printshops` - List all print shop users
- `GET /admin/printshops/{id}/stats` - Get print shop performance stats
- `GET /admin/printshops/{id}/orders` - Get print shop order history
- `POST /admin/orders/{id}/reassign-printshop` - Reassign order to another print shop
- `GET /admin/settlements` - List all settlements
- `POST /admin/settlements/{id}/pay` - Mark settlement as paid
- `GET /admin/printshop-sla` - Get SLA compliance report for all print shops

### Categories (`/api/v1/categories`) - Dynamic Product Catalog
- `GET /categories` - List all categories
- `GET /categories/{id}` - Get category by ID
- `GET /categories/{id}/details` - Get category with attributes, plans, steps
- `POST /categories` - Create category (Admin)
- `PATCH /categories/{id}` - Update category (Admin)
- `DELETE /categories/{id}` - Delete category (Admin)

#### Attributes (`/api/v1/categories/{id}/attributes`)
- `GET /categories/{id}/attributes` - List category attributes
- `POST /categories/{id}/attributes` - Create attribute (Admin)
- `PATCH /attributes/{id}` - Update attribute (Admin)
- `DELETE /attributes/{id}` - Delete attribute (Admin)
- `POST /attributes/{id}/options` - Add option to attribute (Admin)
- `PATCH /options/{id}` - Update option (Admin)
- `DELETE /options/{id}` - Delete option (Admin)

#### Design Plans (`/api/v1/categories/{id}/plans`)
- `GET /categories/{id}/plans` - List design plans
- `POST /categories/{id}/plans` - Create plan (Admin)
- `GET /plans/{id}` - Get plan by ID
- `GET /plans/{id}/details` - Get plan with questions and templates
- `PATCH /plans/{id}` - Update plan (Admin)
- `DELETE /plans/{id}` - Delete plan (Admin)

#### Sections (`/api/v1/plans/{id}/sections`) - Question Grouping
- `GET /plans/{id}/sections` - List questionnaire sections
- `POST /plans/{id}/sections` - Create section (Admin)
- `GET /sections/{id}` - Get section details
- `PATCH /sections/{id}` - Update section (Admin)
- `DELETE /sections/{id}` - Delete section (Admin)
- `PATCH /sections/reorder` - Reorder sections (Admin)

#### Questions (`/api/v1/plans/{id}/questions`) - For Semi-Private Plans
- `GET /plans/{id}/questions` - List questionnaire questions
- `POST /plans/{id}/questions` - Create question with options (Admin)
- `GET /questions/{id}` - Get question details
- `PATCH /questions/{id}` - Update question (Admin)
- `DELETE /questions/{id}` - Delete question (Admin)
- `POST /questions/{id}/options` - Add option to question (Admin)
- `POST /questions/{id}/validate` - Validate an answer against question rules

**Question Input Types:**
- `TEXT` - Short text input
- `TEXTAREA` - Long text input
- `NUMBER` - Numeric input with min/max validation
- `SINGLE_CHOICE` - Single option selection
- `MULTI_CHOICE` - Multiple option selection
- `IMAGE_UPLOAD` - Image file upload
- `FILE_UPLOAD` - Any file upload
- `COLOR_PICKER` - Color selection (hex code)
- `DATE_PICKER` - Date input (Jalali format)
- `SCALE` - Numeric scale (1-5 or 1-10)

**Validation Rules (JSON):**
```json
{
  "min_length": 2,        // For TEXT
  "max_length": 100,
  "min_value": 1,         // For NUMBER/SCALE
  "max_value": 1000,
  "pattern": "^[\\w]+$",  // Regex pattern
  "min_selections": 1,    // For MULTI_CHOICE
  "max_selections": 5
}
```

#### Templates (`/api/v1/plans/{id}/templates`) - For Public Plans
- `GET /plans/{id}/templates` - List design templates
- `POST /plans/{id}/templates` - Create template with placeholder info (Admin)
- `GET /templates/{id}` - Get template details
- `PATCH /templates/{id}` - Update template (Admin)
- `DELETE /templates/{id}` - Delete template (Admin)
- `POST /templates/{id}/apply-logo` - Apply user logo to template placeholder

**Template Placeholder:**
When uploading a template, specify where the user's logo will be placed:
- `placeholder_x`, `placeholder_y` - Top-left corner position
- `placeholder_width`, `placeholder_height` - Size of placeholder area
- The preview will show a red square indicating the logo placement area
- User logos are automatically resized to fit and centered in the placeholder

#### Questionnaire Answers (`/api/v1/orders/{id}/answers`)
- `POST /orders/{id}/answers` - Submit all questionnaire answers
- `GET /orders/{id}/answers` - Get saved answers
- `GET /orders/{id}/answers/summary` - Get formatted answer summary

#### Processed Designs (`/api/v1/orders/{id}/design`)
- `POST /orders/{id}/design` - Create processed design from template + logo
- `GET /orders/{id}/design` - Get order's processed design(s)

#### Step Templates (`/api/v1/categories/{id}/steps`)
- `GET /categories/{id}/steps` - List order step templates
- `POST /categories/{id}/steps` - Create step template (Admin)
- `PATCH /step-templates/{id}` - Update step template (Admin)
- `DELETE /step-templates/{id}` - Delete step template (Admin)

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v

# Run E2E tests only
python -m pytest tests/e2e/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
python -m pytest tests/unit/test_auth_service.py -v

# Run tests matching pattern
python -m pytest tests/ -v -k "auth"
```

### Test Categories

| Category | Path | Description |
|----------|------|-------------|
| Unit Tests | `tests/unit/` | Service layer tests (AuthService, OrderService, etc.) |
| Integration Tests | `tests/integration/` | API endpoint tests with database |
| E2E Tests | `tests/e2e/` | Full flow tests (order creation, payment, etc.) |

### Print Shop Tests

| File | Description |
|------|-------------|
| `tests/unit/test_printshop_service.py` | OrderService print shop methods (accept, complete, ship, stats, queue, enriched PrintShopOrderOut fields) |
| `tests/integration/test_printshop_api.py` | Print shop API endpoints (queue, accept, my-orders, complete, ship, stats, settlements) |
| `tests/integration/test_admin_printshop_api.py` | Admin print shop management endpoints (list, stats, orders, reassign, settlements, SLA) |

### Dynamic Template Builder Tests

| File | Description |
|------|-------------|
| `tests/unit/test_template_models.py` | TemplatePlaceholder, SystemFont models |
| `tests/unit/test_template_schemas.py` | Pydantic validation for placeholder/font schemas |
| `tests/unit/test_dynamic_template_service.py` | Image/text rendering, color parsing, font loading, preview generation |
| `tests/integration/test_fonts_api.py` | Font CRUD API endpoints |
| `tests/integration/test_placeholders_api.py` | Placeholder CRUD API endpoints |
| `tests/integration/test_template_preview_api.py` | Template preview generation API |

### Test Fixtures

Main fixtures are defined in `tests/conftest.py`:
- `client` - Async HTTP client for API testing
- `db_session` - Database session with auto-rollback
- `sample_user_data` - Sample Telegram user data
- `sample_web_user_data` - Sample web user registration data
- `authenticated_user` - Registered and authenticated user
- `auth_headers` - Authorization headers for authenticated requests

## Project Structure

```
backend/
├── alembic/                 # Database migrations
├── app/
│   ├── api/
│   │   ├── deps.py         # Dependencies (DB, auth, role checks)
│   │   └── routers/        # API route handlers
│   ├── core/
│   │   ├── config.py       # Settings (pydantic-settings)
│   │   ├── database.py     # DB connection, UnitOfWork
│   │   ├── security.py     # JWT, password hashing
│   │   └── rate_limit.py   # Rate limiting (slowapi + Redis)
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Database operations (CRUD)
│   ├── schemas/            # Pydantic schemas (input/output)
│   ├── services/           # Business logic
│   ├── tasks/              # Background tasks (SLA enforcement)
│   ├── utils/
│   │   └── logger.py       # Structured JSON logging
│   ├── exceptions.py       # Custom exception classes
│   └── main.py             # FastAPI app
├── tests/
│   ├── conftest.py         # Test fixtures
│   ├── unit/               # Unit tests (services)
│   ├── integration/        # API endpoint tests
│   └── e2e/                # End-to-end flow tests
├── requirements.txt
└── Dockerfile
```

## Data Models

### User Roles
- `CUSTOMER` - Regular customer
- `DESIGNER` - Design staff
- `VALIDATOR` - Validation staff
- `PRINT_SHOP` - Print shop
- `ADMIN` - Administrator

### Order Status Flow
```
PENDING_PAYMENT → PAYMENT_UPLOADED → PAYMENT_APPROVED → PENDING → AWAITING_VALIDATION → NEEDS_ACTION → DESIGNING
                       ↓                                                                                    ↓
                  PAYMENT_REJECTED                                                                   READY_FOR_PRINT
                                                                                                         ↓
                                                                              CANCELLED ← PRINTING → PRINTED → SHIPPED → DELIVERED
```

### Payment Status Flow (Card-to-Card)
```
PENDING → AWAITING_APPROVAL → SUCCESS
                ↓
             FAILED (can re-upload receipt)
```

### Design Plans
- `PUBLIC` - Free ready-made designs
- `SEMI_PRIVATE` - Custom design (600,000 تومان, max 3 revisions)
- `PRIVATE` - Full custom (5,000,000 تومان, unlimited revisions for 14 days)
- `OWN_DESIGN` - Upload own design

## Pricing

| Item | Price (تومان) |
|------|---------------|
| Validation | 50,000 |
| Semi-Private Design | 600,000 |
| Private Design | 5,000,000 |
| Advanced Search Subscription | 250,000/month |

## Rate Limiting

API endpoints are rate-limited using slowapi with Redis backend:

| Endpoint Type | Limit |
|---------------|-------|
| Login/Auth | 5/minute |
| Payment Initiate | 10/minute |
| Receipt Upload | 5/minute |
| File Upload (design/template/font) | 20/minute |
| General Read | 100/minute |
| General Write | 30/minute |
| Admin Promote | 3/hour |

When rate limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

## Authentication

The API supports two authentication methods:

### 1. JWT Token Authentication (Web)
For web application users:
```bash
# Login and get tokens
curl -X POST /api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "09121234567", "password": "yourpassword"}'

# Use access token in requests
curl -H "Authorization: Bearer <access_token>" /api/v1/auth/me

# Refresh expired access token
curl -X POST /api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

### 2. User ID Authentication (Telegram Bot)
For Telegram bot integration, `user_id` query parameter is used.

### Role-Based Access Control

- **Public** - No auth required (health check, product listing)
- **Authenticated** - Valid user required (orders, payments)
- **Admin** - Admin role required (product CRUD, settings, payment approval)
- **Staff** - Any staff role (admin, designer, validator, print_shop)

---

**Last Updated**: 2026-02-11

