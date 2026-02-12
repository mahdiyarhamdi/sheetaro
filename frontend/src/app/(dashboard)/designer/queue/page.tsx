"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import {
  Inbox,
  RefreshCw,
  ArrowLeft,
  Package,
  Palette,
  User,
  Calendar,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardFooter,
  Badge,
  Button,
  PageLoading,
  EmptyState,
} from "@/components/ui";
import { cn, formatPrice, toPersianNumber } from "@/lib/utils";
import toast from "react-hot-toast";

export default function DesignerQueuePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["designerQueue"],
    queryFn: async () => {
      const response = await adminApi.getDesignerQueue();
      return response.data;
    },
    refetchInterval: 15000, // Auto-refresh every 15s
  });

  const acceptMutation = useMutation({
    mutationFn: async (orderId: string) => {
      return await adminApi.designerAcceptOrder(orderId);
    },
    onSuccess: (_, orderId) => {
      toast.success("سفارش با موفقیت پذیرفته شد");
      queryClient.invalidateQueries({ queryKey: ["designerQueue"] });
      queryClient.invalidateQueries({ queryKey: ["designerStats"] });
      queryClient.invalidateQueries({ queryKey: ["designerOrders"] });
      router.push(`/designer/orders/${orderId}`);
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.detail || "خطا در پذیرش سفارش";
      toast.error(msg);
    },
  });

  const orders = data?.items || [];

  const statusLabel: Record<string, string> = {
    SEMI_PRIVATE: "نیمه اختصاصی",
    PRIVATE: "اختصاصی",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Inbox className="w-6 h-6 text-red-600" />
            صف سفارشات جدید
          </h1>
          <p className="text-sm text-muted mt-1">
            سفارشاتی که منتظر پذیرش توسط طراح هستند
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* Queue list */}
      {isLoading ? (
        <PageLoading />
      ) : orders.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="صف خالی است"
          description="در حال حاضر سفارش جدیدی در صف انتظار نیست"
        />
      ) : (
        <div className="space-y-4">
          {orders.map((order: any) => (
            <Card key={order.id} className="overflow-hidden">
              <CardContent className="pt-4 pb-3">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{order.category_icon || "📦"}</span>
                    <div>
                      <h3 className="font-semibold text-foreground">
                        {order.category_name || "سفارش"}
                      </h3>
                      <Badge variant="warning" size="sm" className="mt-1">
                        {statusLabel[order.design_plan] || order.design_plan_label || order.design_plan}
                      </Badge>
                    </div>
                  </div>
                  <span className="font-bold text-primary">
                    {formatPrice(order.total_price)}
                  </span>
                </div>

                {/* Order info */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2 text-muted">
                    <User className="w-4 h-4" />
                    <span>{order.customer_name || "مشتری"}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted">
                    <Package className="w-4 h-4" />
                    <span>تعداد: {toPersianNumber(order.quantity)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {new Date(order.created_at).toLocaleDateString("fa-IR")}
                    </span>
                  </div>
                  {order.enriched_attributes?.length > 0 && (
                    <div className="flex items-center gap-2 text-muted">
                      <Palette className="w-4 h-4" />
                      <span>
                        {order.enriched_attributes
                          .slice(0, 2)
                          .map((a: any) => a.selected_label)
                          .join(" · ")}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex items-center justify-between bg-accent/30 py-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/designer/orders/${order.id}`)}
                  leftIcon={<ArrowLeft className="w-4 h-4" />}
                >
                  مشاهده جزئیات
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => acceptMutation.mutate(order.id)}
                  isLoading={acceptMutation.isPending}
                >
                  پذیرش سفارش
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
