/**
 * Page tests for Register page
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "../utils/test-utils";
import RegisterPage from "@/app/(auth)/register/page";
import { server } from "../mocks/server";

// Mock useAuth hook
const mockRegister = vi.fn();
const mockUseAuth = vi.fn(() => ({
  register: mockRegister,
  isRegistering: false,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("Register Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      register: mockRegister,
      isRegistering: false,
    });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  // ==================== Rendering Tests ====================

  it("PAGE-05: renders all form fields", () => {
    render(<RegisterPage />);
    
    // Name input
    expect(screen.getByLabelText(/نام و نام خانوادگی/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("مثال: علی محمدی")).toBeInTheDocument();
    
    // Phone input
    expect(screen.getByLabelText(/شماره موبایل/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("09123456789")).toBeInTheDocument();
    
    // Password input
    expect(screen.getByLabelText(/^رمز عبور$/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("حداقل ۶ کاراکتر")).toBeInTheDocument();
    
    // Confirm password input
    expect(screen.getByLabelText(/تکرار رمز عبور/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("رمز عبور را تکرار کنید")).toBeInTheDocument();
    
    // Submit button (exact text to avoid Telegram button)
    expect(screen.getByRole("button", { name: /^ثبت‌نام$/i })).toBeInTheDocument();
  });

  it("renders page title and description", () => {
    render(<RegisterPage />);
    
    expect(screen.getByText("ایجاد حساب کاربری")).toBeInTheDocument();
    expect(screen.getByText(/برای استفاده از خدمات/i)).toBeInTheDocument();
  });

  it("renders login link", () => {
    render(<RegisterPage />);
    
    expect(screen.getByRole("link", { name: /وارد شوید/i })).toBeInTheDocument();
  });

  it("renders telegram register button", () => {
    render(<RegisterPage />);
    
    expect(screen.getByRole("button", { name: /ثبت‌نام با تلگرام/i })).toBeInTheDocument();
  });

  it("renders terms and privacy links", () => {
    render(<RegisterPage />);
    
    // There might be multiple links (page + footer), so we check if at least one exists
    const termsLinks = screen.getAllByRole("link", { name: /قوانین و مقررات/i });
    const privacyLinks = screen.getAllByRole("link", { name: /حریم خصوصی/i });
    
    expect(termsLinks.length).toBeGreaterThan(0);
    expect(privacyLinks.length).toBeGreaterThan(0);
  });

  // ==================== Validation Tests ====================

  it("validates all required fields", async () => {
    const { user } = render(<RegisterPage />);
    
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    await user.click(submitButton);
    
    // Should show all validation errors
    await waitFor(() => {
      expect(screen.getByText(/نام باید حداقل ۲ کاراکتر باشد/i)).toBeInTheDocument();
    });
    
    expect(mockRegister).not.toHaveBeenCalled();
  });

  it("validates phone format", async () => {
    const { user } = render(<RegisterPage />);
    
    const nameInput = screen.getByPlaceholderText("مثال: علی محمدی");
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    
    await user.type(nameInput, "Test User");
    await user.type(phoneInput, "12345");
    await user.type(passwordInput, "password123");
    await user.type(confirmInput, "password123");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/شماره موبایل نامعتبر است/i)).toBeInTheDocument();
    });
  });

  it("validates minimum password length", async () => {
    const { user } = render(<RegisterPage />);
    
    const nameInput = screen.getByPlaceholderText("مثال: علی محمدی");
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    
    await user.type(nameInput, "Test User");
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "12345"); // Too short
    await user.type(confirmInput, "12345");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/رمز عبور باید حداقل ۶ کاراکتر باشد/i)).toBeInTheDocument();
    });
  });

  it("PAGE-06: validates password match", async () => {
    const { user } = render(<RegisterPage />);
    
    const nameInput = screen.getByPlaceholderText("مثال: علی محمدی");
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    
    await user.type(nameInput, "Test User");
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "password123");
    await user.type(confirmInput, "different123");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/رمز عبور و تکرار آن مطابقت ندارند/i)).toBeInTheDocument();
    });
    
    expect(mockRegister).not.toHaveBeenCalled();
  });

  // ==================== Form Submission Tests ====================

  it("calls register with form data on valid submission", async () => {
    const { user } = render(<RegisterPage />);
    
    const nameInput = screen.getByPlaceholderText("مثال: علی محمدی");
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    
    await user.type(nameInput, "Test User");
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "password123");
    await user.type(confirmInput, "password123");
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        full_name: "Test User",
        phone: "09121234567",
        password: "password123",
      });
    });
  });

  // ==================== Loading State Tests ====================

  it("shows loading state when registering", () => {
    mockUseAuth.mockReturnValue({
      register: mockRegister,
      isRegistering: true,
    });
    
    render(<RegisterPage />);
    
    const submitButton = screen.getByRole("button", { name: /^ثبت‌نام$/i });
    expect(submitButton).toBeDisabled();
  });

  // ==================== Password Toggle Tests ====================

  it("toggles password visibility", async () => {
    const { user } = render(<RegisterPage />);
    
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const toggleButtons = screen.getAllByRole("button", { name: "" });
    
    // Initially password type
    expect(passwordInput).toHaveAttribute("type", "password");
    
    // Click first toggle (password field)
    await user.click(toggleButtons[0]);
    expect(passwordInput).toHaveAttribute("type", "text");
  });

  it("toggles confirm password visibility", async () => {
    const { user } = render(<RegisterPage />);
    
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    const toggleButtons = screen.getAllByRole("button", { name: "" });
    
    // Initially password type
    expect(confirmInput).toHaveAttribute("type", "password");
    
    // Click second toggle (confirm password field)
    await user.click(toggleButtons[1]);
    expect(confirmInput).toHaveAttribute("type", "text");
  });

  // ==================== Navigation Tests ====================

  it("has correct login link", () => {
    render(<RegisterPage />);
    
    const loginLink = screen.getByRole("link", { name: /وارد شوید/i });
    expect(loginLink).toHaveAttribute("href", "/login");
  });

  it("has correct terms link", () => {
    render(<RegisterPage />);
    
    const termsLinks = screen.getAllByRole("link", { name: /قوانین و مقررات/i });
    // At least one should have href="/terms"
    expect(termsLinks.some(link => link.getAttribute("href") === "/terms")).toBe(true);
  });

  it("has correct privacy link", () => {
    render(<RegisterPage />);
    
    const privacyLinks = screen.getAllByRole("link", { name: /حریم خصوصی/i });
    // At least one should have href="/privacy"
    expect(privacyLinks.some(link => link.getAttribute("href") === "/privacy")).toBe(true);
  });

  // ==================== Accessibility Tests ====================

  it("inputs are associated with labels", () => {
    render(<RegisterPage />);
    
    expect(screen.getByLabelText(/نام و نام خانوادگی/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/شماره موبایل/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^رمز عبور$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/تکرار رمز عبور/i)).toBeInTheDocument();
  });

  it("form can be submitted with Enter key", async () => {
    const { user } = render(<RegisterPage />);
    
    const nameInput = screen.getByPlaceholderText("مثال: علی محمدی");
    const phoneInput = screen.getByPlaceholderText("09123456789");
    const passwordInput = screen.getByPlaceholderText("حداقل ۶ کاراکتر");
    const confirmInput = screen.getByPlaceholderText("رمز عبور را تکرار کنید");
    
    await user.type(nameInput, "Test User");
    await user.type(phoneInput, "09121234567");
    await user.type(passwordInput, "password123");
    await user.type(confirmInput, "password123{Enter}");
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalled();
    });
  });
});

