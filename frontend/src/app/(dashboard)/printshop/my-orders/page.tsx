"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import {
  formatPrice,
  timeAgo,
  toPersianNumber,
} from "@/lib/utils";
import Link from "next/link";
import {
  Package,
  Printer,
  Truck,
  CheckCircle,
  RefreshCw,
  Eye,
  MapPin,
  Clock,
} from "lucide-react";
import { ImagePreview } from "@/components/ui/image-preview";

interface MyOrder {
  id: string;
  quantity: number;
  total_price: number;
  status: string;
  customer_name?: string;
  customer_city?: string;
  created_at: string;
  accepted_at?: string;
  design_preview_url?: string;
  design_final_url?: string;
  category_name?: string;
  category_icon?: string;
  design_plan_label?: string;
  payment_status?: string;
  enriched_attributes?: Array<{ attribute_name: string; value_name: string; price: number }>;
}

const STATUS_TABS = [
  { key: null, label: "همه" },
  { key: "PRINTING", label: "در حال چاپ" },
  { key: "PRINTED", label: "چاپ شده" },
  { key: "SHIPPED", label: "ارسال شده" },
  { key: "DELIVERED", label: "تحویل شده" },
] as const;

const STATUS_LABELS: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  PRINTING: { label: "در حال چاپ", color: "bg-blue-100 text-blue-700", icon: <Printer className="w-4 h-4" /> },
  PRINTED: { label: "چاپ شده", color: "bg-green-100 text-green-700", icon: <CheckCircle className="w-4 h-4" /> },
  SHIPPED: { label: "ارسال شده", color: "bg-purple-100 text-purple-700", icon: <Truck className="w-4 h-4" /> },
  DELIVERED: { label: "تحویل شده", color: "bg-emerald-100 text-emerald-700", icon: <Package className="w-4 h-4" /> },
};

export default function PrintShopMyOrdersPage() {
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["printshopMyOrders", activeTab],
    queryFn: async () => {
      const params: Record<string, unknown> = { page: 1, page_size: 50 };
      if (activeTab) params.status = activeTab;
      const response = await adminApi.getPrintshopMyOrders(params as { status?: string; page?: number; page_size?: number });
      return response.data;
    },
  });

  const completeMutation = useMutation({
    mutationFn: async (orderId: string) => {
      const response = await adminApi.printshopCompleteOrder(orderId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printshopMyOrders"] });
      queryClient.invalidateQueries({ queryKey: ["printshopStats"] });
    },
  });

  const orders: MyOrder[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">📦 سفارش‌های من</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.key ?? "all"}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-primary text-white"
                : "bg-surface border border-border text-muted hover:bg-accent"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Orders */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>سفارشی یافت نشد</p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => {
            const status = order.status;
            const statusInfo = STATUS_LABELS[status] ?? { label: status, color: "bg-gray-100 text-gray-700", icon: null };
            const specTags = (order.enriched_attributes || []).map(a => a.value_name).slice(0, 2);

            return (
              <div key={order.id} className="bg-surface border border-border rounded-xl p-4">
                <div className="flex items-start gap-4">
                  {/* Design thumbnail */}
                  {order.design_preview_url && (
                    <div className="flex-shrink-0 w-16 h-16">
                      <ImagePreview
                        src={order.design_preview_url}
                        alt="طرح"
                        className="w-16 h-16"
                        aspectRatio="aspect-square"
                        thumbnailSize={160}
                        showDownload={false}
                        showExpand={false}
                      />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    {/* Row 1: ID + status + category */}
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="font-mono font-bold text-sm">#{order.id.slice(0, 8)}</span>
                      <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${statusInfo.color}`}>
                        {statusInfo.icon}
                        {statusInfo.label}
                      </span>
                      {order.category_name && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                          {order.category_icon && <span>{order.category_icon}</span>}
                          {order.category_name}
                        </span>
                      )}
                    </div>

                    {/* Row 2: Customer + specs */}
                    <p className="text-sm text-muted mb-0.5">
                      {order.customer_name || "ناشناس"} · {toPersianNumber(order.quantity)} عدد
                      {specTags.length > 0 && ` · ${specTags.join(" · ")}`}
                    </p>

                    {/* Row 3: Price + accepted time */}
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="font-semibold">{formatPrice(order.total_price)}</span>
                      {order.accepted_at && (
                        <span className="flex items-center gap-1 text-muted">
                          <Clock className="w-3.5 h-3.5" />
                          قبول: {timeAgo(order.accepted_at)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {status === "PRINTING" && (
                      <button
                        onClick={() => completeMutation.mutate(order.id)}
                        className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                      >
                        تکمیل چاپ
                      </button>
                    )}
                    {status === "PRINTED" && (
                      <Link
                        href={`/printshop/my-orders/${order.id}`}
                        className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        ارسال
                      </Link>
                    )}
                    <Link
                      href={`/printshop/my-orders/${order.id}`}
                      className="p-2 text-muted hover:text-foreground transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
