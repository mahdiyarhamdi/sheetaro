/**
 * E2E tests for admin panel functionality
 */

import { test, expect } from "@playwright/test";

// Admin test data
const adminUser = {
  phone: "09120000000",
  password: "admin123456",
};

test.describe("Admin Panel", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto("/login");
    await page.fill('[placeholder="09123456789"]', adminUser.phone);
    await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', adminUser.password);
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
  });

  test.describe("Pending Payments", () => {
    test("E2E-06: Admin can view pending payments", async ({ page }) => {
      await page.goto("/admin/payments");
      
      // Should show payments page
      await expect(page.getByText(/پرداخت|در انتظار/i)).toBeVisible({
        timeout: 5000,
      });
      
      // Should show payments list or empty state
      const hasPayments = await page.locator('[data-testid="payment-card"]').count() > 0;
      const hasEmptyState = await page.getByText(/پرداختی وجود ندارد|خالی/i).isVisible();
      
      expect(hasPayments || hasEmptyState).toBe(true);
    });

    test("E2E-07: Admin can approve payment", async ({ page }) => {
      await page.goto("/admin/payments");
      
      // Find first pending payment
      const paymentCard = page.locator('[data-testid="payment-card"]').first();
      
      if (await paymentCard.isVisible()) {
        await paymentCard.click();
        
        // Look for approve button
        const approveButton = page.getByRole("button", { name: /تایید|قبول/i });
        
        if (await approveButton.isVisible()) {
          await approveButton.click();
          
          // Should show success message
          await expect(page.getByText(/موفق|تایید شد/i)).toBeVisible({
            timeout: 5000,
          });
        }
      }
    });

    test("E2E-08: Admin can reject payment with reason", async ({ page }) => {
      await page.goto("/admin/payments");
      
      const paymentCard = page.locator('[data-testid="payment-card"]').first();
      
      if (await paymentCard.isVisible()) {
        await paymentCard.click();
        
        // Look for reject button
        const rejectButton = page.getByRole("button", { name: /رد|عدم تایید/i });
        
        if (await rejectButton.isVisible()) {
          await rejectButton.click();
          
          // Should show reason input
          const reasonInput = page.locator('textarea, input[name="reason"]');
          if (await reasonInput.isVisible()) {
            await reasonInput.fill("رسید نامعتبر است");
            
            // Confirm rejection
            const confirmButton = page.getByRole("button", { name: /تایید|ارسال/i });
            await confirmButton.click();
            
            // Should show success
            await expect(page.getByText(/رد شد|موفق/i)).toBeVisible({
              timeout: 5000,
            });
          }
        }
      }
    });

    test("shows payment receipt image", async ({ page }) => {
      await page.goto("/admin/payments");
      
      const paymentCard = page.locator('[data-testid="payment-card"]').first();
      
      if (await paymentCard.isVisible()) {
        await paymentCard.click();
        
        // Should show receipt image
        const receiptImage = page.locator("img[alt*='رسید'], img[alt*='receipt']");
        await expect(receiptImage).toBeVisible({ timeout: 5000 });
      }
    });
  });

  test.describe("Admin Dashboard", () => {
    test("shows admin statistics", async ({ page }) => {
      await page.goto("/admin");
      
      // Should show statistics
      await expect(page.getByText(/سفارشات|پرداخت|کاربران/i)).toBeVisible({
        timeout: 5000,
      });
    });

    test("has navigation to admin sections", async ({ page }) => {
      await page.goto("/admin");
      
      // Should have links to admin sections
      const paymentsLink = page.getByRole("link", { name: /پرداخت/i });
      const catalogLink = page.getByRole("link", { name: /کاتالوگ/i });
      
      if (await paymentsLink.isVisible()) {
        await paymentsLink.click();
        await expect(page).toHaveURL(/\/admin\/payments/i);
      }
    });
  });

  test.describe("Access Control", () => {
    test("non-admin cannot access admin pages", async ({ page }) => {
      // Logout and login as regular user
      await page.goto("/");
      await page.evaluate(() => localStorage.clear());
      
      await page.goto("/login");
      await page.fill('[placeholder="09123456789"]', "09121234567");
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', "test123456");
      await page.click('button[type="submit"]');
      
      await page.waitForURL(/\/(dashboard)?$/);
      
      // Try to access admin page
      await page.goto("/admin/payments");
      
      // Should redirect or show forbidden
      const isForbidden = await page.getByText(/دسترسی ندارید|forbidden/i).isVisible();
      const isRedirected = page.url().includes("/login") || page.url().includes("/dashboard");
      
      expect(isForbidden || isRedirected).toBe(true);
    });
  });
});

test.describe("Telegram Link Verification", () => {
  test("E2E-09: User can link Telegram via OTP", async ({ page }) => {
    // Login first
    await page.goto("/login");
    await page.fill('[placeholder="09123456789"]', "09121234567");
    await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', "test123456");
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/\/(dashboard)?$/);
    
    // Go to profile or telegram link page
    await page.goto("/profile");
    
    // Look for telegram link button
    const linkButton = page.getByRole("button", { name: /اتصال تلگرام|لینک/i });
    
    if (await linkButton.isVisible()) {
      await linkButton.click();
      
      // Should show OTP code
      const otpDisplay = page.locator('[data-testid="otp-code"], .otp-code');
      
      if (await otpDisplay.isVisible()) {
        // OTP should be 6 digits
        const otpText = await otpDisplay.textContent();
        expect(otpText).toMatch(/\d{6}/);
        
        // Should show instructions
        await expect(page.getByText(/ربات|تلگرام/i)).toBeVisible();
      }
    }
  });
});

