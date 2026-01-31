---
name: Fix Plan Type Mismatch
overview: اصلاح عدم تطابق بین interface فرانت‌اند و پاسخ واقعی بکند برای فیلدهای نوع پلن طراحی.
todos:
  - id: fix-api-interface
    content: اصلاح interface DesignPlan در api.ts
    status: completed
  - id: fix-new-order-logic
    content: اصلاح منطق شرطی در new-order page
    status: completed
  - id: todo-1769900736799-vtv71c64p
    content: آپدیت مستندات و تست ها و کامیت
    status: completed
---

# رفع مشکل نوع پلن طراحی

## مشکل

فرانت‌اند انتظار `plan_type` دارد اما بکند فیلدهای boolean برمی‌گرداند.

## راه‌حل

### 1. اصلاح interface در [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts)

```typescript
export interface DesignPlan {
  id: string;
  category_id: string;
  name_fa: string;
  slug: string;
  // Backend uses flags instead of plan_type
  has_templates: boolean;
  has_questionnaire: boolean;
  has_file_upload: boolean;
  price: number;
  is_active: boolean;
  templates?: Template[];
  questionnaire?: Questionnaire;
}
```

### 2. اصلاح منطق در [`frontend/src/app/(dashboard)/new-order/page.tsx`](frontend/src/app/\\(dashboard)/new-order/page.tsx)

تغییر شرط‌ها از:

```typescript
if (selectedPlan.plan_type === "public")
```

به:

```typescript
if (selectedPlan.has_templates)
```

منطق:

- `has_templates = true` → پلن عمومی (انتخاب قالب)
- `has_questionnaire = true` → پلن نیمه‌خصوصی (پرسشنامه)
- `has_file_upload = true` → پلن خصوصی (آپلود فایل)