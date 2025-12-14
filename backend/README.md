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

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Users (`/api/v1/users`)
- `POST /users` - Create/update user
- `GET /users/{telegram_id}` - Get user by telegram ID
- `PATCH /users/{telegram_id}` - Update user
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
│   │   ├── deps.py         # Dependencies (DB, auth)
│   │   └── routers/        # API route handlers
│   ├── core/
│   │   ├── config.py       # Settings
│   │   ├── database.py     # DB connection
│   │   └── security.py     # JWT, auth
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Database operations
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # Utilities
│   └── main.py             # FastAPI app
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # API tests
│   └── e2e/                # End-to-end tests
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

---

**Last Updated**: 2025-12-14

