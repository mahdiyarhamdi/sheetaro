"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import {
  formatPrice,
  getPaymentStatusInfo,
  timeAgo,
  toPersianNumber,
} from "@/lib/utils";
import { Clock, Package, MapPin, RefreshCw, Check, MessageSquare } from "lucide-react";
import { ImagePreview } from "@/components/ui/image-preview";

interface QueueOrder {
  id: string;
  quantity: number;
  total_price: number;
  customer_name?: string;
  customer_phone?: string;
  customer_city?: string;
  created_at: string;
  status: string;
  design_preview_url?: string;
  design_final_url?: string;
  // Enriched fields
  category_name?: string;
  category_icon?: string;
  design_plan_label?: string;
  template_name?: string;
  customer_notes?: string;
  payment_status?: string;
  enriched_attributes?: Array<{ attribute_name: string; value_name: string; price: number }>;
}

export default function PrintShopQueuePage() {
  const queryClient = useQueryClient();
  const [acceptingId, setAcceptingId] = useState<string | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["printshopQueue"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopQueue({ page: 1, page_size: 50 });
      return response.data;
    },
    refetchInterval: 30000,
  });

  const acceptMutation = useMutation({
    mutationFn: async (orderId: string) => {
      setAcceptingId(orderId);
      const response = await adminApi.printshopAcceptOrder(orderId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printshopQueue"] });
      queryClient.invalidateQueries({ queryKey: ["printshopStats"] });
      setAcceptingId(null);
    },
    onError: () => {
      setAcceptingId(null);
    },
  });

  const orders: QueueOrder[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">📋 صف سفارش‌ها</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg">صف سفارش‌ها خالی است</p>
          <p className="text-sm mt-1">سفارش جدیدی برای چاپ وجود ندارد</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const createdAt = new Date(order.created_at);
            const ageMinutes = Math.round((Date.now() - createdAt.getTime()) / 60000);
            const isUrgent = ageMinutes > 20;
            const specTags = (order.enriched_attributes || []).map(a => a.value_name).slice(0, 3);
            const payInfo = getPaymentStatusInfo(order.payment_status);

            return (
              <div
                key={order.id}
                className={`bg-surface border rounded-xl p-4 ${isUrgent ? "border-red-300 bg-red-50/50" : "border-border"}`}
              >
                <div className="flex items-start gap-4">
                  {/* Design thumbnail */}
                  {order.design_preview_url && (
                    <div className="flex-shrink-0 w-20 h-20">
                      <ImagePreview
                        src={order.design_preview_url}
                        alt="پیش‌نمایش طرح"
                        className="w-20 h-20"
                        aspectRatio="aspect-square"
                        thumbnailSize={200}
                        showDownload={false}
                        downloadFilename={`design-${order.id.slice(0, 8)}`}
                      />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    {/* Row 1: ID + badges */}
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span className="font-mono font-bold text-sm">#{order.id.slice(0, 8)}</span>

                      {order.category_name && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                          {order.category_icon && <span>{order.category_icon}</span>}
                          {order.category_name}
                        </span>
                      )}

                      {order.design_plan_label && (
                        <span className="px-2 py-0.5 bg-purple-50 text-purple-700 text-xs rounded-full">
                          {order.design_plan_label}
                        </span>
                      )}

                      {order.payment_status && (
                        <span className={`px-2 py-0.5 text-xs rounded-full ${payInfo.color}`}>
                          {payInfo.label}
                        </span>
                      )}

                      {isUrgent && (
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                          فوری
                        </span>
                      )}
                    </div>

                    {/* Row 2: Spec tags + quantity */}
                    <div className="flex flex-wrap items-center gap-2 mb-1.5 text-sm">
                      {specTags.map((tag, i) => (
                        <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                          {tag}
                        </span>
                      ))}
                      <span className="flex items-center gap-1 text-muted">
                        <Package className="w-3.5 h-3.5" />
                        {toPersianNumber(order.quantity)} عدد
                      </span>
                    </div>

                    {/* Row 3: Customer + location + time */}
                    <div className="flex flex-wrap gap-3 text-sm text-muted mb-1">
                      {order.customer_name && (
                        <span>مشتری: {order.customer_name}</span>
                      )}
                      {order.customer_city && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5" />
                          {order.customer_city}
                        </span>
                      )}
                    </div>

                    {/* Row 4: Price + age */}
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="font-semibold text-foreground">
                        {formatPrice(order.total_price)}
                      </span>
                      <span className="flex items-center gap-1 text-muted">
                        <Clock className="w-3.5 h-3.5" />
                        {timeAgo(order.created_at)}
                      </span>
                    </div>

                    {/* Row 5: Customer notes (truncated) */}
                    {order.customer_notes && (
                      <p className="mt-1.5 text-xs text-muted flex items-start gap-1 truncate" title={order.customer_notes}>
                        <MessageSquare className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                        <span className="truncate">{order.customer_notes}</span>
                      </p>
                    )}
                  </div>

                  {/* Accept button */}
                  <button
                    onClick={() => acceptMutation.mutate(order.id)}
                    disabled={acceptingId === order.id}
                    className="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 self-center"
                  >
                    <Check className="w-4 h-4" />
                    {acceptingId === order.id ? "..." : "قبول"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
