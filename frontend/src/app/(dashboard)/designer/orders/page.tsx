"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import {
  formatPrice,
  timeAgo,
  toPersianNumber,
  orderStatusLabels,
} from "@/lib/utils";
import {
  PenTool,
  RefreshCw,
  ChevronLeft,
  Package,
  User,
  Clock,
} from "lucide-react";
import { Badge, PageLoading, EmptyState } from "@/components/ui";

interface DesignerOrder {
  id: string;
  quantity: number;
  total_price: number;
  status: string;
  design_plan: string;
  created_at: string;
  customer_name?: string;
  category_name?: string;
  category_icon?: string;
  design_plan_label?: string;
  enriched_attributes?: Array<{ attribute_name: string; value_name: string; price: number }>;
  revision_count?: number;
  max_revisions?: number | null;
}

const statusFilters = [
  { value: "", label: "همه" },
  { value: "DESIGNING", label: "در حال طراحی" },
  { value: "READY_FOR_PRINT", label: "آماده چاپ" },
  { value: "AWAITING_VALIDATION", label: "اعتبارسنجی" },
];

export default function DesignerOrdersPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialStatus = searchParams.get("status") || "";
  const [statusFilter, setStatusFilter] = useState(initialStatus);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["designerOrders", statusFilter],
    queryFn: async () => {
      const params: Record<string, string | number> = { page: 1, page_size: 50 };
      if (statusFilter) params.status = statusFilter;
      const response = await adminApi.getDesignerOrders(params);
      return response.data;
    },
  });

  if (isLoading) return <PageLoading />;

  const orders: DesignerOrder[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">سفارشات طراحی</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {statusFilters.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === f.value
                ? "bg-primary text-white"
                : "bg-surface border border-border text-muted hover:bg-accent"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Orders list */}
      {orders.length === 0 ? (
        <EmptyState
          icon={PenTool}
          title="سفارشی یافت نشد"
          description="در حال حاضر سفارشی در این وضعیت ندارید"
        />
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <div
              key={order.id}
              onClick={() => router.push(`/designer/orders/${order.id}`)}
              className="bg-surface border border-border rounded-xl p-4 cursor-pointer hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {order.category_icon && (
                    <span className="text-lg">{order.category_icon}</span>
                  )}
                  <span className="font-medium text-foreground">
                    {order.category_name || "سفارش"}
                  </span>
                  {order.design_plan_label && (
                    <Badge variant="info" size="sm">
                      {order.design_plan_label}
                    </Badge>
                  )}
                </div>
                <Badge
                  variant={
                    order.status === "DESIGNING"
                      ? "primary"
                      : order.status === "READY_FOR_PRINT"
                      ? "success"
                      : "info"
                  }
                  size="sm"
                >
                  {orderStatusLabels[order.status] || order.status}
                </Badge>
              </div>

              {/* Attributes */}
              {order.enriched_attributes && order.enriched_attributes.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {order.enriched_attributes.map((attr, i) => (
                    <span
                      key={i}
                      className="text-xs bg-accent px-2 py-0.5 rounded"
                    >
                      {attr.attribute_name}: {attr.value_name}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-sm text-muted">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <Package className="w-3.5 h-3.5" />
                    تعداد: {toPersianNumber(order.quantity)}
                  </span>
                  {order.customer_name && (
                    <span className="flex items-center gap-1">
                      <User className="w-3.5 h-3.5" />
                      {order.customer_name}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {timeAgo(order.created_at)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">
                    {formatPrice(order.total_price)}
                  </span>
                  <ChevronLeft className="w-4 h-4" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
