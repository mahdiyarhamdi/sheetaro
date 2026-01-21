import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for E2E tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./e2e",
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["list"],
  ],
  
  // Shared settings for all projects
  use: {
    // Base URL for tests
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    
    // Collect trace when retrying the failed test
    trace: "on-first-retry",
    
    // Take screenshot on failure
    screenshot: "only-on-failure",
    
    // Video recording
    video: "retain-on-failure",
    
    // Locale for the browser
    locale: "fa-IR",
    
    // Timezone
    timezoneId: "Asia/Tehran",
  },
  
  // Configure projects for major browsers
  projects: [
    // Setup project - authenticate user
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
    },
    
    // Desktop Chrome
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
      },
      dependencies: ["setup"],
    },
    
    // Desktop Firefox
    {
      name: "firefox",
      use: {
        ...devices["Desktop Firefox"],
      },
      dependencies: ["setup"],
    },
    
    // Mobile Chrome
    {
      name: "mobile-chrome",
      use: {
        ...devices["Pixel 5"],
      },
      dependencies: ["setup"],
    },
  ],
  
  // Run local dev server before starting tests
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  
  // Test timeout
  timeout: 30 * 1000,
  
  // Assertion timeout
  expect: {
    timeout: 5 * 1000,
  },
});

