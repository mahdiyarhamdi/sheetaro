"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { formatPrice } from "@/lib/utils";
import { Clock, Package, MapPin, RefreshCw, Check } from "lucide-react";
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
    refetchInterval: 30000, // Refresh every 30s
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
                  <div className="flex-1 flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-sm">#{order.id.slice(0, 8)}</span>
                        {isUrgent && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                            فوری
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-muted">
                        <span className="flex items-center gap-1">
                          <Package className="w-4 h-4" />
                          {order.quantity} عدد
                        </span>
                        {order.customer_city && (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {order.customer_city}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {ageMinutes} دقیقه پیش
                        </span>
                      </div>
                      {order.customer_name && (
                        <p className="text-sm">
                          <span className="text-muted">مشتری:</span> {order.customer_name}
                        </p>
                      )}
                      <p className="text-sm font-semibold">
                        {formatPrice(order.total_price)}
                      </p>
                    </div>
                    <button
                      onClick={() => acceptMutation.mutate(order.id)}
                      disabled={acceptingId === order.id}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                    >
                      <Check className="w-4 h-4" />
                      {acceptingId === order.id ? "..." : "قبول"}
                    </button>
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
