"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import {
  Palette,
  PenTool,
  Upload,
  CheckCircle,
  RefreshCw,
  ArrowLeft,
  Inbox,
} from "lucide-react";
import { toPersianNumber } from "@/lib/utils";

export default function DesignerDashboardPage() {
  const router = useRouter();

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ["designerStats"],
    queryFn: async () => {
      const response = await adminApi.getDesignerStats();
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

  const statCards = [
    {
      label: "صف سفارشات جدید",
      value: stats?.queue_count ?? 0,
      icon: Inbox,
      color: "text-red-600",
      bg: "bg-red-50",
    },
    {
      label: "کل سفارشات من",
      value: stats?.total_assigned ?? 0,
      icon: Palette,
      color: "text-primary",
      bg: "bg-primary-50",
    },
    {
      label: "در حال طراحی",
      value: stats?.in_progress ?? 0,
      icon: PenTool,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "تکمیل شده",
      value: stats?.completed ?? 0,
      icon: CheckCircle,
      color: "text-green-600",
      bg: "bg-green-50",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">پنل طراح</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="bg-surface border border-border rounded-xl p-5"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${card.bg}`}>
                <card.icon className={`w-5 h-5 ${card.color}`} />
              </div>
            </div>
            <p className="text-2xl font-bold text-foreground">
              {toPersianNumber(card.value)}
            </p>
            <p className="text-sm text-muted mt-1">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          href="/designer/queue"
          className="flex items-center justify-between p-4 bg-surface border border-border rounded-xl hover:bg-accent transition-colors"
        >
          <div className="flex items-center gap-3">
            <Inbox className="w-5 h-5 text-red-600" />
            <span className="font-medium">صف سفارشات جدید</span>
          </div>
          {(stats?.queue_count ?? 0) > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
              {toPersianNumber(stats?.queue_count ?? 0)}
            </span>
          )}
        </Link>
        <Link
          href="/designer/orders?status=DESIGNING"
          className="flex items-center justify-between p-4 bg-surface border border-border rounded-xl hover:bg-accent transition-colors"
        >
          <div className="flex items-center gap-3">
            <PenTool className="w-5 h-5 text-primary" />
            <span className="font-medium">سفارشات در حال طراحی</span>
          </div>
          <ArrowLeft className="w-5 h-5 text-muted" />
        </Link>
        <Link
          href="/designer/orders"
          className="flex items-center justify-between p-4 bg-surface border border-border rounded-xl hover:bg-accent transition-colors"
        >
          <div className="flex items-center gap-3">
            <Palette className="w-5 h-5 text-primary" />
            <span className="font-medium">همه سفارشات من</span>
          </div>
          <ArrowLeft className="w-5 h-5 text-muted" />
        </Link>
      </div>
    </div>
  );
}
