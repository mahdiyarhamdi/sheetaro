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
 * - Admin user exists with credentials: admin@test.com / admin123456
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import axios, { AxiosInstance } from "axios";

const API_URL = process.env.TEST_API_URL || "http://localhost:3005/api/v1";
const RUN_SMOKE_TESTS = process.env.RUN_SMOKE_TESTS === "true";

// Test data
const ADMIN_CREDENTIALS = {
  email: "admin@test.com",
  password: "admin123456",
};

describe.skipIf(!RUN_SMOKE_TESTS)("Admin Catalog Smoke Tests", () => {
  let api: AxiosInstance;
  let authToken: string;
  let createdCategoryId: string | null = null;

  beforeAll(async () => {
    api = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Login as admin
    try {
      const response = await api.post("/auth/login", {
        email: ADMIN_CREDENTIALS.email,
        password: ADMIN_CREDENTIALS.password,
      });
      authToken = response.data.access_token;
      api.defaults.headers.common["Authorization"] = `Bearer ${authToken}`;
    } catch (error) {
      console.error("Failed to login for smoke tests:", error);
      throw new Error("Smoke test setup failed: Could not authenticate");
    }
  });

  afterAll(async () => {
    // Cleanup: Delete created category if it exists
    if (createdCategoryId) {
      try {
        await api.delete(`/categories/${createdCategoryId}`);
      } catch {
        // Ignore cleanup errors
      }
    }
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
    });

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
    });

    it("SMOKE-03: can read created category", async () => {
      if (!createdCategoryId) {
        console.warn("Skipping: No category was created");
        return;
      }

      const response = await api.get(`/categories/${createdCategoryId}/details`);
      
      expect(response.status).toBe(200);
      expect(response.data.id).toBe(createdCategoryId);
      expect(response.data.name_fa).toBe("دسته تست");
    });

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
    });

    it("SMOKE-05: can delete category", async () => {
      if (!createdCategoryId) {
        console.warn("Skipping: No category was created");
        return;
      }

      const response = await api.delete(`/categories/${createdCategoryId}`);
      
      expect(response.status).toBe(204);
      createdCategoryId = null; // Mark as deleted so afterAll doesn't try again
    });
  });

  describe("Admin Stats Endpoints", () => {
    it("SMOKE-06: can fetch admin dashboard stats", async () => {
      const response = await api.get("/admin/stats");
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("total_users");
      expect(response.data).toHaveProperty("total_orders");
      expect(response.data).toHaveProperty("total_revenue");
    });

    it("SMOKE-07: can fetch order stats", async () => {
      const response = await api.get("/admin/stats/orders");
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("by_status");
    });

    it("SMOKE-08: can fetch revenue stats", async () => {
      const response = await api.get("/admin/stats/revenue");
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("daily");
    });
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
    });

    it("SMOKE-10: can filter users by role", async () => {
      const response = await api.get("/admin/users", {
        params: { role: "ADMIN" },
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty("items");
    });
  });

  describe("Error Response Format", () => {
    it("SMOKE-11: 401 for unauthenticated requests", async () => {
      const unauthApi = axios.create({ baseURL: API_URL });
      
      try {
        await unauthApi.get("/admin/stats");
        expect.fail("Should have thrown 401 error");
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }
    });

    it("SMOKE-12: 404 for non-existent resources", async () => {
      try {
        await api.get("/categories/00000000-0000-0000-0000-000000000000/details");
        expect.fail("Should have thrown 404 error");
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty("detail");
        expect(typeof error.response.data.detail).toBe("string");
      }
    });

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
    });
  });
});

describe.skipIf(!RUN_SMOKE_TESTS)("API URL Construction Smoke Tests", () => {
  let api: AxiosInstance;

  beforeAll(() => {
    api = axios.create({
      baseURL: API_URL,
    });
  });

  it("SMOKE-14: API base URL does not have duplicate /api/v1", async () => {
    // Verify the configured URL is correct
    expect(API_URL).not.toContain("/api/v1/api/v1");
  });

  it("SMOKE-15: health endpoint is reachable", async () => {
    const healthUrl = API_URL.replace("/api/v1", "/health");
    const response = await axios.get(healthUrl);
    
    expect(response.status).toBe(200);
  });

  it("SMOKE-16: categories endpoint returns proper response", async () => {
    const response = await api.get("/categories");
    
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  });
});

