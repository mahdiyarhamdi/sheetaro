/**
 * Page tests for Admin Dashboard page
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "../../utils/test-utils";
import { server } from "../../mocks/server";

// Mock useAuth hook
const mockUseAuth = vi.fn(() => ({
  user: { id: "admin-123", full_name: "Admin User", is_admin: true, role: "ADMIN" },
  isLoadingUser: false,
  isAdmin: true,
  isAuthenticated: true,
}));

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => ({
    get: vi.fn(),
  }),
  usePathname: () => "/admin",
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("Admin Dashboard Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { id: "admin-123", full_name: "Admin User", is_admin: true, role: "ADMIN" },
      isLoadingUser: false,
      isAdmin: true,
      isAuthenticated: true,
    });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== Access Control Tests ====================

  it("ADMIN-PAGE-04: redirects non-admin user to home", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: "user-123", full_name: "Regular User", is_admin: false, role: "CUSTOMER" },
      isLoadingUser: false,
      isAdmin: false,
      isAuthenticated: true,
    });

    const AdminDashboardPage = (await import("@/app/(dashboard)/admin/page")).default;
    
    render(<AdminDashboardPage />);
    
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/");
    }, { timeout: 3000 });
  });

  it("does not redirect while loading", async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoadingUser: true,
      isAdmin: false,
      isAuthenticated: false,
    });

    const AdminDashboardPage = (await import("@/app/(dashboard)/admin/page")).default;
    
    render(<AdminDashboardPage />);
    
    // Should not redirect while loading
    await new Promise((resolve) => setTimeout(resolve, 100));
    expect(mockPush).not.toHaveBeenCalled();
  });
});
