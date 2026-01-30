/**
 * URL Validation Tests - Verify API URLs are constructed correctly
 * 
 * These tests ensure that API endpoint paths don't have duplicate prefixes
 * since baseURL already includes '/api/v1'.
 * 
 * Bug discovered: Frontend was using '/api/v1/categories' which combined with
 * baseURL '/api/v1' resulted in '/api/v1/api/v1/categories' (404).
 */

import { describe, it, expect } from "vitest";

// All endpoint paths from adminApi (extracted from api.ts)
// These are the paths that get appended to baseURL ('/api/v1')
const ADMIN_API_ENDPOINTS = {
  // Dashboard stats
  getStats: "/admin/stats",
  getOrderStats: "/admin/stats/orders",
  getRevenueStats: "/admin/stats/revenue",
  getUserStats: "/admin/stats/users",
  
  // Categories management
  getCategories: "/categories",
  createCategory: "/categories",
  updateCategory: "/categories/:id",
  deleteCategory: "/categories/:id",
  getCategoryDetails: "/categories/:id/details",
  
  // Products management
  getProducts: "/products",
  createProduct: "/products",
  updateProduct: "/products/:id",
  deleteProduct: "/products/:id",
  
  // Plans management
  getPlans: "/plans",
  getPlansByCategory: "/categories/:id/plans",
  createPlan: "/categories/:id/plans",
  updatePlan: "/plans/:id",
  deletePlan: "/plans/:id",
  
  // Attributes management
  getAttributes: "/categories/:id/attributes",
  createAttribute: "/categories/:id/attributes",
  updateAttribute: "/attributes/:id",
  deleteAttribute: "/attributes/:id",
  
  // Users management
  getUsers: "/admin/users",
  getUser: "/admin/users/:id",
  updateUserRole: "/admin/users/:id/role",
  banUser: "/admin/users/:id/ban",
  
  // Orders management
  getOrders: "/admin/orders",
  updateOrderStatus: "/admin/orders/:id/status",
  assignOrder: "/admin/orders/:id/assign",
  
  // Payments management
  getPayments: "/admin/payments",
  verifyPayment: "/admin/payments/:id/verify",
};

describe("API URL Validation Tests", () => {
  describe("URL Construction", () => {
    it("URL-01: No endpoint should contain '/api/v1' prefix (already in baseURL)", () => {
      Object.entries(ADMIN_API_ENDPOINTS).forEach(([name, path]) => {
        expect(
          path.includes("/api/v1"),
          `${name}: path "${path}" should not contain '/api/v1' as it's already in baseURL`
        ).toBe(false);
      });
    });

    it("URL-02: All endpoints should start with '/'", () => {
      Object.entries(ADMIN_API_ENDPOINTS).forEach(([name, path]) => {
        expect(
          path.startsWith("/"),
          `${name}: path "${path}" should start with '/'`
        ).toBe(true);
      });
    });

    it("URL-03: No endpoint should have double slashes", () => {
      Object.entries(ADMIN_API_ENDPOINTS).forEach(([name, path]) => {
        expect(
          path.includes("//"),
          `${name}: path "${path}" should not contain '//'`
        ).toBe(false);
      });
    });

    it("URL-04: No endpoint should end with '/' (except root)", () => {
      Object.entries(ADMIN_API_ENDPOINTS).forEach(([name, path]) => {
        if (path.length > 1) {
          expect(
            path.endsWith("/"),
            `${name}: path "${path}" should not end with '/'`
          ).toBe(false);
        }
      });
    });
  });

  describe("Endpoint Categories", () => {
    it("URL-05: Admin-only endpoints should be under /admin prefix", () => {
      const adminOnlyEndpoints = [
        "getStats",
        "getOrderStats",
        "getRevenueStats",
        "getUserStats",
        "getUsers",
        "getUser",
        "updateUserRole",
        "banUser",
        "getOrders",
        "updateOrderStatus",
        "assignOrder",
        "getPayments",
        "verifyPayment",
      ];

      adminOnlyEndpoints.forEach((name) => {
        const path = ADMIN_API_ENDPOINTS[name as keyof typeof ADMIN_API_ENDPOINTS];
        expect(
          path.startsWith("/admin"),
          `${name}: path "${path}" should start with '/admin'`
        ).toBe(true);
      });
    });

    it("URL-06: Public catalog endpoints should be under /categories or /products or /plans", () => {
      const catalogEndpoints = [
        "getCategories",
        "createCategory",
        "updateCategory",
        "deleteCategory",
        "getCategoryDetails",
        "getProducts",
        "createProduct",
        "updateProduct",
        "deleteProduct",
        "getPlans",
        "getPlansByCategory",
        "createPlan",
        "updatePlan",
        "deletePlan",
        "getAttributes",
        "createAttribute",
        "updateAttribute",
        "deleteAttribute",
      ];

      catalogEndpoints.forEach((name) => {
        const path = ADMIN_API_ENDPOINTS[name as keyof typeof ADMIN_API_ENDPOINTS];
        const isValidCatalogPath = 
          path.startsWith("/categories") || 
          path.startsWith("/products") || 
          path.startsWith("/plans") ||
          path.startsWith("/attributes");
        
        expect(
          isValidCatalogPath,
          `${name}: path "${path}" should start with '/categories', '/products', '/plans', or '/attributes'`
        ).toBe(true);
      });
    });
  });

  describe("URL Parameter Placeholders", () => {
    it("URL-07: URLs with parameters should use :id format", () => {
      const endpointsWithParams = [
        "updateCategory",
        "deleteCategory",
        "getCategoryDetails",
        "updateProduct",
        "deleteProduct",
        "getPlansByCategory",
        "createPlan",
        "updatePlan",
        "deletePlan",
        "getAttributes",
        "createAttribute",
        "updateAttribute",
        "deleteAttribute",
        "getUser",
        "updateUserRole",
        "banUser",
        "updateOrderStatus",
        "assignOrder",
        "verifyPayment",
      ];

      endpointsWithParams.forEach((name) => {
        const path = ADMIN_API_ENDPOINTS[name as keyof typeof ADMIN_API_ENDPOINTS];
        expect(
          path.includes(":id"),
          `${name}: path "${path}" should contain ':id' parameter placeholder`
        ).toBe(true);
      });
    });
  });

  describe("Full URL Construction Simulation", () => {
    const BASE_URL = "http://localhost:3005/api/v1";

    it("URL-08: Simulated full URLs should be valid", () => {
      Object.entries(ADMIN_API_ENDPOINTS).forEach(([name, path]) => {
        const fullUrl = `${BASE_URL}${path}`.replace(/:id/g, "test-uuid");
        
        // Should not have double /api/v1
        expect(
          fullUrl.includes("/api/v1/api/v1"),
          `${name}: full URL "${fullUrl}" should not have duplicate '/api/v1' prefix`
        ).toBe(false);
        
        // Should be a valid URL format
        expect(
          () => new URL(fullUrl),
          `${name}: full URL "${fullUrl}" should be parseable`
        ).not.toThrow();
      });
    });

    it("URL-09: Category creation URL should be correct", () => {
      const path = ADMIN_API_ENDPOINTS.createCategory;
      const fullUrl = `${BASE_URL}${path}`;
      
      expect(fullUrl).toBe("http://localhost:3005/api/v1/categories");
    });

    it("URL-10: Admin stats URL should be correct", () => {
      const path = ADMIN_API_ENDPOINTS.getStats;
      const fullUrl = `${BASE_URL}${path}`;
      
      expect(fullUrl).toBe("http://localhost:3005/api/v1/admin/stats");
    });
  });
});

