"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useOrders } from "@/hooks/useOrders";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  EmptyState,
  CardSkeleton,
} from "@/components/ui";
import {
  ShoppingCart,
  Package,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
  Send,
  Plus,
} from "lucide-react";
import { formatPrice, formatDate, orderStatusLabels, getStatusColor } from "@/lib/utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const { orders, total, isLoading } = useOrders({ pageSize: 5 });

  const stats = {
    total: total,
    pending: orders.filter((o) => o.status === "pending_payment").length,
    inProgress: orders.filter(
      (o) =>
        o.status === "payment_approved" ||
        o.status === "in_progress" ||
        o.status === "payment_uploaded"
    ).length,
    completed: orders.filter((o) => o.status === "completed").length,
  };

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            سلام، {user?.full_name || user?.first_name || "کاربر"}! 👋
          </h1>
          <p className="text-muted mt-1">
            به پنل کاربری شیتارو خوش آمدید
          </p>
        </div>
        <Link href="/new-order">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            سفارش جدید
          </Button>
        </Link>
      </div>

      {/* Telegram link banner */}
      {user && !user.telegram_id && (
        <Card className="bg-gradient-to-l from-primary-50 to-primary-100 border-primary-200">
          <CardContent className="py-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                  <Send className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium text-foreground">
                    حساب تلگرام خود را متصل کنید
                  </p>
                  <p className="text-sm text-muted">
                    با اتصال تلگرام، اطلاع‌رسانی‌ها را سریع‌تر دریافت کنید
                  </p>
                </div>
              </div>
              <Link href="/verify">
                <Button variant="primary" size="sm">
                  اتصال تلگرام
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">کل سفارشات</p>
                <p className="text-2xl font-bold text-foreground mt-1">
                  {stats.total}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                <Package className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">در انتظار پرداخت</p>
                <p className="text-2xl font-bold text-warning mt-1">
                  {stats.pending}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-warning-light flex items-center justify-center">
                <Clock className="w-6 h-6 text-warning" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">در حال انجام</p>
                <p className="text-2xl font-bold text-info mt-1">
                  {stats.inProgress}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-info-light flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-info" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">تکمیل شده</p>
                <p className="text-2xl font-bold text-success mt-1">
                  {stats.completed}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-success-light flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-success" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>سفارشات اخیر</CardTitle>
          <Link href="/orders">
            <Button variant="ghost" size="sm" rightIcon={<ArrowLeft className="w-4 h-4" />}>
              مشاهده همه
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : orders.length === 0 ? (
            <EmptyState
              icon={Package}
              title="سفارشی یافت نشد"
              description="هنوز سفارشی ثبت نکرده‌اید"
              action={{
                label: "ثبت سفارش جدید",
                onClick: () => (window.location.href = "/new-order"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {orders.slice(0, 5).map((order) => (
                <Link
                  key={order.id}
                  href={`/orders/${order.id}`}
                  className="block"
                >
                  <div className="flex items-center justify-between p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-accent/50 transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                        <Package className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">
                          {order.category?.name_fa || "سفارش"}
                        </p>
                        <p className="text-sm text-muted">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge
                        variant={
                          order.status === "completed"
                            ? "success"
                            : order.status === "payment_rejected" ||
                              order.status === "cancelled"
                            ? "danger"
                            : order.status === "pending_payment"
                            ? "warning"
                            : "info"
                        }
                      >
                        {orderStatusLabels[order.status] || order.status}
                      </Badge>
                      <span className="font-medium text-foreground">
                        {formatPrice(order.total_price)}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link href="/new-order">
          <Card className="hover:border-primary/30 hover:shadow-medium transition-all cursor-pointer h-full">
            <CardContent className="pt-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">سفارش جدید</p>
                <p className="text-sm text-muted">
                  ثبت سفارش لیبل یا فاکتور
                </p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/orders">
          <Card className="hover:border-primary/30 hover:shadow-medium transition-all cursor-pointer h-full">
            <CardContent className="pt-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-info-light flex items-center justify-center">
                <Package className="w-6 h-6 text-info" />
              </div>
              <div>
                <p className="font-medium text-foreground">سفارشات من</p>
                <p className="text-sm text-muted">
                  مشاهده و پیگیری سفارشات
                </p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/profile">
          <Card className="hover:border-primary/30 hover:shadow-medium transition-all cursor-pointer h-full">
            <CardContent className="pt-4 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-success-light flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-success" />
              </div>
              <div>
                <p className="font-medium text-foreground">پروفایل</p>
                <p className="text-sm text-muted">
                  مدیریت اطلاعات حساب
                </p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}

