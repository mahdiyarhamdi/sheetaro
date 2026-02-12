"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import {
  formatPrice,
  formatDateTime,
  getPaymentStatusInfo,
  toPersianNumber,
} from "@/lib/utils";
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
  Tag,
  FileText,
  CreditCard,
  MessageSquare,
  ShieldCheck,
  Calendar,
  Layers,
} from "lucide-react";
import { ImagePreview } from "@/components/ui/image-preview";

/** Enriched print shop order detail */
interface PrintShopOrderDetail {
  id: string;
  user_id: string;
  category_id?: string;
  quantity: number;
  total_price: number;
  base_price: number;
  attributes_price: number;
  design_price: number;
  print_price: number;
  validation_price: number;
  fix_price: number;
  status: string;
  design_plan: string;
  design_plan_label?: string;
  design_file_url?: string;
  design_preview_url?: string;
  design_final_url?: string;
  customer_name?: string;
  customer_phone?: string;
  customer_city?: string;
  customer_address?: string;
  category_name?: string;
  category_icon?: string;
  template_name?: string;
  admin_notes?: string;
  customer_notes?: string;
  payment_status?: string;
  payment_paid_at?: string;
  tracking_code?: string;
  shipping_address?: string;
  enriched_attributes?: Array<{ attribute_name: string; value_name: string; price: number }>;
  created_at: string;
  accepted_at?: string;
  printed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
}

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

  const { data: order, isLoading } = useQuery<PrintShopOrderDetail>({
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
  const payInfo = getPaymentStatusInfo(order.payment_status);
  const enrichedAttrs = order.enriched_attributes || [];

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/printshop/my-orders"
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-xl font-bold">جزئیات سفارش #{orderId.slice(0, 8)}</h1>
            <p className="text-sm text-muted">{formatDateTime(order.created_at)}</p>
          </div>
        </div>
        {/* Payment status badge in header */}
        {order.payment_status && (
          <span className={`px-3 py-1 text-sm rounded-full ${payInfo.color}`}>
            {payInfo.label}
          </span>
        )}
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

      {/* Product Info Card */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
          <Tag className="w-4 h-4" />
          اطلاعات محصول
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {order.category_name && (
            <InfoRow
              icon={<span className="text-base">{order.category_icon || "📦"}</span>}
              label="دسته‌بندی"
              value={order.category_name}
            />
          )}
          {order.design_plan_label && (
            <InfoRow icon={<Layers className="w-4 h-4" />} label="نوع طراحی" value={order.design_plan_label} />
          )}
          {order.template_name && (
            <InfoRow icon={<FileText className="w-4 h-4" />} label="قالب" value={order.template_name} />
          )}
          <InfoRow icon={<Calendar className="w-4 h-4" />} label="تاریخ ثبت" value={formatDateTime(order.created_at)} />
        </div>
      </div>

      {/* Print Specifications Card */}
      {(enrichedAttrs.length > 0 || order.quantity > 0) && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
            <Printer className="w-4 h-4" />
            مشخصات چاپ
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <InfoRow icon={<Package className="w-4 h-4" />} label="تعداد" value={`${toPersianNumber(order.quantity)} عدد`} />
            {enrichedAttrs.map((attr, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-muted">•</span>
                <span className="text-muted">{attr.attribute_name}:</span>
                <span className="font-medium">{attr.value_name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Price Breakdown Card */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
          <CreditCard className="w-4 h-4" />
          جزئیات قیمت
        </h2>
        <div className="space-y-2">
          {Number(order.base_price) > 0 && (
            <PriceRow label="قیمت پایه" price={order.base_price} />
          )}
          {Number(order.attributes_price) > 0 && (
            <PriceRow label="هزینه ویژگی‌ها" price={order.attributes_price} />
          )}
          {Number(order.design_price) > 0 && (
            <PriceRow label="هزینه طراحی" price={order.design_price} />
          )}
          {Number(order.print_price) > 0 && (
            <PriceRow label="هزینه چاپ" price={order.print_price} />
          )}
          {Number(order.validation_price) > 0 && (
            <PriceRow label="هزینه اعتبارسنجی" price={order.validation_price} />
          )}
          <div className="border-t border-border pt-2 mt-2 flex items-center justify-between font-bold text-base">
            <span>مبلغ کل</span>
            <span className="text-primary">{formatPrice(order.total_price)}</span>
          </div>
        </div>
      </div>

      {/* Payment Status Card */}
      {order.payment_status && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            وضعیت پرداخت
          </h2>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 text-sm rounded-full ${payInfo.color}`}>
              {payInfo.label}
            </span>
            {order.payment_paid_at && (
              <span className="text-sm text-muted">
                تاریخ تایید: {formatDateTime(order.payment_paid_at)}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Design Preview */}
      {(order.design_preview_url || order.design_final_url || order.design_file_url) && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
            <ImageIcon className="w-4 h-4" />
            پیش‌نمایش طرح
          </h2>
          <div className="max-w-md mx-auto">
            <ImagePreview
              src={(order.design_preview_url || order.design_final_url || order.design_file_url)!}
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

      {/* Notes Section */}
      {(order.customer_notes || order.admin_notes) && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-sm font-semibold text-muted mb-4 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            یادداشت‌ها
          </h2>
          <div className="space-y-3">
            {order.customer_notes && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-xs font-medium text-blue-600 mb-1">یادداشت مشتری</p>
                <p className="text-sm whitespace-pre-wrap">{order.customer_notes}</p>
              </div>
            )}
            {order.admin_notes && (
              <div className="p-3 bg-orange-50 rounded-lg">
                <p className="text-xs font-medium text-orange-600 mb-1 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  یادداشت مدیریت
                </p>
                <p className="text-sm whitespace-pre-wrap">{order.admin_notes}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Order Timestamps */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-muted mb-4">زمان‌بندی سفارش</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <InfoRow icon={<Calendar className="w-4 h-4" />} label="ثبت سفارش" value={formatDateTime(order.created_at)} />
          {order.accepted_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="قبول سفارش" value={formatDateTime(order.accepted_at)} />
          )}
          {order.printed_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="اتمام چاپ" value={formatDateTime(order.printed_at)} />
          )}
          {order.shipped_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="ارسال" value={formatDateTime(order.shipped_at)} />
          )}
          {order.delivered_at && (
            <InfoRow icon={<Clock className="w-4 h-4" />} label="تحویل" value={formatDateTime(order.delivered_at)} />
          )}
          {order.tracking_code && (
            <InfoRow icon={<Truck className="w-4 h-4" />} label="کد رهگیری" value={order.tracking_code} />
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

function PriceRow({ label, price }: { label: string; price: number }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted">{label}</span>
      <span>{formatPrice(price)}</span>
    </div>
  );
}
