"use client";

import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export interface LoadingProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  fullScreen?: boolean;
  className?: string;
}

export function Loading({
  size = "md",
  text,
  fullScreen = false,
  className,
}: LoadingProps) {
  const sizes = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const content = (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <Loader2 className={cn("animate-spin text-primary", sizes[size])} />
      {text && <p className="text-sm text-muted">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}

export function LoadingSpinner({ className }: { className?: string }) {
  return (
    <Loader2 className={cn("w-5 h-5 animate-spin text-primary", className)} />
  );
}

export function LoadingDots({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-1", className)}>
      <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
      <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" />
    </div>
  );
}

export function PageLoading() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Loading size="lg" text="در حال بارگذاری..." />
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-4 border border-border animate-pulse">
      <div className="h-4 bg-accent rounded w-3/4 mb-3" />
      <div className="h-3 bg-accent rounded w-1/2 mb-2" />
      <div className="h-3 bg-accent rounded w-full" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-12 bg-accent rounded animate-pulse"
          style={{ animationDelay: `${i * 100}ms` }}
        />
      ))}
    </div>
  );
}

