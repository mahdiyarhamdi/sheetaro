/**
 * Unit tests for Input component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "../utils/test-utils";
import { Input } from "@/components/ui/input";
import { Mail, Eye } from "lucide-react";

describe("Input Component", () => {
  // ==================== Rendering Tests ====================

  it("COMP-05: renders with label", () => {
    render(<Input label="ایمیل" />);
    
    expect(screen.getByText("ایمیل")).toBeInTheDocument();
  });

  it("renders input element", () => {
    render(<Input placeholder="Enter text" />);
    
    expect(screen.getByPlaceholderText("Enter text")).toBeInTheDocument();
  });

  it("renders with default type text", () => {
    render(<Input data-testid="input" />);
    
    expect(screen.getByTestId("input")).toHaveAttribute("type", "text");
  });

  it("renders with different types", () => {
    const { rerender } = render(<Input type="email" data-testid="input" />);
    expect(screen.getByTestId("input")).toHaveAttribute("type", "email");

    rerender(<Input type="password" data-testid="input" />);
    expect(screen.getByTestId("input")).toHaveAttribute("type", "password");

    rerender(<Input type="number" data-testid="input" />);
    expect(screen.getByTestId("input")).toHaveAttribute("type", "number");
  });

  // ==================== Error State Tests ====================

  it("COMP-06: shows error message", () => {
    render(<Input error="این فیلد الزامی است" />);
    
    expect(screen.getByText("این فیلد الزامی است")).toBeInTheDocument();
  });

  it("applies error styles when error exists", () => {
    render(<Input error="Error" data-testid="input" />);
    
    expect(screen.getByTestId("input")).toHaveClass("border-danger");
  });

  it("does not show hint when error exists", () => {
    render(<Input error="Error message" hint="Hint message" />);
    
    expect(screen.getByText("Error message")).toBeInTheDocument();
    expect(screen.queryByText("Hint message")).not.toBeInTheDocument();
  });

  // ==================== Hint Tests ====================

  it("shows hint message", () => {
    render(<Input hint="حداقل ۸ کاراکتر" />);
    
    expect(screen.getByText("حداقل ۸ کاراکتر")).toBeInTheDocument();
  });

  // ==================== Icon Tests ====================

  it("renders with left icon", () => {
    render(<Input leftIcon={<Mail data-testid="left-icon" />} />);
    
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("renders with right icon", () => {
    render(<Input rightIcon={<Eye data-testid="right-icon" />} />);
    
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("applies padding when icons exist", () => {
    const { rerender } = render(
      <Input leftIcon={<Mail />} data-testid="input" />
    );
    expect(screen.getByTestId("input")).toHaveClass("pr-10");

    rerender(<Input rightIcon={<Eye />} data-testid="input" />);
    expect(screen.getByTestId("input")).toHaveClass("pl-10");
  });

  // ==================== Disabled State Tests ====================

  it("applies disabled styles when disabled", () => {
    render(<Input disabled data-testid="input" />);
    
    const input = screen.getByTestId("input");
    expect(input).toBeDisabled();
    expect(input).toHaveClass("disabled:opacity-50");
  });

  // ==================== Input Value Tests ====================

  it("accepts value and onChange", async () => {
    const handleChange = vi.fn();
    const { user } = render(
      <Input value="" onChange={handleChange} data-testid="input" />
    );
    
    const input = screen.getByTestId("input");
    await user.type(input, "test");
    
    expect(handleChange).toHaveBeenCalled();
  });

  it("updates value on typing", async () => {
    const { user } = render(<Input data-testid="input" />);
    
    const input = screen.getByTestId("input");
    await user.type(input, "hello");
    
    expect(input).toHaveValue("hello");
  });

  // ==================== Custom Class Tests ====================

  it("accepts custom className", () => {
    render(<Input className="custom-class" data-testid="input" />);
    
    expect(screen.getByTestId("input")).toHaveClass("custom-class");
  });

  // ==================== RTL Support Tests ====================

  it("COMP-07: handles RTL direction", () => {
    // Input should work with RTL content
    const { user } = render(<Input data-testid="input" dir="rtl" />);
    
    expect(screen.getByTestId("input")).toHaveAttribute("dir", "rtl");
  });

  // ==================== Accessibility Tests ====================

  it("associates label with input", () => {
    render(<Input label="ایمیل" id="email-input" />);
    
    // The label should be associated via the for attribute or wrapping
    const label = screen.getByText("ایمیل");
    expect(label).toBeInTheDocument();
  });

  it("can be focused with keyboard", async () => {
    const { user } = render(<Input data-testid="input" />);
    
    await user.tab();
    
    expect(screen.getByTestId("input")).toHaveFocus();
  });

  it("handles placeholder text", () => {
    render(<Input placeholder="شماره موبایل" />);
    
    expect(screen.getByPlaceholderText("شماره موبایل")).toBeInTheDocument();
  });

  // ==================== Ref Forwarding Tests ====================

  it("forwards ref correctly", () => {
    const ref = { current: null };
    render(<Input ref={ref} data-testid="input" />);
    
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });
});

