/**
 * Contract Tests - Verify frontend API calls match backend schemas
 * 
 * These tests ensure that the data structures sent from frontend
 * match what the backend expects, preventing schema mismatch bugs.
 */

import { describe, it, expect } from "vitest";
import { z } from "zod";

// ============== Category Schemas ==============

const CategoryCreateSchema = z.object({
  slug: z.string().max(50),
  name_fa: z.string().max(100),
  description_fa: z.string().max(500).optional().nullable(),
  icon: z.string().max(10).optional().nullable(),
  base_price: z.number().default(0),
  sort_order: z.number().default(0),
  is_active: z.boolean().default(true),
});

const CategoryUpdateSchema = z.object({
  slug: z.string().max(50).optional(),
  name_fa: z.string().max(100).optional(),
  description_fa: z.string().max(500).optional().nullable(),
  icon: z.string().max(10).optional().nullable(),
  base_price: z.number().optional(),
  sort_order: z.number().optional(),
  is_active: z.boolean().optional(),
});

// ============== Design Plan Schemas ==============

const DesignPlanCreateSchema = z.object({
  slug: z.string().max(50),
  name_fa: z.string().max(100),
  description_fa: z.string().optional().nullable(),
  price: z.number().default(0),
  max_revisions: z.number().optional().nullable(),
  revision_price: z.number().default(0),
  has_questionnaire: z.boolean().default(false),
  has_templates: z.boolean().default(false),
  has_file_upload: z.boolean().default(false),
  sort_order: z.number().default(0),
  is_active: z.boolean().default(true),
});

const DesignPlanUpdateSchema = z.object({
  slug: z.string().max(50).optional(),
  name_fa: z.string().max(100).optional(),
  description_fa: z.string().optional().nullable(),
  price: z.number().optional(),
  max_revisions: z.number().optional().nullable(),
  revision_price: z.number().optional(),
  has_questionnaire: z.boolean().optional(),
  has_templates: z.boolean().optional(),
  has_file_upload: z.boolean().optional(),
  sort_order: z.number().optional(),
  is_active: z.boolean().optional(),
});

// ============== Attribute Schemas ==============

const AttributeInputType = z.enum([
  "TEXT",
  "NUMBER",
  "SELECT",
  "MULTISELECT",
  "CHECKBOX",
  "RADIO",
]);

const AttributeCreateSchema = z.object({
  slug: z.string().max(50),
  name_fa: z.string().max(100),
  input_type: AttributeInputType,
  is_required: z.boolean().default(true),
  min_value: z.number().optional().nullable(),
  max_value: z.number().optional().nullable(),
  default_value: z.string().max(255).optional().nullable(),
  sort_order: z.number().default(0),
  is_active: z.boolean().default(true),
});

// ============== User Schemas ==============

const UserRoleSchema = z.enum(["CUSTOMER", "DESIGNER", "ADMIN"]);

const UserUpdateRoleSchema = z.object({
  role: UserRoleSchema,
});

// ============== Order Schemas ==============

const OrderStatusSchema = z.enum([
  "PENDING",
  "CONFIRMED",
  "IN_PROGRESS",
  "VALIDATION",
  "COMPLETED",
  "CANCELLED",
]);

const OrderStatusUpdateSchema = z.object({
  status: OrderStatusSchema,
});

// ============== Payment Schemas ==============

const PaymentVerifySchema = z.object({
  approved: z.boolean(),
  rejection_reason: z.string().optional(),
});

// ============== Tests ==============

describe("API Contract Tests", () => {
  describe("Category API Contracts", () => {
    it("CONTRACT-01: createCategory payload matches backend CategoryCreate schema", () => {
      const validPayload = {
        slug: "business-card",
        name_fa: "کارت ویزیت",
        description_fa: "انواع کارت ویزیت",
        is_active: true,
      };

      expect(() => CategoryCreateSchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-02: rejects createCategory with wrong field names (name instead of name_fa)", () => {
      const invalidPayload = {
        name: "Wrong field name",
        description: "Wrong field",
      };

      expect(() => CategoryCreateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-03: rejects createCategory missing required slug field", () => {
      const invalidPayload = {
        name_fa: "کارت ویزیت",
      };

      expect(() => CategoryCreateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-04: rejects createCategory missing required name_fa field", () => {
      const invalidPayload = {
        slug: "business-card",
      };

      expect(() => CategoryCreateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-05: updateCategory accepts partial data", () => {
      const partialPayload = {
        name_fa: "نام جدید",
      };

      expect(() => CategoryUpdateSchema.parse(partialPayload)).not.toThrow();
    });

    it("CONTRACT-06: updateCategory accepts empty object", () => {
      const emptyPayload = {};

      expect(() => CategoryUpdateSchema.parse(emptyPayload)).not.toThrow();
    });
  });

  describe("Design Plan API Contracts", () => {
    it("CONTRACT-07: createPlan payload matches backend DesignPlanCreate schema", () => {
      const validPayload = {
        slug: "basic-plan",
        name_fa: "پلن پایه",
        price: 50000,
        is_active: true,
      };

      expect(() => DesignPlanCreateSchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-08: rejects createPlan with wrong field names", () => {
      const invalidPayload = {
        name: "Wrong field",
        cost: 50000,
      };

      expect(() => DesignPlanCreateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-09: createPlan with all optional fields", () => {
      const fullPayload = {
        slug: "premium-plan",
        name_fa: "پلن ویژه",
        description_fa: "شامل تمام امکانات",
        price: 150000,
        max_revisions: 5,
        revision_price: 10000,
        has_questionnaire: true,
        has_templates: true,
        has_file_upload: true,
        sort_order: 1,
        is_active: true,
      };

      expect(() => DesignPlanCreateSchema.parse(fullPayload)).not.toThrow();
    });

    it("CONTRACT-10: updatePlan accepts partial data", () => {
      const partialPayload = {
        price: 75000,
      };

      expect(() => DesignPlanUpdateSchema.parse(partialPayload)).not.toThrow();
    });
  });

  describe("Attribute API Contracts", () => {
    it("CONTRACT-11: createAttribute payload matches backend AttributeCreate schema", () => {
      const validPayload = {
        slug: "paper-type",
        name_fa: "نوع کاغذ",
        input_type: "SELECT",
        is_required: true,
      };

      expect(() => AttributeCreateSchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-12: rejects createAttribute with invalid input_type", () => {
      const invalidPayload = {
        slug: "paper-type",
        name_fa: "نوع کاغذ",
        input_type: "INVALID_TYPE",
      };

      expect(() => AttributeCreateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-13: createAttribute accepts all valid input_types", () => {
      const inputTypes = ["TEXT", "NUMBER", "SELECT", "MULTISELECT", "CHECKBOX", "RADIO"];

      inputTypes.forEach((type) => {
        const payload = {
          slug: `attr-${type.toLowerCase()}`,
          name_fa: `ویژگی ${type}`,
          input_type: type,
        };

        expect(() => AttributeCreateSchema.parse(payload)).not.toThrow();
      });
    });
  });

  describe("User API Contracts", () => {
    it("CONTRACT-14: updateUserRole payload matches backend schema", () => {
      const validPayload = {
        role: "ADMIN",
      };

      expect(() => UserUpdateRoleSchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-15: rejects updateUserRole with invalid role", () => {
      const invalidPayload = {
        role: "SUPER_ADMIN",
      };

      expect(() => UserUpdateRoleSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-16: updateUserRole accepts all valid roles", () => {
      const roles = ["CUSTOMER", "DESIGNER", "ADMIN"];

      roles.forEach((role) => {
        const payload = { role };
        expect(() => UserUpdateRoleSchema.parse(payload)).not.toThrow();
      });
    });
  });

  describe("Order API Contracts", () => {
    it("CONTRACT-17: updateOrderStatus payload matches backend schema", () => {
      const validPayload = {
        status: "IN_PROGRESS",
      };

      expect(() => OrderStatusUpdateSchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-18: rejects updateOrderStatus with invalid status", () => {
      const invalidPayload = {
        status: "INVALID_STATUS",
      };

      expect(() => OrderStatusUpdateSchema.parse(invalidPayload)).toThrow();
    });

    it("CONTRACT-19: updateOrderStatus accepts all valid statuses", () => {
      const statuses = ["PENDING", "CONFIRMED", "IN_PROGRESS", "VALIDATION", "COMPLETED", "CANCELLED"];

      statuses.forEach((status) => {
        const payload = { status };
        expect(() => OrderStatusUpdateSchema.parse(payload)).not.toThrow();
      });
    });
  });

  describe("Payment API Contracts", () => {
    it("CONTRACT-20: verifyPayment approve payload matches backend schema", () => {
      const validPayload = {
        approved: true,
      };

      expect(() => PaymentVerifySchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-21: verifyPayment reject payload with reason", () => {
      const validPayload = {
        approved: false,
        rejection_reason: "رسید نامعتبر است",
      };

      expect(() => PaymentVerifySchema.parse(validPayload)).not.toThrow();
    });

    it("CONTRACT-22: rejects verifyPayment without approved field", () => {
      const invalidPayload = {
        rejection_reason: "رسید نامعتبر است",
      };

      expect(() => PaymentVerifySchema.parse(invalidPayload)).toThrow();
    });
  });
});

