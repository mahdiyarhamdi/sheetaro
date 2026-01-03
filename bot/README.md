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
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token from BotFather | Yes |
| `BACKEND_URL` | Backend API URL | Yes |

## Features

### Customer Features
- 🆕 Register with `/start`
- 🛒 Order products (dynamic categories: labels, invoices, etc.)
- 📦 Track orders
- 👤 Edit profile (phone, address)
- 💳 Upload payment receipts

### Admin Features
- 🔧 Admin Panel (only for admins)
- 💰 Review pending payments
- ✅ Approve/reject receipts
- 📂 Manage product catalog (categories, attributes, plans)
- 📝 Manage questionnaires for semi-private plans
- 🖼️ Manage templates for public plans
- ⚙️ Configure payment card

### Become Admin
- Send `/makeadmin` command to instantly become an admin

## Architecture

### Unified Flow Management

The bot uses a **unified flow management** system instead of `ConversationHandler`. This provides:

- **Centralized State**: All state is managed through `flow_manager.py`
- **Single Router**: `text_router.py` routes all text input to appropriate handlers
- **No ConversationHandler**: Removed complex handler stacking issues
- **Clear Flow Separation**: Each flow (admin, catalog, orders, etc.) has its own handler module

```
User Input (Text/Callback)
         │
         ▼
┌─────────────────────┐
│    text_router      │  ← Routes based on current_flow & flow_step
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┬──────────┬──────────┐
    ▼             ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ catalog │ │  admin  │ │ orders  │ │products │ │ profile │
│  flow   │ │  flow   │ │  flow   │ │  flow   │ │  flow   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Flow State

State is stored in `context.user_data`:

```python
context.user_data = {
    'current_flow': 'catalog',      # Active flow name
    'flow_step': 'category_create_name',  # Current step
    'flow_data': {                  # Flow-specific data
        'category_name': 'لیبل',
        'category_slug': 'label'
    }
}
```

## Project Structure

```
bot/
├── bot.py                  # Main entry point
├── handlers/               # Message & callback handlers
│   ├── start.py           # /start and /makeadmin commands
│   ├── menu.py            # Main menu handler
│   ├── products.py        # Product selection & ordering (legacy)
│   ├── dynamic_order.py   # Dynamic product ordering (new)
│   ├── orders.py          # Order management
│   ├── profile.py         # Profile editing
│   ├── tracking.py        # Order tracking
│   ├── admin_payments.py  # Admin payment review
│   ├── admin_settings.py  # Admin settings (payment card)
│   ├── admin_catalog.py   # Admin catalog management
│   ├── text_router.py     # Central text input router
│   └── flows/             # Flow-specific text handlers
│       ├── catalog_flow.py
│       ├── admin_flow.py
│       ├── order_flow.py
│       ├── product_flow.py
│       └── profile_flow.py
├── keyboards/              # Telegram keyboards
│   ├── main_menu.py       # Main menu (dynamic for admin/customer)
│   ├── products.py        # Product selection keyboards
│   ├── orders.py          # Order-related keyboards
│   ├── profile.py         # Profile edit keyboards
│   ├── admin.py           # Admin panel keyboards
│   └── manager.py         # Keyboard manager utilities
├── utils/
│   ├── api_client.py      # Backend API client
│   ├── helpers.py         # Helper functions (role-based menu)
│   ├── flow_manager.py    # Unified flow state management
│   └── notifications.py   # Admin notification utilities
├── requirements.txt
└── Dockerfile
```

## User Flows

### Order Flow
```
1. Main Menu → 🛒 ثبت سفارش
2. Select category (Label/Invoice/etc.)
3. Select/fill attributes
4. Select design plan (Public/Semi-private/Private/Own)
5. [Public] Select template, upload logo
6. [Semi-private] Fill questionnaire
7. Select validation option
8. Enter quantity
9. Confirm & Pay
10. Upload receipt → Admin reviews → Order confirmed
```

### Payment Flow (Card-to-Card)
```
1. Order created → Payment initiated
2. Customer receives card details (copyable, no hyphens)
3. Customer transfers money and uploads receipt photo
4. Admin receives notification with receipt image
5. Admin approves/rejects
6. Customer notified of result
```

### Admin Menu (only for role=ADMIN)
```
🔧 پنل مدیریت
├── 💰 پرداخت‌های در انتظار
├── مدیریت کاتالوگ
│   ├── دسته‌بندی‌ها (+ قیمت پایه)
│   ├── ویژگی‌ها و گزینه‌ها
│   ├── پلن‌های طراحی
│   ├── پرسشنامه‌ها (نیمه‌خصوصی)
│   └── قالب‌ها (عمومی)
└── ⚙️ تنظیمات سیستم
```

## Dynamic Menus

The main menu is role-based:
- **Customers**: 6 buttons (order, orders, track, profile, support, about)
- **Admins**: 7 buttons (same + Admin Panel)

Role is stored in `context.user_data['user_role']` after `/start`.

## Key Components

### Flow Manager (`utils/flow_manager.py`)

Provides unified state management:

```python
# Set current flow
set_flow(context, FLOW_CATALOG, 'category_create_name', {'category_name': 'لیبل'})

# Get current flow info
flow = get_flow(context)      # 'catalog'
step = get_step(context)      # 'category_create_name'
data = get_flow_data(context) # {'category_name': 'لیبل'}

# Update step
set_step(context, 'category_create_slug')

# Update flow data
update_flow_data(context, 'slug', 'label')

# Clear flow when done
clear_flow(context)
```

### Text Router (`handlers/text_router.py`)

Routes all text input:

```python
async def route_text_input(update, context):
    current_flow = get_flow(context)
    
    if current_flow == FLOW_CATALOG:
        await route_catalog_text(update, context, step)
    elif current_flow == FLOW_ADMIN:
        await route_admin_text(update, context, step)
    # ... etc
```

### API Client (`utils/api_client.py`)

Communicates with backend API using `httpx`:
- User registration/updates
- Product listing
- Order management
- Payment operations
- Admin operations
- Category/attribute/plan management

### Helpers (`utils/helpers.py`)
- `get_user_menu_keyboard(context)` - Returns appropriate menu for user role

### Notifications (`utils/notifications.py`)
- `notify_admin_new_receipt()` - Notifies admins of new payment receipts

## Flow Handlers

| Flow | Steps | Purpose |
|------|-------|---------|
| `catalog` | 20+ steps | Category, attribute, plan, question, template management |
| `admin` | 6 steps | Payment review, admin management |
| `orders` | 6 steps | Order listing, details, cancellation |
| `products` | 7 steps | Legacy product ordering |
| `profile` | 4 steps | Profile viewing and editing |
| `tracking` | 2 steps | Order tracking by ID |

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and show main menu |
| `/makeadmin` | Become an admin (self-promotion) |

## Callback Query Handling

All callback queries are handled by standalone handlers registered in `bot.py`:

```python
# Catalog callbacks
application.add_handler(CallbackQueryHandler(show_category_list, pattern="^catalog_categories$"))
application.add_handler(CallbackQueryHandler(start_category_create, pattern="^cat_create$"))
# ... etc
```

This ensures callbacks work regardless of conversation state.

---

**Last Updated**: 2026-01-03
