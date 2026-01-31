# راهنمای تست‌نویسی شیتارو

## فهرست مطالب

1. [ساختار تست‌ها](#ساختار-تستها)
2. [انواع تست‌ها](#انواع-تستها)
3. [نحوه اجرای تست‌ها](#نحوه-اجرای-تستها)
4. [نوشتن تست جدید](#نوشتن-تست-جدید)
5. [چک‌لیست قبل از PR](#چکلیست-قبل-از-pr)
6. [CI/CD Pipeline](#cicd-pipeline)

---

## ساختار تست‌ها

```
src/__tests__/
├── audits/                      # تست‌های اوديت خودکار
│   ├── interactive-elements.test.tsx  # بررسی دکمه‌ها و المان‌های تعاملی
│   ├── form-validation.test.tsx       # بررسی validation فرم‌ها
│   └── link-href.test.tsx             # بررسی لینک‌ها
│
├── templates/                   # الگوهای تست
│   └── crud.template.ts         # الگوی CRUD برای entity های جدید
│
├── components/                  # تست کامپوننت‌ها
│   ├── Button.test.tsx
│   ├── Modal.test.tsx
│   └── Input.test.tsx
│
├── hooks/                       # تست hooks
│   ├── useAuth.test.tsx
│   └── useOrders.test.tsx
│
├── pages/                       # تست صفحات
│   ├── login.test.tsx
│   ├── register.test.tsx
│   └── admin/
│       ├── dashboard.test.tsx
│       └── payments.test.tsx
│
├── contracts/                   # تست هماهنگی schema ها
│   └── api-contracts.test.ts
│
├── api/                         # تست URL validation
│   └── url-validation.test.ts
│
├── utils/                       # تست utility functions
│   └── error-handling.test.ts
│
└── smoke/                       # تست با backend واقعی
    └── admin-catalog.smoke.test.ts

e2e/                             # تست‌های E2E با Playwright
├── auth.spec.ts
├── order.spec.ts
├── admin.spec.ts
└── admin-catalog.spec.ts
```

---

## انواع تست‌ها

### 1. Audit Tests (تست‌های اوديت)

تست‌هایی که به صورت خودکار کد را بررسی می‌کنند:

- **interactive-elements**: بررسی اینکه همه دکمه‌ها `onClick` دارند
- **form-validation**: بررسی اینکه همه فرم‌ها validation دارند
- **link-href**: بررسی اینکه همه لینک‌ها `href` معتبر دارند

```bash
npm run test:audit
```

### 2. Unit Tests (تست‌های واحد)

تست کامپوننت‌ها، hooks و utility functions به صورت مجزا:

```bash
npm run test:unit
```

### 3. Contract Tests (تست قرارداد)

اطمینان از هماهنگی schema های frontend با backend:

```bash
npm run test:contracts
```

### 4. Smoke Tests (تست دود)

تست با backend واقعی برای اطمینان از کارکرد API:

```bash
npm run test:smoke
```

### 5. E2E Tests (تست سرتاسری)

تست کامل flow های کاربری با Playwright:

```bash
npm run test:e2e
npm run test:e2e:ui  # با UI
```

---

## نحوه اجرای تست‌ها

### اجرای همه تست‌ها

```bash
npm test
```

### اجرای تست‌های خاص

```bash
# فقط audit tests
npm run test:audit

# فقط unit tests
npm run test:unit

# فقط contract tests
npm run test:contracts

# فقط تست‌های تغییر یافته
npm run test:changed

# تست با coverage
npm run test:coverage
```

### اجرای تست در حالت watch

```bash
npm run test:watch
```

### اجرای E2E tests

```bash
# اجرای headless
npm run test:e2e

# اجرای با UI
npm run test:e2e:ui
```

---

## نوشتن تست جدید

### قانون ۱: هر دکمه باید تست شود

```typescript
test('button X triggers action Y', async () => {
  const user = userEvent.setup();
  render(<Component />);
  
  const button = screen.getByRole('button', { name: /متن دکمه/i });
  expect(button).toBeInTheDocument();
  
  await user.click(button);
  
  // بررسی نتیجه
  expect(mockFn).toHaveBeenCalled();
});
```

### قانون ۲: هر فرم باید validation تست داشته باشد

```typescript
test('form validates required fields', async () => {
  const user = userEvent.setup();
  render(<FormComponent />);
  
  // کلیک روی submit بدون پر کردن فرم
  await user.click(screen.getByRole('button', { name: /ارسال/i }));
  
  // باید خطا نشان دهد
  expect(screen.getByText(/اجباری/i)).toBeInTheDocument();
});
```

### قانون ۳: از الگوی CRUD استفاده کنید

برای entity های جدید از template استفاده کنید:

```typescript
import { generateAllCrudTests } from '@/__tests__/templates/crud.template';

const config = {
  entityName: 'category',
  entityNamePersian: 'دسته‌بندی',
  PageComponent: CatalogPage,
  api: { list, create, update, delete },
  sampleData: { ... },
  ui: { ... },
};

generateAllCrudTests(config);
```

### قانون ۴: Contract test برای schema های جدید

```typescript
import { z } from 'zod';

const CategorySchema = z.object({
  slug: z.string().min(1),
  name_fa: z.string().min(1),
  is_active: z.boolean(),
});

test('CategoryCreate schema matches backend', () => {
  expect(() => CategorySchema.parse({
    slug: 'test',
    name_fa: 'تست',
    is_active: true,
  })).not.toThrow();
});
```

---

## چک‌لیست قبل از PR

### برای هر فیچر جدید:

- [ ] تمام دکمه‌ها `onClick` دارند
- [ ] فرم‌ها validation دارند
- [ ] لینک‌ها `href` معتبر دارند
- [ ] Unit test برای کامپوننت‌های جدید
- [ ] Contract test برای schema های جدید
- [ ] E2E test برای flow های اصلی

### اجرای تست‌ها:

```bash
# قبل از commit
npm run test:precommit

# قبل از PR
npm test
npm run test:e2e
```

---

## CI/CD Pipeline

### مراحل Pipeline

1. **Audit** - بررسی دکمه‌ها و لینک‌ها
2. **Unit Tests** - تست‌های واحد با coverage
3. **Contract Tests** - بررسی schema ها
4. **TypeScript Check** - بررسی type errors
5. **E2E Tests** - تست سرتاسری

### Coverage Threshold

- حداقل 50% coverage برای unit tests
- هدف: 80% coverage

---

## ابزارها و کتابخانه‌ها

| ابزار | کاربرد |
|-------|--------|
| Vitest | Test runner |
| React Testing Library | تست کامپوننت‌ها |
| MSW | Mock کردن API |
| Playwright | تست E2E |
| Zod | Contract testing |

---

## مثال‌های کاربردی

### تست دکمه با modal

```typescript
test('new category button opens modal', async () => {
  const user = userEvent.setup();
  render(<CatalogPage />, { wrapper: createWrapper() });

  await user.click(screen.getByRole('button', { name: /دسته‌بندی جدید/i }));

  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByText(/ایجاد دسته‌بندی/i)).toBeVisible();
});
```

### تست API call

```typescript
test('form submission calls API', async () => {
  const mockCreate = vi.fn().mockResolvedValue({ data: {} });
  vi.mocked(adminApi.createCategory).mockImplementation(mockCreate);

  const user = userEvent.setup();
  render(<CatalogPage />, { wrapper: createWrapper() });

  await user.click(screen.getByRole('button', { name: /دسته‌بندی جدید/i }));
  await user.type(screen.getByLabelText(/نام/i), 'تست');
  await user.click(screen.getByRole('button', { name: /ایجاد/i }));

  expect(mockCreate).toHaveBeenCalled();
});
```

### تست E2E با Playwright

```typescript
test('admin can create category', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto('/admin/catalog');
  
  await page.click('text=دسته‌بندی جدید');
  await page.fill('[placeholder*="کارت ویزیت"]', 'تست');
  await page.click('text=ایجاد');
  
  await expect(page.getByText('ایجاد شد')).toBeVisible();
});
```

---

## سوالات متداول

### چرا تست‌ها fail می‌شوند؟

1. **دکمه بدون onClick**: از `npm run lint:buttons` استفاده کنید
2. **API mock نشده**: MSW handler اضافه کنید
3. **Async issues**: از `waitFor` استفاده کنید

### چطور mock اضافه کنم؟

در فایل `src/__tests__/mocks/handlers.ts`:

```typescript
http.post('/api/v1/new-endpoint', () => {
  return HttpResponse.json({ data: 'response' });
}),
```

---

## منابع بیشتر

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)

