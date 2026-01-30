/**
 * Error Handling Tests - Verify all error formats are handled correctly
 * 
 * These tests ensure that getErrorMessage can handle all types of errors
 * returned from the backend, including Pydantic validation errors.
 * 
 * Bug discovered: Pydantic validation errors were being returned as objects
 * which React tried to render directly, causing runtime errors.
 */

import { describe, it, expect } from "vitest";
import { AxiosError, AxiosHeaders } from "axios";
import { getErrorMessage } from "@/lib/api";

// Helper to create AxiosError with response data
function createAxiosError(detail: unknown, status = 400): AxiosError {
  const error = new AxiosError("Request failed") as AxiosError;
  error.response = {
    data: { detail },
    status,
    statusText: status === 400 ? "Bad Request" : "Unprocessable Entity",
    headers: {},
    config: {
      headers: new AxiosHeaders(),
    },
  };
  return error;
}

describe("getErrorMessage", () => {
  describe("String Detail Responses", () => {
    it("ERR-01: handles simple string detail", () => {
      const error = createAxiosError("این ایمیل قبلاً ثبت شده است");
      expect(getErrorMessage(error)).toBe("این ایمیل قبلاً ثبت شده است");
    });

    it("ERR-02: handles English string detail", () => {
      const error = createAxiosError("User not found");
      expect(getErrorMessage(error)).toBe("User not found");
    });

    it("ERR-03: handles empty string detail", () => {
      const error = createAxiosError("");
      // Empty string is still a string, returns empty string
      expect(getErrorMessage(error)).toBe("");
    });
  });

  describe("Pydantic Validation Errors (Array of Objects)", () => {
    it("ERR-04: handles single Pydantic validation error", () => {
      const error = createAxiosError(
        [{ type: "missing", loc: ["body", "slug"], msg: "Field required", input: {} }],
        422
      );
      const message = getErrorMessage(error);
      expect(message).toContain("slug");
      expect(message).toContain("Field required");
    });

    it("ERR-05: handles multiple Pydantic validation errors", () => {
      const error = createAxiosError(
        [
          { type: "missing", loc: ["body", "slug"], msg: "Field required", input: {} },
          { type: "missing", loc: ["body", "name_fa"], msg: "Field required", input: {} },
        ],
        422
      );
      const message = getErrorMessage(error);
      expect(message).toContain("slug");
      expect(message).toContain("name_fa");
      expect(message).toContain("Field required");
      // Should be joined with Persian comma
      expect(message).toContain("،");
    });

    it("ERR-06: handles Pydantic type validation error", () => {
      const error = createAxiosError(
        [
          {
            type: "int_parsing",
            loc: ["body", "price"],
            msg: "Input should be a valid integer, unable to parse string as an integer",
            input: "not-a-number",
          },
        ],
        422
      );
      const message = getErrorMessage(error);
      expect(message).toContain("price");
      expect(message).toContain("integer");
    });

    it("ERR-07: handles Pydantic string length validation error", () => {
      const error = createAxiosError(
        [
          {
            type: "string_too_long",
            loc: ["body", "name_fa"],
            msg: "String should have at most 100 characters",
            input: "a".repeat(200),
          },
        ],
        422
      );
      const message = getErrorMessage(error);
      expect(message).toContain("name_fa");
      expect(message).toContain("100 characters");
    });

    it("ERR-08: handles nested loc paths", () => {
      const error = createAxiosError(
        [
          {
            type: "missing",
            loc: ["body", "options", 0, "value"],
            msg: "Field required",
            input: {},
          },
        ],
        422
      );
      const message = getErrorMessage(error);
      // Should extract last element from loc
      expect(message).toContain("value");
    });

    it("ERR-09: handles empty array detail gracefully", () => {
      const error = createAxiosError([], 422);
      const message = getErrorMessage(error);
      // Empty array should result in empty string or fallback
      expect(typeof message).toBe("string");
    });
  });

  describe("Object Detail Responses", () => {
    it("ERR-10: handles object detail by stringifying", () => {
      const error = createAxiosError({ code: "INVALID_TOKEN", reason: "Token expired" });
      const message = getErrorMessage(error);
      expect(message).toContain("INVALID_TOKEN");
      expect(message).toContain("Token expired");
    });

    it("ERR-11: handles nested object detail", () => {
      const error = createAxiosError({
        error: {
          type: "validation",
          fields: ["email", "password"],
        },
      });
      const message = getErrorMessage(error);
      expect(message).toContain("validation");
    });
  });

  describe("Network and Connection Errors", () => {
    it("ERR-12: handles AxiosError without response (network error)", () => {
      const error = new AxiosError("Network Error");
      error.code = "ERR_NETWORK";
      expect(getErrorMessage(error)).toBe("Network Error");
    });

    it("ERR-13: handles AxiosError with null response", () => {
      const error = new AxiosError("Request timeout");
      error.response = undefined;
      expect(getErrorMessage(error)).toBe("Request timeout");
    });
  });

  describe("Non-Axios Errors", () => {
    it("ERR-14: handles standard Error object", () => {
      const error = new Error("Something went wrong");
      expect(getErrorMessage(error)).toBe("Something went wrong");
    });

    it("ERR-15: handles unknown error types", () => {
      const error = { foo: "bar" };
      expect(getErrorMessage(error)).toBe("خطای ناشناخته");
    });

    it("ERR-16: handles null error", () => {
      expect(getErrorMessage(null)).toBe("خطای ناشناخته");
    });

    it("ERR-17: handles undefined error", () => {
      expect(getErrorMessage(undefined)).toBe("خطای ناشناخته");
    });

    it("ERR-18: handles string error", () => {
      const error = "Just a string";
      expect(getErrorMessage(error)).toBe("خطای ناشناخته");
    });
  });

  describe("Edge Cases", () => {
    it("ERR-19: handles Pydantic error without msg field", () => {
      const error = createAxiosError(
        [{ type: "missing", loc: ["body", "field"] }],
        422
      );
      const message = getErrorMessage(error);
      // Should convert to string without crashing
      expect(typeof message).toBe("string");
    });

    it("ERR-20: handles Pydantic error without loc field", () => {
      const error = createAxiosError(
        [{ type: "missing", msg: "Field required" }],
        422
      );
      const message = getErrorMessage(error);
      expect(typeof message).toBe("string");
    });

    it("ERR-21: handles mixed array content", () => {
      const error = createAxiosError(
        [
          { type: "missing", loc: ["body", "slug"], msg: "Field required" },
          "plain string error",
          123,
        ],
        422
      );
      const message = getErrorMessage(error);
      expect(message).toContain("slug");
      expect(message).toContain("plain string error");
      expect(message).toContain("123");
    });

    it("ERR-22: result should always be a string (never object)", () => {
      const testCases = [
        createAxiosError("string"),
        createAxiosError([{ type: "error", loc: ["field"], msg: "msg" }]),
        createAxiosError({ key: "value" }),
        createAxiosError(null),
        new Error("test"),
        { random: "object" },
        null,
        undefined,
      ];

      testCases.forEach((testCase) => {
        const result = getErrorMessage(testCase);
        expect(
          typeof result === "string",
          `getErrorMessage should return string, got ${typeof result} for ${JSON.stringify(testCase)}`
        ).toBe(true);
      });
    });

    it("ERR-23: result should be safe to render in React (no objects)", () => {
      const pydanticError = createAxiosError(
        [
          { type: "missing", loc: ["body", "slug"], msg: "Field required", input: {} },
          { type: "missing", loc: ["body", "name_fa"], msg: "Field required", input: {} },
        ],
        422
      );
      
      const message = getErrorMessage(pydanticError);
      
      // Should not be an object
      expect(typeof message).not.toBe("object");
      
      // Should be directly usable in JSX
      expect(typeof message).toBe("string");
      
      // Should not contain [object Object]
      expect(message).not.toContain("[object Object]");
    });
  });
});

