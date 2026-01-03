# Bot Manual Test Checklist

This document provides a comprehensive checklist for manually testing the Sheetaro Telegram bot.

## Prerequisites

- [ ] Backend API is running and healthy (`/health` returns 200)
- [ ] Bot is running and connected to Telegram
- [ ] Database migrations are applied (`alembic upgrade head`)
- [ ] Test database has required enum types

---

## 1. User Registration & Authentication

### 1.1 New User Registration
- [ ] Send `/start` command
- [ ] Welcome message is displayed with correct username
- [ ] User is created in database
- [ ] Profile photo is saved (if available)
- [ ] Main menu keyboard appears (6 buttons for customer)

### 1.2 Existing User Login
- [ ] Send `/start` command again
- [ ] User data is updated (not duplicated)
- [ ] Correct role is reflected (CUSTOMER/ADMIN)
- [ ] Menu shows appropriate options
- [ ] `context.user_data['user_role']` is set correctly

---

## 2. Admin Promotion

### 2.1 Promote to Admin
- [ ] Send `/makeadmin` command
- [ ] Success message is displayed
- [ ] User role changes to ADMIN in database
- [ ] After `/start`, admin menu appears (7 buttons including "🔧 پنل مدیریت")

### 2.2 Already Admin
- [ ] Send `/makeadmin` when already admin
- [ ] "Already admin" message is displayed
- [ ] No duplicate promotion occurs

---

## 3. Profile Management

### 3.1 View Profile
- [ ] Click "👤 پروفایل" button
- [ ] Profile information is displayed correctly
- [ ] Edit button appears

### 3.2 Edit Profile
- [ ] Click "✏️ ویرایش پروفایل"
- [ ] Edit options appear
- [ ] Can update phone number
- [ ] Can update city
- [ ] Can update address
- [ ] Changes are saved to database
- [ ] "بازگشت" returns to profile view

---

## 4. Catalog Management (Admin Only)

### 4.1 Access Control
- [ ] Non-admin cannot access catalog menu (shows access denied)
- [ ] Admin can access "مدیریت کاتالوگ" (no emoji in button text)
- [ ] Catalog menu shows options correctly

### 4.2 Category Management
- [ ] "مدیریت دسته بندی ها" shows category list
- [ ] "➕ ایجاد دسته‌بندی جدید" button works
- [ ] Can enter category name (Persian)
- [ ] Can enter category slug (English)
- [ ] Can enter category icon (emoji)
- [ ] Can enter base price (number)
- [ ] Category is created successfully
- [ ] Can view category details
- [ ] Can delete category

### 4.3 Attribute Management
- [ ] Can access attributes from category actions
- [ ] Can add attributes to category
- [ ] Can set attribute type (TEXT/SELECT)
- [ ] For SELECT: can add options with label, value, price
- [ ] Can delete attribute

### 4.4 Design Plan Management
- [ ] Can access plans from category actions
- [ ] Can create PUBLIC plan (has_templates=true)
- [ ] Can create SEMI_PRIVATE plan (has_questionnaire=true)
- [ ] Can set price for plan
- [ ] Can delete plan

### 4.5 Question Management (Semi-Private Plans)
- [ ] Can access questions from semi-private plan
- [ ] Can add questions with Persian text
- [ ] Can set question type (TEXT/SINGLE_CHOICE/MULTI_CHOICE)
- [ ] For choice types: can add options
- [ ] Can set question as required
- [ ] Questions appear in correct order

### 4.6 Template Management (Public Plans)
- [ ] Can access templates from public plan
- [ ] Can add template with name
- [ ] Can set preview URL
- [ ] Can set file URL
- [ ] Can set placeholder coordinates (x, y, width, height)

---

## 5. Order Flow (Customer)

### 5.1 Start Order
- [ ] Click "🛒 ثبت سفارش"
- [ ] Category selection appears (dynamic list)

### 5.2 Select Category
- [ ] Categories show name and base price
- [ ] Can select a category

### 5.3 Fill Attributes
- [ ] TEXT attributes show input prompt
- [ ] SELECT attributes show option buttons
- [ ] All required attributes are collected

### 5.4 Select Design Plan
- [ ] Design plan options appear
- [ ] Price for each plan is shown
- [ ] Can select a plan

### 5.5 Plan-Specific Steps
- [ ] **PUBLIC**: Template list is shown, can select, upload logo works
- [ ] **SEMI_PRIVATE**: Questionnaire appears, all questions shown in order
- [ ] **PRIVATE**: Direct to quantity
- [ ] **OWN_DESIGN**: Upload prompt appears

### 5.6 Enter Quantity
- [ ] Quantity prompt appears
- [ ] Minimum quantity is enforced
- [ ] Invalid input shows error

### 5.7 Confirm Order
- [ ] Order summary is displayed
- [ ] Total price is calculated correctly
- [ ] Can confirm order
- [ ] Order is created in database

---

## 6. Payment Flow

### 6.1 Initiate Payment
- [ ] After order confirmation, payment info appears
- [ ] Card number is displayed (copyable, **no hyphens**)
- [ ] Card holder name is shown
- [ ] Bank name is shown
- [ ] Amount is correct (no scientific notation)

### 6.2 Upload Receipt
- [ ] Can upload receipt image (photo)
- [ ] Image is saved correctly
- [ ] Confirmation message appears
- [ ] Payment status changes to AWAITING_APPROVAL

### 6.3 Admin Review (Admin)
- [ ] Admin receives notification
- [ ] Receipt **image is sent as photo** (not just URL)
- [ ] Payment details in caption
- [ ] Approve/Reject buttons work
- [ ] Can approve payment
- [ ] Can reject payment with reason input

### 6.4 Payment Result
- [ ] Customer is notified of approval
- [ ] Customer is notified of rejection (with reason)
- [ ] Order status updates accordingly

---

## 7. Order Management

### 7.1 View Orders
- [ ] Click "📦 سفارشات من"
- [ ] Order list is displayed
- [ ] Orders show status and date
- [ ] Prices display correctly (no scientific notation)

### 7.2 Order Details
- [ ] Can view order details
- [ ] Product info is shown
- [ ] Payment status is shown
- [ ] Can cancel pending order

### 7.3 Order Tracking
- [ ] Click "🔍 رهگیری سفارش"
- [ ] Can enter order ID
- [ ] Status is displayed correctly

---

## 8. Flow Management (Technical)

### 8.1 State Persistence
- [ ] `current_flow` is set when entering a flow
- [ ] `flow_step` updates correctly on each step
- [ ] `flow_data` accumulates data correctly
- [ ] `clear_flow()` is called when exiting

### 8.2 Text Router
- [ ] Text input routes to correct flow handler
- [ ] Unknown flow clears state and shows menu
- [ ] Logs show flow/step for debugging

### 8.3 Callback Queries
- [ ] Callbacks work regardless of conversation state
- [ ] Pattern matching is correct (no encoding issues)
- [ ] No emojis in callback patterns

### 8.4 Navigation
- [ ] "بازگشت" buttons work in all flows
- [ ] Can navigate back to menu from any state
- [ ] Flow state clears on menu return

---

## 9. Error Handling

### 9.1 API Errors
- [ ] Graceful error message when API is down
- [ ] Retry option is offered where appropriate
- [ ] No stack traces shown to user

### 9.2 Invalid Input
- [ ] Invalid quantity shows error
- [ ] Invalid phone number shows error
- [ ] Empty required fields show error
- [ ] Non-numeric price input shows error

### 9.3 Database Errors
- [ ] Missing tables show appropriate error (not raw SQL error)
- [ ] Missing columns handled gracefully

---

## 10. Edge Cases

### 10.1 Concurrent Access
- [ ] Multiple users can use bot simultaneously
- [ ] No data corruption occurs
- [ ] User A's state doesn't affect User B

### 10.2 Session Handling
- [ ] Bot works after restart
- [ ] Flow state persists (in user_data)

### 10.3 Encoding
- [ ] Persian text displays correctly
- [ ] Emojis display correctly
- [ ] No encoding issues in callbacks (buttons without emojis)

---

## 11. Integration Tests

### 11.1 Backend API
- [ ] Health check passes
- [ ] User creation works
- [ ] Category API works
- [ ] Order creation works
- [ ] Payment flow works

### 11.2 Database
- [ ] All migrations applied
- [ ] Enum types exist
- [ ] Foreign key constraints work

---

## Test Results Summary

| Section | Passed | Failed | Notes |
|---------|--------|--------|-------|
| 1. Registration | | | |
| 2. Admin | | | |
| 3. Profile | | | |
| 4. Catalog | | | |
| 5. Orders | | | |
| 6. Payment | | | |
| 7. Management | | | |
| 8. Flow Mgmt | | | |
| 9. Errors | | | |
| 10. Edge Cases | | | |
| 11. Integration | | | |

**Tested By:** _______________  
**Date:** _______________  
**Environment:** _______________  
**Bot Version:** _______________  
**Backend Version:** _______________

---

## Quick Debug Commands

```bash
# Check bot logs
docker compose -f docker-compose.prod.yml logs bot --tail 100

# Check backend logs  
docker compose -f docker-compose.prod.yml logs backend --tail 100

# Check if migrations applied
docker compose -f docker-compose.prod.yml exec backend alembic current

# Restart bot
docker compose -f docker-compose.prod.yml restart bot

# Check database
docker compose -f docker-compose.prod.yml exec db psql -U sheetaro -c "SELECT * FROM users LIMIT 5;"
```

---

**Last Updated**: 2026-01-03
