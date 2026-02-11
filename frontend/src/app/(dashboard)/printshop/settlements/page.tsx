"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { DollarSign, CheckCircle, Clock, RefreshCw } from "lucide-react";

export default function PrintShopSettlementsPage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["printshopSettlements"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopSettlements({ page: 1, page_size: 50 });
      return response.data;
    },
  });

  const settlements = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">💰 تسویه‌حساب</h1>
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
      ) : settlements.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg">هنوز تسویه‌حسابی ثبت نشده</p>
        </div>
      ) : (
        <div className="space-y-4">
          {settlements.map((s: Record<string, unknown>) => (
            <div key={s.id as string} className="bg-surface border border-border rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      📅 {s.period_start as string} تا {s.period_end as string}
                    </span>
                    <span
                      className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                        s.status === "PAID"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {s.status === "PAID" ? (
                        <>
                          <CheckCircle className="w-3 h-3" /> پرداخت شده
                        </>
                      ) : (
                        <>
                          <Clock className="w-3 h-3" /> در انتظار
                        </>
                      )}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted">سفارش‌ها</p>
                      <p className="font-bold">{s.total_orders as number}</p>
                    </div>
                    <div>
                      <p className="text-muted">درآمد کل</p>
                      <p className="font-bold">
                        {Number(s.total_revenue).toLocaleString("fa-IR")} تومان
                      </p>
                    </div>
                    <div>
                      <p className="text-muted">کمیسیون (۱۰٪)</p>
                      <p className="font-bold text-red-600">
                        {Number(s.platform_commission).toLocaleString("fa-IR")} تومان
                      </p>
                    </div>
                    <div>
                      <p className="text-muted">خالص دریافتی</p>
                      <p className="font-bold text-green-600">
                        {Number(s.net_amount).toLocaleString("fa-IR")} تومان
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
