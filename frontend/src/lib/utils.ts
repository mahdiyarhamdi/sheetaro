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
 * Formats a number as Persian currency (Toman) with thousand separators.
 * e.g. 60000 -> "۶۰,۰۰۰ تومان"
 */
export function formatPrice(price: number | string | null | undefined): string {
  if (price == null) return "۰ تومان";
  const num = typeof price === "string" ? parseFloat(price) : price;
  if (isNaN(num)) return "۰ تومان";
  const formatted = Math.round(num).toLocaleString("en-US"); // "60,000"
  return `${toPersianNumber(formatted)} تومان`;
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
 * Formats selected_attributes JSONB into human-readable labels.
 * Input: [{attribute_name: "اندازه", value_name: "A4", ...}, ...]
 * Output: ["A4", "گلاسه", "UV"]
 */
export function formatSelectedAttributes(
  attrs?: Array<{ attribute_name?: string; value_name?: string; value?: string }> | null
): string[] {
  if (!attrs || !Array.isArray(attrs)) return [];
  return attrs
    .map((a) => a.value_name || a.value || "")
    .filter(Boolean);
}

/**
 * Returns Persian label for a DesignPlan enum value.
 */
export function getDesignPlanLabel(plan?: string | null): string {
  if (!plan) return "";
  const labels: Record<string, string> = {
    PUBLIC: "قالب آماده",
    SEMI_PRIVATE: "نیمه اختصاصی",
    PRIVATE: "اختصاصی",
    OWN_DESIGN: "طرح مشتری",
  };
  return labels[plan] || plan;
}

/**
 * Returns Persian label + color for a payment status.
 */
export function getPaymentStatusInfo(status?: string | null): { label: string; color: string } {
  if (!status) return { label: "نامشخص", color: "bg-gray-100 text-gray-600" };
  const map: Record<string, { label: string; color: string }> = {
    SUCCESS: { label: "پرداخت شده", color: "bg-green-100 text-green-700" },
    AWAITING_APPROVAL: { label: "در انتظار تایید", color: "bg-yellow-100 text-yellow-700" },
    PENDING: { label: "پرداخت نشده", color: "bg-red-100 text-red-700" },
    FAILED: { label: "ناموفق", color: "bg-red-100 text-red-700" },
  };
  return map[status] || { label: status, color: "bg-gray-100 text-gray-600" };
}

/**
 * Relative time in Persian (e.g. "۱۵ دقیقه پیش", "۲ ساعت پیش", "۳ روز پیش")
 */
export function timeAgo(date: string | Date | null | undefined): string {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  const diff = Math.round((Date.now() - d.getTime()) / 1000);
  if (diff < 60) return "لحظاتی پیش";
  if (diff < 3600) return `${toPersianNumber(Math.round(diff / 60))} دقیقه پیش`;
  if (diff < 86400) return `${toPersianNumber(Math.round(diff / 3600))} ساعت پیش`;
  return `${toPersianNumber(Math.round(diff / 86400))} روز پیش`;
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
  PENDING_DESIGNER: "در صف طراحی",
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

