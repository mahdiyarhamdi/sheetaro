/**
 * Unit tests for Button component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "../utils/test-utils";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

describe("Button Component", () => {
  // ==================== Rendering Tests ====================
  
  it("COMP-01: renders with correct text", () => {
    render(<Button>Click me</Button>);
    
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("renders with default variant and size", () => {
    render(<Button>Default Button</Button>);
    
    const button = screen.getByRole("button");
    expect(button).toHaveClass("bg-primary");
    expect(button).toHaveClass("h-10"); // md size
  });

  it("renders with different variants", () => {
    const { rerender } = render(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-primary-50");

    rerender(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole("button")).toHaveClass("border");

    rerender(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-transparent");

    rerender(<Button variant="danger">Danger</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-danger");
  });

  it("renders with different sizes", () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole("button")).toHaveClass("h-8");

    rerender(<Button size="md">Medium</Button>);
    expect(screen.getByRole("button")).toHaveClass("h-10");

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole("button")).toHaveClass("h-12");
  });

  // ==================== Loading State Tests ====================

  it("COMP-02: shows loading state", () => {
    render(<Button isLoading>Loading</Button>);
    
    const button = screen.getByRole("button");
    // Should have spinner class
    expect(button.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("COMP-04: is disabled when isLoading", () => {
    render(<Button isLoading>Loading</Button>);
    
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("hides icons when loading", () => {
    render(
      <Button isLoading leftIcon={<span data-testid="left-icon">Left</span>}>
        Loading
      </Button>
    );
    
    expect(screen.queryByTestId("left-icon")).not.toBeInTheDocument();
  });

  // ==================== Click Handler Tests ====================

  it("COMP-03: calls onClick when clicked", async () => {
    const handleClick = vi.fn();
    const { user } = render(<Button onClick={handleClick}>Click me</Button>);
    
    await user.click(screen.getByRole("button"));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("does not call onClick when disabled", async () => {
    const handleClick = vi.fn();
    const { user } = render(
      <Button onClick={handleClick} disabled>
        Disabled
      </Button>
    );
    
    await user.click(screen.getByRole("button"));
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("does not call onClick when loading", async () => {
    const handleClick = vi.fn();
    const { user } = render(
      <Button onClick={handleClick} isLoading>
        Loading
      </Button>
    );
    
    await user.click(screen.getByRole("button"));
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  // ==================== Icon Tests ====================

  it("renders with left icon", () => {
    render(
      <Button leftIcon={<ChevronRight data-testid="left-icon" />}>
        With Icon
      </Button>
    );
    
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("renders with right icon", () => {
    render(
      <Button rightIcon={<ChevronLeft data-testid="right-icon" />}>
        With Icon
      </Button>
    );
    
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("renders with both icons", () => {
    render(
      <Button
        leftIcon={<ChevronRight data-testid="left-icon" />}
        rightIcon={<ChevronLeft data-testid="right-icon" />}
      >
        With Both Icons
      </Button>
    );
    
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  // ==================== Disabled State Tests ====================

  it("applies disabled styles when disabled", () => {
    render(<Button disabled>Disabled</Button>);
    
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveClass("disabled:opacity-50");
  });

  // ==================== Custom Class Tests ====================

  it("accepts custom className", () => {
    render(<Button className="custom-class">Custom</Button>);
    
    expect(screen.getByRole("button")).toHaveClass("custom-class");
  });

  // ==================== Accessibility Tests ====================

  it("can be focused with keyboard", async () => {
    const { user } = render(<Button>Focusable</Button>);
    
    await user.tab();
    
    expect(screen.getByRole("button")).toHaveFocus();
  });

  it("can be triggered with Enter key", async () => {
    const handleClick = vi.fn();
    const { user } = render(<Button onClick={handleClick}>Press Enter</Button>);
    
    await user.tab();
    await user.keyboard("{Enter}");
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("can be triggered with Space key", async () => {
    const handleClick = vi.fn();
    const { user } = render(<Button onClick={handleClick}>Press Space</Button>);
    
    await user.tab();
    await user.keyboard(" ");
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

