# Bot Manual Test Checklist

This document provides a comprehensive checklist for manually testing the Sheetaro Telegram bot.

## Prerequisites

- [ ] Backend API is running and healthy
- [ ] Bot is running and connected to Telegram
- [ ] Test database is set up with initial data

---

## 1. User Registration & Authentication

### 1.1 New User Registration
- [ ] Send `/start` command
- [ ] Welcome message is displayed
- [ ] User is created in database
- [ ] Profile photo is saved (if available)
- [ ] Main menu keyboard appears

### 1.2 Existing User Login
- [ ] Send `/start` command again
- [ ] User data is updated (not duplicated)
- [ ] Correct role is reflected (CUSTOMER/ADMIN)
- [ ] Menu shows appropriate options

---

## 2. Admin Promotion

### 2.1 Promote to Admin
- [ ] Send `/makeadmin` command
- [ ] Success message is displayed
- [ ] User role changes to ADMIN in database
- [ ] Admin menu button appears after `/start`

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

---

## 4. Catalog Management (Admin Only)

### 4.1 Access Control
- [ ] Non-admin cannot access catalog menu
- [ ] Admin can access "📂 مدیریت کاتالوگ"
- [ ] Catalog menu shows options

### 4.2 Category Management
- [ ] "مدیریت دسته‌بندی‌ها" shows category list
- [ ] Can create new category (name, slug, icon)
- [ ] Can view category details
- [ ] Can delete category

### 4.3 Attribute Management
- [ ] Can add attributes to category
- [ ] Can set attribute type (TEXT/SELECT)
- [ ] Can add options to SELECT attribute
- [ ] Can delete attribute

### 4.4 Design Plan Management
- [ ] Can create PUBLIC plan (has_templates=true)
- [ ] Can create SEMI_PRIVATE plan (has_questionnaire=true)
- [ ] Can set price for plan
- [ ] Can delete plan

### 4.5 Question Management (Semi-Private)
- [ ] Can add questions to semi-private plan
- [ ] Can add options to SELECT question
- [ ] Can set question as required
- [ ] Questions appear in correct order

### 4.6 Template Management (Public)
- [ ] Can add templates to public plan
- [ ] Can set placeholder coordinates (x, y, w, h)
- [ ] Preview URL works
- [ ] File URL works

---

## 5. Order Flow (Customer)

### 5.1 Start Order
- [ ] Click "🛒 ثبت سفارش"
- [ ] Product type selection appears

### 5.2 Select Product
- [ ] Product list is displayed
- [ ] Products show name and price
- [ ] Can select a product

### 5.3 Select Design Plan
- [ ] Design plan options appear
- [ ] Price for each plan is shown
- [ ] Can select a plan

### 5.4 Fill Details
- [ ] For PUBLIC: Can select template
- [ ] For SEMI_PRIVATE: Questionnaire appears
- [ ] Can enter quantity
- [ ] Minimum quantity is enforced

### 5.5 Confirm Order
- [ ] Order summary is displayed
- [ ] Total price is calculated correctly
- [ ] Can confirm order
- [ ] Order is created in database

---

## 6. Payment Flow

### 6.1 Initiate Payment
- [ ] After order confirmation, payment info appears
- [ ] Card number is displayed (copyable, no hyphens)
- [ ] Card holder name is shown
- [ ] Amount is correct

### 6.2 Upload Receipt
- [ ] Can upload receipt image
- [ ] Image is saved correctly
- [ ] Confirmation message appears
- [ ] Payment status changes to AWAITING_APPROVAL

### 6.3 Admin Review (Admin)
- [ ] Admin receives notification
- [ ] Receipt image is visible
- [ ] Can approve payment
- [ ] Can reject payment with reason

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

### 7.2 Order Details
- [ ] Can view order details
- [ ] Product info is shown
- [ ] Payment status is shown
- [ ] Can cancel pending order

### 7.3 Order Tracking
- [ ] Click "🔍 رهگیری سفارش"
- [ ] Can enter order ID
- [ ] Status is displayed

---

## 8. Error Handling

### 8.1 API Errors
- [ ] Graceful error message when API is down
- [ ] Retry option is offered
- [ ] No stack traces shown to user

### 8.2 Invalid Input
- [ ] Invalid quantity shows error
- [ ] Invalid phone number shows error
- [ ] Empty required fields show error

---

## 9. Edge Cases

### 9.1 Concurrent Access
- [ ] Multiple users can use bot simultaneously
- [ ] No data corruption occurs

### 9.2 Session Handling
- [ ] Bot works after restart
- [ ] User context is maintained

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
| 8. Errors | | | |
| 9. Edge Cases | | | |

**Tested By:** _______________  
**Date:** _______________  
**Environment:** _______________

