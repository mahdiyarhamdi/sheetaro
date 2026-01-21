/**
 * E2E tests for authentication flow
 */

import { test, expect } from "@playwright/test";

// Test data
const testUser = {
  phone: "09121234567",
  password: "test123456",
  full_name: "کاربر تست",
};

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.clear();
    });
  });

  test.describe("Registration", () => {
    test("E2E-01: User can register with valid data", async ({ page }) => {
      await page.goto("/register");
      
      // Fill registration form
      await page.fill('[placeholder="مثال: علی محمدی"]', testUser.full_name);
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="حداقل ۶ کاراکتر"]', testUser.password);
      await page.fill('[placeholder="رمز عبور را تکرار کنید"]', testUser.password);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard or home
      await expect(page).toHaveURL(/\/(dashboard)?$/, { timeout: 10000 });
    });

    test("shows error for duplicate phone", async ({ page }) => {
      // First registration
      await page.goto("/register");
      await page.fill('[placeholder="مثال: علی محمدی"]', testUser.full_name);
      await page.fill('[placeholder="09123456789"]', "09000000000"); // Duplicate phone
      await page.fill('[placeholder="حداقل ۶ کاراکتر"]', testUser.password);
      await page.fill('[placeholder="رمز عبور را تکرار کنید"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.getByText(/قبلاً ثبت شده/i)).toBeVisible({ timeout: 5000 });
    });

    test("validates phone format", async ({ page }) => {
      await page.goto("/register");
      
      await page.fill('[placeholder="مثال: علی محمدی"]', testUser.full_name);
      await page.fill('[placeholder="09123456789"]', "12345");
      await page.fill('[placeholder="حداقل ۶ کاراکتر"]', testUser.password);
      await page.fill('[placeholder="رمز عبور را تکرار کنید"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await expect(page.getByText(/شماره موبایل نامعتبر است/i)).toBeVisible();
    });

    test("validates password match", async ({ page }) => {
      await page.goto("/register");
      
      await page.fill('[placeholder="مثال: علی محمدی"]', testUser.full_name);
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="حداقل ۶ کاراکتر"]', testUser.password);
      await page.fill('[placeholder="رمز عبور را تکرار کنید"]', "different");
      await page.click('button[type="submit"]');
      
      await expect(page.getByText(/مطابقت ندارند/i)).toBeVisible();
    });
  });

  test.describe("Login", () => {
    test("E2E-02: User can login after registration", async ({ page }) => {
      await page.goto("/login");
      
      // Fill login form
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', testUser.password);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/\/(dashboard)?$/, { timeout: 10000 });
    });

    test("shows error for wrong password", async ({ page }) => {
      await page.goto("/login");
      
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', "wrong_password");
      await page.click('button[type="submit"]');
      
      await expect(page.getByText(/اشتباه/i)).toBeVisible({ timeout: 5000 });
    });

    test("validates required fields", async ({ page }) => {
      await page.goto("/login");
      
      // Try to submit empty form
      await page.click('button[type="submit"]');
      
      await expect(page.getByText(/شماره موبایل الزامی است/i)).toBeVisible();
    });

    test("toggles password visibility", async ({ page }) => {
      await page.goto("/login");
      
      const passwordInput = page.locator('[placeholder="رمز عبور خود را وارد کنید"]');
      const toggleButton = page.locator('button').filter({ has: page.locator('svg') }).last();
      
      // Initially password type
      await expect(passwordInput).toHaveAttribute("type", "password");
      
      // Click toggle
      await toggleButton.click();
      
      // Should be text type
      await expect(passwordInput).toHaveAttribute("type", "text");
    });
  });

  test.describe("Dashboard Access", () => {
    test("E2E-03: User sees dashboard after login", async ({ page }) => {
      // Login first
      await page.goto("/login");
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', testUser.password);
      await page.click('button[type="submit"]');
      
      // Wait for redirect
      await page.waitForURL(/\/(dashboard)?$/, { timeout: 10000 });
      
      // Dashboard should be visible
      await expect(page.getByRole("heading", { name: /داشبورد|سفارشات/i })).toBeVisible();
    });

    test("redirects unauthenticated users to login", async ({ page }) => {
      await page.goto("/dashboard");
      
      // Should redirect to login
      await expect(page).toHaveURL(/\/login/i, { timeout: 5000 });
    });
  });

  test.describe("Session Persistence", () => {
    test("E2E-10: User session persists on refresh", async ({ page }) => {
      // Login
      await page.goto("/login");
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.waitForURL(/\/(dashboard)?$/);
      
      // Refresh page
      await page.reload();
      
      // Should still be logged in
      await expect(page).not.toHaveURL(/\/login/i);
    });
  });

  test.describe("Logout", () => {
    test("User can logout", async ({ page }) => {
      // Login first
      await page.goto("/login");
      await page.fill('[placeholder="09123456789"]', testUser.phone);
      await page.fill('[placeholder="رمز عبور خود را وارد کنید"]', testUser.password);
      await page.click('button[type="submit"]');
      
      await page.waitForURL(/\/(dashboard)?$/);
      
      // Look for logout button/link
      const logoutButton = page.getByRole("button", { name: /خروج/i });
      if (await logoutButton.isVisible()) {
        await logoutButton.click();
        
        // Should redirect to login
        await expect(page).toHaveURL(/\/login/i, { timeout: 5000 });
      }
    });
  });

  test.describe("Navigation", () => {
    test("login page has register link", async ({ page }) => {
      await page.goto("/login");
      
      const registerLink = page.getByRole("link", { name: /ثبت‌نام/i });
      await expect(registerLink).toBeVisible();
      await registerLink.click();
      
      await expect(page).toHaveURL(/\/register/i);
    });

    test("register page has login link", async ({ page }) => {
      await page.goto("/register");
      
      const loginLink = page.getByRole("link", { name: /وارد شوید/i });
      await expect(loginLink).toBeVisible();
      await loginLink.click();
      
      await expect(page).toHaveURL(/\/login/i);
    });
  });
});

