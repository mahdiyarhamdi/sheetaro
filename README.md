# Sheetaro - ربات تلگرام چاپ

سیستم سفارش لیبل و کارت ویزیت با ربات تلگرام و API RESTful

## ویژگی‌ها

- ✅ ربات تلگرام با UX/CX عالی
- ✅ **وب اپلیکیشن Next.js**: ثبت‌نام، سفارش، پرداخت
- ✅ FastAPI Backend با Swagger
- ✅ **سیستم کاتالوگ داینامیک**: دسته‌بندی، ویژگی، پلن طراحی
- ✅ **پلن عمومی**: قالب‌های آماده با جایگذاری خودکار لوگو
- ✅ **پلن نیمه‌خصوصی**: پرسشنامه طراحی
- ✅ پرداخت کارت به کارت با تأیید ادمین
- ✅ **اتصال حساب تلگرام به وب** با کد OTP
- ✅ PostgreSQL + Redis
- ✅ معماری لایه‌ای و scalable
- ✅ Docker Compose برای اجرای آسان
- ✅ **CI/CD با GitHub Actions**: تست خودکار

## مستندات

- [SCOPE.md](SCOPE.md) - اسکوپ MVP و فیچرها
- [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) - معماری سیستم
- [docs/](docs/) - تصمیمات معماری (ADR)

## پیش‌نیازها

- Docker و Docker Compose
- Python 3.12+ (برای development محلی)
- توکن ربات تلگرام

## راه‌اندازی سریع

### 1. تنظیمات اولیه

```bash
# کپی فایل محیطی
cp .env.example .env

# ویرایش .env و تنظیم متغیرهای لازم
# حداقل باید این موارد را تنظیم کنید:
# - POSTGRES_PASSWORD
# - SECRET_KEY (با دستور: openssl rand -hex 32)
# - TELEGRAM_BOT_TOKEN (از @BotFather)
nano .env
```

### 2. اجرای پروژه

```bash
# ساخت و اجرای همه سرویس‌ها
docker-compose up --build

# یا در background:
docker-compose up -d --build
```

### 3. دسترسی به سرویس‌ها

- **Swagger UI**: http://localhost:3005/docs
- **ReDoc**: http://localhost:3005/redoc
- **Health Check**: http://localhost:3005/health
- **ربات تلگرام**: جستجو کنید و /start بزنید

> **توجه**: پورت‌های پیش‌فرض تغییر یافته‌اند تا با پروژه‌های دیگر تداخل نداشته باشند:
> - Backend: 3005 (به جای 3001)
> - PostgreSQL: 5435 (به جای 5432)
> - Redis: 6381 (به جای 6379)

## ساختار پروژه

```
Sheetaro/
├── backend/              # FastAPI Application
│   ├── app/
│   │   ├── api/         # API routers & dependencies
│   │   ├── core/        # Config, security, database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/ # Database operations
│   │   └── utils/       # Utilities (logging, etc.)
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests (unit, integration, e2e)
│   └── Dockerfile
├── bot/                 # Telegram Bot
│   ├── handlers/        # Command & message handlers
│   │   ├── flows/       # Flow-specific text handlers
│   │   └── text_router.py # Central text input router
│   ├── keyboards/       # Keyboard layouts
│   ├── utils/           # API client, flow_manager & utilities
│   ├── tests/           # Bot tests
│   ├── bot.py           # Bot entry point
│   └── Dockerfile
├── frontend/            # Next.js Web Application
│   ├── src/
│   │   ├── app/         # Next.js App Router pages
│   │   ├── components/  # Reusable components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── lib/         # API client & utilities
│   │   └── __tests__/   # Frontend tests (Vitest)
│   ├── e2e/             # E2E tests (Playwright)
│   └── Dockerfile
├── .github/workflows/   # GitHub Actions CI/CD
└── docker-compose.yml
```

## API Endpoints

### Health
- `GET /health` - بررسی سلامت سیستم

### Users
- `POST /api/v1/users` - ایجاد یا به‌روزرسانی کاربر
- `GET /api/v1/users/{telegram_id}` - دریافت اطلاعات کاربر
- `PATCH /api/v1/users/{telegram_id}` - به‌روزرسانی کاربر

## دستورات کاربردی

### مدیریت Container ها

```bash
# مشاهده لاگ‌ها
docker-compose logs -f

# لاگ سرویس خاص
docker-compose logs -f backend
docker-compose logs -f bot

# توقف سرویس‌ها
docker-compose down

# توقف و حذف volumes
docker-compose down -v
```

### Database Migration

```bash
# ورود به container backend
docker-compose exec backend bash

# ساخت migration جدید
alembic revision --autogenerate -m "description"

# اجرای migration
alembic upgrade head

# بازگشت migration
alembic downgrade -1
```

### Development محلی

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

# Bot
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## منوی ربات تلگرام

### منوی مشتری
- 🛒 **ثبت سفارش** - ثبت سفارش جدید
- 📦 **سفارشات من** - مشاهده و پیگیری سفارشات
- 🔍 **رهگیری سفارش** - رهگیری با کد سفارش
- 👤 **پروفایل من** - مشاهده و ویرایش پروفایل
- ❓ **راهنما** - راهنمای استفاده
- 📞 **پشتیبانی** - ارتباط با پشتیبانی

### منوی ادمین (اضافه بر موارد بالا)
- 🔧 **پنل مدیریت**
  - 💰 پرداخت‌های در انتظار
  - 📂 مدیریت کاتالوگ (دسته‌بندی، ویژگی، پلن، قالب، پرسشنامه)
  - ⚙️ تنظیمات سیستم

### دستورات
- `/start` - ثبت‌نام و نمایش منو
- `/makeadmin` - ارتقا به ادمین

## تکنولوژی‌ها

### Backend
- FastAPI 0.115
- SQLAlchemy 2.x (Async)
- Alembic (Migrations)
- Pydantic v2
- PostgreSQL 16
- Redis 7

### Bot
- python-telegram-bot 21.x
- httpx (Async HTTP client)
- Unified Flow Manager (بدون ConversationHandler)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Redis

## متغیرهای محیطی

| متغیر | توضیح | مثال |
|-------|-------|------|
| `DATABASE_URL` | آدرس دیتابیس | `postgresql+asyncpg://user:pass@postgres:5432/db` |
| `REDIS_URL` | آدرس Redis | `redis://redis:6379/0` |
| `CORS_ORIGINS` | Origin های مجاز | `http://localhost:3000` |
| `SECRET_KEY` | کلید امنیتی | `your-secret-key` |
| `TELEGRAM_BOT_TOKEN` | توکن ربات تلگرام | `123456:ABC-DEF...` |
| `API_BASE_URL` | آدرس API | `http://backend:3001` |
| `DEBUG` | فعال‌سازی حالت دیباگ | `false` |
| `APP_NAME` | نام اپلیکیشن | `Sheetaro` |
| `APP_VERSION` | نسخه اپلیکیشن | `1.0.0` |

## Logging

لاگ‌ها به صورت structured JSON ذخیره می‌شوند:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "event_type": "user.signup",
  "telegram_id": 123456,
  "username": "user123",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "request_id": "abc12345"
}
```

## محدودیت نرخ (Rate Limiting)

API ها با استفاده از slowapi و Redis محدود شده‌اند:

| نوع درخواست | محدودیت |
|-------------|---------|
| ورود/احراز هویت | 5 در دقیقه |
| شروع پرداخت | 10 در دقیقه |
| آپلود رسید | 5 در دقیقه |
| آپلود فایل | 20 در دقیقه |
| خواندن | 100 در دقیقه |
| نوشتن | 30 در دقیقه |

## معماری ربات

ربات تلگرام از معماری **Unified Flow Management** استفاده می‌کند:

```
ورودی کاربر
     │
     ▼
┌─────────────────┐
│   text_router   │ ← مسیریابی بر اساس flow و step
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼
 catalog   admin    orders  products  profile
   flow     flow     flow     flow      flow
```

### مزایا نسبت به ConversationHandler
- بدون تداخل Handler ها
- State شفاف و قابل دیباگ
- ناوبری آسان بین flowها
- Callback های مستقل از state

برای جزییات بیشتر: [bot/README.md](bot/README.md)

## تست‌ها

### Backend Tests

```bash
# اجرای تست‌های backend
docker-compose exec backend python -m pytest tests/ -v

# تست‌های واحد
docker-compose exec backend python -m pytest tests/unit -v

# تست‌های یکپارچه
docker-compose exec backend python -m pytest tests/integration -v

# با coverage
docker-compose exec backend python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Frontend Tests

```bash
# تست‌های واحد (Vitest)
cd frontend && npm test

# تست‌های E2E (Playwright)
cd frontend && npx playwright test
```

### Bot Tests

```bash
# اجرای تست‌های bot
cd bot && python -m pytest tests/ -v
```

### CI/CD

تست‌ها به صورت خودکار در GitHub Actions اجرا می‌شوند:
- Backend Unit & Integration Tests
- Frontend Unit Tests (Vitest)
- E2E Tests (Playwright)
- Bot Tests

فایل workflow: [.github/workflows/test.yml](.github/workflows/test.yml)

چک‌لیست تست دستی: [docs/BOT_TEST_CHECKLIST.md](docs/BOT_TEST_CHECKLIST.md)

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.

---

**Last Updated**: 2026-01-21

