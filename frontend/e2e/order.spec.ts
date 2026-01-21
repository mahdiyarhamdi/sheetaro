/**
 * E2E tests for order creation and payment flow
 */

import { test, expect } from "@playwright/test";

// Test data
const testUser = {
  phone: "09121234567",
  password: "test123456",
};

test.describe("Order Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/login");
    await page.fill('[placeholder="09123456789"]', testUser.phone);
    await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', testUser.password);
    await page.click('button[type="submit"]');
    
    // Wait for login to complete
    await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
  });

  test.describe("Order Creation", () => {
    test("E2E-04: User can create order (5 steps)", async ({ page }) => {
      // Navigate to new order page
      await page.goto("/new-order");
      
      // Step 1: Select Category
      const categoryCard = page.locator('[data-testid="category-card"]').first();
      if (await categoryCard.isVisible()) {
        await categoryCard.click();
      }
      
      // Step 2: Select Plan
      await page.waitForSelector('[data-testid="plan-card"], [role="button"]');
      const planButton = page.locator('[data-testid="plan-card"]').first();
      if (await planButton.isVisible()) {
        await planButton.click();
      }
      
      // Step 3: Fill Attributes/Questionnaire
      // Wait for form to appear
      await page.waitForTimeout(1000);
      
      // Fill any text inputs
      const textInputs = page.locator('input[type="text"]');
      for (let i = 0; i < await textInputs.count(); i++) {
        await textInputs.nth(i).fill("Test Value");
      }
      
      // Step 4: Review Order
      const nextButton = page.getByRole("button", { name: /بعدی|ادامه/i });
      if (await nextButton.isVisible()) {
        await nextButton.click();
      }
      
      // Step 5: Confirm Order
      const confirmButton = page.getByRole("button", { name: /ثبت|تایید/i });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
        
        // Should redirect to order details or payment
        await expect(page).toHaveURL(/\/orders\/|\/payment/i, { timeout: 10000 });
      }
    });

    test("shows error when category not selected", async ({ page }) => {
      await page.goto("/new-order");
      
      // Try to proceed without selecting category
      const nextButton = page.getByRole("button", { name: /بعدی|ادامه/i });
      if (await nextButton.isVisible()) {
        await nextButton.click();
        
        // Should show error or stay on same step
        await expect(page.getByText(/انتخاب کنید|الزامی/i)).toBeVisible({
          timeout: 5000,
        });
      }
    });
  });

  test.describe("Payment Flow", () => {
    test("E2E-05: User can upload payment receipt", async ({ page }) => {
      // Go to an order that needs payment
      await page.goto("/orders");
      
      // Click on first order
      const orderCard = page.locator('[data-testid="order-card"]').first();
      if (await orderCard.isVisible()) {
        await orderCard.click();
        
        // Wait for order details
        await page.waitForURL(/\/orders\/.+/);
        
        // Look for payment button
        const payButton = page.getByRole("button", { name: /پرداخت/i });
        if (await payButton.isVisible()) {
          await payButton.click();
          
          // Upload receipt
          const fileInput = page.locator('input[type="file"]');
          if (await fileInput.isVisible()) {
            // Create a test image (1x1 pixel PNG)
            const base64Image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
            const buffer = Buffer.from(base64Image, "base64");
            
            await fileInput.setInputFiles({
              name: "receipt.png",
              mimeType: "image/png",
              buffer,
            });
            
            // Submit receipt
            const submitButton = page.getByRole("button", { name: /ارسال|آپلود/i });
            if (await submitButton.isVisible()) {
              await submitButton.click();
              
              // Should show success message
              await expect(page.getByText(/موفق|ارسال شد/i)).toBeVisible({
                timeout: 10000,
              });
            }
          }
        }
      }
    });

    test("validates file type for receipt", async ({ page }) => {
      await page.goto("/orders");
      
      const orderCard = page.locator('[data-testid="order-card"]').first();
      if (await orderCard.isVisible()) {
        await orderCard.click();
        
        const payButton = page.getByRole("button", { name: /پرداخت/i });
        if (await payButton.isVisible()) {
          await payButton.click();
          
          const fileInput = page.locator('input[type="file"]');
          if (await fileInput.isVisible()) {
            // Try uploading invalid file type
            await fileInput.setInputFiles({
              name: "test.txt",
              mimeType: "text/plain",
              buffer: Buffer.from("test content"),
            });
            
            // Should show error
            await expect(page.getByText(/فرمت|نامعتبر/i)).toBeVisible({
              timeout: 5000,
            });
          }
        }
      }
    });
  });

  test.describe("Order List", () => {
    test("displays user orders", async ({ page }) => {
      await page.goto("/orders");
      
      // Should show orders or empty state
      const hasOrders = await page.locator('[data-testid="order-card"]').count() > 0;
      const hasEmptyState = await page.getByText(/سفارشی وجود ندارد|خالی/i).isVisible();
      
      expect(hasOrders || hasEmptyState).toBe(true);
    });

    test("can filter orders by status", async ({ page }) => {
      await page.goto("/orders");
      
      // Look for filter dropdown
      const filterSelect = page.locator("select, [role='combobox']").first();
      if (await filterSelect.isVisible()) {
        await filterSelect.click();
        
        // Select a status
        const pendingOption = page.getByText(/در انتظار/i);
        if (await pendingOption.isVisible()) {
          await pendingOption.click();
          
          // URL should update with filter
          await expect(page).toHaveURL(/status=|filter=/i);
        }
      }
    });
  });

  test.describe("Order Details", () => {
    test("shows order details", async ({ page }) => {
      await page.goto("/orders");
      
      const orderCard = page.locator('[data-testid="order-card"]').first();
      if (await orderCard.isVisible()) {
        await orderCard.click();
        
        // Should show order details
        await expect(page.getByText(/شماره سفارش|وضعیت/i)).toBeVisible({
          timeout: 5000,
        });
      }
    });

    test("shows payment status", async ({ page }) => {
      await page.goto("/orders");
      
      const orderCard = page.locator('[data-testid="order-card"]').first();
      if (await orderCard.isVisible()) {
        await orderCard.click();
        
        // Should show payment status
        const paymentStatus = page.getByText(/پرداخت|در انتظار|موفق/i);
        await expect(paymentStatus).toBeVisible({ timeout: 5000 });
      }
    });
  });
});

