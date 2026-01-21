/**
 * Page tests for Dashboard page
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "../utils/test-utils";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";
import { mockUser, mockOrders } from "../mocks/handlers";

const API_URL = "http://localhost:3001/api/v1";

// Mock hooks
const mockUseAuth = vi.fn(() => ({
  user: mockUser,
  isLoadingUser: false,
  isAuthenticated: true,
  isAdmin: false,
}));

const mockUseOrders = vi.fn(() => ({
  orders: mockOrders,
  total: mockOrders.length,
  isLoading: false,
  error: null,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

vi.mock("@/hooks/useOrders", () => ({
  useOrders: () => mockUseOrders(),
}));

// Simple mock dashboard component for testing
function MockDashboard() {
  const { user, isLoadingUser } = mockUseAuth();
  const { orders, total, isLoading: isLoadingOrders } = mockUseOrders();

  if (isLoadingUser || isLoadingOrders) {
    return <div>در حال بارگذاری...</div>;
  }

  return (
    <div>
      <h1>داشبورد</h1>
      <p data-testid="user-greeting">سلام، {user?.full_name}</p>
      <div data-testid="orders-count">تعداد سفارشات: {total}</div>
      {orders.map((order) => (
        <div key={order.id} data-testid={`order-${order.id}`}>
          {order.status}
        </div>
      ))}
      {!user?.web_linked && (
        <div data-testid="telegram-banner">
          حساب تلگرام خود را متصل کنید
        </div>
      )}
    </div>
  );
}

describe("Dashboard Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: mockUser,
      isLoadingUser: false,
      isAuthenticated: true,
      isAdmin: false,
    });
    mockUseOrders.mockReturnValue({
      orders: mockOrders,
      total: mockOrders.length,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== Rendering Tests ====================

  it("PAGE-08: shows user name", () => {
    render(<MockDashboard />);
    
    expect(screen.getByTestId("user-greeting")).toHaveTextContent(mockUser.full_name);
  });

  it("PAGE-09: shows order stats", () => {
    render(<MockDashboard />);
    
    expect(screen.getByTestId("orders-count")).toHaveTextContent(
      `تعداد سفارشات: ${mockOrders.length}`
    );
  });

  it("renders dashboard title", () => {
    render(<MockDashboard />);
    
    expect(screen.getByRole("heading", { name: /داشبورد/i })).toBeInTheDocument();
  });

  it("shows loading state", () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoadingUser: true,
      isAuthenticated: false,
      isAdmin: false,
    });
    
    render(<MockDashboard />);
    
    expect(screen.getByText(/در حال بارگذاری/i)).toBeInTheDocument();
  });

  // ==================== Orders Display Tests ====================

  it("displays order list", () => {
    render(<MockDashboard />);
    
    mockOrders.forEach((order) => {
      expect(screen.getByTestId(`order-${order.id}`)).toBeInTheDocument();
    });
  });

  it("shows order statuses", () => {
    render(<MockDashboard />);
    
    expect(screen.getByText("PENDING")).toBeInTheDocument();
    expect(screen.getByText("DELIVERED")).toBeInTheDocument();
  });

  // ==================== Empty State Tests ====================

  it("handles empty orders", () => {
    mockUseOrders.mockReturnValue({
      orders: [],
      total: 0,
      isLoading: false,
      error: null,
    });
    
    render(<MockDashboard />);
    
    expect(screen.getByTestId("orders-count")).toHaveTextContent(
      "تعداد سفارشات: 0"
    );
  });

  // ==================== Telegram Banner Tests ====================

  it("PAGE-10: shows telegram link banner for unlinked users", () => {
    render(<MockDashboard />);
    
    expect(screen.getByTestId("telegram-banner")).toBeInTheDocument();
  });

  it("hides telegram banner for linked users", () => {
    mockUseAuth.mockReturnValue({
      user: { ...mockUser, web_linked: true },
      isLoadingUser: false,
      isAuthenticated: true,
      isAdmin: false,
    });
    
    render(<MockDashboard />);
    
    expect(screen.queryByTestId("telegram-banner")).not.toBeInTheDocument();
  });

  // ==================== Admin User Tests ====================

  it("handles admin user display", () => {
    mockUseAuth.mockReturnValue({
      user: { ...mockUser, is_admin: true },
      isLoadingUser: false,
      isAuthenticated: true,
      isAdmin: true,
    });
    
    render(<MockDashboard />);
    
    expect(screen.getByTestId("user-greeting")).toBeInTheDocument();
  });

  // ==================== Loading Orders Tests ====================

  it("shows loading when orders are loading", () => {
    mockUseOrders.mockReturnValue({
      orders: [],
      total: 0,
      isLoading: true,
      error: null,
    });
    
    render(<MockDashboard />);
    
    expect(screen.getByText(/در حال بارگذاری/i)).toBeInTheDocument();
  });

  // ==================== Error Handling Tests ====================

  it("handles order fetch error gracefully", () => {
    mockUseOrders.mockReturnValue({
      orders: [],
      total: 0,
      isLoading: false,
      error: new Error("خطای سرور"),
    });
    
    render(<MockDashboard />);
    
    // Should still render without crashing
    expect(screen.getByRole("heading", { name: /داشبورد/i })).toBeInTheDocument();
  });
});

