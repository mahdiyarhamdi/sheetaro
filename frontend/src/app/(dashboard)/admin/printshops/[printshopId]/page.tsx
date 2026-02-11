"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
  ArrowRight,
  BarChart3,
  Package,
  Clock,
  CheckCircle,
  Truck,
  DollarSign,
  RefreshCw,
} from "lucide-react";
import { useState } from "react";

const statusLabels: Record<string, string> = {
  PRINTING: "در حال چاپ",
  PRINTED: "چاپ شده",
  SHIPPED: "ارسال شده",
  DELIVERED: "تحویل شده",
  CANCELLED: "لغو شده",
};

const statusColors: Record<string, string> = {
  PRINTING: "bg-blue-100 text-blue-700",
  PRINTED: "bg-purple-100 text-purple-700",
  SHIPPED: "bg-orange-100 text-orange-700",
  DELIVERED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
};

export default function AdminPrintShopDetailPage() {
  const { printshopId } = useParams<{ printshopId: string }>();
  const router = useRouter();
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("orders");

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["adminPrintshopStats", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshopStats(printshopId);
      return response.data;
    },
    enabled: isAdmin && !!printshopId,
  });

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ["adminPrintshopOrders", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshopOrders(printshopId, {
        page: 1,
        page_size: 50,
      });
      return response.data;
    },
    enabled: isAdmin && !!printshopId && activeTab === "orders",
  });

  const { data: settlementsData, isLoading: settlementsLoading } = useQuery({
    queryKey: ["adminPrintshopSettlements", printshopId],
    queryFn: async () => {
      const response = await adminApi.getAdminSettlements({
        page: 1,
        page_size: 50,
        printshop_id: printshopId,
      });
      return response.data;
    },
    enabled: isAdmin && !!printshopId && activeTab === "settlements",
  });

  const paySettlement = useMutation({
    mutationFn: (settlementId: string) => adminApi.markSettlementPaid(settlementId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPrintshopSettlements", printshopId] });
    },
  });

  const orders = ordersData?.items ?? [];
  const settlements = settlementsData?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/admin/printshops")}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
        >
          <ArrowRight className="w-5 h-5" />
        </button>
        <h1 className="text-2xl font-bold text-foreground">جزئیات چاپخانه</h1>
      </div>

      {/* Stats Cards */}
      {statsLoading ? (
        <div className="flex items-center justify-center min-h-[100px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Package className="w-6 h-6 mx-auto text-blue-500 mb-2" />
            <p className="text-xl font-bold">{stats.total_orders ?? 0}</p>
            <p className="text-sm text-muted">کل سفارش‌ها</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <CheckCircle className="w-6 h-6 mx-auto text-green-500 mb-2" />
            <p className="text-xl font-bold">{stats.printed ?? 0}</p>
            <p className="text-sm text-muted">چاپ شده</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Truck className="w-6 h-6 mx-auto text-orange-500 mb-2" />
            <p className="text-xl font-bold">{stats.shipped ?? 0}</p>
            <p className="text-sm text-muted">ارسال شده</p>
          </div>
          <div className="bg-surface border border-border rounded-xl p-4 text-center">
            <Clock className="w-6 h-6 mx-auto text-purple-500 mb-2" />
            <p className="text-xl font-bold">
              {stats.avg_print_time_hours != null
                ? `${Number(stats.avg_print_time_hours).toFixed(1)}h`
                : "-"}
            </p>
            <p className="text-sm text-muted">میانگین زمان چاپ</p>
          </div>
        </div>
      ) : null}

      {/* Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab("orders")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "orders"
              ? "border-primary text-primary"
              : "border-transparent text-muted hover:text-foreground"
          }`}
        >
          سفارش‌ها
        </button>
        <button
          onClick={() => setActiveTab("settlements")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "settlements"
              ? "border-primary text-primary"
              : "border-transparent text-muted hover:text-foreground"
          }`}
        >
          تسویه‌حساب
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "orders" && (
        <div className="space-y-3">
          {ordersLoading ? (
            <div className="flex items-center justify-center min-h-[100px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : orders.length === 0 ? (
            <p className="text-center py-8 text-muted">سفارشی یافت نشد</p>
          ) : (
            orders.map((o: Record<string, unknown>) => (
              <div
                key={o.id as string}
                className="bg-surface border border-border rounded-xl p-4 flex items-center justify-between"
              >
                <div className="space-y-1">
                  <p className="font-medium">سفارش #{(o.id as string).slice(0, 8)}</p>
                  <p className="text-sm text-muted">
                    {o.quantity as number} عدد · {o.customer_city as string || "بدون شهر"}
                  </p>
                </div>
                <div className="text-left">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs ${
                      statusColors[o.status as string] ?? "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {statusLabels[o.status as string] ?? (o.status as string)}
                  </span>
                  <p className="text-sm text-muted mt-1">
                    {Number(o.total_price).toLocaleString("fa-IR")} تومان
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "settlements" && (
        <div className="space-y-3">
          {settlementsLoading ? (
            <div className="flex items-center justify-center min-h-[100px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : settlements.length === 0 ? (
            <p className="text-center py-8 text-muted">تسویه‌حسابی یافت نشد</p>
          ) : (
            settlements.map((s: Record<string, unknown>) => (
              <div
                key={s.id as string}
                className="bg-surface border border-border rounded-xl p-4 flex items-center justify-between"
              >
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    📅 {s.period_start as string} تا {s.period_end as string}
                  </p>
                  <p className="text-sm text-muted">
                    {s.total_orders as number} سفارش ·{" "}
                    {Number(s.net_amount).toLocaleString("fa-IR")} تومان
                  </p>
                </div>
                <div className="text-left">
                  {s.status === "PAID" ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      پرداخت شده
                    </span>
                  ) : (
                    <button
                      onClick={() => paySettlement.mutate(s.id as string)}
                      disabled={paySettlement.isPending}
                      className="px-3 py-1 bg-primary text-white rounded-lg text-xs hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                      {paySettlement.isPending ? "..." : "تسویه"}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
