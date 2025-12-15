# Sheetaro Telegram Bot

Telegram bot for the Sheetaro print ordering system using `python-telegram-bot`.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

## Docker

```bash
docker-compose up bot
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from BotFather | Yes |
| `BACKEND_URL` | Backend API URL | Yes |

## Features

### Customer Features
- 🆕 Register with `/start`
- 🛒 Order products (labels, invoices)
- 📦 Track orders
- 👤 Edit profile (phone, address)
- 💳 Upload payment receipts

### Admin Features
- 🔧 Admin Panel (only for admins)
- 💰 Review pending payments
- ✅ Approve/reject receipts
- 👥 Manage admins (promote/demote)
- ⚙️ Configure payment card

## Project Structure

```
bot/
├── bot.py                  # Main entry point
├── handlers/               # Message & callback handlers
│   ├── start.py           # /start command
│   ├── menu.py            # Main menu handler
│   ├── products.py        # Product selection & ordering
│   ├── orders.py          # Order management
│   ├── profile.py         # Profile editing
│   ├── tracking.py        # Order tracking
│   ├── admin_payments.py  # Admin payment review
│   └── admin_settings.py  # Admin settings (payment card)
├── keyboards/              # Telegram keyboards
│   ├── main_menu.py       # Main menu (dynamic for admin/customer)
│   ├── products.py        # Product selection keyboards
│   ├── orders.py          # Order-related keyboards
│   ├── profile.py         # Profile edit keyboards
│   └── admin.py           # Admin panel keyboards
├── utils/
│   ├── api_client.py      # Backend API client
│   ├── helpers.py         # Helper functions (role-based menu)
│   └── notifications.py   # Admin notification utilities
├── requirements.txt
└── Dockerfile
```

## User Flows

### Order Flow
```
1. Main Menu → 🛒 ثبت سفارش
2. Select product type (Label/Invoice)
3. Select specific product
4. Select design plan (Public/Semi-private/Private/Own)
5. Select validation option
6. Enter quantity
7. Confirm & Pay
8. Upload receipt → Admin reviews → Order confirmed
```

### Payment Flow (Card-to-Card)
```
1. Order created → Payment initiated
2. Customer receives card details (copyable)
3. Customer transfers money and uploads receipt photo
4. Admin receives notification with receipt image
5. Admin approves/rejects
6. Customer notified of result
```

### Admin Menu (only for role=ADMIN)
```
🔧 پنل مدیریت
├── 💰 پرداخت‌های در انتظار
├── 👥 مدیریت ادمین‌ها
└── ⚙️ تنظیمات سیستم
```

## Dynamic Menus

The main menu is role-based:
- **Customers**: 6 buttons (order, orders, track, profile, support, about)
- **Admins**: 7 buttons (same + Admin Panel)

Role is stored in `context.user_data['user_role']` after `/start`.

## Key Components

### API Client (`utils/api_client.py`)
Communicates with backend API using `httpx`:
- User registration/updates
- Product listing
- Order management
- Payment operations
- Admin operations

### Helpers (`utils/helpers.py`)
- `get_user_menu_keyboard(context)` - Returns appropriate menu for user role

### Notifications (`utils/notifications.py`)
- `notify_admin_new_receipt()` - Notifies admins of new payment receipts

## Conversation Handlers

| Handler | States | Purpose |
|---------|--------|---------|
| `product_conversation` | 7 states | Product selection & ordering |
| `orders_conversation` | 5 states | Order management & payment |
| `profile_conversation` | 2 states | Profile editing |
| `admin_payments_conversation` | 6 states | Payment review |
| `admin_settings_conversation` | 3 states | System settings |

---

**Last Updated**: 2025-12-14

