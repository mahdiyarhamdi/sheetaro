"use client";

import { useEffect } from "react";
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
  ArrowLeft,
  FolderOpen,
  DollarSign,
} from "lucide-react";
import { formatPrice, toPersianNumber } from "@/lib/utils";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { user, isLoadingUser, isAdmin } = useAuth();

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isLoadingUser, isAdmin, router]);

  const { data: stats, isLoading: isLoadingStats } = useQuery({
    queryKey: ["adminStats"],
    queryFn: async () => {
      const response = await adminApi.getStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  if (isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const statCards = [
    {
      title: "کل سفارشات",
      value: stats?.total_orders ?? 0,
      icon: Package,
      color: "bg-primary-50 text-primary",
      iconColor: "text-primary",
    },
    {
      title: "پرداخت‌های در انتظار",
      value: stats?.pending_payments ?? 0,
      icon: CreditCard,
      color: "bg-warning-light text-warning",
      iconColor: "text-warning",
      href: "/admin/payments",
    },
    {
      title: "درآمد کل",
      value: formatPrice(stats?.total_revenue ?? 0),
      icon: DollarSign,
      color: "bg-success-light text-success",
      iconColor: "text-success",
      isPrice: true,
    },
    {
      title: "کاربران جدید امروز",
      value: stats?.new_users_today ?? 0,
      icon: Users,
      color: "bg-info-light text-info",
      iconColor: "text-info",
    },
  ];

  const quickActions = [
    {
      title: "پرداخت‌های در انتظار",
      description: "بررسی و تأیید رسیدهای پرداخت",
      icon: CreditCard,
      href: "/admin/payments",
      badge: stats?.pending_payments,
    },
    {
      title: "مدیریت کاتالوگ",
      description: "دسته‌بندی‌ها، ویژگی‌ها و پلن‌ها",
      icon: FolderOpen,
      href: "/admin/catalog",
    },
    {
      title: "کاربران",
      description: "مدیریت کاربران سیستم",
      icon: Users,
      href: "/admin/users",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">پنل مدیریت</h1>
        <p className="text-muted mt-1">
          سلام {user?.full_name || "مدیر"}! خلاصه وضعیت سیستم را ببینید
        </p>
      </div>

      {/* Stats */}
      {isLoadingStats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-4">
                <div className="h-16 bg-accent rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((stat, index) => (
            <Card key={index} className={stat.href ? "hover:border-primary/30 transition-colors" : ""}>
              {stat.href ? (
                <Link href={stat.href}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted">{stat.title}</p>
                        <p className="text-2xl font-bold text-foreground mt-1">
                          {stat.isPrice ? stat.value : toPersianNumber(stat.value)}
                        </p>
                      </div>
                      <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
                        <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
                      </div>
                    </div>
                  </CardContent>
                </Link>
              ) : (
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted">{stat.title}</p>
                      <p className="text-2xl font-bold text-foreground mt-1">
                        {stat.isPrice ? stat.value : toPersianNumber(stat.value)}
                      </p>
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

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>دسترسی سریع</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {quickActions.map((action, index) => (
              <Link key={index} href={action.href}>
                <div className="flex items-center gap-4 p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-accent/50 transition-all">
                  <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
                    <action.icon className="w-6 h-6 text-primary" />
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
    </div>
  );
}

