"use client";

import { forwardRef, ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const variants = {
      primary:
        "bg-primary text-white hover:bg-primary-800 focus:ring-primary/30",
      secondary:
        "bg-primary-50 text-primary hover:bg-primary-100 focus:ring-primary/20",
      outline:
        "border border-border bg-transparent text-foreground hover:bg-accent focus:ring-primary/20",
      ghost:
        "bg-transparent text-foreground hover:bg-accent focus:ring-primary/20",
      danger:
        "bg-danger text-white hover:bg-red-600 focus:ring-danger/30",
    };

    const sizes = {
      sm: "h-8 px-3 text-sm gap-1.5",
      md: "h-10 px-4 text-base gap-2",
      lg: "h-12 px-6 text-lg gap-2.5",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium rounded-lg",
          "transition-all duration-200 ease-in-out",
          "focus:outline-none focus:ring-2 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : leftIcon ? (
          <span className="shrink-0">{leftIcon}</span>
        ) : null}
        {children}
        {!isLoading && rightIcon && (
          <span className="shrink-0">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button };

