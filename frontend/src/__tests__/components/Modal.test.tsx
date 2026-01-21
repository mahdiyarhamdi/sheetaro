/**
 * Unit tests for Modal component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "../utils/test-utils";
import { Modal } from "@/components/ui/modal";

describe("Modal Component", () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    children: <div>Modal content</div>,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==================== Rendering Tests ====================

  it("COMP-08: opens when isOpen is true", () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("COMP-08: closes when isOpen is false", () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("COMP-09: renders children", () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByText("Modal content")).toBeInTheDocument();
  });

  it("renders with title", () => {
    render(<Modal {...defaultProps} title="تایید حذف" />);
    
    expect(screen.getByText("تایید حذف")).toBeInTheDocument();
  });

  it("renders with description", () => {
    render(
      <Modal
        {...defaultProps}
        title="تایید"
        description="آیا مطمئن هستید؟"
      />
    );
    
    expect(screen.getByText("آیا مطمئن هستید؟")).toBeInTheDocument();
  });

  // ==================== Close Button Tests ====================

  it("renders close button by default", () => {
    render(<Modal {...defaultProps} title="Title" />);
    
    expect(screen.getByRole("button", { name: /بستن/i })).toBeInTheDocument();
  });

  it("hides close button when showCloseButton is false", () => {
    render(
      <Modal {...defaultProps} title="Title" showCloseButton={false} />
    );
    
    expect(screen.queryByRole("button", { name: /بستن/i })).not.toBeInTheDocument();
  });

  it("calls onClose when close button clicked", async () => {
    const onClose = vi.fn();
    const { user } = render(
      <Modal {...defaultProps} onClose={onClose} title="Title" />
    );
    
    await user.click(screen.getByRole("button", { name: /بستن/i }));
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  // ==================== Overlay Click Tests ====================

  it("calls onClose when overlay clicked (default)", async () => {
    const onClose = vi.fn();
    const { user } = render(<Modal {...defaultProps} onClose={onClose} />);
    
    // Click on the backdrop (first div with bg-black/50)
    const backdrop = document.querySelector('[aria-hidden="true"]');
    if (backdrop) {
      await user.click(backdrop);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });

  it("does not call onClose when closeOnOverlayClick is false", async () => {
    const onClose = vi.fn();
    const { user } = render(
      <Modal {...defaultProps} onClose={onClose} closeOnOverlayClick={false} />
    );
    
    const backdrop = document.querySelector('[aria-hidden="true"]');
    if (backdrop) {
      await user.click(backdrop);
      expect(onClose).not.toHaveBeenCalled();
    }
  });

  // ==================== Escape Key Tests ====================

  it("calls onClose when Escape key pressed", async () => {
    const onClose = vi.fn();
    const { user } = render(<Modal {...defaultProps} onClose={onClose} />);
    
    await user.keyboard("{Escape}");
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("does not call onClose when Escape pressed and modal is closed", async () => {
    const onClose = vi.fn();
    const { user } = render(
      <Modal {...defaultProps} onClose={onClose} isOpen={false} />
    );
    
    await user.keyboard("{Escape}");
    
    expect(onClose).not.toHaveBeenCalled();
  });

  // ==================== Size Tests ====================

  it("renders with different sizes", () => {
    const { rerender } = render(<Modal {...defaultProps} size="sm" />);
    expect(screen.getByRole("dialog").querySelector(".max-w-sm")).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="md" />);
    expect(screen.getByRole("dialog").querySelector(".max-w-md")).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="lg" />);
    expect(screen.getByRole("dialog").querySelector(".max-w-lg")).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="xl" />);
    expect(screen.getByRole("dialog").querySelector(".max-w-xl")).toBeInTheDocument();
  });

  // ==================== Body Scroll Prevention Tests ====================

  it("prevents body scroll when open", () => {
    render(<Modal {...defaultProps} />);
    
    expect(document.body.style.overflow).toBe("hidden");
  });

  it("restores body scroll when closed", () => {
    const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
    expect(document.body.style.overflow).toBe("hidden");

    rerender(<Modal {...defaultProps} isOpen={false} />);
    expect(document.body.style.overflow).toBe("");
  });

  // ==================== Accessibility Tests ====================

  it("has role dialog", () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("has aria-modal attribute", () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
  });

  it("has aria-labelledby when title exists", () => {
    render(<Modal {...defaultProps} title="Modal Title" />);
    
    expect(screen.getByRole("dialog")).toHaveAttribute(
      "aria-labelledby",
      "modal-title"
    );
  });

  it("does not have aria-labelledby when no title", () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByRole("dialog")).not.toHaveAttribute("aria-labelledby");
  });

  // ==================== Focus Management Tests ====================

  it("traps focus inside modal", async () => {
    const { user } = render(
      <Modal {...defaultProps} title="Title">
        <button>First Button</button>
        <button>Second Button</button>
      </Modal>
    );
    
    // Tab through elements
    await user.tab();
    await user.tab();
    await user.tab();
    
    // Focus should stay within modal
    const dialog = screen.getByRole("dialog");
    expect(dialog.contains(document.activeElement)).toBe(true);
  });
});

