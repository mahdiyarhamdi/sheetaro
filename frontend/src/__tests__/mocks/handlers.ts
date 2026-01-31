/**
 * MSW request handlers for mocking API calls in tests
 */

import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:3005/api/v1";

// Mock user data
export const mockUser = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  phone_number: "09121234567",
  full_name: "Test User",
  first_name: "Test",
  last_name: "User",
  telegram_id: null,
  is_admin: false,
  phone_verified: false,
  web_linked: false,
  created_at: "2024-01-01T00:00:00Z",
  role: "CUSTOMER",
  is_active: true,
};

export const mockAdminUser = {
  ...mockUser,
  id: "admin-123e4567-e89b-12d3-a456-426614174001",
  phone_number: "09120000000",
  full_name: "Admin User",
  first_name: "Admin",
  last_name: "User",
  is_admin: true,
  role: "ADMIN",
};

export const mockTokens = {
  access_token: "mock-access-token",
  refresh_token: "mock-refresh-token",
  token_type: "bearer",
};

// Mock orders
export const mockOrders = [
  {
    id: "order-1",
    user_id: mockUser.id,
    category_id: "cat-1",
    plan_id: "plan-1",
    status: "PENDING",
    total_price: 50000,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: "order-2",
    user_id: mockUser.id,
    category_id: "cat-1",
    plan_id: "plan-2",
    status: "DELIVERED",
    total_price: 100000,
    created_at: "2024-01-02T00:00:00Z",
    updated_at: "2024-01-05T00:00:00Z",
  },
];

// Mock categories
export const mockCategories = [
  {
    id: "cat-1",
    name_fa: "لیبل",
    slug: "label",
    icon: "tag",
    base_price: 10000,
    is_active: true,
  },
  {
    id: "cat-2",
    name_fa: "فاکتور",
    slug: "invoice",
    icon: "file-text",
    base_price: 20000,
    is_active: true,
  },
];

// Mock plans
export const mockPlans = [
  {
    id: "plan-1",
    category_id: "cat-1",
    name_fa: "عمومی",
    slug: "public",
    plan_type: "public",
    price: 0,
    is_active: true,
  },
  {
    id: "plan-2",
    category_id: "cat-1",
    name_fa: "نیمه خصوصی",
    slug: "semi-private",
    plan_type: "semi_private",
    price: 50000,
    is_active: true,
  },
];

// Mock payments
export const mockPayments = [
  {
    id: "payment-1",
    order_id: "order-1",
    amount: 50000,
    status: "AWAITING_APPROVAL",
    receipt_url: "https://example.com/receipt.jpg",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
];

// Handlers
export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/auth/register`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    
    // Simulate duplicate phone
    if (body.phone === "09000000000") {
      return HttpResponse.json(
        { detail: "این شماره موبایل قبلاً ثبت شده است" },
        { status: 409 }
      );
    }
    
    return HttpResponse.json(
      {
        ...mockTokens,
        user: {
          ...mockUser,
          phone: body.phone,
          full_name: body.full_name,
        },
      },
      { status: 201 }
    );
  }),

  http.post(`${API_URL}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    
    // Simulate wrong password
    if (body.password === "wrong_password") {
      return HttpResponse.json(
        { detail: "شماره موبایل یا رمز عبور اشتباه است" },
        { status: 401 }
      );
    }
    
    return HttpResponse.json({
      ...mockTokens,
      user: mockUser,
    });
  }),

  http.post(`${API_URL}/auth/refresh`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    
    if (body.refresh_token === "invalid") {
      return HttpResponse.json(
        { detail: "توکن نامعتبر است" },
        { status: 401 }
      );
    }
    
    return HttpResponse.json({
      ...mockTokens,
      user: mockUser,
    });
  }),

  http.get(`${API_URL}/auth/me`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return HttpResponse.json(
        { detail: "توکن احراز هویت ارسال نشده است" },
        { status: 401 }
      );
    }
    
    return HttpResponse.json(mockUser);
  }),

  http.post(`${API_URL}/auth/telegram-link`, () => {
    return HttpResponse.json({
      otp: "123456",
      expires_at: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
      message: "کد تایید را در ربات تلگرام وارد کنید",
    });
  }),

  // Orders endpoints
  http.get(`${API_URL}/orders`, () => {
    return HttpResponse.json({
      items: mockOrders,
      total: mockOrders.length,
      page: 1,
      page_size: 10,
    });
  }),

  http.get(`${API_URL}/orders/:id`, ({ params }) => {
    const order = mockOrders.find((o) => o.id === params.id);
    if (!order) {
      return HttpResponse.json(
        { detail: "Order not found" },
        { status: 404 }
      );
    }
    return HttpResponse.json(order);
  }),

  http.post(`${API_URL}/orders`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(
      {
        id: "new-order-id",
        ...body,
        user_id: mockUser.id,
        status: "PENDING",
        total_price: 50000,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    );
  }),

  // Categories endpoints
  http.get(`${API_URL}/categories`, () => {
    return HttpResponse.json({
      items: mockCategories,
    });
  }),

  http.get(`${API_URL}/categories/:id/plans`, () => {
    return HttpResponse.json({
      items: mockPlans,
    });
  }),

  http.get(`${API_URL}/categories/:id/attributes`, () => {
    return HttpResponse.json({
      items: [],
    });
  }),

  // Plans endpoints
  http.get(`${API_URL}/plans/:id`, ({ params }) => {
    const plan = mockPlans.find((p) => p.id === params.id);
    if (!plan) {
      return HttpResponse.json(
        { detail: "Plan not found" },
        { status: 404 }
      );
    }
    return HttpResponse.json(plan);
  }),

  http.get(`${API_URL}/plans/:id/templates`, () => {
    return HttpResponse.json({
      items: [],
    });
  }),

  http.get(`${API_URL}/plans/:id/questionnaire`, () => {
    return HttpResponse.json({
      id: "questionnaire-1",
      plan_id: "plan-2",
      sections: [
        {
          id: "section-1",
          title_fa: "اطلاعات برند",
          order_index: 1,
          questions: [
            {
              id: "q-1",
              text_fa: "نام برند شما چیست؟",
              input_type: "TEXT",
              is_required: true,
              order_index: 1,
            },
          ],
        },
      ],
    });
  }),

  // Payments endpoints
  http.post(`${API_URL}/payments/initiate`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({
      id: "payment-new",
      order_id: body.order_id,
      amount: 50000,
      status: "PENDING",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }),

  http.get(`${API_URL}/payments/pending`, () => {
    return HttpResponse.json({
      items: mockPayments,
      total: mockPayments.length,
    });
  }),

  http.post(`${API_URL}/payments/:id/approve`, ({ params }) => {
    return HttpResponse.json({
      ...mockPayments[0],
      id: params.id,
      status: "SUCCESS",
    });
  }),

  http.post(`${API_URL}/payments/:id/reject`, ({ params }) => {
    return HttpResponse.json({
      ...mockPayments[0],
      id: params.id,
      status: "FAILED",
    });
  }),

  // ==================== Admin Endpoints ====================

  // Admin Dashboard Stats
  http.get(`${API_URL}/admin/stats`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      total_orders: 150,
      pending_payments: 5,
      total_revenue: 15000000,
      new_users_today: 3,
      active_users: 120,
      orders_today: 8,
      orders_this_week: 42,
      pending_orders: 12,
    });
  }),

  // Admin Order Stats
  http.get(`${API_URL}/admin/stats/orders`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      total: 150,
      by_status: {
        PENDING: 12,
        DESIGNING: 8,
        READY_FOR_PRINT: 5,
        PRINTING: 3,
        SHIPPED: 10,
        DELIVERED: 110,
        CANCELLED: 2,
      },
      by_day: [
        { date: "2024-01-01", count: 5 },
        { date: "2024-01-02", count: 8 },
        { date: "2024-01-03", count: 6 },
        { date: "2024-01-04", count: 10 },
        { date: "2024-01-05", count: 7 },
        { date: "2024-01-06", count: 4 },
        { date: "2024-01-07", count: 8 },
      ],
    });
  }),

  // Admin Revenue Stats
  http.get(`${API_URL}/admin/stats/revenue`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      total_revenue: 15000000,
      this_month: 4500000,
      last_month: 3800000,
      by_day: [
        { date: "2024-01-01", amount: 500000 },
        { date: "2024-01-02", amount: 750000 },
        { date: "2024-01-03", amount: 600000 },
        { date: "2024-01-04", amount: 900000 },
        { date: "2024-01-05", amount: 650000 },
        { date: "2024-01-06", amount: 400000 },
        { date: "2024-01-07", amount: 700000 },
      ],
    });
  }),

  // Admin User Stats
  http.get(`${API_URL}/admin/stats/users`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      by_role: {
        CUSTOMER: 100,
        DESIGNER: 5,
        VALIDATOR: 3,
        PRINT_SHOP: 2,
        ADMIN: 2,
      },
      daily_signups: [
        { date: "2024-01-01", count: 2 },
        { date: "2024-01-02", count: 5 },
        { date: "2024-01-03", count: 3 },
        { date: "2024-01-04", count: 7 },
        { date: "2024-01-05", count: 4 },
        { date: "2024-01-06", count: 2 },
        { date: "2024-01-07", count: 3 },
      ],
    });
  }),

  // Admin Users List
  http.get(`${API_URL}/admin/users`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const search = url.searchParams.get("search");
    const role = url.searchParams.get("role");
    const page = parseInt(url.searchParams.get("page") || "1");
    const pageSize = parseInt(url.searchParams.get("page_size") || "20");
    
    let users = [mockUser, mockAdminUser];
    
    if (role) {
      users = users.filter(u => u.role === role);
    }
    
    if (search) {
      users = users.filter(u => 
        u.full_name.toLowerCase().includes(search.toLowerCase()) ||
        u.phone_number.includes(search)
      );
    }
    
    return HttpResponse.json({
      items: users,
      total: users.length,
      page,
      page_size: pageSize,
    });
  }),

  // Admin Get User
  http.get(`${API_URL}/admin/users/:id`, ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    if (params.id === mockUser.id) {
      return HttpResponse.json(mockUser);
    }
    if (params.id === mockAdminUser.id) {
      return HttpResponse.json(mockAdminUser);
    }
    
    return HttpResponse.json({ detail: "کاربر یافت نشد" }, { status: 404 });
  }),

  // Admin Update User Role
  http.patch(`${API_URL}/admin/users/:id/role`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as { role: string };
    
    return HttpResponse.json({
      ...mockUser,
      id: params.id,
      role: body.role,
    });
  }),

  // Admin Ban/Unban User
  http.post(`${API_URL}/admin/users/:id/ban`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    // Cannot ban self
    if (params.id === mockAdminUser.id) {
      return HttpResponse.json(
        { detail: "نمی‌توانید خودتان را مسدود کنید" },
        { status: 400 }
      );
    }
    
    const body = (await request.json()) as { is_active: boolean; reason?: string };
    
    return HttpResponse.json({
      ...mockUser,
      id: params.id,
      is_active: body.is_active,
    });
  }),

  // Admin Orders List
  http.get(`${API_URL}/admin/orders`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const status = url.searchParams.get("status");
    const page = parseInt(url.searchParams.get("page") || "1");
    const pageSize = parseInt(url.searchParams.get("page_size") || "20");
    
    let orders = mockOrders;
    if (status) {
      orders = orders.filter(o => o.status === status);
    }
    
    return HttpResponse.json({
      items: orders,
      total: orders.length,
      page,
      page_size: pageSize,
    });
  }),

  // Admin Update Order Status
  http.patch(`${API_URL}/admin/orders/:id/status`, ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const newStatus = url.searchParams.get("new_status");
    
    const order = mockOrders.find(o => o.id === params.id);
    if (!order) {
      return HttpResponse.json({ detail: "سفارش یافت نشد" }, { status: 404 });
    }
    
    return HttpResponse.json({
      success: true,
      order_id: params.id,
      old_status: order.status,
      new_status: newStatus,
    });
  }),

  // Admin Assign Order
  http.post(`${API_URL}/admin/orders/:id/assign`, ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const designerId = url.searchParams.get("designer_id");
    const validatorId = url.searchParams.get("validator_id");
    const printshopId = url.searchParams.get("printshop_id");
    
    const order = mockOrders.find(o => o.id === params.id);
    if (!order) {
      return HttpResponse.json({ detail: "سفارش یافت نشد" }, { status: 404 });
    }
    
    return HttpResponse.json({
      success: true,
      order_id: params.id,
      assigned_designer_id: designerId,
      assigned_validator_id: validatorId,
      assigned_printshop_id: printshopId,
    });
  }),

  // Admin Payments List
  http.get(`${API_URL}/admin/payments`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const status = url.searchParams.get("status");
    const page = parseInt(url.searchParams.get("page") || "1");
    const pageSize = parseInt(url.searchParams.get("page_size") || "20");
    
    let payments = mockPayments;
    if (status) {
      payments = payments.filter(p => p.status === status);
    }
    
    return HttpResponse.json({
      items: payments,
      total: payments.length,
      page,
      page_size: pageSize,
    });
  }),

  // Admin Verify Payment
  http.post(`${API_URL}/admin/payments/:id/verify`, ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const url = new URL(request.url);
    const approved = url.searchParams.get("approved") === "true";
    
    const payment = mockPayments.find(p => p.id === params.id);
    if (!payment) {
      return HttpResponse.json({ detail: "پرداخت یافت نشد" }, { status: 404 });
    }
    
    if (payment.status === "SUCCESS" || payment.status === "FAILED") {
      return HttpResponse.json(
        { detail: "این پرداخت قبلاً بررسی شده است" },
        { status: 400 }
      );
    }
    
    return HttpResponse.json({
      success: true,
      payment_id: params.id,
      status: approved ? "SUCCESS" : "FAILED",
    });
  }),

  // ==================== Template Builder Endpoints ====================

  // Fonts CRUD
  http.get(`${API_URL}/fonts`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      items: [
        {
          id: "font-1",
          name: "IRANSans",
          name_fa: "ایران سنس",
          file_url: "https://example.com/iransans.woff2",
          variants: [
            { weight: 400, style: "normal", file_url: "https://example.com/iransans-regular.woff2" },
            { weight: 700, style: "normal", file_url: "https://example.com/iransans-bold.woff2" },
          ],
          sample_text: "نمونه متن فارسی",
          is_active: true,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });
  }),

  http.post(`${API_URL}/fonts`, async ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(
      {
        id: "font-new",
        ...body,
        variants: body.variants || [],
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    );
  }),

  http.patch(`${API_URL}/fonts/:id`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({
      id: params.id,
      name: body.name || "IRANSans",
      name_fa: body.name_fa || "ایران سنس",
      file_url: body.file_url || null,
      variants: body.variants || [],
      sample_text: body.sample_text || "نمونه متن",
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: new Date().toISOString(),
    });
  }),

  http.delete(`${API_URL}/fonts/:id`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return new HttpResponse(null, { status: 204 });
  }),

  // Font file upload
  http.post(`${API_URL}/fonts/upload`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      filename: "test-font.ttf",
      file_url: "/files/fonts/20260131_abc123.ttf",
      file_size: 1024000,
      content_type: "font/ttf",
    }, { status: 201 });
  }),

  // Template image upload
  http.post(`${API_URL}/templates/upload`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      filename: "test-template.png",
      file_url: "/files/templates/20260131_abc123.png",
      preview_url: "/files/templates/20260131_abc123.png",
      file_size: 2048000,
      content_type: "image/png",
      width: 1000,
      height: 1400,
    }, { status: 201 });
  }),

  // Template Placeholders CRUD
  http.get(`${API_URL}/templates/:templateId/placeholders`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      items: [
        {
          id: "ph-1",
          template_id: "template-1",
          type: "IMAGE",
          name: "logo",
          label_fa: "لوگو",
          x: 100,
          y: 100,
          width: 200,
          height: 200,
          rotation: 0,
          is_required: true,
          sort_order: 0,
          font_family: null,
          font_size: null,
          font_weight: null,
          font_color: null,
          text_align: null,
          max_length: null,
          default_value: null,
          is_active: true,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });
  }),

  http.post(`${API_URL}/templates/:templateId/placeholders`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(
      {
        id: "ph-new",
        template_id: params.templateId,
        type: body.type || "IMAGE",
        name: body.name || "placeholder",
        label_fa: body.label_fa || "جایگاه",
        x: body.x || 0,
        y: body.y || 0,
        width: body.width || 100,
        height: body.height || 100,
        rotation: body.rotation || 0,
        is_required: body.is_required ?? true,
        sort_order: body.sort_order || 0,
        font_family: body.font_family || null,
        font_size: body.font_size || null,
        font_weight: body.font_weight || null,
        font_color: body.font_color || null,
        text_align: body.text_align || null,
        max_length: body.max_length || null,
        default_value: body.default_value || null,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    );
  }),

  // Update placeholder - using /placeholders/:id (NOT /templates/placeholders/:id)
  http.patch(`${API_URL}/placeholders/:id`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({
      id: params.id,
      template_id: "template-1",
      type: body.type || "IMAGE",
      name: body.name || "placeholder",
      label_fa: body.label_fa || "جایگاه",
      x: body.x ?? 100,
      y: body.y ?? 100,
      width: body.width ?? 200,
      height: body.height ?? 200,
      rotation: body.rotation ?? 0,
      is_required: body.is_required ?? true,
      sort_order: body.sort_order ?? 0,
      font_family: body.font_family || null,
      font_size: body.font_size || null,
      font_weight: body.font_weight || null,
      font_color: body.font_color || null,
      text_align: body.text_align || null,
      max_length: body.max_length || null,
      default_value: body.default_value || null,
      is_active: body.is_active ?? true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: new Date().toISOString(),
    });
  }),

  // Delete placeholder - using /placeholders/:id (NOT /templates/placeholders/:id)
  http.delete(`${API_URL}/placeholders/:id`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return new HttpResponse(null, { status: 204 });
  }),

  // Reorder placeholders - using /placeholders/reorder (NOT /templates/placeholders/reorder)
  http.patch(`${API_URL}/placeholders/reorder`, async ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    const body = (await request.json()) as { items: Array<{ id: string; sort_order: number }> };
    return HttpResponse.json({
      success: true,
      updated: body.items?.length || 0,
    });
  }),

  // Template Preview
  http.post(`${API_URL}/templates/:templateId/preview`, async ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      preview_url: `https://example.com/previews/${params.templateId}.png`,
      width: 800,
      height: 600,
    });
  }),

  // Get Template Details
  http.get(`${API_URL}/templates/:templateId/details`, ({ params, request }) => {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }
    
    return HttpResponse.json({
      id: params.templateId,
      plan_id: "plan-1",
      name_fa: "قالب تست",
      description_fa: "توضیحات قالب",
      preview_url: "https://example.com/preview.png",
      file_url: "https://example.com/template.png",
      image_width: 800,
      image_height: 600,
      placeholder_x: null,
      placeholder_y: null,
      placeholder_width: null,
      placeholder_height: null,
      placeholder_rotation: null,
      sort_order: 0,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
      placeholders: [
        {
          id: "ph-1",
          template_id: params.templateId,
          type: "IMAGE",
          name: "logo",
          label_fa: "لوگو",
          x: 100,
          y: 100,
          width: 200,
          height: 200,
          rotation: 0,
          is_required: true,
          sort_order: 0,
          font_family: null,
          font_size: null,
          font_weight: null,
          font_color: null,
          text_align: null,
          max_length: null,
          default_value: null,
          is_active: true,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
      ],
    });
  }),
];

