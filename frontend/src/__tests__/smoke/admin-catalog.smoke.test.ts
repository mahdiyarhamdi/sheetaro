/**
 * Smoke Tests - Real API calls to running backend
 * 
 * These tests make actual HTTP requests to a running backend server.
 * They are skipped by default and only run when RUN_SMOKE_TESTS=true.
 * 
 * Run with: npm run test:smoke
 * 
 * Prerequisites:
 * - Backend server running on localhost:3005
 * - Admin user exists with credentials in database
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import axios, { AxiosInstance } from "axios";
import { server } from "../mocks/server";

const API_URL = process.env.TEST_API_URL || "http://localhost:3005/api/v1";
const RUN_SMOKE_TESTS = process.env.RUN_SMOKE_TESTS === "true";

// Admin credentials - should match an admin user in the database
const ADMIN_CREDENTIALS = {
  phone: "09120000000",
  password: "admin123456",
};

describe.skipIf(!RUN_SMOKE_TESTS)("Admin Catalog Smoke Tests", () => {
  let api: AxiosInstance;
  let authToken: string;
  let createdCategoryId: string | null = null;

  beforeAll(async () => {
    // IMPORTANT: Close MSW server to allow real HTTP requests
    server.close();
    
    api = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 10000, // 10 second timeout
    });

    // Login as admin
    try {
      const response = await api.post("/auth/login", {
        phone: ADMIN_CREDENTIALS.phone,
        password: ADMIN_CREDENTIALS.password,
      });
      authToken = response.data.access_token;
      api.defaults.headers.common["Authorization"] = `Bearer ${authToken}`;
    } catch (error: any) {
      console.error("Failed to login for smoke tests:", error?.response?.data || error.message);
      throw new Error("Smoke test setup failed: Could not authenticate. Make sure an admin user exists.");
    }
  }, 30000); // 30 second timeout for setup

  afterAll(async () => {
    // Cleanup: Delete created category if it exists
    if (createdCategoryId) {
      try {
        await api.delete(`/categories/${createdCategoryId}`);
      } catch {
        // Ignore cleanup errors
      }
    }
    
    // Restart MSW server for other tests
    server.listen({ onUnhandledRequest: "error" });
  });

  describe("Category CRUD Operations", () => {
    const testCategorySlug = `smoke-test-${Date.now()}`;

    it("SMOKE-01: can create a category with correct schema", async () => {
      const response = await api.post("/categories", {
        slug: testCategorySlug,
        name_fa: "دسته تست",
        description_fa: "برای smoke test ایجاد شده",
        is_active: true,
      });

      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty("id");
      expect(response.data.slug).toBe(testCategorySlug);
      expect(response.data.name_fa).toBe("دسته تست");

      createdCategoryId = response.data.id;
    }, 10000);

    it("SMOKE-02: returns 422 for missing required fields", async () => {
      try {
        await api.post("/categories", {
          name: "Wrong field name", // Should be name_fa
        });
        expect.fail("Should have thrown 422 error");
      } catch (error: any) {
        expect(error.response.status).toBe(422);
        expect(error.response.data.detail).toBeInstanceOf(Array);
        
        // Verify Pydantic error format
        const validationErrors = error.response.data.detail;
        expect(validationErrors.length).toBeGreaterThan(0);
        expect(validationErrors[0]).toHaveProperty("loc");
        expect(validationErrors[0]).toHaveProperty("msg");
      }
    }, 10000);

    it("SMOKE-03: can read created category", async () => {
      if (!createdCategoryId) {
        console.warn("Skipping: No category was created");
        return;
      }

      const response = await api.get(`/categories/${createdCategoryId}/details`);
      
      expect(response.status).toBe(200);
      expect(response.data.id).toBe(createdCategoryId);
      expect(response.data.name_fa).toBe("دسته تست");
    }, 10000);

    it("SMOKE-04: can update category", async () => {
      if (!createdCategoryId) {
        console.warn("Skipping: No category was created");
        return;
      }

      const response = await api.patch(`/categories/${createdCategoryId}`, {
        name_fa: "دسته تست آپدیت شده",
      });

      expect(response.status).toBe(200);
      expect(response.data.name_fa).toBe("دسته تست آپدیت شده");
    }, 10000);

    it("SMOKE-05: can delete category", async () => {
      if (!createdCategoryId) {
        console.warn("Skipping: No category was created");
        return;
      }

      const response = await api.delete(`/categories/${createdCategoryId}`);
      
      expect(response.status).toBe(204);
      createdCategoryId = null; // Mark as deleted so afterAll doesn't try again
    }, 10000);
  });

  describe("Admin Stats Endpoints", () => {
    it("SMOKE-06: can fetch admin dashboard stats", async () => {
      const response = await api.get("/admin/stats");
      
      expect(response.status).toBe(200);
      // Check for actual API response fields
      expect(response.data).toHaveProperty("total_orders");
      expect(response.data).toHaveProperty("total_revenue");
      expect(response.data).toHaveProperty("active_users");
    }, 10000);

    it("SMOKE-07: can fetch order stats", async () => {
      const response = await api.get("/admin/stats/orders");
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("by_status");
    }, 10000);

    it("SMOKE-08: can fetch revenue stats", async () => {
      const response = await api.get("/admin/stats/revenue");
      
      expect(response.status).toBe(200);
      // Check for actual API response fields
      expect(response.data).toHaveProperty("total_revenue");
      expect(response.data).toHaveProperty("by_day");
    }, 10000);
  });

  describe("Users Management", () => {
    it("SMOKE-09: can list users with pagination", async () => {
      const response = await api.get("/admin/users", {
        params: { page: 1, page_size: 10 },
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("items");
      expect(response.data).toHaveProperty("total");
      expect(response.data).toHaveProperty("page");
      expect(response.data).toHaveProperty("page_size");
      expect(Array.isArray(response.data.items)).toBe(true);
    }, 10000);

    it("SMOKE-10: can filter users by role", async () => {
      const response = await api.get("/admin/users", {
        params: { role: "ADMIN" },
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("items");
    }, 10000);
  });

  describe("Error Response Format", () => {
    it("SMOKE-11: 401 for unauthenticated requests", async () => {
      const unauthApi = axios.create({ baseURL: API_URL, timeout: 10000 });
      
      try {
        await unauthApi.get("/admin/stats");
        expect.fail("Should have thrown 401 error");
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }
    }, 10000);

    it("SMOKE-12: 404 for non-existent resources", async () => {
      try {
        await api.get("/categories/00000000-0000-0000-0000-000000000000/details");
        expect.fail("Should have thrown 404 error");
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty("detail");
        expect(typeof error.response.data.detail).toBe("string");
      }
    }, 10000);

    it("SMOKE-13: validation error format is consistent", async () => {
      try {
        await api.post("/categories", {
          // Missing all required fields
        });
        expect.fail("Should have thrown 422 error");
      } catch (error: any) {
        expect(error.response.status).toBe(422);
        
        const detail = error.response.data.detail;
        expect(Array.isArray(detail)).toBe(true);
        
        // Each validation error should have standard Pydantic format
        detail.forEach((err: any) => {
          expect(err).toHaveProperty("type");
          expect(err).toHaveProperty("loc");
          expect(err).toHaveProperty("msg");
        });
      }
    }, 10000);
  });
});

describe.skipIf(!RUN_SMOKE_TESTS)("API URL Construction Smoke Tests", () => {
  let api: AxiosInstance;

  beforeAll(() => {
    // IMPORTANT: Close MSW server to allow real HTTP requests
    server.close();
    
    api = axios.create({
      baseURL: API_URL,
      timeout: 10000,
    });
  });

  afterAll(() => {
    // Restart MSW server for other tests
    server.listen({ onUnhandledRequest: "error" });
  });

  it("SMOKE-14: API base URL does not have duplicate /api/v1", async () => {
    // Verify the configured URL is correct
    expect(API_URL).not.toContain("/api/v1/api/v1");
  });

  it("SMOKE-15: health endpoint is reachable", async () => {
    const healthUrl = API_URL.replace("/api/v1", "/health");
    const response = await axios.get(healthUrl, { timeout: 10000 });
    
    expect(response.status).toBe(200);
  }, 10000);

  it("SMOKE-16: categories endpoint returns proper response", async () => {
    const response = await api.get("/categories");
    
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  }, 10000);
});
