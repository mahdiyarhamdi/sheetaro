/**
 * MSW request handlers for mocking API calls in tests
 */

import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:3001/api/v1";

// Mock user data
export const mockUser = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  phone: "09121234567",
  full_name: "Test User",
  first_name: "Test",
  last_name: "User",
  telegram_id: null,
  is_admin: false,
  phone_verified: false,
  web_linked: false,
  created_at: "2024-01-01T00:00:00Z",
};

export const mockAdminUser = {
  ...mockUser,
  id: "admin-123",
  is_admin: true,
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

  // Admin endpoints
  http.get(`${API_URL}/admin/stats`, () => {
    return HttpResponse.json({
      total_orders: 150,
      pending_payments: 5,
      total_revenue: 15000000,
      new_users_today: 3,
    });
  }),
];

