import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines class names using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Converts English numbers to Persian
 */
export function toPersianNumber(num: number | string): string {
  const persianDigits = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
  return String(num).replace(/\d/g, (d) => persianDigits[parseInt(d)]);
}

/**
 * Formats a number as Persian currency (Toman)
 */
export function formatPrice(price: number): string {
  return `${toPersianNumber(price.toLocaleString("fa-IR"))} تومان`;
}

/**
 * Formats a date to Persian locale string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("fa-IR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Formats a date with time to Persian locale string
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("fa-IR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Truncates text to a specified length with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

/**
 * Validates Iranian phone number
 */
export function isValidPhoneNumber(phone: string): boolean {
  const cleaned = phone.replace(/\D/g, "");
  return /^09\d{9}$/.test(cleaned) || /^9\d{9}$/.test(cleaned);
}

/**
 * Normalizes Iranian phone number to standard format
 */
export function normalizePhoneNumber(phone: string): string {
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.startsWith("98")) return "0" + cleaned.slice(2);
  if (cleaned.startsWith("9") && cleaned.length === 10) return "0" + cleaned;
  return cleaned;
}

/**
 * Generates a random string for IDs
 */
export function generateId(length: number = 8): string {
  return Math.random()
    .toString(36)
    .substring(2, 2 + length);
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Sleep utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Gets initials from a name
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

/**
 * Order status translations
 * Maps backend OrderStatus enum values to Persian labels
 */
export const orderStatusLabels: Record<string, string> = {
  // Payment statuses
  PENDING_PAYMENT: "در انتظار پرداخت",
  PAYMENT_UPLOADED: "رسید ارسال شده",
  PAYMENT_APPROVED: "پرداخت تأیید شده",
  PAYMENT_REJECTED: "پرداخت رد شده",
  // Order processing statuses
  PENDING: "در انتظار بررسی",
  AWAITING_VALIDATION: "در انتظار اعتبارسنجی",
  NEEDS_ACTION: "نیاز به اقدام",
  DESIGNING: "در حال طراحی",
  READY_FOR_PRINT: "آماده چاپ",
  PRINTING: "در حال چاپ",
  SHIPPED: "ارسال شده",
  DELIVERED: "تحویل شده",
  CANCELLED: "لغو شده",
  // Legacy lowercase mappings for backwards compatibility
  pending_payment: "در انتظار پرداخت",
  payment_uploaded: "رسید ارسال شده",
  payment_approved: "پرداخت تأیید شده",
  payment_rejected: "پرداخت رد شده",
  in_progress: "در حال انجام",
  design_ready: "طراحی آماده",
  completed: "تکمیل شده",
  cancelled: "لغو شده",
};

/**
 * Gets status color class based on status
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    // Payment statuses (uppercase)
    PENDING_PAYMENT: "bg-warning-light text-warning",
    PAYMENT_UPLOADED: "bg-info-light text-info",
    PAYMENT_APPROVED: "bg-success-light text-success",
    PAYMENT_REJECTED: "bg-danger-light text-danger",
    // Order processing statuses (uppercase)
    PENDING: "bg-warning-light text-warning",
    AWAITING_VALIDATION: "bg-info-light text-info",
    NEEDS_ACTION: "bg-warning-light text-warning",
    DESIGNING: "bg-primary-50 text-primary",
    READY_FOR_PRINT: "bg-primary-100 text-primary-800",
    PRINTING: "bg-primary-50 text-primary",
    SHIPPED: "bg-info-light text-info",
    DELIVERED: "bg-success-light text-success",
    CANCELLED: "bg-muted text-muted-foreground",
    // Legacy lowercase mappings
    pending_payment: "bg-warning-light text-warning",
    payment_uploaded: "bg-info-light text-info",
    payment_approved: "bg-success-light text-success",
    payment_rejected: "bg-danger-light text-danger",
    in_progress: "bg-primary-50 text-primary",
    design_ready: "bg-primary-100 text-primary-800",
    completed: "bg-success-light text-success",
    cancelled: "bg-muted text-muted-foreground",
  };
  return colors[status] || "bg-muted text-muted-foreground";
}

