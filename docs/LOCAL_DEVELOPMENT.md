# راهنمای توسعه محلی Sheetaro

این راهنما نحوه راه‌اندازی و اجرای پروژه Sheetaro را در محیط توسعه محلی توضیح می‌دهد.

## پیش‌نیازها

قبل از شروع، مطمئن شوید که موارد زیر نصب شده‌اند:

- **Docker** (نسخه 20.10 یا بالاتر)
- **Docker Compose** (نسخه 2.0 یا بالاتر)
- **Git**

## شروع سریع

```bash
# کلون کردن پروژه
git clone <repository-url>
cd Sheetaro

# اجرای محیط توسعه
./scripts/run-local.sh start
```

## دستورات اسکریپت

اسکریپت `./scripts/run-local.sh` دستورات زیر را پشتیبانی می‌کند:

| دستور | توضیح |
|-------|-------|
| `start` | شروع تمام سرویس‌ها (پیش‌فرض) |
| `stop` | توقف تمام سرویس‌ها |
| `restart` | راه‌اندازی مجدد سرویس‌ها |
| `logs` | نمایش لاگ‌های تمام سرویس‌ها |
| `backend` | نمایش لاگ‌های بکند |
| `frontend` | نمایش لاگ‌های فرانت‌اند |
| `db` | نمایش لاگ‌های دیتابیس |
| `shell` | ورود به شل کانتینر بکند |
| `migrate` | اجرای مایگریشن‌های دیتابیس |
| `seed` | پر کردن دیتابیس با داده‌های تست |
| `clean` | توقف سرویس‌ها و حذف والیوم‌ها |
| `status` | نمایش وضعیت سرویس‌ها |
| `help` | نمایش راهنما |

### مثال‌ها

```bash
# شروع محیط توسعه
./scripts/run-local.sh start

# مشاهده لاگ‌های بکند
./scripts/run-local.sh backend

# اجرای مایگریشن‌ها
./scripts/run-local.sh migrate

# ورود به شل کانتینر بکند
./scripts/run-local.sh shell

# توقف همه سرویس‌ها
./scripts/run-local.sh stop
```

## آدرس‌های سرویس‌ها

| سرویس | آدرس | توضیح |
|-------|------|-------|
| **فرانت‌اند** | http://localhost:3000 | رابط کاربری اصلی |
| **بکند API** | http://localhost:3005 | API بکند |
| **مستندات API** | http://localhost:3005/docs | مستندات Swagger |
| **MailHog** | http://localhost:8025 | سرویس تست ایمیل |
| **pgAdmin** | http://localhost:5050 | مدیریت دیتابیس (اختیاری) |

## اطلاعات ورود

### کاربر ادمین پیش‌فرض
```
ایمیل: admin@sheetaro.ir
رمز عبور: admin123
```

## ساختار پروژه

```
Sheetaro/
├── backend/                 # بکند FastAPI
│   ├── app/
│   │   ├── api/            # روترهای API
│   │   ├── core/           # تنظیمات و امنیت
│   │   ├── models/         # مدل‌های دیتابیس
│   │   ├── schemas/        # اسکیماهای Pydantic
│   │   ├── services/       # لایه سرویس
│   │   └── repositories/   # لایه دیتابیس
│   ├── alembic/            # مایگریشن‌های دیتابیس
│   └── tests/              # تست‌های بکند
├── frontend/               # فرانت‌اند Next.js
│   ├── src/
│   │   ├── app/           # صفحات Next.js
│   │   ├── components/    # کامپوننت‌های React
│   │   └── lib/           # کتابخانه‌ها و API
│   └── public/            # فایل‌های استاتیک
├── bot/                    # ربات تلگرام (اختیاری)
├── docs/                   # مستندات
├── scripts/                # اسکریپت‌های کمکی
└── docker-compose.yml      # تنظیمات Docker
```

## توسعه

### افزودن مایگریشن جدید

```bash
# ورود به شل بکند
./scripts/run-local.sh shell

# ساخت مایگریشن جدید
alembic revision --autogenerate -m "توضیح تغییرات"

# اجرای مایگریشن
alembic upgrade head
```

### اجرای تست‌ها

```bash
# تست‌های بکند
./scripts/run-local.sh shell
pytest tests/ -v

# تست‌های فرانت‌اند (در محیط لوکال)
cd frontend
npm test
```

### مشاهده لاگ‌ها

```bash
# تمام لاگ‌ها
./scripts/run-local.sh logs

# فقط بکند
./scripts/run-local.sh backend

# فقط فرانت‌اند
./scripts/run-local.sh frontend
```

## عیب‌یابی

### مشکل: کانتینرها شروع نمی‌شوند

```bash
# بررسی وضعیت داکر
docker info

# بررسی لاگ‌های خطا
docker-compose logs

# پاک کردن و شروع مجدد
./scripts/run-local.sh clean
./scripts/run-local.sh start
```

### مشکل: دیتابیس متصل نمی‌شود

```bash
# بررسی وضعیت دیتابیس
docker-compose ps db

# ری‌استارت دیتابیس
docker-compose restart db

# مشاهده لاگ‌های دیتابیس
docker-compose logs db
```

### مشکل: تغییرات کد اعمال نمی‌شود

```bash
# ری‌استارت سرویس موردنظر
docker-compose restart backend
# یا
docker-compose restart frontend

# بازسازی کامل (برای تغییرات package)
docker-compose up -d --build
```

## متغیرهای محیطی

فایل `.env` در ریشه پروژه شامل تنظیمات زیر است:

```env
# دیتابیس
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/sheetaro

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ایمیل (MailHog برای توسعه)
SMTP_HOST=mailhog
SMTP_PORT=1025

# فرانت‌اند
NEXT_PUBLIC_API_URL=http://localhost:3005
```

## نکات مهم

1. **هرگز** اطلاعات حساس را در کد کامیت نکنید
2. قبل از کامیت، تست‌ها را اجرا کنید
3. از Conventional Commits استفاده کنید
4. مستندات را همراه با کد آپدیت کنید

## پشتیبانی

در صورت بروز مشکل:
1. لاگ‌ها را بررسی کنید
2. مستندات را مطالعه کنید
3. Issue جدید ایجاد کنید

