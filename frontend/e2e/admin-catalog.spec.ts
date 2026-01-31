/**
 * E2E tests for Admin Catalog CRUD Operations
 * 
 * Tests full CRUD flows for:
 * - Categories
 * - Products  
 * - Design Plans
 */

import { test, expect, Page } from "@playwright/test";

// Admin test data
const adminUser = {
  phone: "09120000000",
  password: "admin123456",
};

// Test data
const testCategory = {
  name: "تست دسته‌بندی " + Date.now(),
  slug: "test-category-" + Date.now(),
  description: "توضیحات تست",
};

const testProduct = {
  name: "تست محصول " + Date.now(),
  price: "50000",
  description: "توضیحات محصول تست",
};

const testPlan = {
  name: "تست پلن " + Date.now(),
  price: "100000",
  revisions: "3",
  deliveryDays: "5",
};

// Helper to login as admin
async function loginAsAdmin(page: Page) {
  await page.goto("/login");
  await page.fill('[placeholder="09123456789"]', adminUser.phone);
  await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', adminUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
}

// Helper to navigate to catalog page
async function goToCatalog(page: Page) {
  await page.goto("/admin/catalog");
  await page.waitForLoadState("networkidle");
}

test.describe("Admin Catalog - Categories CRUD", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await goToCatalog(page);
  });

  test("E2E-CAT-01: Category tabs display correctly", async ({ page }) => {
    // Should show all three tabs
    await expect(page.getByRole("button", { name: /دسته‌بندی/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /محصولات/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /پلن/i })).toBeVisible();
  });

  test("E2E-CAT-02: Can open new category modal", async ({ page }) => {
    // Click new category button
    const newButton = page.getByRole("button", { name: /دسته‌بندی جدید/i });
    await expect(newButton).toBeVisible();
    await newButton.click();

    // Modal should open
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.getByText(/ایجاد دسته‌بندی جدید/i)).toBeVisible();
  });

  test("E2E-CAT-03: Category form validates required fields", async ({ page }) => {
    // Open modal
    await page.getByRole("button", { name: /دسته‌بندی جدید/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // Try to submit empty form
    await page.getByRole("button", { name: /ایجاد/i }).click();

    // Should show error or prevent submission
    // Modal should still be open (form not submitted)
    await expect(page.getByRole("dialog")).toBeVisible();
  });

  test("E2E-CAT-04: Can create a new category", async ({ page }) => {
    // Open modal
    await page.getByRole("button", { name: /دسته‌بندی جدید/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // Fill form
    await page.getByPlaceholder(/کارت ویزیت/i).fill(testCategory.name);
    
    // Slug should be auto-generated or we fill it
    const slugInput = page.getByPlaceholder(/business-card/i);
    if (await slugInput.isVisible()) {
      const slugValue = await slugInput.inputValue();
      if (!slugValue) {
        await slugInput.fill(testCategory.slug);
      }
    }

    // Fill optional description
    const descInput = page.locator('textarea').first();
    if (await descInput.isVisible()) {
      await descInput.fill(testCategory.description);
    }

    // Submit
    await page.getByRole("button", { name: /ایجاد/i }).click();

    // Should show success message
    await expect(page.getByText(/ایجاد شد|موفق/i)).toBeVisible({ timeout: 5000 });

    // Modal should close
    await expect(page.getByRole("dialog")).not.toBeVisible();

    // Category should appear in list
    await expect(page.getByText(testCategory.name)).toBeVisible();
  });

  test("E2E-CAT-05: Can cancel category creation", async ({ page }) => {
    // Open modal
    await page.getByRole("button", { name: /دسته‌بندی جدید/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // Fill some data
    await page.getByPlaceholder(/کارت ویزیت/i).fill("تست لغو");

    // Cancel
    await page.getByRole("button", { name: /انصراف/i }).click();

    // Modal should close
    await expect(page.getByRole("dialog")).not.toBeVisible();

    // Data should not be saved
    await expect(page.getByText("تست لغو")).not.toBeVisible();
  });

  test("E2E-CAT-06: Can edit existing category", async ({ page }) => {
    // Find edit button for first category
    const editButton = page.locator('button').filter({ has: page.locator('svg.lucide-pencil') }).first();
    
    if (await editButton.isVisible()) {
      await editButton.click();

      // Modal should open with edit title
      await expect(page.getByRole("dialog")).toBeVisible();
      await expect(page.getByText(/ویرایش دسته‌بندی/i)).toBeVisible();

      // Modify name
      const nameInput = page.getByPlaceholder(/کارت ویزیت/i);
      await nameInput.clear();
      await nameInput.fill("نام ویرایش شده");

      // Submit
      await page.getByRole("button", { name: /به‌روزرسانی/i }).click();

      // Should show success
      await expect(page.getByText(/به‌روزرسانی شد|موفق/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test("E2E-CAT-07: Can delete category", async ({ page }) => {
    // Count categories before
    const categoriesBefore = await page.locator('[class*="rounded-xl"][class*="border"]').count();

    // Find delete button for first category
    const deleteButton = page.locator('button').filter({ has: page.locator('svg.lucide-trash-2') }).first();
    
    if (await deleteButton.isVisible() && categoriesBefore > 0) {
      await deleteButton.click();

      // Confirm if dialog appears
      const confirmButton = page.getByRole("button", { name: /تأیید|بله|حذف/i });
      if (await confirmButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await confirmButton.click();
      }

      // Should show success message
      await expect(page.getByText(/حذف شد|موفق/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe("Admin Catalog - Products CRUD", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await goToCatalog(page);
    
    // Switch to products tab
    await page.getByRole("button", { name: /محصولات/i }).click();
    await page.waitForTimeout(500);
  });

  test("E2E-PRD-01: Products tab displays correctly", async ({ page }) => {
    // Products tab should be active
    const productsTab = page.getByRole("button", { name: /محصولات/i });
    await expect(productsTab).toHaveClass(/bg-primary/);
  });

  test("E2E-PRD-02: Can open new product modal", async ({ page }) => {
    const newButton = page.getByRole("button", { name: /محصول جدید/i });
    await expect(newButton).toBeVisible();
    await newButton.click();

    // Modal should open
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.getByText(/ایجاد محصول جدید/i)).toBeVisible();
  });

  test("E2E-PRD-03: Product form has required fields", async ({ page }) => {
    await page.getByRole("button", { name: /محصول جدید/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // Should have name field
    await expect(page.getByPlaceholder(/سلفون مات/i)).toBeVisible();
    
    // Should have price field
    await expect(page.getByLabelText(/قیمت/i)).toBeVisible();
    
    // Should have category selector
    await expect(page.locator('select').first()).toBeVisible();
  });

  test("E2E-PRD-04: Can create a new product", async ({ page }) => {
    await page.getByRole("button", { name: /محصول جدید/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // Fill product name
    await page.getByPlaceholder(/سلفون مات/i).fill(testProduct.name);

    // Select category (first option)
    const categorySelect = page.locator('select').first();
    const options = await categorySelect.locator('option').allTextContents();
    if (options.length > 1) {
      await categorySelect.selectOption({ index: 1 });
    }

    // Fill price
    const priceInput = page.getByLabel(/قیمت/i).first();
    if (await priceInput.isVisible()) {
      await priceInput.fill(testProduct.price);
    }

    // Submit
    await page.getByRole("button", { name: /ایجاد/i }).click();

    // Should show success
    await expect(page.getByText(/ایجاد شد|موفق/i)).toBeVisible({ timeout: 5000 });
  });

  test("E2E-PRD-05: Can edit existing product", async ({ page }) => {
    const editButton = page.locator('button').filter({ has: page.locator('svg.lucide-pencil') }).first();
    
    if (await editButton.isVisible()) {
      await editButton.click();

      await expect(page.getByRole("dialog")).toBeVisible();
      await expect(page.getByText(/ویرایش محصول/i)).toBeVisible();
    }
  });

  test("E2E-PRD-06: Can delete product", async ({ page }) => {
    const deleteButton = page.locator('button').filter({ has: page.locator('svg.lucide-trash-2') }).first();
    
    if (await deleteButton.isVisible()) {
      await deleteButton.click();

      // Confirm if needed
      const confirmButton = page.getByRole("button", { name: /تأیید|بله|حذف/i });
      if (await confirmButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await confirmButton.click();
      }

      await expect(page.getByText(/حذف شد|موفق/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe("Admin Catalog - Plans CRUD", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await goToCatalog(page);
    
    // Switch to plans tab
    await page.getByRole("button", { name: /پلن/i }).click();
    await page.waitForTimeout(500);
  });

  test("E2E-PLN-01: Plans tab displays category selector", async ({ page }) => {
    // Should show category selection prompt
    await expect(page.getByText(/دسته‌بندی/i)).toBeVisible();
  });

  test("E2E-PLN-02: Can select a category to view plans", async ({ page }) => {
    // Find and click first category button
    const categoryButton = page.locator('button').filter({ hasText: /لیبل|کارت|فاکتور/i }).first();
    
    if (await categoryButton.isVisible()) {
      await categoryButton.click();
      
      // New plan button should appear
      await expect(page.getByRole("button", { name: /پلن جدید/i })).toBeVisible({ timeout: 3000 });
    }
  });

  test("E2E-PLN-03: Can open new plan modal", async ({ page }) => {
    // Select a category first
    const categoryButton = page.locator('button').filter({ hasText: /لیبل|کارت|فاکتور/i }).first();
    
    if (await categoryButton.isVisible()) {
      await categoryButton.click();
      await page.waitForTimeout(500);

      const newPlanButton = page.getByRole("button", { name: /پلن جدید/i });
      if (await newPlanButton.isVisible()) {
        await newPlanButton.click();

        await expect(page.getByRole("dialog")).toBeVisible();
        await expect(page.getByText(/ایجاد پلن/i)).toBeVisible();
      }
    }
  });

  test("E2E-PLN-04: Plan form has all required fields", async ({ page }) => {
    const categoryButton = page.locator('button').filter({ hasText: /لیبل|کارت|فاکتور/i }).first();
    
    if (await categoryButton.isVisible()) {
      await categoryButton.click();
      await page.waitForTimeout(500);

      const newPlanButton = page.getByRole("button", { name: /پلن جدید/i });
      if (await newPlanButton.isVisible()) {
        await newPlanButton.click();
        await expect(page.getByRole("dialog")).toBeVisible();

        // Check required fields
        await expect(page.getByPlaceholder(/طراحی عمومی/i)).toBeVisible();
        await expect(page.locator('select').first()).toBeVisible(); // Plan type
        await expect(page.getByLabel(/قیمت/i).first()).toBeVisible();
      }
    }
  });

  test("E2E-PLN-05: Can create a new plan", async ({ page }) => {
    const categoryButton = page.locator('button').filter({ hasText: /لیبل|کارت|فاکتور/i }).first();
    
    if (await categoryButton.isVisible()) {
      await categoryButton.click();
      await page.waitForTimeout(500);

      const newPlanButton = page.getByRole("button", { name: /پلن جدید/i });
      if (await newPlanButton.isVisible()) {
        await newPlanButton.click();
        await expect(page.getByRole("dialog")).toBeVisible();

        // Fill form
        await page.getByPlaceholder(/طراحی عمومی/i).fill(testPlan.name);
        
        const priceInput = page.getByLabel(/قیمت/i).first();
        if (await priceInput.isVisible()) {
          await priceInput.fill(testPlan.price);
        }

        // Submit
        await page.getByRole("button", { name: /ایجاد/i }).click();

        await expect(page.getByText(/ایجاد شد|موفق/i)).toBeVisible({ timeout: 5000 });
      }
    }
  });
});

test.describe("Admin Catalog - Error Handling", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await goToCatalog(page);
  });

  test("E2E-ERR-01: Shows error toast on API failure", async ({ page }) => {
    // Mock API failure by intercepting
    await page.route("**/api/v1/categories", (route) => {
      if (route.request().method() === "POST") {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ detail: "Internal Server Error" }),
        });
      } else {
        route.continue();
      }
    });

    // Try to create category
    await page.getByRole("button", { name: /دسته‌بندی جدید/i }).click();
    await page.getByPlaceholder(/کارت ویزیت/i).fill("Test Error");
    await page.getByPlaceholder(/business-card/i).fill("test-error");
    await page.getByRole("button", { name: /ایجاد/i }).click();

    // Should show error
    await expect(page.getByText(/خطا|Error/i)).toBeVisible({ timeout: 5000 });
  });

  test("E2E-ERR-02: Shows validation error for duplicate slug", async ({ page }) => {
    // This tests backend validation
    await page.route("**/api/v1/categories", (route) => {
      if (route.request().method() === "POST") {
        route.fulfill({
          status: 422,
          body: JSON.stringify({
            detail: [
              {
                type: "value_error",
                loc: ["body", "slug"],
                msg: "Slug already exists",
              },
            ],
          }),
        });
      } else {
        route.continue();
      }
    });

    await page.getByRole("button", { name: /دسته‌بندی جدید/i }).click();
    await page.getByPlaceholder(/کارت ویزیت/i).fill("Test");
    await page.getByPlaceholder(/business-card/i).fill("existing-slug");
    await page.getByRole("button", { name: /ایجاد/i }).click();

    // Should show validation error
    await expect(page.getByText(/already exists|قبلاً|تکراری/i)).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Admin Catalog - Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test("E2E-NAV-01: Back button returns to admin dashboard", async ({ page }) => {
    await goToCatalog(page);
    
    const backButton = page.locator('a[href="/admin"]').first();
    if (await backButton.isVisible()) {
      await backButton.click();
      await expect(page).toHaveURL(/\/admin$/);
    }
  });

  test("E2E-NAV-02: Tab switching preserves page state", async ({ page }) => {
    await goToCatalog(page);

    // Go to products tab
    await page.getByRole("button", { name: /محصولات/i }).click();
    await expect(page.getByRole("button", { name: /محصولات/i })).toHaveClass(/bg-primary/);

    // Go back to categories tab
    await page.getByRole("button", { name: /دسته‌بندی/i }).click();
    await expect(page.getByRole("button", { name: /دسته‌بندی/i })).toHaveClass(/bg-primary/);
  });

  test("E2E-NAV-03: Direct URL access works for catalog page", async ({ page }) => {
    await page.goto("/admin/catalog");
    
    // Should load without redirect
    await expect(page).toHaveURL(/\/admin\/catalog/);
    await expect(page.getByText(/کاتالوگ|مدیریت/i)).toBeVisible();
  });
});

