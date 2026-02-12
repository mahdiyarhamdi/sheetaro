"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { formatPrice, formatDateTime } from "@/lib/utils";
import Link from "next/link";
import {
  ArrowRight,
  Package,
  User,
  Phone,
  MapPin,
  Truck,
  CheckCircle,
  Printer,
  Clock,
  Hash,
  ImageIcon,
} from "lucide-react";
import { ImagePreview } from "@/components/ui/image-preview";

const STATUS_TIMELINE = [
  { key: "PRINTING", label: "در حال چاپ", icon: Printer },
  { key: "PRINTED", label: "چاپ شده", icon: CheckCircle },
  { key: "SHIPPED", label: "ارسال شده", icon: Truck },
  { key: "DELIVERED", label: "تحویل شده", icon: Package },
];

export default function PrintShopOrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const orderId = params.orderId as string;
  const [trackingCode, setTrackingCode] = useState("");
  const [error, setError] = useState("");

  const { data: order, isLoading } = useQuery({
    queryKey: ["printshopOrder", orderId],
    queryFn: async () => {
      const response = await adminApi.getPrintshopOrderDetail(orderId);
      return response.data;
    },
  });

  const completeMutation = useMutation({
    mutationFn: async () => {
      const response = await adminApi.printshopCompleteOrder(orderId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printshopOrder", orderId] });
      queryClient.invalidateQueries({ queryKey: ["printshopMyOrders"] });
    },
  });

  const shipMutation = useMutation({
    mutationFn: async () => {
      if (trackingCode.length < 5) {
        throw new Error("کد رهگیری باید حداقل ۵ کاراکتر باشد");
      }
      const response = await adminApi.printshopShipOrder(orderId, { tracking_code: trackingCode });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printshopOrder", orderId] });
      queryClient.invalidateQueries({ queryKey: ["printshopMyOrders"] });
      setTrackingCode("");
      setError("");
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="text-center py-12">
        <p className="text-muted">سفارش یافت نشد</p>
        <Link href="/printshop/my-orders" className="text-primary mt-2 inline-block">
          بازگشت به لیست
        </Link>
      </div>
    );
  }

  const currentStatusIndex = STATUS_TIMELINE.findIndex((s) => s.key === order.status);

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link
          href="/printshop/my-orders"
          className="p-2 rounded-lg hover:bg-accent transition-colors"
        >
          <ArrowRight className="w-5 h-5" />
        </Link>
        <h1 className="text-xl font-bold">جزئیات سفارش #{orderId.slice(0, 8)}</h1>
      </div>

      {/* Status Timeline */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4">وضعیت سفارش</h2>
        <div className="flex items-center justify-between">
          {STATUS_TIMELINE.map((step, index) => {
            const isActive = index <= currentStatusIndex;
            const Icon = step.icon;
            return (
              <div key={step.key} className="flex flex-col items-center gap-1 flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isActive ? "bg-primary text-white" : "bg-gray-100 text-gray-400"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <span className={`text-xs ${isActive ? "text-primary font-medium" : "text-muted"}`}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Design Preview */}
      {(order.design_preview_url || order.design_final_url || order.design_file_url) && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
            <ImageIcon className="w-4 h-4" />
            پیش‌نمایش طرح
          </h2>
          <div className="max-w-md mx-auto">
            <ImagePreview
              src={order.design_preview_url || order.design_final_url || order.design_file_url}
              alt="طرح سفارش"
              className="w-full"
              aspectRatio="aspect-auto"
              thumbnailSize={600}
              showDownload={true}
              showExpand={true}
              downloadFilename={`design-order-${orderId.slice(0, 8)}`}
            />
          </div>
        </div>
      )}

      {/* Customer Info */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4">اطلاعات مشتری</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <InfoRow icon={<User className="w-4 h-4" />} label="نام" value={order.customer_name || "ناشناس"} />
          <InfoRow icon={<Phone className="w-4 h-4" />} label="تلفن" value={order.customer_phone || "-"} />
          <InfoRow icon={<MapPin className="w-4 h-4" />} label="شهر" value={order.customer_city || "-"} />
          <InfoRow icon={<MapPin className="w-4 h-4" />} label="آدرس" value={order.shipping_address || order.customer_address || "-"} />
        </div>
      </div>

      {/* Order Info */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4">اطلاعات سفارش</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <InfoRow icon={<Package className="w-4 h-4" />} label="تعداد" value={`${order.quantity} عدد`} />
          <InfoRow icon={<Hash className="w-4 h-4" />} label="مبلغ کل" value={formatPrice(order.total_price)} />
          {order.tracking_code && (
            <InfoRow icon={<Truck className="w-4 h-4" />} label="کد رهگیری" value={order.tracking_code} />
          )}
          {order.accepted_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="زمان قبول" value={new Date(order.accepted_at).toLocaleString("fa-IR")} />
          )}
          {order.printed_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="زمان چاپ" value={new Date(order.printed_at).toLocaleString("fa-IR")} />
          )}
          {order.shipped_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="زمان ارسال" value={new Date(order.shipped_at).toLocaleString("fa-IR")} />
          )}
        </div>
      </div>

      {/* Actions */}
      {order.status === "PRINTING" && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4">عملیات</h2>
          <button
            onClick={() => completeMutation.mutate()}
            disabled={completeMutation.isPending}
            className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-medium"
          >
            {completeMutation.isPending ? "در حال ثبت..." : "✅ چاپ تکمیل شد"}
          </button>
        </div>
      )}

      {order.status === "PRINTED" && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4">ارسال سفارش</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">کد رهگیری پستی</label>
              <input
                type="text"
                value={trackingCode}
                onChange={(e) => setTrackingCode(e.target.value)}
                placeholder="کد رهگیری را وارد کنید..."
                className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button
              onClick={() => shipMutation.mutate()}
              disabled={shipMutation.isPending || trackingCode.length < 5}
              className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 font-medium"
            >
              {shipMutation.isPending ? "در حال ثبت..." : "📮 ارسال سفارش"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-muted">{icon}</span>
      <span className="text-muted">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
