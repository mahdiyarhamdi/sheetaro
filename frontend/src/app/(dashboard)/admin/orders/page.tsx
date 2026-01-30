"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  PageLoading,
  Input,
} from "@/components/ui";
import {
  Package,
  Search,
  ArrowRight,
  Clock,
  CheckCircle,
  XCircle,
  Truck,
  Printer,
  Palette,
  Eye,
  MoreVertical,
  ChevronDown,
  Filter,
  User,
  Calendar,
  RefreshCw,
} from "lucide-react";
import toast from "react-hot-toast";
import { toPersianNumber, formatPrice, formatDate } from "@/lib/utils";

const ORDER_STATUSES = [
  { value: "PENDING", label: "در انتظار", color: "bg-warning-light text-warning", icon: Clock },
  { value: "AWAITING_VALIDATION", label: "در حال اعتبارسنجی", color: "bg-info-light text-info", icon: Eye },
  { value: "NEEDS_ACTION", label: "نیاز به اقدام", color: "bg-danger-light text-danger", icon: XCircle },
  { value: "DESIGNING", label: "در حال طراحی", color: "bg-primary-50 text-primary", icon: Palette },
  { value: "READY_FOR_PRINT", label: "آماده چاپ", color: "bg-success-light text-success", icon: CheckCircle },
  { value: "PRINTING", label: "در حال چاپ", color: "bg-primary-50 text-primary", icon: Printer },
  { value: "SHIPPED", label: "ارسال شده", color: "bg-info-light text-info", icon: Truck },
  { value: "DELIVERED", label: "تحویل شده", color: "bg-success-light text-success", icon: CheckCircle },
  { value: "CANCELLED", label: "لغو شده", color: "bg-muted/20 text-muted", icon: XCircle },
];

export default function OrdersManagementPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [showStatusMenu, setShowStatusMenu] = useState<string | null>(null);

  // Wait for initial auth check
  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Redirect non-admin users
  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  // Fetch orders
  const { data: ordersData, isLoading: isLoadingOrders, refetch } = useQuery({
    queryKey: ["adminOrders", statusFilter, page],
    queryFn: async () => {
      const response = await adminApi.getOrders({ 
        status: statusFilter || undefined,
        page,
        page_size: 20,
      });
      return response.data;
    },
    enabled: isAdmin,
  });

  // Fetch order stats
  const { data: orderStats } = useQuery({
    queryKey: ["adminOrderStats"],
    queryFn: async () => {
      const response = await adminApi.getOrderStats();
      return response.data;
    },
    enabled: isAdmin,
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }: { orderId: string; status: string }) =>
      adminApi.updateOrderStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminOrders"] });
      queryClient.invalidateQueries({ queryKey: ["adminOrderStats"] });
      toast.success("وضعیت سفارش به‌روزرسانی شد");
      setShowStatusMenu(null);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const orders = ordersData?.items ?? [];
  const totalOrders = ordersData?.total ?? 0;
  const totalPages = Math.ceil(totalOrders / 20);

  const getStatusInfo = (status: string) => {
    return ORDER_STATUSES.find(s => s.value === status) ?? ORDER_STATUSES[0];
  };

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
            <h1 className="text-2xl font-bold text-foreground">مدیریت سفارشات</h1>
            <p className="text-muted mt-1">
              {toPersianNumber(totalOrders)} سفارش
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          leftIcon={<RefreshCw className="w-4 h-4" />}
        >
          به‌روزرسانی
        </Button>
      </div>

      {/* Stats Cards */}
      {orderStats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4">
          {ORDER_STATUSES.slice(0, 5).map((status) => {
            const count = orderStats.by_status?.[status.value] ?? 0;
            return (
              <Card 
                key={status.value}
                className={`cursor-pointer transition-all ${
                  statusFilter === status.value ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => {
                  setStatusFilter(statusFilter === status.value ? null : status.value);
                  setPage(1);
                }}
              >
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted">{status.label}</p>
                      <p className="text-xl font-bold">{toPersianNumber(count)}</p>
                    </div>
                    <div className={`w-10 h-10 rounded-lg ${status.color} flex items-center justify-center`}>
                      <status.icon className="w-5 h-5" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Status Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => {
            setStatusFilter(null);
            setPage(1);
          }}
          className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            !statusFilter ? "bg-primary text-white" : "bg-accent hover:bg-accent/80"
          }`}
        >
          همه
        </button>
        {ORDER_STATUSES.map((status) => (
          <button
            key={status.value}
            onClick={() => {
              setStatusFilter(status.value);
              setPage(1);
            }}
            className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === status.value ? "bg-primary text-white" : "bg-accent hover:bg-accent/80"
            }`}
          >
            <status.icon className="w-4 h-4" />
            {status.label}
          </button>
        ))}
      </div>

      {/* Orders List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            لیست سفارشات
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingOrders ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-20 bg-accent rounded-lg animate-pulse" />
              ))}
            </div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12 text-muted">
              <Package className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">سفارشی یافت نشد</p>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map((order: any) => {
                const statusInfo = getStatusInfo(order.status);
                return (
                  <div
                    key={order.id}
                    className="flex items-center justify-between p-4 rounded-xl border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${statusInfo.color}`}>
                        <statusInfo.icon className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-foreground">
                            سفارش #{order.id.slice(0, 8)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-muted mt-1">
                          <span className="flex items-center gap-1">
                            <User className="w-3.5 h-3.5" />
                            {order.user_id?.slice(0, 8)}...
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {formatDate(order.created_at)}
                          </span>
                          <span className="font-medium text-foreground">
                            {formatPrice(order.total_price)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {/* Status dropdown */}
                      <div className="relative">
                        <button
                          onClick={() => setShowStatusMenu(showStatusMenu === order.id ? null : order.id)}
                          className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${statusInfo.color}`}
                        >
                          {statusInfo.label}
                          <ChevronDown className="w-3 h-3" />
                        </button>
                        {showStatusMenu === order.id && (
                          <div className="absolute left-0 mt-2 w-48 bg-surface border border-border rounded-xl shadow-lg z-10 max-h-64 overflow-y-auto">
                            {ORDER_STATUSES.map((status) => (
                              <button
                                key={status.value}
                                onClick={() => updateStatusMutation.mutate({ orderId: order.id, status: status.value })}
                                className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors first:rounded-t-xl last:rounded-b-xl ${
                                  order.status === status.value ? "bg-accent" : ""
                                }`}
                              >
                                <status.icon className="w-4 h-4" />
                                {status.label}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      {/* View button */}
                      <Link href={`/orders/${order.id}`}>
                        <button className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground">
                          <Eye className="w-5 h-5" />
                        </button>
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                قبلی
              </Button>
              <span className="text-sm text-muted">
                صفحه {toPersianNumber(page)} از {toPersianNumber(totalPages)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                بعدی
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

