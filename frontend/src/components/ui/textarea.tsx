"use client";

import { forwardRef, TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, hint, disabled, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-foreground mb-1.5">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            "w-full min-h-[100px] px-3 py-2 rounded-lg border bg-surface text-foreground resize-y",
            "placeholder:text-muted transition-colors duration-200",
            "focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-accent",
            error
              ? "border-danger focus:ring-danger/30 focus:border-danger"
              : "border-border",
            className
          )}
          disabled={disabled}
          {...props}
        />
        {error && <p className="mt-1.5 text-sm text-danger">{error}</p>}
        {hint && !error && (
          <p className="mt-1.5 text-sm text-muted">{hint}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";

export { Textarea };

