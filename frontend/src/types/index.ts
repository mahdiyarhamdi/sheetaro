// Re-export types from API
export type {
  User,
  Order,
  Category,
  Attribute,
  AttributeOption,
  DesignPlan,
  Template,
  Questionnaire,
  QuestionnaireSection,
  Question,
  Payment,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  CreateOrderRequest,
  OrdersListResponse,
} from "@/lib/api";

// Additional types

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// Order status type (matches backend OrderStatus enum)
export type OrderStatus =
  // Payment statuses
  | "PENDING_PAYMENT"
  | "PAYMENT_UPLOADED"
  | "PAYMENT_APPROVED"
  | "PAYMENT_REJECTED"
  // Order processing statuses
  | "PENDING"
  | "AWAITING_VALIDATION"
  | "NEEDS_ACTION"
  | "DESIGNING"
  | "READY_FOR_PRINT"
  | "PRINTING"
  | "SHIPPED"
  | "DELIVERED"
  | "CANCELLED";

// Payment status type
export type PaymentStatus =
  | "pending"
  | "uploaded"
  | "approved"
  | "rejected";

// Plan type
export type PlanType = "public" | "semi_private" | "private";

// Question input type
export type QuestionInputType =
  | "text"
  | "textarea"
  | "number"
  | "select"
  | "multi_select"
  | "file"
  | "color";

// Attribute input type
export type AttributeInputType =
  | "text"
  | "number"
  | "select"
  | "color"
  | "file";

// Form state
export interface FormState<T> {
  data: T;
  errors: Record<keyof T, string>;
  isSubmitting: boolean;
  isValid: boolean;
}

// Navigation item
export interface NavItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: number;
  children?: NavItem[];
}

// Breadcrumb item
export interface BreadcrumbItem {
  label: string;
  href?: string;
}

// Toast notification
export interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
}

// File upload
export interface UploadedFile {
  id: string;
  url: string;
  name: string;
  size: number;
  type: string;
}

// Select option
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

// Table column
export interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

// Modal props
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

// Button variants
export type ButtonVariant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "danger";

export type ButtonSize = "sm" | "md" | "lg";

// Input variants
export type InputSize = "sm" | "md" | "lg";

// Card variants
export type CardVariant = "default" | "bordered" | "elevated";

