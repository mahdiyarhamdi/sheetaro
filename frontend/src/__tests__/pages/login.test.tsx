/**
 * Page tests for Login page
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "../utils/test-utils";
import LoginPage from "@/app/(auth)/login/page";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:3001/api/v1";

// Mock useAuth hook
const mockLogin = vi.fn();
const mockUseAuth = vi.fn(() => ({
  login: mockLogin,
  isLoggingIn: false,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("Login Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      login: mockLogin,
      isLoggingIn: false,
    });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== Rendering Tests ====================

  it("PAGE-01: renders form inputs", () => {
    render(<LoginPage />);
    
    // Phone input
    expect(screen.getByLabelText(/شماره موبایل/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("09123456789")).toBeInTheDocument();
    
    // Password input
    expect(screen.getByLabelText(/رمز عبور/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("رمز عبور خود را وارد کنید")).toBeInTheDocument();
    
    // Submit button (exact text to avoid Telegram button)
    expect(screen.getByRole("button", { name: /^ورود$/i })).toBeInTheDocument();
  });

  it("renders page title and description", () => {
    render(<LoginPage />);
    
    expect(screen.getByText("ورود به حساب")).toBeInTheDocument();
    expect(screen.getByText(/خوش آمدید/i)).toBeInTheDocument();
  });

  it("renders register link", () => {
    render(<LoginPage />);
    
    expect(screen.getByRole("link", { name: /ثبت‌نام کنید/i })).toBeInTheDocument();
  });

  it("renders telegram login button", () => {
    render(<LoginPage />);
    
    expect(screen.getByRole("button", { name: /ورود با تلگرام/i })).toBeInTheDocument();
  });

  it("renders forgot password link", () => {
    render(<LoginPage />);
    
    expect(screen.getByRole("link", { name: /فراموشی رمز عبور/i })).toBeInTheDocument();
  });

  // ==================== Validation Tests ====================

  it("PAGE-02: validates phone format", async () => {
    const { user } = render(<LoginPage />);
    
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("رمز عبور خود را وارد کنید");
    const submitButton = screen.getByRole("button", { name: /^ورود$/i });
    
    // Enter invalid phone
    await user.type(phoneInput, "12345");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/شماره موبایل نامعتبر است/i)).toBeInTheDocument();
    });
    
    // login should not be called
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it("shows error for empty phone", async () => {
    const { user } = render(<LoginPage />);
    
    const passwordInput = screen.getByPlaceholderText("رمز عبور خود را وارد کنید");
    const submitButton = screen.getByRole("button", { name: /^ورود$/i });
    
    await user.type(passwordInput, "password123");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/شماره موبایل الزامی است/i)).toBeInTheDocument();
    });
  });

  it("shows error for empty password", async () => {
    const { user } = render(<LoginPage />);
    
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const submitButton = screen.getByRole("button", { name: /^ورود$/i });
    
    await user.type(phoneInput, "09121234567");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/رمز عبور الزامی است/i)).toBeInTheDocument();
    });
  });

  // ==================== Form Submission Tests ====================

  it("calls login with form data on valid submission", async () => {
    const { user } = render(<LoginPage />);
    
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("رمز عبور خود را وارد کنید");
    const submitButton = screen.getByRole("button", { name: /^ورود$/i });
    
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        phone: "09121234567",
        password: "password123",
      });
    });
  });

  // ==================== Loading State Tests ====================

  it("shows loading state when logging in", () => {
    mockUseAuth.mockReturnValue({
      login: mockLogin,
      isLoggingIn: true,
    });
    
    render(<LoginPage />);
    
    const submitButton = screen.getByRole("button", { name: /^ورود$/i });
    expect(submitButton).toBeDisabled();
  });

  // ==================== Password Toggle Tests ====================

  it("toggles password visibility", async () => {
    const { user } = render(<LoginPage />);
    
    const passwordInput = screen.getByPlaceholderText("رمز عبور خود را وارد کنید");
    const toggleButton = screen.getByRole("button", { name: "" }); // Eye icon button
    
    // Initially should be password type
    expect(passwordInput).toHaveAttribute("type", "password");
    
    // Click toggle
    await user.click(toggleButton);
    
    // Should change to text
    expect(passwordInput).toHaveAttribute("type", "text");
    
    // Click again
    await user.click(toggleButton);
    
    // Should change back to password
    expect(passwordInput).toHaveAttribute("type", "password");
  });

  // ==================== Navigation Tests ====================

  it("has correct register link", () => {
    render(<LoginPage />);
    
    const registerLink = screen.getByRole("link", { name: /ثبت‌نام کنید/i });
    expect(registerLink).toHaveAttribute("href", "/register");
  });

  it("has correct forgot password link", () => {
    render(<LoginPage />);
    
    const forgotLink = screen.getByRole("link", { name: /فراموشی رمز عبور/i });
    expect(forgotLink).toHaveAttribute("href", "/forgot-password");
  });

  // ==================== Accessibility Tests ====================

  it("inputs are associated with labels", () => {
    render(<LoginPage />);
    
    expect(screen.getByLabelText(/شماره موبایل/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/رمز عبور/i)).toBeInTheDocument();
  });

  it("form can be submitted with Enter key", async () => {
    const { user } = render(<LoginPage />);
    
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("رمز عبور خود را وارد کنید");
    
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "password123{Enter}");
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
  });
});

