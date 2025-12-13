# SCOPE.md - Sheetaro MVP Scope Definition

## Overview

**Sheetaro** یک ربات تلگرام چندنقشی برای سفارش‌گیری چاپ لیبل و فاکتور است با:
- مسیرهای طراحی (عمومی/نیمه‌خصوصی/خصوصی)
- اعتبارسنجی طرح/لوگو
- مدیریت فرایند چاپ توسط چاپخانه‌های همکار
- تحویل فایل‌های استاندارد و سوابق فاکتور

---

## اهداف عددپذیر MVP (۳ ماه اول)

| شاخص | هدف |
|------|-----|
| تکمیل موفق سفارش | ≥ 85% |
| TAT اعتبارسنجی طرح | ≤ 2 ساعت در 90% موارد |
| TAT طرح اولیه نیمه‌خصوصی | ≤ 24 ساعت در 90% موارد |
| TAT چاپ و تحویل به پست | ≤ 48 ساعت در 90% موارد |
| خطای سازگاری فایل چاپ | ≤ 3% |
| موفقیت دانلود فاکتور با شماره | ≥ 95% |
| کاربران پرداخت‌کننده فعال | ≥ 200 |
| چاپخانه همکار فعال | ≥ 10 |
| درآمد ماهانه | ≥ 150,000,000 تومان |

---

## نقش‌ها و پنل‌ها

### 1. مدیرکل (Super Admin)
- تنظیمات قیمت/کمیسیون
- مدیریت کاربران/چاپخانه‌ها/طراحان
- حل اختلاف
- مالی/تسویه

### 2. مشتری (Customer)
- انتخاب محصول (لیبل/فاکتور)
- انتخاب مسیر طراحی/اعتبارسنجی
- پرداخت
- رهگیری سفارش
- دریافت فایل‌ها

### 3. طراح (Designer)
- دریافت بریف نیمه‌خصوصی/خصوصی
- تولید طرح
- مدیریت اصلاحات
- تحویل نهایی

### 4. اعتبارسنج (QA Design)
- بررسی فنی/چاپی فایل‌ها
- گزارش ایراد
- پیشنهاد هزینه اصلاح
- انجام اصلاح در صورت تأیید

### 5. چاپخانه (Print Shop)
- مشاهده/قبول سفارش
- چاپ
- بارگذاری مدرک ارسال (رسید/کدرهگیری)
- تنظیم وضعیت

---

## محصولات

### لیبل
- انتخاب سایز/جنس/تیراژ
- مسیر «دارای طرح» + اعتبارسنجی اختیاری
- مسیر «بدون طرح» با سه پلن طراحی

### فاکتور
- انتخاب طرح آماده
- نهایی‌سازی لوگو/اعتبارسنجی
- چاپ
- **پس از خرید:** ورود داده‌های فاکتور و دریافت فایل PDF قابل پرینت
- ذخیره و دانلود مجدد با شماره فاکتور

---

## پلن‌های طراحی

| پلن | قیمت | شرح |
|-----|------|-----|
| **عمومی** | رایگان | گالری طرح‌های آماده + جایگذاری لوگو |
| **نیمه‌خصوصی** | 600k–1.8m تومان | پرسشنامه سلیقه، حداکثر 3 دور اصلاح |
| **خصوصی** | 5,000,000 تومان | اصلاح نامحدود تا 14 روز |

---

## قیمت‌گذاری

| مورد | مبلغ | توضیح |
|------|------|-------|
| اعتبارسنجی طرح/لوگو | **50,000 تومان** | ثابت، غیرقابل استرداد پس از انجام |
| اصلاح طرح پس از اعتبارسنجی | 100k–600k تومان | براساس پیچیدگی، پیشنهاد اعتبارسنج |
| اشتراک جستجوی پیشرفته سوابق | **250,000 تومان/ماه** | فیلتر نام/تاریخ/مبلغ، خروجی CSV |
| کارمزد پلتفرم | 10% | از چاپخانه کسر، تسویه هفتگی |

---

## جریان‌های کاربری

### لیبل — مشتری دارای طرح

```
Start → انتخاب لیبل (سایز/جنس) → آپلود فایل → [پیشنهاد اعتبارسنجی 50,000]
    ├─ بله → پرداخت → ارسال به اعتبارسنج → گزارش ایراد + پیشنهاد اصلاح
    │         ├─ قبول → پرداخت اصلاح → انجام → تأیید نهایی
    │         └─ رد → ادامه با فایل فعلی (به‌ریسک مشتری)
    └─ خیر → ادامه با فایل فعلی
→ پرداخت چاپ → انتشار به چاپخانه‌ها → Accept ≤30 دقیقه → چاپ → ارسال
```

### لیبل — مشتری بدون طرح

```
Start → انتخاب لیبل → انتخاب پلن طراحی:
    ├─ عمومی: ارسال لوگو → [اعتبارسنجی؟] → انتخاب طرح آماده → پیش‌نمایش → تأیید
    ├─ نیمه‌خصوصی: پرسشنامه → پرداخت 100% → طرح ≤24h → ≤3 اصلاح → تأیید
    └─ خصوصی: پرداخت 5M → طرح اولیه → اصلاح نامحدود 14 روز → تأیید
→ پرداخت چاپ → چاپخانه → ارسال
```

### فاکتور

```
Start → نهایی‌سازی لوگو (+اعتبارسنجی) → انتخاب طرح آماده → پیش‌نمایش
→ پرداخت چاپ → چاپخانه → چاپ → تحویل
→ [پس از خرید] ورود اطلاعات فاکتور → تولید PDF → ذخیره → دانلود با شماره فاکتور
```

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
| city | String(100) | no | City |
| address | Text | no | Delivery address |
| role | Enum | yes | CUSTOMER / DESIGNER / VALIDATOR / PRINT_SHOP / ADMIN |
| is_active | Boolean | yes | Account status |
| created_at | DateTime | auto | Created timestamp |
| updated_at | DateTime | auto | Last update |

### Product (Label/Invoice Template)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| type | Enum | yes | LABEL / INVOICE |
| name | String | yes | Product name |
| size | String | yes | e.g., "5x5cm", "A5" |
| material | Enum | no | PAPER / PVC / METALLIC (for labels) |
| base_price | Decimal | yes | Base price |
| is_active | Boolean | yes | Available for order |

### Order

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| user_id | UUID | yes | FK to users |
| product_id | UUID | yes | FK to products |
| design_plan | Enum | yes | PUBLIC / SEMI_PRIVATE / PRIVATE / OWN_DESIGN |
| status | Enum | yes | See status list below |
| quantity | Integer | yes | Number of items |
| design_file_url | String | no | Uploaded/final design |
| validation_status | Enum | no | PENDING / PASSED / FAILED / FIXED |
| assigned_designer_id | UUID | no | FK to users (designer) |
| assigned_validator_id | UUID | no | FK to users (validator) |
| assigned_printshop_id | UUID | no | FK to users (print shop) |
| revision_count | Integer | default 0 | Number of revisions used |
| total_price | Decimal | yes | Total amount |
| tracking_code | String | no | Shipping tracking |
| created_at | DateTime | auto | Order date |
| updated_at | DateTime | auto | Last update |

### Order Status Values

```
PENDING                → در انتظار
AWAITING_VALIDATION    → در حال اعتبارسنجی
NEEDS_ACTION           → نیاز به اقدام
DESIGNING              → در حال طراحی
READY_FOR_PRINT        → آماده چاپ
PRINTING               → در حال چاپ
SHIPPED                → ارسال شده
DELIVERED              → تحویل شده
CANCELLED              → لغو شده
```

### Invoice (Post-Purchase)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| order_id | UUID | yes | FK to orders |
| invoice_number | String | yes | Unique, searchable |
| customer_name | String | yes | Invoice recipient |
| customer_code | String | no | Customer code |
| items | JSONB | yes | Line items array |
| total_amount | Decimal | yes | Invoice total |
| issue_date | Date | yes | Invoice date |
| pdf_file_url | String | yes | Generated PDF |
| created_at | DateTime | auto | Created |

### Payment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| order_id | UUID | yes | FK to orders |
| amount | Decimal | yes | Payment amount |
| type | Enum | yes | VALIDATION / DESIGN / FIX / PRINT / SUBSCRIPTION |
| status | Enum | yes | PENDING / SUCCESS / FAILED |
| transaction_id | String | no | PSP transaction ID |
| created_at | DateTime | auto | Payment time |

### Subscription

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | auto | Primary key |
| user_id | UUID | yes | FK to users |
| plan | Enum | yes | ADVANCED_SEARCH |
| price | Decimal | yes | 250,000 |
| start_date | Date | yes | Subscription start |
| end_date | Date | yes | Subscription end |
| is_active | Boolean | yes | Active status |

---

## API Endpoints

### Phase 0 (Current)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/health` | Health check | ✅ Done |
| POST | `/api/v1/users` | Create/update user | ✅ Done |
| GET | `/api/v1/users/{telegram_id}` | Get user | ✅ Done |
| PATCH | `/api/v1/users/{telegram_id}` | Update user | ✅ Done |

### Phase 1 (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/products` | List products (labels/templates) |
| GET | `/api/v1/products/{id}` | Get product details |
| POST | `/api/v1/orders` | Create order |
| GET | `/api/v1/orders` | List user orders |
| GET | `/api/v1/orders/{id}` | Get order details |
| PATCH | `/api/v1/orders/{id}/status` | Update order status |
| POST | `/api/v1/files/upload` | Upload design file |
| POST | `/api/v1/payments/initiate` | Initiate payment |
| POST | `/api/v1/payments/callback` | Payment callback |

### Phase 2-4 (Future)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/validation/request` | Request design validation |
| POST | `/api/v1/validation/{id}/report` | Submit validation report |
| POST | `/api/v1/design/revision` | Submit revision request |
| GET | `/api/v1/printshop/orders` | Print shop order queue |
| POST | `/api/v1/printshop/accept/{id}` | Accept order |
| POST | `/api/v1/invoices` | Create invoice record |
| GET | `/api/v1/invoices/{number}` | Get invoice by number |
| GET | `/api/v1/invoices/search` | Advanced search (subscription) |
| POST | `/api/v1/subscriptions` | Create subscription |
| POST | `/api/v1/tickets` | Create support ticket |

---

## SLAs

| نقش | SLA |
|-----|-----|
| اعتبارسنج | پاسخ اولیه ≤ 2 ساعت (09:00–21:00)، 90% رعایت |
| طراح نیمه‌خصوصی | طرح اولیه ≤ 24 ساعت، هر دور اصلاح ≤ 8 ساعت کاری |
| طراح خصوصی | طرح اولیه ≤ 24 ساعت، هر اصلاح ≤ 6 ساعت کاری |
| چاپخانه | پذیرش ≤ 30 دقیقه، چاپ و تحویل به پست ≤ 48 ساعت |
| پشتیبانی | پاسخ تیکت ≤ 2 ساعت کاری، حل اختلاف ≤ 2 روز کاری |

---

## قوانین کسب‌وکار

### اعتبارسنجی
- هزینه ثابت **50,000 تومان**
- شامل گزارش ایرادات (رزولوشن، فونت، برش، رنگ، فرمت)
- پیشنهاد اصلاح: 100,000–600,000 تومان

### اصلاحات
- **نیمه‌خصوصی:** حداکثر 3 دور؛ دور 4+ با هزینه 150,000 تومان
- **خصوصی:** نامحدود تا 14 روز پس از تحویل اولیه

### چاپخانه
- ملزم به چاپ مطابق فایل نهایی
- خطای چاپخانه → چاپ مجدد رایگان
- Accept ظرف 30 دقیقه، در غیر این‌صورت به بعدی

### لغو سفارش
- تا قبل از شروع چاپ امکان‌پذیر
- هزینه‌های انجام‌شده غیرقابل استرداد

### فایل چاپ
- استاندارد: PDF/X-1a، CMYK، 300DPI، Bleed 3mm
- فرمت‌های ورودی: PDF/AI/PSD/PNG/SVG (حداکثر 100MB)

---

## نیازمندی‌های غیرکارکردی (NFRs)

| شاخص | هدف |
|------|-----|
| زمان پاسخ ربات | ≤ 800ms (P95) |
| تولید پیش‌نمایش | ≤ 3 ثانیه |
| محاسبات قیمت | ≤ 300ms |
| سفارش/روز | 500 |
| همزمانی فعال | 100 |
| آپتایم | ≥ 99.5% ماهانه |
| TLS | تمام تبادلات |
| رمزنگاری فایل‌ها | AES-256 |
| نگهداری فایل نهایی | 12 ماه |
| نگهداری فایل موقت | 30 روز |
| حذف به درخواست کاربر | ≤ 5 روز کاری |

---

## نقشه راه (Roadmap)

### فاز 0 (هفته 1-2) ✅ Current
- [x] Bot پایه، پرداخت، ذخیره‌سازی
- [x] مدیریت کاربران
- [ ] کاتالوگ لیبل/فاکتور
- [ ] پنل‌های سبک

### فاز 1 (هفته 3-6)
- [ ] اعتبارسنجی فایل
- [ ] پلن طراحی عمومی
- [ ] توزیع سفارش به چاپخانه
- [ ] وضعیت‌ها/اعلان‌ها
- [ ] چاپ و ارسال

### فاز 2 (هفته 7-10)
- [ ] پلن نیمه‌خصوصی/خصوصی
- [ ] مدیریت اصلاحات
- [ ] گزارش‌ها و داشبورد

### فاز 3 (هفته 11-12)
- [ ] ماژول فاکتور پس از خرید (PDF دقیق)
- [ ] دانلود با شماره فاکتور

### فاز 4 (هفته 13-14)
- [ ] اشتراک جستجوی پیشرفته
- [ ] خروجی CSV
- [ ] داشبورد SLA

### پس از MVP
- مزایده قیمت چاپخانه
- کوپن‌ها/تخفیف‌ها
- اپ موبایل
- ادغام ERP/WMS
- چندزبانه

---

## Out of Scope (MVP)

- ❌ مزایده قیمت چاپخانه‌ها
- ❌ تخفیف‌های پویا/کوپن‌ها
- ❌ بارکد/QR پیشرفته روی لیبل
- ❌ ادغام با ERP/WMS
- ❌ اپ موبایل اختصاصی
- ❌ چندزبانه

---

## پیش‌فرض‌های حیاتی ⚑

1. ⚑ **کارمزد پلتفرم 10%** از چاپ بر عهده چاپخانه، تسویه هفتگی
2. ⚑ **پنجره اصلاح نامحدود پلن خصوصی = 14 روز** از تحویل اولیه
3. ⚑ **حداکثر حجم فایل ورودی 100MB** برای MVP
4. ⚑ **Profile رنگ پیش‌فرض FOGRA39** برای چاپ

---

## پرسش‌های باز

1. نرخ نهایی کارمزد پلتفرم (10% پیشنهادی)؟
2. مدل ارسال: تجمیع قرارداد پستی یا واگذاری به چاپخانه؟
3. تنوع سایز/جنس لیبل در MVP (Top-5 + 3 جنس)؟
4. سقف قیمت اصلاح اعتبارسنجی (>600k نیاز به تأیید)؟
5. تسویه طراح/اعتبارسنج: هفتگی یا سفارش‌به‌سفارش؟

---

## Change Management

هر تغییر در این اسکوپ نیاز دارد به:
1. تأیید کتبی از صاحب پروژه
2. سند ADR در `docs/`
3. به‌روزرسانی این فایل SCOPE.md

---

**Last Updated**: 2024-12-13  
**Source**: PRD_Telegram_Print_Bot_RTL_FIXED.docx
