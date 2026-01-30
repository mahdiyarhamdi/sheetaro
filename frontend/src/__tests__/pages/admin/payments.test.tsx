/**
 * Page tests for Admin Payments page
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
  usePathname: () => "/admin/payments",
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock next/image
vi.mock("next/image", () => ({
  default: ({ src, alt }: { src: string; alt: string }) => (
    <img src={src} alt={alt} data-testid="payment-receipt" />
  ),
}));

// Mock react-hot-toast
vi.mock("react-hot-toast", () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe("Admin Payments Page", () => {
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

  it("ADMIN-PAY-06: redirects non-admin to home", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: "user-123", full_name: "Regular User", is_admin: false, role: "CUSTOMER" },
      isLoadingUser: false,
      isAdmin: false,
      isAuthenticated: true,
    });

    const AdminPaymentsPage = (await import("@/app/(dashboard)/admin/payments/page")).default;
    
    render(<AdminPaymentsPage />);
    
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/");
    }, { timeout: 3000 });
  });

  // ==================== Rendering Tests ====================

  it("ADMIN-PAY-01: renders page when user is admin", async () => {
    const AdminPaymentsPage = (await import("@/app/(dashboard)/admin/payments/page")).default;
    
    render(<AdminPaymentsPage />);
    
    // Should render the page title
    await waitFor(() => {
      expect(screen.getByText(/پرداخت‌های در انتظار/i)).toBeInTheDocument();
    });
  });

  it("has back button to admin dashboard", async () => {
    const AdminPaymentsPage = (await import("@/app/(dashboard)/admin/payments/page")).default;
    
    render(<AdminPaymentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/بازگشت/i)).toBeInTheDocument();
    });
  });
});
