"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import {
  BarChart3,
  Package,
  Printer,
  Truck,
  CheckCircle,
  Clock,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";

export default function PrintShopDashboardPage() {
  const router = useRouter();

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ["printshopStats"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopStats();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">🏭 پنل چاپخانه</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatsCard
          title="صف انتظار"
          value={stats?.pending_orders ?? 0}
          icon={<Clock className="w-6 h-6 text-yellow-500" />}
          color="bg-yellow-50 border-yellow-200"
        />
        <StatsCard
          title="در حال چاپ"
          value={stats?.in_progress_orders ?? 0}
          icon={<Printer className="w-6 h-6 text-blue-500" />}
          color="bg-blue-50 border-blue-200"
        />
        <StatsCard
          title="چاپ شده"
          value={stats?.printed_orders ?? 0}
          icon={<CheckCircle className="w-6 h-6 text-green-500" />}
          color="bg-green-50 border-green-200"
        />
        <StatsCard
          title="ارسال شده"
          value={stats?.shipped_orders ?? 0}
          icon={<Truck className="w-6 h-6 text-purple-500" />}
          color="bg-purple-50 border-purple-200"
        />
        <StatsCard
          title="تحویل شده"
          value={stats?.delivered_orders ?? 0}
          icon={<Package className="w-6 h-6 text-emerald-500" />}
          color="bg-emerald-50 border-emerald-200"
        />
        <StatsCard
          title="کل سفارش‌ها"
          value={stats?.total_orders ?? 0}
          icon={<BarChart3 className="w-6 h-6 text-gray-500" />}
          color="bg-gray-50 border-gray-200"
        />
      </div>

      {/* Performance */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">📊 عملکرد</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted">میانگین زمان چاپ</p>
            <p className="text-xl font-bold">
              {stats?.avg_print_time_hours != null ? `${stats.avg_print_time_hours} ساعت` : "بدون داده"}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted">میانگین زمان ارسال</p>
            <p className="text-xl font-bold">
              {stats?.avg_ship_time_hours != null ? `${stats.avg_ship_time_hours} ساعت` : "بدون داده"}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted">انطباق SLA</p>
            <p className="text-xl font-bold">
              {stats?.sla_compliance_percent != null ? `${stats.sla_compliance_percent}%` : "بدون داده"}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/printshop/orders"
          className="flex items-center gap-3 p-4 bg-surface border border-border rounded-xl hover:bg-accent transition-colors"
        >
          <Clock className="w-8 h-8 text-primary" />
          <div>
            <p className="font-semibold">صف سفارش‌ها</p>
            <p className="text-sm text-muted">مشاهده و قبول سفارش‌های جدید</p>
          </div>
          <ArrowLeft className="w-5 h-5 mr-auto text-muted" />
        </Link>
        <Link
          href="/printshop/my-orders"
          className="flex items-center gap-3 p-4 bg-surface border border-border rounded-xl hover:bg-accent transition-colors"
        >
          <Package className="w-8 h-8 text-primary" />
          <div>
            <p className="font-semibold">سفارش‌های من</p>
            <p className="text-sm text-muted">مدیریت سفارش‌های قبول شده</p>
          </div>
          <ArrowLeft className="w-5 h-5 mr-auto text-muted" />
        </Link>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <div className={`p-4 rounded-xl border ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        {icon}
      </div>
    </div>
  );
}
