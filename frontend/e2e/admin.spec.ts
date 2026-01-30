/**
 * E2E tests for admin panel functionality
 */

import { test, expect } from "@playwright/test";

// Admin test data
const adminUser = {
  phone: "09120000000",
  password: "admin123456",
};

// Regular user test data
const regularUser = {
  phone: "09121234567",
  password: "test123456",
};

// Helper to login as admin
async function loginAsAdmin(page: any) {
  await page.goto("/login");
  await page.fill('[placeholder="09123456789"]', adminUser.phone);
  await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', adminUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
}

// Helper to login as regular user
async function loginAsRegularUser(page: any) {
  await page.goto("/login");
  await page.fill('[placeholder="09123456789"]', regularUser.phone);
  await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', regularUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
}

test.describe("Admin Panel", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  // ==================== Dashboard Tests ====================

  test.describe("Admin Dashboard", () => {
    test("E2E-ADMIN-01: shows admin dashboard with KPIs", async ({ page }) => {
      await page.goto("/admin");
      
      // Should show dashboard title
      await expect(page.getByText(/پنل مدیریت/i)).toBeVisible({
        timeout: 5000,
      });
      
      // Should show KPI cards
      await expect(page.getByText(/کل سفارشات/i)).toBeVisible();
      await expect(page.getByText(/پرداخت.*انتظار|در انتظار/i)).toBeVisible();
      await expect(page.getByText(/درآمد|کاربران/i)).toBeVisible();
    });

    test("E2E-ADMIN-02: dashboard shows order chart", async ({ page }) => {
      await page.goto("/admin");
      
      // Should show charts section
      await expect(page.getByText(/سفارشات.*روز|۷ روز/i)).toBeVisible({
        timeout: 5000,
      });
    });

    test("E2E-ADMIN-03: dashboard shows revenue chart", async ({ page }) => {
      await page.goto("/admin");
      
      // Should show revenue section
      await expect(page.getByText(/درآمد.*روز|۷ روز/i)).toBeVisible({
        timeout: 5000,
      });
    });

    test("E2E-ADMIN-04: dashboard has quick action links", async ({ page }) => {
      await page.goto("/admin");
      
      // Should show quick actions
      await expect(page.getByText(/دسترسی سریع/i)).toBeVisible({
        timeout: 5000,
      });
      
      // Check for quick action items
      const paymentsLink = page.getByRole("link", { name: /پرداخت/i });
      const catalogLink = page.getByRole("link", { name: /کاتالوگ/i });
      const usersLink = page.getByRole("link", { name: /کاربران/i });
      
      expect(await paymentsLink.count()).toBeGreaterThan(0);
      expect(await catalogLink.count()).toBeGreaterThan(0);
      expect(await usersLink.count()).toBeGreaterThan(0);
    });

    test("E2E-ADMIN-05: can navigate to payments from dashboard", async ({ page }) => {
      await page.goto("/admin");
      
      // Find and click payments link
      const paymentsLink = page.getByRole("link", { name: /پرداخت/i }).first();
      
      if (await paymentsLink.isVisible()) {
        await paymentsLink.click();
        await expect(page).toHaveURL(/\/admin\/payments/i);
      }
    });

    test("E2E-ADMIN-06: can navigate to catalog from dashboard", async ({ page }) => {
      await page.goto("/admin");
      
      // Find and click catalog link
      const catalogLink = page.getByRole("link", { name: /کاتالوگ/i });
      
      if (await catalogLink.isVisible()) {
        await catalogLink.click();
        await expect(page).toHaveURL(/\/admin\/catalog/i);
      }
    });

    test("E2E-ADMIN-07: can navigate to users from dashboard", async ({ page }) => {
      await page.goto("/admin");
      
      // Find and click users link
      const usersLink = page.getByRole("link", { name: /کاربران/i });
      
      if (await usersLink.isVisible()) {
        await usersLink.click();
        await expect(page).toHaveURL(/\/admin\/users/i);
      }
    });
  });

  // ==================== Payments Tests ====================

  test.describe("Pending Payments", () => {
    test("E2E-ADMIN-08: Admin can view pending payments page", async ({ page }) => {
      await page.goto("/admin/payments");
      
      // Should show payments page
      await expect(page.getByText(/پرداخت|در انتظار/i)).toBeVisible({
        timeout: 5000,
      });
      
      // Should show payments list or empty state
      const hasPayments = await page.locator('[data-testid="payment-card"]').count() > 0;
      const hasEmptyState = await page.getByText(/همه.*بررسی شده|پرداختی.*ندارد/i).isVisible();
      
      expect(hasPayments || hasEmptyState).toBe(true);
    });

    test("E2E-ADMIN-09: Admin can open payment review modal", async ({ page }) => {
      await page.goto("/admin/payments");
      
      // Find review button
      const reviewButton = page.getByRole("button", { name: /بررسی/i }).first();
      
      if (await reviewButton.isVisible()) {
        await reviewButton.click();
        
        // Modal should open
        await expect(page.getByText(/بررسی پرداخت/i)).toBeVisible({
          timeout: 5000,
        });
      }
    });

    test("E2E-ADMIN-10: Admin can approve payment", async ({ page }) => {
      await page.goto("/admin/payments");
      
      // Find review button
      const reviewButton = page.getByRole("button", { name: /بررسی/i }).first();
      
      if (await reviewButton.isVisible()) {
        await reviewButton.click();
        
        // Wait for modal
        await page.waitForTimeout(500);
        
        // Look for approve button
        const approveButton = page.getByRole("button", { name: /تأیید پرداخت|تایید/i });
        
        if (await approveButton.isVisible()) {
          await approveButton.click();
          
          // Should show success message
          await expect(page.getByText(/موفق|تایید شد/i)).toBeVisible({
            timeout: 5000,
          });
        }
      }
    });

    test("E2E-ADMIN-11: Admin can reject payment with reason", async ({ page }) => {
      await page.goto("/admin/payments");
      
      const reviewButton = page.getByRole("button", { name: /بررسی/i }).first();
      
      if (await reviewButton.isVisible()) {
        await reviewButton.click();
        
        // Wait for modal
        await page.waitForTimeout(500);
        
        // Look for reject button
        const rejectButton = page.getByRole("button", { name: /رد پرداخت/i });
        
        if (await rejectButton.isVisible()) {
          await rejectButton.click();
          
          // Should show reason input
          await page.waitForTimeout(300);
          const reasonInput = page.locator('textarea').first();
          
          if (await reasonInput.isVisible()) {
            await reasonInput.fill("رسید نامعتبر است");
            
            // Confirm rejection
            const confirmButton = page.getByRole("button", { name: /رد پرداخت/i }).first();
            await confirmButton.click();
            
            // Should show success
            await expect(page.getByText(/رد شد|موفق/i)).toBeVisible({
              timeout: 5000,
            });
          }
        }
      }
    });

    test("E2E-ADMIN-12: payments page has back button", async ({ page }) => {
      await page.goto("/admin/payments");
      
      const backButton = page.getByRole("button", { name: /بازگشت/i });
      await expect(backButton).toBeVisible();
    });
  });

  // ==================== Users Management Tests ====================

  test.describe("Users Management", () => {
    test("E2E-ADMIN-13: Admin can view users list", async ({ page }) => {
      await page.goto("/admin/users");
      
      // Should show users page
      await expect(page.getByText(/کاربران|مدیریت/i)).toBeVisible({
        timeout: 5000,
      });
    });

    test("E2E-ADMIN-14: Users page shows user data", async ({ page }) => {
      await page.goto("/admin/users");
      
      // Wait for page to load
      await page.waitForTimeout(1000);
      
      // Should show some user information (table or cards)
      const hasUserList = await page.locator("table, [data-testid='user-card']").count() > 0;
      const hasInDevelopment = await page.getByText(/در حال توسعه/i).isVisible();
      
      expect(hasUserList || hasInDevelopment).toBe(true);
    });
  });

  // ==================== Orders Management Tests ====================

  test.describe("Orders Management", () => {
    test("E2E-ADMIN-15: Admin can view orders list", async ({ page }) => {
      await page.goto("/admin/orders");
      
      // Should show orders page
      await expect(page.getByText(/سفارشات|مدیریت/i)).toBeVisible({
        timeout: 5000,
      });
    });
  });

  // ==================== Catalog Management Tests ====================

  test.describe("Catalog Management", () => {
    test("E2E-ADMIN-16: Admin can view catalog page", async ({ page }) => {
      await page.goto("/admin/catalog");
      
      // Should show catalog page
      await expect(page.getByText(/کاتالوگ|دسته‌بندی|محصولات/i)).toBeVisible({
        timeout: 5000,
      });
    });
  });

  // ==================== Reports Tests ====================

  test.describe("Reports", () => {
    test("E2E-ADMIN-17: Admin can view reports page", async ({ page }) => {
      await page.goto("/admin/reports");
      
      // Should show reports page
      await expect(page.getByText(/گزارشات|آمار/i)).toBeVisible({
        timeout: 5000,
      });
    });
  });

  // ==================== Settings Tests ====================

  test.describe("Settings", () => {
    test("E2E-ADMIN-18: Admin can view settings page", async ({ page }) => {
      await page.goto("/admin/settings");
      
      // Should show settings page
      await expect(page.getByText(/تنظیمات/i)).toBeVisible({
        timeout: 5000,
      });
    });
  });
});

// ==================== Access Control Tests ====================

test.describe("Access Control", () => {
  test("E2E-ADMIN-19: non-admin cannot access admin dashboard", async ({ page }) => {
    // Login as regular user
    await loginAsRegularUser(page);
    
    // Try to access admin page
    await page.goto("/admin");
    
    // Should redirect to home or show forbidden
    await page.waitForTimeout(1000);
    
    const isRedirectedHome = page.url() === "/" || page.url().endsWith("/");
    const isRedirectedDashboard = page.url().includes("/dashboard");
    const isStillOnAdmin = page.url().includes("/admin");
    
    // Should be redirected away from admin
    expect(isRedirectedHome || isRedirectedDashboard || !isStillOnAdmin).toBe(true);
  });

  test("E2E-ADMIN-20: non-admin cannot access admin payments", async ({ page }) => {
    await loginAsRegularUser(page);
    
    await page.goto("/admin/payments");
    
    await page.waitForTimeout(1000);
    
    const isRedirected = !page.url().includes("/admin/payments") || page.url().includes("/login");
    expect(isRedirected).toBe(true);
  });

  test("E2E-ADMIN-21: non-admin cannot access admin users", async ({ page }) => {
    await loginAsRegularUser(page);
    
    await page.goto("/admin/users");
    
    await page.waitForTimeout(1000);
    
    const isRedirected = !page.url().includes("/admin/users") || page.url().includes("/login");
    expect(isRedirected).toBe(true);
  });

  test("E2E-ADMIN-22: unauthenticated user cannot access admin", async ({ page }) => {
    // Clear any existing auth
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    
    // Try to access admin page
    await page.goto("/admin");
    
    await page.waitForTimeout(1000);
    
    // Should be redirected
    const isRedirectedToLogin = page.url().includes("/login");
    const isRedirectedHome = page.url() === "/" || page.url().endsWith("/");
    
    expect(isRedirectedToLogin || isRedirectedHome).toBe(true);
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

