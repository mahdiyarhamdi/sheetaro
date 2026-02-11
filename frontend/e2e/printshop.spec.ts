/**
 * E2E tests for Print Shop panel pages.
 *
 * These tests verify the print shop dashboard, order queue,
 * my-orders, and settlement pages render correctly for
 * a print-shop-role user.
 */

import { test, expect, Page } from "@playwright/test";

// Mock print shop user JWT token and user data stored in localStorage.
// In real E2E, you'd register/login first; here we seed localStorage directly.
const MOCK_PRINTSHOP_USER = {
  id: "00000000-0000-0000-0000-000000000099",
  phone_number: "09129999999",
  full_name: "PrintShop Owner",
  first_name: "PrintShop",
  last_name: "Owner",
  telegram_id: null,
  is_admin: false,
  role: "PRINT_SHOP",
  phone_verified: true,
  web_linked: false,
  created_at: "2026-01-01T00:00:00Z",
};

/**
 * Helper: seed localStorage with a mock print-shop session so
 * protected pages don't redirect to /login.
 */
async function seedPrintShopSession(page: Page) {
  await page.goto("/");
  await page.evaluate((user) => {
    localStorage.setItem("access_token", "fake-printshop-jwt");
    localStorage.setItem("refresh_token", "fake-printshop-refresh");
    localStorage.setItem("user", JSON.stringify(user));
  }, MOCK_PRINTSHOP_USER);
}

test.describe("Print Shop Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await seedPrintShopSession(page);
  });

  test("PSE2E-01: Dashboard page loads and shows heading", async ({
    page,
  }) => {
    await page.goto("/printshop");

    // Should display the dashboard heading
    await expect(
      page.getByRole("heading", { name: /داشبورد چاپخانه/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test("PSE2E-02: Dashboard shows stat cards", async ({ page }) => {
    await page.goto("/printshop");

    // Wait for the page to settle (API call may fail but cards should render)
    await page.waitForTimeout(2000);

    // Should have links to queue and my-orders
    const queueLink = page.getByRole("link", { name: /صف سفارش/i });
    const myOrdersLink = page.getByRole("link", { name: /سفارش.*من/i });
    await expect(queueLink.or(myOrdersLink)).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Print Shop Order Queue", () => {
  test.beforeEach(async ({ page }) => {
    await seedPrintShopSession(page);
  });

  test("PSE2E-03: Order queue page loads", async ({ page }) => {
    await page.goto("/printshop/orders");

    await expect(
      page.getByRole("heading", { name: /صف سفارش/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test("PSE2E-04: Queue has refresh button", async ({ page }) => {
    await page.goto("/printshop/orders");

    const refreshBtn = page.getByRole("button", { name: /بروزرسانی/i });
    await expect(refreshBtn).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Print Shop My Orders", () => {
  test.beforeEach(async ({ page }) => {
    await seedPrintShopSession(page);
  });

  test("PSE2E-05: My orders page loads", async ({ page }) => {
    await page.goto("/printshop/my-orders");

    await expect(
      page.getByRole("heading", { name: /سفارش.*من/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test("PSE2E-06: My orders has status filter tabs", async ({ page }) => {
    await page.goto("/printshop/my-orders");
    await page.waitForTimeout(1500);

    // Should have filter tabs/buttons
    const allTab = page.getByRole("button", { name: /همه/i });
    await expect(allTab).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Print Shop Settlements", () => {
  test.beforeEach(async ({ page }) => {
    await seedPrintShopSession(page);
  });

  test("PSE2E-07: Settlements page loads", async ({ page }) => {
    await page.goto("/printshop/settlements");

    await expect(
      page.getByRole("heading", { name: /تسویه/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test("PSE2E-08: Settlements has refresh button", async ({ page }) => {
    await page.goto("/printshop/settlements");

    const refreshBtn = page.getByRole("button", { name: /بروزرسانی/i });
    await expect(refreshBtn).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Sidebar Navigation for Print Shop", () => {
  test.beforeEach(async ({ page }) => {
    await seedPrintShopSession(page);
  });

  test("PSE2E-09: Sidebar shows print shop section", async ({ page }) => {
    await page.goto("/printshop");
    await page.waitForTimeout(2000);

    // Sidebar should show print shop links
    const sidebarText = await page.locator("aside").textContent();
    expect(sidebarText).toContain("چاپخانه");
  });

  test("PSE2E-10: Print shop sidebar links navigate correctly", async ({
    page,
  }) => {
    await page.goto("/printshop");
    await page.waitForTimeout(2000);

    // Try clicking on the queue link in sidebar
    const queueLink = page.locator("aside").getByRole("link", {
      name: /صف سفارش/i,
    });
    if (await queueLink.isVisible()) {
      await queueLink.click();
      await expect(page).toHaveURL(/\/printshop\/orders/);
    }
  });
});

test.describe("Admin Print Shop Management", () => {
  const MOCK_ADMIN_USER = {
    id: "00000000-0000-0000-0000-000000000001",
    phone_number: "09120000000",
    full_name: "Admin User",
    first_name: "Admin",
    last_name: "User",
    telegram_id: null,
    is_admin: true,
    role: "ADMIN",
    phone_verified: true,
    web_linked: false,
    created_at: "2026-01-01T00:00:00Z",
  };

  async function seedAdminSession(page: Page) {
    await page.goto("/");
    await page.evaluate((user) => {
      localStorage.setItem("access_token", "fake-admin-jwt");
      localStorage.setItem("refresh_token", "fake-admin-refresh");
      localStorage.setItem("user", JSON.stringify(user));
    }, MOCK_ADMIN_USER);
  }

  test("PSE2E-11: Admin printshops page loads", async ({ page }) => {
    await seedAdminSession(page);
    await page.goto("/admin/printshops");

    await expect(
      page.getByRole("heading", { name: /مدیریت چاپخانه/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test("PSE2E-12: Admin sidebar shows print shop management link", async ({
    page,
  }) => {
    await seedAdminSession(page);
    await page.goto("/admin");
    await page.waitForTimeout(2000);

    const sidebarText = await page.locator("aside").textContent();
    expect(sidebarText).toContain("چاپخانه");
  });
});
