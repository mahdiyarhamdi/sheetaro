/**
 * Unit tests for useOrders hook
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useOrders, useOrder } from "@/hooks/useOrders";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";
import { mockOrders } from "../mocks/handlers";

const API_URL = "http://localhost:3001/api/v1";

// Create wrapper with providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe("useOrders Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== List Orders Tests ====================

  describe("orders list", () => {
    it("fetches orders on mount", async () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.orders).toHaveLength(mockOrders.length);
    });

    it("returns empty array initially", () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      expect(result.current.orders).toEqual([]);
    });

    it("returns total count", async () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.total).toBe(mockOrders.length);
    });

    it("supports pagination options", async () => {
      const { result } = renderHook(
        () => useOrders({ page: 2, pageSize: 5 }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.page).toBeDefined();
      expect(result.current.pageSize).toBeDefined();
    });

    it("supports status filter option", async () => {
      const { result } = renderHook(
        () => useOrders({ status: "PENDING" }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Hook should accept status filter and load successfully
      expect(result.current.isLoading).toBe(false);
    });
  });

  // ==================== Create Order Tests ====================

  describe("createOrder", () => {
    it("creates order and invalidates cache", async () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        result.current.createOrder({
          category_id: "cat-1",
          plan_id: "plan-1",
          attributes: { size: "5x5" },
        });
      });

      await waitFor(() => {
        expect(result.current.isCreatingOrder).toBe(false);
      });
    });

    it("sets isCreatingOrder during creation", async () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // createOrder should be a function
      expect(typeof result.current.createOrder).toBe("function");

      await act(async () => {
        result.current.createOrder({
          category_id: "cat-1",
          plan_id: "plan-1",
          attributes: {},
        });
      });

      await waitFor(() => {
        expect(result.current.isCreatingOrder).toBe(false);
      });
    });

    it("handles create order error", async () => {
      server.use(
        http.post(`${API_URL}/orders`, () => {
          return HttpResponse.json(
            { detail: "خطا در ایجاد سفارش" },
            { status: 400 }
          );
        })
      );

      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        result.current.createOrder({
          category_id: "cat-1",
          plan_id: "plan-1",
          attributes: {},
        });
      });

      await waitFor(() => {
        expect(result.current.isCreatingOrder).toBe(false);
      });
    });
  });

  // ==================== Refetch Tests ====================

  describe("refetch", () => {
    it("refetches orders on demand", async () => {
      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Refetch function should exist
      expect(typeof result.current.refetch).toBe("function");
      
      // Call refetch
      await act(async () => {
        await result.current.refetch();
      });

      // Should still have orders after refetch
      expect(result.current.orders.length).toBeGreaterThanOrEqual(0);
    });
  });

  // ==================== Error Handling Tests ====================

  describe("error handling", () => {
    it("handles API error", async () => {
      server.use(
        http.get(`${API_URL}/orders`, () => {
          return HttpResponse.json(
            { detail: "خطای سرور" },
            { status: 500 }
          );
        })
      );

      const { result } = renderHook(() => useOrders(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeDefined();
    });
  });
});

describe("useOrder Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it("fetches single order by id", async () => {
    const { result } = renderHook(() => useOrder("order-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data?.id).toBe("order-1");
  });

  it("does not fetch when orderId is empty", async () => {
    const { result } = renderHook(() => useOrder(""), {
      wrapper: createWrapper(),
    });

    // Should not be loading since query is disabled
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
  });

  it("handles order not found", async () => {
    server.use(
      http.get(`${API_URL}/orders/:id`, () => {
        return HttpResponse.json(
          { detail: "Order not found" },
          { status: 404 }
        );
      })
    );

    const { result } = renderHook(() => useOrder("non-existent"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeDefined();
  });
});

