import axios, { AxiosError, AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005";

/**
 * Creates an axios instance with default configuration
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: `${API_URL}/api/v1`,
    headers: {
      "Content-Type": "application/json",
    },
    withCredentials: true,
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling and token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // Handle 401 and try to refresh token
      if (error.response?.status === 401 && originalRequest) {
        try {
          const refreshToken = localStorage.getItem("refresh_token");
          if (refreshToken) {
            const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token: newRefreshToken } = response.data;
            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", newRefreshToken);

            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return client(originalRequest);
          }
        } catch {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const api = createApiClient();

// ============ Auth API ============

export interface LoginRequest {
  phone: string;
  password: string;
}

export interface RegisterRequest {
  phone: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface User {
  id: string;
  phone_number: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  telegram_id?: number | null;
  is_admin: boolean;
  role?: string | null;
  phone_verified: boolean;
  web_linked: boolean;
  city?: string | null;
  address?: string | null;
  postal_code?: string | null;
  bio?: string | null;
  created_at: string;
}

export const authApi = {
  register: (data: RegisterRequest) =>
    api.post<AuthResponse>("/auth/register", data),

  login: (data: LoginRequest) =>
    api.post<AuthResponse>("/auth/login", data),

  refresh: (refreshToken: string) =>
    api.post<AuthResponse>("/auth/refresh", { refresh_token: refreshToken }),

  // Generate OTP for Telegram linking
  generateTelegramLink: () =>
    api.post<{ otp: string; expires_at: string }>("/auth/telegram-link"),

  // Verify OTP and link Telegram account
  verifyTelegramLink: (otp: string) =>
    api.post<{ success: boolean; telegram_id: number }>("/auth/telegram-verify", { otp }),

  // Get current user
  me: () => api.get<User>("/auth/me"),
};

// ============ Profile API ============

export interface ProfileUpdateData {
  full_name?: string;
  city?: string;
  address?: string;
  postal_code?: string;
  bio?: string;
}

export const profileApi = {
  update: (data: ProfileUpdateData) => api.patch<User>("/users/me", data),
};

// ============ Order Draft API ============

export interface OrderDraft {
  id: string;
  current_step: string;
  data: Record<string, unknown>;
  updated_at: string;
}

export const draftsApi = {
  get: () => api.get<OrderDraft>("/orders/draft"),
  save: (data: { current_step: string; data: Record<string, unknown> }) =>
    api.put<OrderDraft>("/orders/draft", data),
  delete: () => api.delete("/orders/draft"),
};

// ============ Proxy API ============

export interface ProxyStatus {
  enabled: boolean;
  link: string | null;
  protocol: string | null;
  server: string | null;
  connected: boolean;
}

export interface ProxyTestResult {
  success: boolean;
  latency_ms: number;
  message: string;
}

export const proxyApi = {
  getStatus: () => api.get<ProxyStatus>("/admin/proxy"),
  setLink: (link: string) => api.post<ProxyStatus>("/admin/proxy", { link }),
  test: () => api.post<ProxyTestResult>("/admin/proxy/test"),
  remove: () => api.delete("/admin/proxy"),
  restart: () => api.post<{ message: string }>("/admin/proxy/restart"),
};

// ============ Orders API ============

export interface EnrichedAttribute {
  attribute_name: string;
  value_name: string;
  price: number;
}

export interface Order {
  id: string;
  user_id: string;
  category_id: string;
  plan_id: string;
  design_plan_id?: string;
  status: string;
  quantity: number;
  base_price: number;
  attributes_price: number;
  design_price: number;
  validation_price: number;
  fix_price: number;
  print_price: number;
  total_price: number;
  design_plan: string;
  selected_attributes?: unknown[];
  attributes: Record<string, unknown>;
  questionnaire_answers?: Record<string, unknown>;
  design_file_url?: string;
  tracking_code?: string;
  shipping_address?: string;
  customer_notes?: string;
  revision_count?: number;
  max_revisions?: number | null;
  assigned_designer_id?: string;
  accepted_at?: string;
  printed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
  cancelled_at?: string;
  created_at: string;
  updated_at: string;
  // Enriched fields (from CustomerOrderDetailOut)
  category_name?: string;
  category_icon?: string;
  design_plan_label?: string;
  template_name?: string;
  enriched_attributes?: EnrichedAttribute[];
  design_preview_url?: string;
  design_final_url?: string;
  payment_status?: string;
  payment_paid_at?: string;
  // Legacy nested
  category?: Category;
  plan?: DesignPlan;
}

// ============ Design Revision Types ============

export type RevisionStatus = "PENDING_REVIEW" | "APPROVED" | "REJECTED";

export interface DesignRevision {
  id: string;
  order_id: string;
  version: number;
  designer_id: string;
  design_file_url: string;
  customer_feedback?: string;
  status: RevisionStatus;
  created_at: string;
  reviewed_at?: string;
}

export interface DesignRevisionListResponse {
  items: DesignRevision[];
  total: number;
}

// ============ Chat Message Types ============

export interface ChatMessage {
  id: string;
  order_id: string;
  sender_id: string;
  sender_name?: string;
  content: string;
  file_url?: string;
  is_read: boolean;
  created_at: string;
}

export interface ChatMessageListResponse {
  items: ChatMessage[];
  total: number;
  page: number;
  page_size: number;
}

export interface OrdersListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

export interface PlaceholderValueItem {
  placeholder_id: string;
  image_url?: string;
  text_value?: string;
}

export interface SaveOrderDesignRequest {
  template_id: string;
  placeholder_values: PlaceholderValueItem[];
}

export interface ProcessedDesignResponse {
  id: string;
  order_id: string;
  template_id: string;
  logo_url: string;
  preview_url: string;
  final_url: string;
  created_at: string;
}

export const ordersApi = {
  list: (params?: { page?: number; page_size?: number; status?: string }) =>
    api.get<OrdersListResponse>("/orders", { params }),

  get: (id: string) => api.get<Order>(`/orders/${id}`),

  create: (data: CreateOrderRequest, userId: string) =>
    api.post<Order>(`/orders?user_id=${userId}`, data),

  updateStatus: (id: string, status: string) =>
    api.patch<Order>(`/orders/${id}/status`, { status }),

  // Save order design with placeholder values
  saveDesign: (orderId: string, data: SaveOrderDesignRequest) =>
    api.post<ProcessedDesignResponse>(`/orders/${orderId}/design`, data),

  // Delivery confirmation
  confirmDelivery: (orderId: string) =>
    api.post<Order>(`/orders/${orderId}/confirm-delivery`),

  // Reviews
  submitReview: (orderId: string, data: { rating: number; comment?: string; review_type?: string }) =>
    api.post(`/orders/${orderId}/review`, data),
  getReview: (orderId: string, reviewType?: string) =>
    api.get(`/orders/${orderId}/review`, { params: reviewType ? { review_type: reviewType } : undefined }),
  getReviews: (orderId: string) =>
    api.get(`/orders/${orderId}/reviews`),

  // Questionnaire answers
  submitAnswers: (orderId: string, answers: Array<{ question_id: string; answer_text?: string; answer_values?: string[]; answer_file_url?: string }>) =>
    api.post(`/orders/${orderId}/answers`, { answers }),
  getAnswers: (orderId: string) =>
    api.get(`/orders/${orderId}/answers`),

  // Design approval/rejection
  approveDesign: (orderId: string) =>
    api.post<DesignRevision>(`/orders/${orderId}/approve-design`),
  rejectDesign: (orderId: string, data: { feedback: string }) =>
    api.post<DesignRevision>(`/orders/${orderId}/reject-design`, data),
  getRevisions: (orderId: string) =>
    api.get<DesignRevisionListResponse>(`/orders/${orderId}/revisions`),

  // Chat messages
  getMessages: (orderId: string, params?: { page?: number; page_size?: number }) =>
    api.get<ChatMessageListResponse>(`/orders/${orderId}/messages`, { params }),
  sendMessage: (orderId: string, data: { content: string; file_url?: string }) =>
    api.post<ChatMessage>(`/orders/${orderId}/messages`, data),
  markMessagesRead: (orderId: string) =>
    api.patch(`/orders/${orderId}/messages/read`),
};

export type DesignPlanType = "PUBLIC" | "SEMI_PRIVATE" | "PRIVATE" | "OWN_DESIGN";

export interface SelectedAttributeItem {
  attribute_id: string;
  option_id: string;
}

export interface CreateOrderRequest {
  category_id: string;
  design_plan: DesignPlanType;
  plan_id?: string;
  selected_attributes: SelectedAttributeItem[];
  quantity: number;
  validation_requested?: boolean;
  template_id?: string;
  design_file_url?: string;
  shipping_address?: string;
  customer_notes?: string;
}

// ============ Categories API ============

export interface Category {
  id: string;
  name_fa: string;
  slug: string;
  icon?: string;
  base_price: number;
  is_active: boolean;
}

export type AttributePriceType = "FIXED" | "MULTIPLIER";

export interface Attribute {
  id: string;
  category_id: string;
  name_fa: string;
  slug: string;
  input_type: string;
  price_type: AttributePriceType;
  options?: AttributeOption[];
}

export interface AttributeOption {
  id: string;
  label_fa: string;
  value: string;
  price_modifier: number;
}

export const catalogApi = {
  // Categories
  getCategories: () => api.get<Category[]>("/categories"),
  getCategory: (id: string) => api.get<Category>(`/categories/${id}`),

  // Attributes
  getCategoryAttributes: (categoryId: string) =>
    api.get<Attribute[]>(`/categories/${categoryId}/attributes`),

  // Plans
  getCategoryPlans: (categoryId: string) =>
    api.get<DesignPlan[]>(`/categories/${categoryId}/plans`),
};

// ============ Plans API ============

export interface DesignPlan {
  id: string;
  category_id: string;
  name_fa: string;
  slug: string;
  plan_type?: "PUBLIC" | "SEMI_PRIVATE" | "PRIVATE" | "OWN_DESIGN";
  has_templates: boolean;
  has_questionnaire: boolean;
  has_file_upload: boolean;
  price: number;
  is_active: boolean;
  templates?: Template[];
  questionnaire?: Questionnaire;
}

export interface Template {
  id: string;
  plan_id: string;
  name_fa: string;
  description_fa?: string;
  preview_url?: string;
  file_url?: string;
  image_width?: number;
  image_height?: number;
  placeholder_x?: number;
  placeholder_y?: number;
  placeholder_width?: number;
  placeholder_height?: number;
  placeholder_rotation?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  placeholders?: TemplatePlaceholder[];
}

// ============ Dynamic Template Types ============

export type PlaceholderType = "IMAGE" | "TEXT";
export type TextAlign = "left" | "center" | "right";

export interface TemplatePlaceholder {
  id: string;
  template_id: string;
  type: PlaceholderType;
  name: string;
  label_fa: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  is_required: boolean;
  sort_order: number;
  // Text-specific fields
  font_family?: string;
  font_size?: number;
  font_weight?: number;
  font_color?: string;
  text_align?: TextAlign;
  max_length?: number;
  default_value?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlaceholderCreateData {
  type: PlaceholderType;
  name: string;
  label_fa: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  rotation?: number;
  is_required?: boolean;
  sort_order?: number;
  font_family?: string;
  font_size?: number;
  font_weight?: number;
  font_color?: string;
  text_align?: TextAlign;
  max_length?: number;
  default_value?: string;
}

export interface FontVariant {
  weight: number;
  style: string;
  file_url?: string;
  file_woff?: string;
  file_woff2?: string;
}

export interface SystemFont {
  id: string;
  name: string;
  name_fa: string;
  file_url?: string;
  variants: FontVariant[];
  sample_text?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FontCreateData {
  name: string;
  name_fa: string;
  file_url?: string;
  variants?: FontVariant[];
  sample_text?: string;
}

export interface PlaceholderPreviewData {
  placeholder_id: string;
  image_url?: string;
  text_value?: string;
}

export interface TemplatePreviewResponse {
  preview_url: string;
  width: number;
  height: number;
}

export interface TemplateImageUploadResponse {
  filename: string;
  file_url: string;
  preview_url: string;
  file_size: number;
  content_type: string;
  width: number;
  height: number;
}

export interface FontUploadResponse {
  filename: string;
  file_url: string;
  file_size: number;
  content_type: string;
}

export interface Questionnaire {
  plan_id: string;
  sections: QuestionnaireSection[];
}

export interface QuestionnaireSection {
  id: string;
  title_fa: string;
  description_fa?: string;
  sort_order: number;
  is_active: boolean;
  questions: Question[];
}

export interface QuestionOption {
  id: string;
  value: string;
  label_fa: string;
  image_url?: string;
  sort_order: number;
}

export interface Question {
  id: string;
  question_fa: string;
  input_type: string; // "TEXT", "TEXTAREA", "SINGLE_CHOICE", "MULTI_CHOICE", "NUMBER", "IMAGE_UPLOAD", "FILE_UPLOAD", "COLOR_PICKER", "DATE_PICKER", "SCALE"
  is_required: boolean;
  placeholder_fa?: string;
  help_text_fa?: string;
  options: QuestionOption[];
  sort_order: number;
}

export const plansApi = {
  getPlan: (id: string) => api.get<DesignPlan>(`/plans/${id}`),
  getPlanTemplates: (planId: string) =>
    api.get<Template[]>(`/plans/${planId}/templates`),
  getPlanQuestionnaire: (planId: string) =>
    api.get<Questionnaire>(`/plans/${planId}/questionnaire`),
};

// ============ Payments API ============

export interface Payment {
  id: string;
  order_id: string;
  user_id: string;
  type: string;
  amount: number;
  status: string;
  transaction_id?: string;
  authority?: string;
  ref_id?: string;
  card_pan?: string;
  description?: string;
  receipt_image_url?: string;
  rejection_reason?: string;
  approved_by?: string;
  approved_at?: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
  // Extended fields for pending payments
  order_short_id?: string;
  customer_name?: string;
  customer_telegram_id?: number;
  order?: Order;
}

export const paymentsApi = {
  initiate: (orderId: string) =>
    api.post<Payment>("/payments/initiate", { order_id: orderId }),

  uploadReceipt: (paymentId: string, file: File) => {
    const formData = new FormData();
    formData.append("receipt", file);
    return api.post<Payment>(`/payments/${paymentId}/upload-receipt`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // Admin endpoints
  getPending: (params?: { page?: number; page_size?: number }) =>
    api.get<{ items: Payment[]; total: number }>("/payments/pending-approval", { params }),

  approve: (paymentId: string) =>
    api.post<Payment>(`/payments/${paymentId}/approve`),

  reject: (paymentId: string, reason: string) =>
    api.post<Payment>(`/payments/${paymentId}/reject`, { reason }),
};

// ============ Files API ============

export interface PlaceholderImageUploadResponse {
  filename: string;
  file_url: string;
  preview_url: string;
  file_size: number;
  content_type: string;
  width: number;
  height: number;
}

export const filesApi = {
  upload: (file: File, type: string = "design", userId?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("type", type);
    let uid = userId;
    if (!uid && typeof window !== "undefined") {
      try {
        const userStr = localStorage.getItem("user");
        if (userStr) uid = JSON.parse(userStr).id;
      } catch { /* ignore */ }
    }
    if (!uid) throw new Error("User ID is required for file upload");
    return api.post<{ file_url: string; url?: string; filename: string; file_size: number; content_type: string }>(`/files/upload?user_id=${uid}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  
  uploadPlaceholderImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<PlaceholderImageUploadResponse>("/placeholder-images/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ============ Admin API ============

export interface AdminStats {
  total_orders: number;
  pending_payments: number;
  total_revenue: number;
  new_users_today: number;
  active_users: number;
  orders_today: number;
  orders_this_week: number;
  pending_orders: number;
}

export interface OrderStats {
  total: number;
  by_status: Record<string, number>;
  by_day: Array<{ date: string; count: number }>;
}

export interface RevenueStats {
  total_revenue: number;
  this_month: number;
  last_month: number;
  by_day: Array<{ date: string; amount: number }>;
}

// ============ Questionnaire Types ============

export type QuestionInputType = 
  | "TEXT" 
  | "TEXTAREA" 
  | "NUMBER" 
  | "SINGLE_CHOICE" 
  | "MULTI_CHOICE" 
  | "IMAGE_UPLOAD" 
  | "FILE_UPLOAD" 
  | "COLOR_PICKER" 
  | "DATE_PICKER" 
  | "SCALE";

export interface ValidationRules {
  min_length?: number;
  max_length?: number;
  min_value?: number;
  max_value?: number;
  regex?: string;
  allowed_extensions?: string[];
  error_message_fa?: string;
}

export interface QuestionCreateData {
  question_fa: string;
  input_type: QuestionInputType;
  is_required?: boolean;
  placeholder_fa?: string;
  help_text_fa?: string;
  validation_rules?: ValidationRules;
  depends_on_question_id?: string;
  depends_on_values?: string[];
  sort_order?: number;
  is_active?: boolean;
  options?: Array<{
    value: string;
    label_fa: string;
    price_modifier?: number;
    sort_order?: number;
    is_active?: boolean;
  }>;
}

export interface QuestionOptionData {
  value: string;
  label_fa: string;
  price_modifier?: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface SectionData {
  id: string;
  plan_id: string;
  title_fa: string;
  description_fa?: string;
  sort_order: number;
  is_active: boolean;
  questions?: QuestionData[];
}

export interface QuestionData {
  id: string;
  plan_id: string;
  section_id?: string;
  question_fa: string;
  input_type: QuestionInputType;
  is_required: boolean;
  placeholder_fa?: string;
  help_text_fa?: string;
  validation_rules?: ValidationRules;
  depends_on_question_id?: string;
  depends_on_values?: string[];
  sort_order: number;
  is_active: boolean;
  options?: QuestionOptionData[];
}

// ============ Template Types ============

export interface TemplateCreateData {
  name_fa: string;
  description_fa?: string;
  preview_url?: string;
  file_url?: string;
  image_width?: number;
  image_height?: number;
  placeholder_x?: number;
  placeholder_y?: number;
  placeholder_width?: number;
  placeholder_height?: number;
  placeholder_rotation?: number;
  is_active?: boolean;
}

export interface TemplateData {
  id: string;
  plan_id: string;
  name_fa: string;
  description_fa?: string;
  preview_url?: string;
  file_url?: string;
  image_width?: number;
  image_height?: number;
  placeholder_x?: number;
  placeholder_y?: number;
  placeholder_width?: number;
  placeholder_height?: number;
  placeholder_rotation?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============ Validation Types ============

export type ValidationStatus = "PENDING" | "PASSED" | "FAILED";

export interface ValidationRequest {
  id: string;
  user_id: string;
  user_name?: string;
  user_phone?: string;
  category_name?: string;
  plan_name?: string;
  template_name?: string;
  validation_status?: ValidationStatus;
  total_price: number;
  validation_price: number;
  created_at: string;
  design_preview_url?: string;
}

export interface ValidationListResponse {
  items: ValidationRequest[];
  total: number;
  page: number;
  page_size: number;
}

export const adminApi = {
  // Dashboard stats
  getStats: () => api.get<AdminStats>("/admin/stats"),
  getOrderStats: () => api.get<OrderStats>("/admin/stats/orders"),
  getRevenueStats: () => api.get<RevenueStats>("/admin/stats/revenue"),
  getUserStats: () => api.get<{ by_role: Record<string, number>; daily_signups: Array<{ date: string; count: number }> }>("/admin/stats/users"),

  // Categories management (uses existing categories API)
  getCategories: () => api.get<Category[]>("/categories"),
  createCategory: (data: { slug: string; name_fa: string; description_fa?: string; icon?: string; is_active?: boolean }) =>
    api.post<Category>("/categories", data),
  updateCategory: (id: string, data: Partial<Category>) =>
    api.patch<Category>(`/categories/${id}`, data),
  deleteCategory: (id: string) => api.delete(`/categories/${id}`),
  getCategoryDetails: (id: string) => api.get<Category>(`/categories/${id}/details`),

  // Products management
  getProducts: (params?: { type?: string; active_only?: boolean; page?: number; page_size?: number }) =>
    api.get<{ items: any[]; total: number; page: number; page_size: number }>("/products", { params }),
  createProduct: (data: any) => api.post<any>("/products", data),
  updateProduct: (id: string, data: any) => api.patch<any>(`/products/${id}`, data),
  deleteProduct: (id: string) => api.delete(`/products/${id}`),

  // Plans management (uses existing plans API)
  getPlans: (categoryId?: string) => 
    categoryId 
      ? api.get<any[]>(`/categories/${categoryId}/plans`)
      : api.get<any[]>("/plans"),
  createPlan: (categoryId: string, data: any) => api.post<any>(`/categories/${categoryId}/plans`, data),
  updatePlan: (id: string, data: any) => api.patch<any>(`/plans/${id}`, data),
  deletePlan: (id: string) => api.delete(`/plans/${id}`),

  // Attributes management
  getAttributes: (categoryId: string) => api.get<any[]>(`/categories/${categoryId}/attributes`),
  createAttribute: (categoryId: string, data: any) => api.post<any>(`/categories/${categoryId}/attributes`, data),
  updateAttribute: (id: string, data: any) => api.patch<any>(`/attributes/${id}`, data),
  deleteAttribute: (id: string) => api.delete(`/attributes/${id}`),

  // Attribute Options management
  createAttributeOption: (attributeId: string, data: any) => 
    api.post<any>(`/attributes/${attributeId}/options`, data),
  updateAttributeOption: (optionId: string, data: any) => 
    api.patch<any>(`/options/${optionId}`, data),
  deleteAttributeOption: (optionId: string) => 
    api.delete(`/options/${optionId}`),

  // Users management
  getUsers: (params?: { page?: number; page_size?: number; search?: string; role?: string; is_active?: boolean }) =>
    api.get<{ items: User[]; total: number; page: number; page_size: number }>("/admin/users", { params }),
  getUser: (id: string) => api.get<User>(`/admin/users/${id}`),
  updateUserRole: (id: string, role: string) => api.patch<User>(`/admin/users/${id}/role`, { role }),
  banUser: (id: string, is_active: boolean, reason?: string) => 
    api.post<User>(`/admin/users/${id}/ban`, { is_active, reason }),

  // Orders management
  getOrders: (params?: { status?: string; user_id?: string; page?: number; page_size?: number }) =>
    api.get<{ items: any[]; total: number; page: number; page_size: number }>("/admin/orders", { params }),
  updateOrderStatus: (id: string, status: string) =>
    api.patch<any>(`/admin/orders/${id}/status`, null, { params: { new_status: status } }),
  assignOrder: (id: string, assignments: { designer_id?: string; validator_id?: string; printshop_id?: string }) =>
    api.post<any>(`/admin/orders/${id}/assign`, null, { params: assignments }),

  // Payments management
  getPayments: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get<{ items: any[]; total: number; page: number; page_size: number }>("/admin/payments", { params }),
  verifyPayment: (id: string, approved: boolean, reason?: string) =>
    api.post<any>(`/admin/payments/${id}/verify`, null, { params: { approved, reason } }),

  // ============ Questionnaire Builder API ============

  // Sections management
  getPlanSections: (planId: string) =>
    api.get<any[]>(`/plans/${planId}/sections`),
  createSection: (planId: string, data: { title_fa: string; description_fa?: string; sort_order?: number; is_active?: boolean }) =>
    api.post<any>(`/plans/${planId}/sections`, data),
  updateSection: (id: string, data: { title_fa?: string; description_fa?: string; sort_order?: number; is_active?: boolean }) =>
    api.patch<any>(`/sections/${id}`, data),
  deleteSection: (id: string) =>
    api.delete(`/sections/${id}`),
  reorderSections: (items: Array<{ id: string; sort_order: number }>) =>
    api.patch<any>(`/sections/reorder`, { items }),

  // Questions management
  getSectionQuestions: (sectionId: string) =>
    api.get<any[]>(`/sections/${sectionId}/questions`),
  createQuestion: (sectionId: string, data: QuestionCreateData) =>
    api.post<any>(`/sections/${sectionId}/questions`, data),
  updateQuestion: (id: string, data: Partial<QuestionCreateData>) =>
    api.patch<any>(`/questions/${id}`, data),
  deleteQuestion: (id: string) =>
    api.delete(`/questions/${id}`),
  reorderQuestions: (items: Array<{ id: string; sort_order: number }>) =>
    api.patch<any>(`/questions/reorder`, { items }),

  // Question Options management
  createQuestionOption: (questionId: string, data: { value: string; label_fa: string; price_modifier?: number; sort_order?: number; is_active?: boolean }) =>
    api.post<any>(`/questions/${questionId}/options`, data),
  updateQuestionOption: (optionId: string, data: { value?: string; label_fa?: string; price_modifier?: number; sort_order?: number; is_active?: boolean }) =>
    api.patch<any>(`/question-options/${optionId}`, data),
  deleteQuestionOption: (optionId: string) =>
    api.delete(`/question-options/${optionId}`),

  // ============ Template Gallery API ============

  // Templates management
  getPlanTemplates: (planId: string) =>
    api.get<Template[]>(`/plans/${planId}/templates`),
  getTemplateDetails: (id: string) =>
    api.get<Template>(`/templates/${id}/details`),
  createTemplate: (planId: string, data: TemplateCreateData) =>
    api.post<Template>(`/plans/${planId}/templates`, data),
  updateTemplate: (id: string, data: Partial<TemplateCreateData>) =>
    api.patch<Template>(`/templates/${id}`, data),
  deleteTemplate: (id: string) =>
    api.delete(`/templates/${id}`),
  uploadTemplateImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<TemplateImageUploadResponse>("/templates/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // ============ Dynamic Template Placeholders API ============

  // Placeholders management
  getTemplatePlaceholders: (templateId: string) =>
    api.get<TemplatePlaceholder[]>(`/templates/${templateId}/placeholders`),
  createPlaceholder: (templateId: string, data: PlaceholderCreateData) =>
    api.post<TemplatePlaceholder>(`/templates/${templateId}/placeholders`, data),
  updatePlaceholder: (id: string, data: Partial<PlaceholderCreateData>) =>
    api.patch<TemplatePlaceholder>(`/placeholders/${id}`, data),
  deletePlaceholder: (id: string) =>
    api.delete(`/placeholders/${id}`),
  reorderPlaceholders: (items: Array<{ id: string; sort_order: number }>) =>
    api.patch<{ success: boolean }>(`/placeholders/reorder`, { items }),
  
  // Template preview
  generateTemplatePreview: (templateId: string, data: { placeholders: PlaceholderPreviewData[] }) =>
    api.post<TemplatePreviewResponse>(`/templates/${templateId}/preview`, data),

  // ============ System Fonts API ============

  // Fonts management
  getFonts: (activeOnly?: boolean) =>
    api.get<SystemFont[]>("/fonts", { params: { active_only: activeOnly } }),
  getFont: (id: string) =>
    api.get<SystemFont>(`/fonts/${id}`),
  createFont: (data: FontCreateData) =>
    api.post<SystemFont>("/fonts", data),
  updateFont: (id: string, data: Partial<FontCreateData & { is_active?: boolean }>) =>
    api.patch<SystemFont>(`/fonts/${id}`, data),
  deleteFont: (id: string) =>
    api.delete(`/fonts/${id}`),
  addFontVariant: (fontId: string, weight: number, style?: string, fileUrl?: string) =>
    api.post<SystemFont>(`/fonts/${fontId}/variants`, null, { 
      params: { weight, style: style || "normal", file_url: fileUrl }
    }),
  deleteFontVariant: (fontId: string, weight: number, style?: string) =>
    api.delete(`/fonts/${fontId}/variants/${weight}`, {
      params: { style: style || "normal" }
    }),
  uploadFontFile: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<FontUploadResponse>("/fonts/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // ============ Validation Management API ============

  // Get pending validations
  getValidations: (params?: { status?: ValidationStatus; page?: number; page_size?: number }) =>
    api.get<ValidationListResponse>("/admin/validations", { params }),

  // Approve validation
  approveValidation: (orderId: string) =>
    api.post(`/admin/validations/${orderId}/approve`),

  // Reject validation
  rejectValidation: (orderId: string, comment: string) =>
    api.post(`/admin/validations/${orderId}/reject`, { comment }),

  // ============ Print Shop API ============

  // Print shop queue (READY_FOR_PRINT orders)
  getPrintshopQueue: (params?: { page?: number; page_size?: number }) =>
    api.get("/printshop/orders", { params }),

  // Print shop's own assigned orders
  getPrintshopMyOrders: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get("/printshop/my-orders", { params }),

  // Print shop order detail
  getPrintshopOrderDetail: (orderId: string) =>
    api.get(`/printshop/my-orders/${orderId}`),

  // Accept order from queue
  printshopAcceptOrder: (orderId: string) =>
    api.post(`/printshop/accept/${orderId}`),

  // Mark as printed
  printshopCompleteOrder: (orderId: string) =>
    api.post(`/printshop/orders/${orderId}/complete`),

  // Ship order with tracking code
  printshopShipOrder: (orderId: string, data: { tracking_code: string; shipping_notes?: string }) =>
    api.post(`/printshop/orders/${orderId}/ship`, data),

  // Print shop stats
  getPrintshopStats: () =>
    api.get("/printshop/stats"),

  // Print shop settlements
  getPrintshopSettlements: (params?: { page?: number; page_size?: number }) =>
    api.get("/printshop/settlements", { params }),

  // ============ Admin Print Shop Management API ============

  // List all print shops (includes admin acting as printshop)
  getAdminPrintshops: (params?: { search?: string; is_active?: boolean; page?: number; page_size?: number }) =>
    api.get("/admin/printshops", { params }),

  // Create a new printshop user
  createPrintshop: (data: {
    first_name: string;
    last_name?: string;
    phone_number: string;
    password: string;
    city?: string;
    description?: string;
    capabilities?: string[];
    service_areas?: string[];
    max_daily_capacity?: number;
  }) => api.post("/admin/printshops", data),

  // Get printshop capabilities list
  getPrintshopCapabilities: () =>
    api.get<{ capabilities: string[] }>("/admin/printshops/capabilities"),

  // Get print shop profile
  getAdminPrintshopProfile: (printshopId: string) =>
    api.get(`/admin/printshops/${printshopId}/profile`),

  // Update print shop profile
  updatePrintshopProfile: (printshopId: string, data: {
    description?: string;
    capabilities?: string[];
    max_daily_capacity?: number;
    service_areas?: string[];
    is_featured?: boolean;
  }) => api.put(`/admin/printshops/${printshopId}/profile`, data),

  // Toggle printshop active/inactive
  togglePrintshopActive: (printshopId: string) =>
    api.post(`/admin/printshops/${printshopId}/toggle-active`),

  // Get print shop stats (admin)
  getAdminPrintshopStats: (printshopId: string) =>
    api.get(`/admin/printshops/${printshopId}/stats`),

  // Get print shop orders (admin)
  getAdminPrintshopOrders: (printshopId: string, params?: { status?: string; page?: number; page_size?: number }) =>
    api.get(`/admin/printshops/${printshopId}/orders`, { params }),

  // Reassign print shop
  reassignPrintshop: (orderId: string, newPrintshopId?: string) =>
    api.post(`/admin/orders/${orderId}/reassign-printshop`, null, {
      params: newPrintshopId ? { new_printshop_id: newPrintshopId } : {},
    }),

  // Admin settlements
  getAdminSettlements: (params?: { printshop_id?: string; status?: string; page?: number; page_size?: number }) =>
    api.get("/admin/settlements", { params }),

  // Mark settlement as paid
  markSettlementPaid: (settlementId: string) =>
    api.post(`/admin/settlements/${settlementId}/pay`),

  // Get SLA compliance report
  getPrintshopSlaReport: () =>
    api.get("/admin/printshop-sla"),

  // ============ Designer Management (Admin) ============

  getAdminDesigners: (params?: { search?: string; is_active?: boolean; page?: number; page_size?: number }) =>
    api.get("/admin/designers", { params }),
  createDesigner: (data: { first_name: string; last_name?: string; phone_number: string; password: string; city?: string; bio?: string }) =>
    api.post("/admin/designers", data),
  toggleDesignerActive: (designerId: string) =>
    api.post(`/admin/designers/${designerId}/toggle-active`),
  getAdminDesignerStats: (designerId: string) =>
    api.get(`/admin/designers/${designerId}/stats`),

  // ============ Designer API ============

  getDesignerQueue: (params?: { page?: number; page_size?: number }) =>
    api.get("/designer/queue", { params }),
  getDesignerOrders: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get("/designer/orders", { params }),
  getDesignerOrderDetail: (orderId: string) =>
    api.get(`/designer/orders/${orderId}`),
  designerAcceptOrder: (orderId: string) =>
    api.post(`/designer/orders/${orderId}/accept`),
  designerUploadDesign: (orderId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<DesignRevision>(`/designer/orders/${orderId}/upload-design`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getDesignerRevisions: (orderId: string) =>
    api.get<DesignRevisionListResponse>(`/designer/orders/${orderId}/revisions`),
  getDesignerStats: () =>
    api.get("/designer/stats"),

  // ============ Designer Validation API ============

  getDesignerValidations: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get("/designer/validations", { params }),
  approveDesignerValidation: (orderId: string) =>
    api.post(`/designer/validations/${orderId}/approve`),
  rejectDesignerValidation: (orderId: string, comment: string) =>
    api.post(`/designer/validations/${orderId}/reject`, { comment }),

  // ============ Review Management API ============
  getReviews: (params?: { printshop_id?: string; is_approved?: boolean; page?: number; page_size?: number }) =>
    api.get<{ items: any[]; total: number; page: number; page_size: number }>("/admin/reviews", { params }),
  approveReview: (reviewId: string) =>
    api.post(`/admin/reviews/${reviewId}/approve`),
  rejectReview: (reviewId: string) =>
    api.post(`/admin/reviews/${reviewId}/reject`),
};

// Error helper
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;

    // Handle string detail
    if (typeof detail === "string") {
      return detail;
    }

    // Handle Pydantic validation errors (array of objects with type, loc, msg, input)
    if (Array.isArray(detail)) {
      return detail
        .map((err) => {
          if (typeof err === "object" && err !== null && "msg" in err && "loc" in err) {
            const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : "field";
            return `${field}: ${err.msg}`;
          }
          return String(err);
        })
        .join("، ");
    }

    // Handle object detail
    if (typeof detail === "object" && detail !== null) {
      return JSON.stringify(detail);
    }

    return error.message || "خطای سرور";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "خطای ناشناخته";
}

