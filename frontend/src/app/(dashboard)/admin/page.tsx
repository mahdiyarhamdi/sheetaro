"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
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
  CreditCard,
  Users,
  Package,
  TrendingUp,
  TrendingDown,
  ArrowLeft,
  FolderOpen,
  DollarSign,
  Clock,
  CheckCircle,
  Activity,
  Calendar,
  Settings,
} from "lucide-react";
import { formatPrice, toPersianNumber } from "@/lib/utils";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);

  // Wait for initial auth check before deciding to redirect
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsChecked(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Redirect non-admin users only after initial check
  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  const { data: stats, isLoading: isLoadingStats } = useQuery({
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

  // Show loading until checked and confirmed admin
  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const statCards = [
    {
      title: "کل سفارشات",
      value: stats?.total_orders ?? 0,
      subValue: `${toPersianNumber(stats?.orders_today ?? 0)} سفارش امروز`,
      icon: Package,
      color: "bg-primary-50 text-primary",
      iconColor: "text-primary",
      href: "/admin/orders",
    },
    {
      title: "پرداخت‌های در انتظار",
      value: stats?.pending_payments ?? 0,
      subValue: "نیاز به بررسی",
      icon: CreditCard,
      color: "bg-warning-light text-warning",
      iconColor: "text-warning",
      href: "/admin/payments",
      alert: (stats?.pending_payments ?? 0) > 0,
    },
    {
      title: "درآمد کل",
      value: formatPrice(stats?.total_revenue ?? 0),
      subValue: revenueStats ? `${formatPrice(revenueStats.this_month)} این ماه` : "",
      icon: DollarSign,
      color: "bg-success-light text-success",
      iconColor: "text-success",
      isPrice: true,
    },
    {
      title: "کاربران فعال",
      value: stats?.active_users ?? 0,
      subValue: `${toPersianNumber(stats?.new_users_today ?? 0)} کاربر جدید امروز`,
      icon: Users,
      color: "bg-info-light text-info",
      iconColor: "text-info",
      href: "/admin/users",
    },
  ];

  const quickActions = [
    {
      title: "پرداخت‌های در انتظار",
      description: "بررسی و تأیید رسیدهای پرداخت",
      icon: CreditCard,
      href: "/admin/payments",
      badge: stats?.pending_payments,
      color: "bg-warning-light",
      iconColor: "text-warning",
    },
    {
      title: "سفارشات",
      description: "مدیریت و پیگیری سفارشات",
      icon: Package,
      href: "/admin/orders",
      badge: stats?.pending_orders,
      color: "bg-primary-50",
      iconColor: "text-primary",
    },
    {
      title: "مدیریت کاتالوگ",
      description: "دسته‌بندی‌ها، محصولات و پلن‌ها",
      icon: FolderOpen,
      href: "/admin/catalog",
      color: "bg-info-light",
      iconColor: "text-info",
    },
    {
      title: "کاربران",
      description: "مدیریت کاربران سیستم",
      icon: Users,
      href: "/admin/users",
      color: "bg-success-light",
      iconColor: "text-success",
    },
    {
      title: "گزارشات",
      description: "آمار و گزارشات تحلیلی",
      icon: BarChart3,
      href: "/admin/reports",
      color: "bg-primary-50",
      iconColor: "text-primary",
    },
    {
      title: "تنظیمات",
      description: "تنظیمات پلتفرم و سیستم",
      icon: Settings,
      href: "/admin/settings",
      color: "bg-muted/20",
      iconColor: "text-muted",
    },
  ];

  // Calculate max for chart
  const maxOrderCount = Math.max(...(orderStats?.by_day?.map((d: any) => d.count) ?? [1]), 1);
  const maxRevenueAmount = Math.max(...(revenueStats?.by_day?.map((d: any) => d.amount) ?? [1]), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">پنل مدیریت</h1>
          <p className="text-muted mt-1">
            سلام {user?.full_name || "مدیر"}! خلاصه وضعیت سیستم را ببینید
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted">
          <Calendar className="w-4 h-4" />
          {new Date().toLocaleDateString("fa-IR", { 
            weekday: "long", 
            year: "numeric", 
            month: "long", 
            day: "numeric" 
          })}
        </div>
      </div>

      {/* Stats */}
      {isLoadingStats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-4">
                <div className="h-20 bg-accent rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((stat, index) => (
            <Card 
              key={index} 
              className={`transition-all ${stat.href ? "hover:border-primary/30 cursor-pointer" : ""} ${stat.alert ? "ring-2 ring-warning" : ""}`}
            >
              {stat.href ? (
                <Link href={stat.href}>
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-muted">{stat.title}</p>
                        <p className="text-2xl font-bold text-foreground mt-1">
                          {stat.isPrice ? stat.value : toPersianNumber(stat.value)}
                        </p>
                        {stat.subValue && (
                          <p className="text-xs text-muted mt-1">{stat.subValue}</p>
                        )}
                      </div>
                      <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
                        <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
                      </div>
                    </div>
                  </CardContent>
                </Link>
              ) : (
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-muted">{stat.title}</p>
                      <p className="text-2xl font-bold text-foreground mt-1">
                        {stat.isPrice ? stat.value : toPersianNumber(stat.value)}
                      </p>
                      {stat.subValue && (
                        <p className="text-xs text-muted mt-1">{stat.subValue}</p>
                      )}
                    </div>
                    <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
                      <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Orders Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              سفارشات ۷ روز اخیر
            </CardTitle>
          </CardHeader>
          <CardContent>
            {orderStats?.by_day ? (
              <div className="space-y-3">
                {orderStats.by_day.map((day: any, index: number) => {
                  const percentage = (day.count / maxOrderCount) * 100;
                  return (
                    <div key={index} className="flex items-center gap-3">
                      <span className="text-xs text-muted w-16 shrink-0">
                        {new Date(day.date).toLocaleDateString("fa-IR", { weekday: "short" })}
                      </span>
                      <div className="flex-1 h-6 bg-accent rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full transition-all"
                          style={{ width: `${Math.max(percentage, 2)}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-8 text-left">
                        {toPersianNumber(day.count)}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted">
                در حال بارگذاری...
              </div>
            )}
          </CardContent>
        </Card>

        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                درآمد ۷ روز اخیر
              </CardTitle>
              {revenueStats && (
                <div className="text-left">
                  <p className="text-xs text-muted">این ماه</p>
                  <p className="text-sm font-bold text-success">{formatPrice(revenueStats.this_month)}</p>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {revenueStats?.by_day ? (
              <div className="space-y-3">
                {revenueStats.by_day.map((day: any, index: number) => {
                  const percentage = (day.amount / maxRevenueAmount) * 100;
                  return (
                    <div key={index} className="flex items-center gap-3">
                      <span className="text-xs text-muted w-16 shrink-0">
                        {new Date(day.date).toLocaleDateString("fa-IR", { weekday: "short" })}
                      </span>
                      <div className="flex-1 h-6 bg-accent rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-success rounded-full transition-all"
                          style={{ width: `${Math.max(percentage, 2)}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium w-20 text-left truncate">
                        {formatPrice(day.amount)}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted">
                در حال بارگذاری...
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>دسترسی سریع</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action, index) => (
              <Link key={index} href={action.href}>
                <div className="flex items-center gap-4 p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-accent/50 transition-all">
                  <div className={`w-12 h-12 rounded-xl ${action.color} flex items-center justify-center shrink-0`}>
                    <action.icon className={`w-6 h-6 ${action.iconColor}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-foreground">{action.title}</p>
                      {action.badge && action.badge > 0 && (
                        <span className="px-2 py-0.5 bg-warning text-white text-xs rounded-full">
                          {toPersianNumber(action.badge)}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted truncate">{action.description}</p>
                  </div>
                  <ArrowLeft className="w-5 h-5 text-muted shrink-0" />
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Order Status Summary */}
      {orderStats?.by_status && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              وضعیت سفارشات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {Object.entries(orderStats.by_status).map(([status, count]: [string, any]) => {
                const statusLabels: Record<string, { label: string; color: string }> = {
                  PENDING: { label: "در انتظار", color: "bg-warning-light text-warning" },
                  AWAITING_VALIDATION: { label: "اعتبارسنجی", color: "bg-info-light text-info" },
                  DESIGNING: { label: "در حال طراحی", color: "bg-primary-50 text-primary" },
                  READY_FOR_PRINT: { label: "آماده چاپ", color: "bg-success-light text-success" },
                  PRINTING: { label: "در حال چاپ", color: "bg-primary-50 text-primary" },
                  SHIPPED: { label: "ارسال شده", color: "bg-info-light text-info" },
                  DELIVERED: { label: "تحویل شده", color: "bg-success-light text-success" },
                  CANCELLED: { label: "لغو شده", color: "bg-muted/20 text-muted" },
                };
                const info = statusLabels[status] ?? { label: status, color: "bg-accent" };
                return (
                  <div key={status} className={`p-4 rounded-xl ${info.color}`}>
                    <p className="text-2xl font-bold">{toPersianNumber(count)}</p>
                    <p className="text-sm opacity-80">{info.label}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
