"use client";

import { forwardRef, SelectHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, "size"> {
  label?: string;
  error?: string;
  hint?: string;
  options: SelectOption[];
  placeholder?: string;
  size?: "sm" | "md" | "lg";
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      label,
      error,
      hint,
      options,
      placeholder,
      size = "md",
      disabled,
      ...props
    },
    ref
  ) => {
    const sizes = {
      sm: "h-8 px-2 text-sm",
      md: "h-10 px-3 text-base",
      lg: "h-12 px-4 text-lg",
    };

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-foreground mb-1.5">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={cn(
              "w-full appearance-none rounded-lg border bg-surface text-foreground",
              "transition-colors duration-200 cursor-pointer",
              "focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-accent",
              error
                ? "border-danger focus:ring-danger/30 focus:border-danger"
                : "border-border",
              sizes[size],
              "pl-8", // Space for chevron on left (RTL)
              className
            )}
            disabled={disabled}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
        </div>
        {error && <p className="mt-1.5 text-sm text-danger">{error}</p>}
        {hint && !error && (
          <p className="mt-1.5 text-sm text-muted">{hint}</p>
        )}
      </div>
    );
  }
);

Select.displayName = "Select";

export { Select };

