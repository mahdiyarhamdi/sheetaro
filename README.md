# Sheetaro - ربات تلگرام چاپ

سیستم سفارش لیبل و کارت ویزیت با ربات تلگرام و API RESTful

## ویژگی‌ها

- ✅ ربات تلگرام با UX/CX عالی
- ✅ FastAPI Backend با Swagger
- ✅ همگام‌سازی کامل بین تلگرام و web app
- ✅ PostgreSQL + Redis
- ✅ معماری لایه‌ای و scalable
- ✅ Docker Compose برای اجرای آسان

## پیش‌نیازها

- Docker و Docker Compose
- Python 3.12+ (برای development محلی)
- توکن ربات تلگرام

## راه‌اندازی سریع

### 1. تنظیمات اولیه

```bash
# کپی فایل محیطی
cp .env.example .env

# ویرایش .env و تنظیم TELEGRAM_BOT_TOKEN
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
│   └── Dockerfile
├── bot/                 # Telegram Bot
│   ├── handlers/        # Command & message handlers
│   ├── keyboards/       # Keyboard layouts
│   ├── utils/           # API client & utilities
│   ├── bot.py           # Bot entry point
│   └── Dockerfile
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

- 🏷️ **سفارش لیبل** - ثبت سفارش لیبل جدید
- 💼 **سفارش کارت ویزیت** - ثبت سفارش کارت ویزیت
- 📦 **سفارشات من** - مشاهده و پیگیری سفارشات
- 👤 **پروفایل من** - مشاهده اطلاعات پروفایل
- ❓ **راهنما** - راهنمای استفاده
- 📞 **پشتیبانی** - ارتباط با پشتیبانی

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

## Logging

لاگ‌ها به صورت structured JSON ذخیره می‌شوند:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "level": "INFO",
  "event_type": "user.signup",
  "telegram_id": 123456,
  "username": "user123"
}
```

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.

