"use client";

import { useState } from "react";
import Link from "next/link";
import { useOrders } from "@/hooks/useOrders";
import {
  Card,
  CardContent,
  Button,
  Badge,
  EmptyState,
  PageLoading,
  Select,
} from "@/components/ui";
import { Package, Plus, Search, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import { formatPrice, formatDate, orderStatusLabels, toPersianNumber } from "@/lib/utils";

const statusOptions = [
  { value: "", label: "همه وضعیت‌ها" },
  // Payment statuses
  { value: "PENDING_PAYMENT", label: "در انتظار پرداخت" },
  { value: "PAYMENT_UPLOADED", label: "رسید ارسال شده" },
  { value: "PAYMENT_APPROVED", label: "پرداخت تأیید شده" },
  { value: "PAYMENT_REJECTED", label: "پرداخت رد شده" },
  // Order processing statuses
  { value: "AWAITING_VALIDATION", label: "در انتظار اعتبارسنجی" },
  { value: "DESIGNING", label: "در حال طراحی" },
  { value: "READY_FOR_PRINT", label: "آماده چاپ" },
  { value: "PRINTING", label: "در حال چاپ" },
  { value: "SHIPPED", label: "ارسال شده" },
  { value: "DELIVERED", label: "تحویل شده" },
  { value: "CANCELLED", label: "لغو شده" },
];

export default function OrdersPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const pageSize = 10;

  const { orders, total, isLoading, error } = useOrders({
    page,
    pageSize,
    status: statusFilter || undefined,
  });

  const totalPages = Math.ceil(total / pageSize);

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "DELIVERED":
      case "PAYMENT_APPROVED":
        return "success";
      case "PAYMENT_REJECTED":
      case "CANCELLED":
        return "danger";
      case "PENDING_PAYMENT":
      case "PENDING":
      case "NEEDS_ACTION":
        return "warning";
      case "DESIGNING":
      case "READY_FOR_PRINT":
      case "PRINTING":
        return "primary";
      default:
        return "info";
    }
  };

  if (isLoading && page === 1) {
    return <PageLoading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">سفارشات من</h1>
          <p className="text-muted mt-1">
            مشاهده و پیگیری سفارشات شما
          </p>
        </div>
        <Link href="/new-order">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            سفارش جدید
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 max-w-xs">
              <Select
                options={statusOptions}
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                placeholder="فیلتر بر اساس وضعیت"
              />
            </div>
            <div className="text-sm text-muted self-center">
              {total > 0 && (
                <span>
                  نمایش{" "}
                  <strong>
                    {toPersianNumber((page - 1) * pageSize + 1)} -{" "}
                    {toPersianNumber(Math.min(page * pageSize, total))}
                  </strong>{" "}
                  از <strong>{toPersianNumber(total)}</strong> سفارش
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Orders list */}
      {orders.length === 0 ? (
        <EmptyState
          icon={Package}
          title="سفارشی یافت نشد"
          description={
            statusFilter
              ? "سفارشی با این وضعیت یافت نشد"
              : "هنوز سفارشی ثبت نکرده‌اید"
          }
          action={
            statusFilter
              ? {
                  label: "حذف فیلتر",
                  onClick: () => setStatusFilter(""),
                }
              : {
                  label: "ثبت سفارش جدید",
                  onClick: () => (window.location.href = "/new-order"),
                }
          }
        />
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link key={order.id} href={`/orders/${order.id}`}>
              <Card className="hover:border-primary/30 hover:shadow-medium transition-all cursor-pointer">
                <CardContent className="py-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                        <Package className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">
                          {order.category?.name_fa || "سفارش"} -{" "}
                          {order.plan?.name_fa || ""}
                        </p>
                        <p className="text-sm text-muted">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 sm:gap-6">
                      <Badge variant={getStatusBadgeVariant(order.status)}>
                        {orderStatusLabels[order.status] || order.status}
                      </Badge>
                      <div className="text-left">
                        <p className="text-sm text-muted">مبلغ کل</p>
                        <p className="font-semibold text-foreground">
                          {formatPrice(order.total_price)}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>

              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }

                  return (
                    <Button
                      key={pageNum}
                      variant={page === pageNum ? "primary" : "ghost"}
                      size="sm"
                      onClick={() => setPage(pageNum)}
                      className="w-10"
                    >
                      {toPersianNumber(pageNum)}
                    </Button>
                  );
                })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

