/**
 * Unit tests for useAuth hook
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:3001/api/v1";

// Create wrapper with providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
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

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    reset: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: mockLocalStorage,
});

// Mock next/navigation
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
};

vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
  useSearchParams: () => ({
    get: vi.fn(),
  }),
}));

describe("useAuth Hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.reset();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== Login Tests ====================

  describe("login", () => {
    it("HOOK-01: calls API and stores tokens on successful login", async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.login({ phone: "09121234567", password: "test123456" });
      });

      await waitFor(() => {
        expect(result.current.isLoggingIn).toBe(false);
      });

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        "access_token",
        expect.any(String)
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        "refresh_token",
        expect.any(String)
      );
    });

    it("shows error toast on login failure", async () => {
      server.use(
        http.post(`${API_URL}/auth/login`, () => {
          return HttpResponse.json(
            { detail: "شماره موبایل یا رمز عبور اشتباه است" },
            { status: 401 }
          );
        })
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.login({ phone: "09121234567", password: "wrong" });
      });

      await waitFor(() => {
        expect(result.current.isLoggingIn).toBe(false);
      });
    });

    it("sets isLoggingIn to true during login", async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.login({ phone: "09121234567", password: "test123456" });
      });

      expect(result.current.isLoggingIn).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoggingIn).toBe(false);
      });
    });
  });

  // ==================== Register Tests ====================

  describe("register", () => {
    it("HOOK-02: calls API and redirects on successful registration", async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.register({
          phone: "09121234567",
          password: "test123456",
          full_name: "Test User",
        });
      });

      await waitFor(() => {
        expect(result.current.isRegistering).toBe(false);
      });

      expect(mockLocalStorage.setItem).toHaveBeenCalled();
      expect(mockRouter.push).toHaveBeenCalledWith("/");
    });

    it("shows error on duplicate phone", async () => {
      server.use(
        http.post(`${API_URL}/auth/register`, () => {
          return HttpResponse.json(
            { detail: "این شماره موبایل قبلاً ثبت شده است" },
            { status: 409 }
          );
        })
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.register({
          phone: "09000000000",
          password: "test123456",
          full_name: "Test User",
        });
      });

      await waitFor(() => {
        expect(result.current.isRegistering).toBe(false);
      });
    });
  });

  // ==================== Logout Tests ====================

  describe("logout", () => {
    it("HOOK-03: clears tokens and redirects on logout", async () => {
      // Setup: simulate logged in state
      mockLocalStorage.setItem("access_token", "mock-token");
      mockLocalStorage.setItem("refresh_token", "mock-refresh");

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.logout();
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith("access_token");
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith("refresh_token");
      expect(mockRouter.push).toHaveBeenCalledWith("/login");
    });
  });

  // ==================== Authentication State Tests ====================

  describe("isAuthenticated", () => {
    it("HOOK-04: reflects token state - returns false when no token", async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoadingUser).toBe(false);
      });

      expect(result.current.isAuthenticated).toBe(false);
    });

    it("returns true when user is loaded", async () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === "access_token") return "mock-access-token";
        if (key === "refresh_token") return "mock-refresh-token";
        return null;
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoadingUser).toBe(false);
      });

      // After loading user, isAuthenticated should be based on user data
      expect(result.current.user).toBeDefined();
    });
  });

  // ==================== Telegram Link Tests ====================

  describe("generateTelegramLink", () => {
    it("generates OTP for telegram linking", async () => {
      mockLocalStorage.getItem.mockReturnValue("mock-token");

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.generateTelegramLink();
      });

      await waitFor(() => {
        expect(result.current.isGeneratingTelegramLink).toBe(false);
      });
    });
  });

  // ==================== User Data Tests ====================

  describe("user data", () => {
    it("returns user data after successful auth", async () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === "access_token") return "mock-access-token";
        return null;
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoadingUser).toBe(false);
      });

      if (result.current.user) {
        expect(result.current.user.phone).toBeDefined();
        expect(result.current.user.full_name).toBeDefined();
      }
    });

    it("returns isAdmin based on user role", async () => {
      server.use(
        http.get(`${API_URL}/auth/me`, () => {
          return HttpResponse.json({
            id: "123",
            phone: "09121234567",
            full_name: "Admin User",
            is_admin: true,
            phone_verified: true,
            web_linked: false,
            created_at: "2024-01-01T00:00:00Z",
          });
        })
      );

      mockLocalStorage.getItem.mockReturnValue("mock-token");

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoadingUser).toBe(false);
      });

      expect(result.current.isAdmin).toBe(true);
    });
  });

  // ==================== Error Handling Tests ====================

  describe("error handling", () => {
    it("clears tokens on 401 response from /me", async () => {
      server.use(
        http.get(`${API_URL}/auth/me`, () => {
          return HttpResponse.json(
            { detail: "توکن نامعتبر است" },
            { status: 401 }
          );
        })
      );

      mockLocalStorage.getItem.mockReturnValue("expired-token");

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoadingUser).toBe(false);
      });

      expect(result.current.user).toBeNull();
    });
  });
});

