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

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

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

### Print Shop (`/api/v1/printshop`)
- `GET /printshop/orders` - Get orders ready for printing
- `POST /printshop/accept/{id}` - Accept order

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

### Files (`/api/v1/files`)
- `POST /files/upload` - Upload design file
- `GET /files/designs/{user_id}/{filename}` - Download file
- `DELETE /files/designs/{user_id}/{filename}` - Delete file

### Settings (`/api/v1/settings`)
- `GET /settings/payment-card` - Get payment card info
- `PUT /settings/payment-card` - Set payment card info (Admin)
- `PATCH /settings/payment-card` - Update payment card info (Admin)

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
pytest

# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run E2E tests
pytest tests/e2e

# Run with coverage
pytest --cov=app
```

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
PENDING → AWAITING_VALIDATION → NEEDS_ACTION → DESIGNING → READY_FOR_PRINT → PRINTING → SHIPPED → DELIVERED
                                                              ↓
                                                          CANCELLED
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
| File Upload | 20/minute |
| General Read | 100/minute |
| General Write | 30/minute |
| Admin Promote | 3/hour |

When rate limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

## Authentication

Most endpoints require authentication via `user_id` query parameter. Role-based access control:

- **Public** - No auth required (health check, product listing)
- **Authenticated** - Valid user_id required
- **Admin** - Admin role required (product CRUD, settings)
- **Staff** - Any staff role (admin, designer, validator, print_shop)

---

**Last Updated**: 2026-01-04

