"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  PageLoading,
} from "@/components/ui";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Users,
  Package,
  DollarSign,
  Calendar,
  Download,
} from "lucide-react";
import { formatPrice, toPersianNumber } from "@/lib/utils";

export default function ReportsPage() {
  const router = useRouter();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  const { data: stats } = useQuery({
    queryKey: ["adminStats"],
    queryFn: async () => {
      const response = await adminApi.getStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: orderStats } = useQuery({
    queryKey: ["adminOrderStats"],
    queryFn: async () => {
      const response = await adminApi.getOrderStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: revenueStats } = useQuery({
    queryKey: ["adminRevenueStats"],
    queryFn: async () => {
      const response = await adminApi.getRevenueStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  const { data: userStats } = useQuery({
    queryKey: ["adminUserStats"],
    queryFn: async () => {
      const response = await adminApi.getUserStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const revenueChange = revenueStats 
    ? ((revenueStats.this_month - revenueStats.last_month) / (revenueStats.last_month || 1)) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/admin"
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-foreground">گزارشات</h1>
            <p className="text-muted mt-1">آمار و گزارشات تحلیلی پلتفرم</p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          leftIcon={<Download className="w-4 h-4" />}
        >
          دانلود گزارش
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                <Package className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted">سفارشات این هفته</p>
                <p className="text-2xl font-bold">{toPersianNumber(stats?.orders_this_week ?? 0)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-success-light flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted">درآمد این ماه</p>
                <p className="text-xl font-bold">{formatPrice(revenueStats?.this_month ?? 0)}</p>
                <div className={`flex items-center gap-1 text-xs ${revenueChange >= 0 ? "text-success" : "text-danger"}`}>
                  {revenueChange >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {toPersianNumber(Math.abs(revenueChange).toFixed(1))}% نسبت به ماه قبل
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-info-light flex items-center justify-center">
                <Users className="w-6 h-6 text-info" />
              </div>
              <div>
                <p className="text-sm text-muted">کاربران جدید امروز</p>
                <p className="text-2xl font-bold">{toPersianNumber(stats?.new_users_today ?? 0)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-warning-light flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-warning" />
              </div>
              <div>
                <p className="text-sm text-muted">نرخ تبدیل</p>
                <p className="text-2xl font-bold">
                  {toPersianNumber(((stats?.total_orders ?? 0) / (stats?.active_users || 1) * 100).toFixed(1))}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Orders by Status */}
        <Card>
          <CardHeader>
            <CardTitle>توزیع وضعیت سفارشات</CardTitle>
          </CardHeader>
          <CardContent>
            {orderStats?.by_status ? (
              <div className="space-y-4">
                {Object.entries(orderStats.by_status).map(([status, count]: [string, any]) => {
                  const total = orderStats.total || 1;
                  const percentage = (count / total) * 100;
                  const statusLabels: Record<string, { label: string; color: string }> = {
                    PENDING: { label: "در انتظار", color: "bg-warning" },
                    AWAITING_VALIDATION: { label: "اعتبارسنجی", color: "bg-info" },
                    DESIGNING: { label: "در حال طراحی", color: "bg-primary" },
                    READY_FOR_PRINT: { label: "آماده چاپ", color: "bg-success" },
                    PRINTING: { label: "در حال چاپ", color: "bg-primary" },
                    SHIPPED: { label: "ارسال شده", color: "bg-info" },
                    DELIVERED: { label: "تحویل شده", color: "bg-success" },
                    CANCELLED: { label: "لغو شده", color: "bg-muted" },
                  };
                  const info = statusLabels[status] ?? { label: status, color: "bg-accent" };
                  
                  return (
                    <div key={status} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>{info.label}</span>
                        <span className="font-medium">{toPersianNumber(count)} ({toPersianNumber(percentage.toFixed(1))}%)</span>
                      </div>
                      <div className="h-2 bg-accent rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${info.color} rounded-full transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted">
                داده‌ای موجود نیست
              </div>
            )}
          </CardContent>
        </Card>

        {/* Users by Role */}
        <Card>
          <CardHeader>
            <CardTitle>توزیع کاربران بر اساس نقش</CardTitle>
          </CardHeader>
          <CardContent>
            {userStats?.by_role ? (
              <div className="space-y-4">
                {Object.entries(userStats.by_role).map(([role, count]: [string, any]) => {
                  const total = Object.values(userStats.by_role).reduce((a: any, b: any) => a + b, 0) as number || 1;
                  const percentage = (count / total) * 100;
                  const roleLabels: Record<string, { label: string; color: string }> = {
                    CUSTOMER: { label: "مشتری", color: "bg-accent" },
                    ADMIN: { label: "مدیر", color: "bg-danger" },
                    DESIGNER: { label: "طراح", color: "bg-primary" },
                    VALIDATOR: { label: "اعتبارسنج", color: "bg-warning" },
                    PRINT_SHOP: { label: "چاپخانه", color: "bg-success" },
                  };
                  const info = roleLabels[role] ?? { label: role, color: "bg-accent" };
                  
                  return (
                    <div key={role} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>{info.label}</span>
                        <span className="font-medium">{toPersianNumber(count)} ({toPersianNumber(percentage.toFixed(1))}%)</span>
                      </div>
                      <div className="h-2 bg-accent rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${info.color} rounded-full transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted">
                داده‌ای موجود نیست
              </div>
            )}
          </CardContent>
        </Card>

        {/* Daily Signups */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              ثبت‌نام کاربران جدید (۷ روز اخیر)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {userStats?.daily_signups ? (
              <div className="flex items-end gap-2 h-48">
                {userStats.daily_signups.map((day: any, index: number) => {
                  const maxCount = Math.max(...userStats.daily_signups.map((d: any) => d.count), 1);
                  const height = (day.count / maxCount) * 100;
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div className="w-full bg-accent rounded-t-lg flex items-end justify-center" style={{ height: "150px" }}>
                        <div 
                          className="w-full bg-primary rounded-t-lg transition-all hover:bg-primary/80"
                          style={{ height: `${Math.max(height, 5)}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted">
                        {new Date(day.date).toLocaleDateString("fa-IR", { weekday: "short" })}
                      </span>
                      <span className="text-xs font-medium">{toPersianNumber(day.count)}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted">
                داده‌ای موجود نیست
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

