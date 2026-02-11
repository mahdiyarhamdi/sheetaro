"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Factory, BarChart3, Package, Users, RefreshCw } from "lucide-react";

export default function AdminPrintShopsPage() {
  const { isAdmin } = useAuth();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["adminPrintshops"],
    queryFn: async () => {
      const response = await adminApi.getAdminPrintshops({ page: 1, page_size: 100 });
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: slaReport } = useQuery({
    queryKey: ["adminSlaReport"],
    queryFn: async () => {
      const response = await adminApi.getPrintshopSlaReport();
      return response.data;
    },
    enabled: isAdmin,
  });

  const printshops = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">🏭 مدیریت چاپخانه‌ها</h1>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </button>
      </div>

      {/* SLA Overview */}
      {slaReport && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-3">📊 نمای کلی</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{slaReport.queue_size ?? 0}</p>
              <p className="text-sm text-muted">صف انتظار</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{printshops.length}</p>
              <p className="text-sm text-muted">چاپخانه فعال</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {slaReport.printshops?.length ?? 0}
              </p>
              <p className="text-sm text-muted">چاپخانه‌ها با SLA</p>
            </div>
          </div>
        </div>
      )}

      {/* Print Shops List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : printshops.length === 0 ? (
        <div className="text-center py-12 text-muted">
          <Factory className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg">هیچ چاپخانه‌ای ثبت نشده</p>
          <p className="text-sm mt-1">کاربران با نقش PRINT_SHOP اینجا نمایش داده می‌شوند</p>
        </div>
      ) : (
        <div className="space-y-3">
          {printshops.map((ps: Record<string, unknown>) => {
            const slaInfo = slaReport?.printshops?.find(
              (p: Record<string, unknown>) => p.printshop_id === ps.id
            );

            return (
              <Link
                key={ps.id as string}
                href={`/admin/printshops/${ps.id}`}
                className="block bg-surface border border-border rounded-xl p-4 hover:bg-accent transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Factory className="w-5 h-5 text-primary" />
                      <span className="font-semibold">
                        {ps.first_name as string} {ps.last_name as string || ""}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          ps.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                        }`}
                      >
                        {ps.is_active ? "فعال" : "غیرفعال"}
                      </span>
                    </div>
                    <p className="text-sm text-muted">
                      {ps.phone_number as string || "بدون شماره"} · {ps.city as string || "بدون شهر"}
                    </p>
                  </div>
                  <div className="text-left text-sm">
                    {slaInfo && (
                      <>
                        <p>
                          سفارش‌ها: <span className="font-bold">{slaInfo.total_orders}</span>
                        </p>
                        <p>
                          SLA:{" "}
                          <span className="font-bold">
                            {slaInfo.sla_compliance_percent != null
                              ? `${slaInfo.sla_compliance_percent}%`
                              : "-"}
                          </span>
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
