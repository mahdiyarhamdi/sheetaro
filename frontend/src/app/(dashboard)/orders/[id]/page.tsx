"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useOrder } from "@/hooks/useOrders";
import { ImagePreview } from "@/components/ui/image-preview";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { paymentsApi, ordersApi, getErrorMessage } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
  Button,
  Badge,
  PageLoading,
  EmptyState,
  Modal,
} from "@/components/ui";
import {
  Package,
  ArrowRight,
  CreditCard,
  Upload,
  CheckCircle,
  XCircle,
  Clock,
  Copy,
  Check,
  Image as ImageIcon,
  FileText,
  X,
  Truck,
  Star,
  MessageSquare,
  Send,
} from "lucide-react";
import { formatPrice, formatDate, formatDateTime, orderStatusLabels, toPersianNumber, cn } from "@/lib/utils";
import toast from "react-hot-toast";

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const orderId = params.id as string;

  const { data: order, isLoading, error } = useOrder(orderId);

  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Review state
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewHover, setReviewHover] = useState(0);
  const [reviewComment, setReviewComment] = useState("");

  // Fetch review for delivered orders
  const { data: existingReview, refetch: refetchReview } = useQuery({
    queryKey: ["orderReview", orderId],
    queryFn: async () => {
      const res = await ordersApi.getReview(orderId);
      return res.data;
    },
    enabled: !!order && order.status === "DELIVERED",
  });

  // Confirm delivery mutation
  const confirmDeliveryMutation = useMutation({
    mutationFn: async () => {
      return ordersApi.confirmDelivery(orderId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
      toast.success("تحویل سفارش با موفقیت تایید شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Submit review mutation
  const submitReviewMutation = useMutation({
    mutationFn: async () => {
      if (reviewRating === 0) throw new Error("لطفا امتیاز را انتخاب کنید");
      return ordersApi.submitReview(orderId, {
        rating: reviewRating,
        comment: reviewComment.trim() || undefined,
      });
    },
    onSuccess: () => {
      refetchReview();
      toast.success("نظر شما با موفقیت ثبت شد. ممنون از بازخوردتان!");
      setReviewRating(0);
      setReviewComment("");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Bank card info (should come from API/settings)
  const bankInfo = {
    cardNumber: "6037-9979-1234-5678",
    cardHolder: "شرکت شیتارو",
    bank: "بانک ملی",
  };

  // Upload receipt mutation
  const uploadReceiptMutation = useMutation({
    mutationFn: async () => {
      if (!receiptFile || !order) throw new Error("فایل رسید انتخاب نشده");
      // First initiate payment if not exists
      const paymentRes = await paymentsApi.initiate(order.id);
      // Then upload receipt
      return paymentsApi.uploadReceipt(paymentRes.data.id, receiptFile);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
      toast.success("رسید پرداخت با موفقیت ارسال شد");
      setShowPaymentModal(false);
      setReceiptFile(null);
      setReceiptPreview(null);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setReceiptFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setReceiptPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCopyCard = async () => {
    await navigator.clipboard.writeText(bankInfo.cardNumber.replace(/-/g, ""));
    setCopied(true);
    toast.success("شماره کارت کپی شد");
    setTimeout(() => setCopied(false), 2000);
  };

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
      case "PAYMENT_UPLOADED":
      case "AWAITING_VALIDATION":
      case "SHIPPED":
        return "info";
      case "DESIGNING":
      case "READY_FOR_PRINT":
      case "PRINTING":
        return "primary";
      default:
        return "info";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "DELIVERED":
      case "PAYMENT_APPROVED":
        return CheckCircle;
      case "PAYMENT_REJECTED":
      case "CANCELLED":
        return XCircle;
      case "PENDING_PAYMENT":
      case "PENDING":
        return Clock;
      default:
        return Package;
    }
  };

  if (isLoading) {
    return <PageLoading />;
  }

  if (error || !order) {
    return (
      <EmptyState
        icon={Package}
        title="سفارش یافت نشد"
        description="سفارش مورد نظر پیدا نشد یا دسترسی به آن ندارید"
        action={{
          label: "بازگشت به سفارشات",
          onClick: () => router.push("/orders"),
        }}
      />
    );
  }

  const StatusIcon = getStatusIcon(order.status);

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/orders">
          <Button variant="ghost" size="sm">
            <ArrowRight className="w-4 h-4 ml-1" />
            بازگشت
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-foreground">
            جزئیات سفارش
          </h1>
          <p className="text-sm text-muted">
            شناسه: {order.id.slice(0, 8)}...
          </p>
        </div>
        <Badge variant={getStatusBadgeVariant(order.status)} size="md">
          <StatusIcon className="w-4 h-4 ml-1" />
          {orderStatusLabels[order.status] || order.status}
        </Badge>
      </div>

      {/* Order info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5 text-primary" />
            اطلاعات سفارش
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted">محصول</p>
              <p className="font-medium">{order.category?.name_fa || "-"}</p>
            </div>
            <div>
              <p className="text-sm text-muted">نوع طراحی</p>
              <p className="font-medium">{order.plan?.name_fa || "-"}</p>
            </div>
            <div>
              <p className="text-sm text-muted">تاریخ ثبت</p>
              <p className="font-medium">{formatDateTime(order.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted">آخرین بروزرسانی</p>
              <p className="font-medium">{formatDateTime(order.updated_at)}</p>
            </div>
          </div>

          {/* Attributes */}
          {order.attributes && Object.keys(order.attributes).length > 0 && (
            <div className="pt-4 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-2">ویژگی‌های انتخابی:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(order.attributes).map(([key, value]) => (
                  <Badge key={key} variant="outline">
                    {String(value)}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payment section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-primary" />
            پرداخت
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <span className="text-muted">مبلغ کل سفارش</span>
            <span className="text-2xl font-bold text-primary">
              {formatPrice(order.total_price)}
            </span>
          </div>

          {order.status === "PENDING_PAYMENT" && (
            <div className="bg-warning-light rounded-xl p-4 mb-4">
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">در انتظار پرداخت</p>
                  <p className="text-sm text-muted mt-1">
                    لطفاً مبلغ سفارش را به شماره کارت زیر واریز و رسید را ارسال کنید
                  </p>
                </div>
              </div>
            </div>
          )}

          {order.status === "PAYMENT_UPLOADED" && (
            <div className="bg-info-light rounded-xl p-4 mb-4">
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-info shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">رسید ارسال شده</p>
                  <p className="text-sm text-muted mt-1">
                    رسید پرداخت شما در حال بررسی است. نتیجه به شما اطلاع داده خواهد شد.
                  </p>
                </div>
              </div>
            </div>
          )}

          {order.status === "PAYMENT_APPROVED" && (
            <div className="bg-success-light rounded-xl p-4 mb-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-success shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">پرداخت تأیید شد</p>
                  <p className="text-sm text-muted mt-1">
                    پرداخت شما تأیید شده و سفارش در حال انجام است.
                  </p>
                </div>
              </div>
            </div>
          )}

          {order.status === "PAYMENT_REJECTED" && (
            <div className="bg-danger-light rounded-xl p-4 mb-4">
              <div className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-danger shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">پرداخت رد شد</p>
                  <p className="text-sm text-muted mt-1">
                    رسید پرداخت شما تأیید نشد. لطفاً مجدداً رسید معتبر ارسال کنید.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>

        {(order.status === "PENDING_PAYMENT" || order.status === "PAYMENT_REJECTED") && (
          <CardFooter>
            <Button
              variant="primary"
              className="w-full"
              onClick={() => setShowPaymentModal(true)}
              leftIcon={<Upload className="w-4 h-4" />}
            >
              ارسال رسید پرداخت
            </Button>
          </CardFooter>
        )}
      </Card>

      {/* Design file preview + download (if ready) */}
      {order.design_file_url && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              فایل طراحی
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <ImagePreview
              src={order.design_file_url}
              alt="پیش‌نمایش طرح سفارش"
              className="w-full max-w-md mx-auto rounded-xl"
              aspectRatio="aspect-auto"
              thumbnailSize={600}
              showDownload={true}
              showExpand={true}
              downloadFilename={`design-order-${order.id?.toString().slice(0, 8)}`}
            />
          </CardContent>
        </Card>
      )}

      {/* Shipping & Delivery section */}
      {(order.status === "SHIPPED" || order.status === "DELIVERED") && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Truck className="w-5 h-5 text-primary" />
              وضعیت ارسال
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {order.tracking_code && (
              <div className="flex items-center justify-between p-3 bg-accent/50 rounded-lg">
                <span className="text-sm text-muted">کد رهگیری</span>
                <span className="font-mono font-bold" dir="ltr">
                  {order.tracking_code}
                </span>
              </div>
            )}

            {order.status === "SHIPPED" && (
              <div className="bg-info-light rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <Truck className="w-5 h-5 text-info shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-foreground">سفارش ارسال شده</p>
                    <p className="text-sm text-muted mt-1">
                      سفارش شما ارسال شده است. پس از دریافت، دکمه تحویل گرفتم را بزنید.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {order.status === "DELIVERED" && (
              <div className="bg-success-light rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-foreground">تحویل داده شد</p>
                    <p className="text-sm text-muted mt-1">
                      {order.delivered_at
                        ? `تاریخ تحویل: ${formatDateTime(order.delivered_at)}`
                        : "سفارش تحویل داده شده است"}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>

          {order.status === "SHIPPED" && (
            <CardFooter>
              <Button
                variant="primary"
                className="w-full"
                onClick={() => confirmDeliveryMutation.mutate()}
                isLoading={confirmDeliveryMutation.isPending}
                leftIcon={<CheckCircle className="w-4 h-4" />}
              >
                تحویل گرفتم
              </Button>
            </CardFooter>
          )}
        </Card>
      )}

      {/* Review section (only for delivered orders) */}
      {order.status === "DELIVERED" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-primary" />
              امتیاز و نظر
            </CardTitle>
          </CardHeader>
          <CardContent>
            {existingReview ? (
              /* Show submitted review */
              <div className="space-y-4">
                <div className="bg-success-light rounded-xl p-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-foreground">نظر شما ثبت شده است</p>
                      <p className="text-sm text-muted mt-1">
                        ممنون از بازخورد شما!
                      </p>
                    </div>
                  </div>
                </div>

                {/* Star display */}
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={cn(
                        "w-6 h-6",
                        star <= existingReview.rating
                          ? "text-yellow-400 fill-yellow-400"
                          : "text-gray-300"
                      )}
                    />
                  ))}
                  <span className="text-sm text-muted mr-2">
                    {toPersianNumber(existingReview.rating)}/۵
                  </span>
                </div>

                {existingReview.comment && (
                  <div className="p-3 bg-accent/50 rounded-lg">
                    <p className="text-sm text-foreground">{existingReview.comment}</p>
                  </div>
                )}
              </div>
            ) : (
              /* Review form */
              <div className="space-y-4">
                <p className="text-sm text-muted">
                  تجربه خود از این سفارش را با ما به اشتراک بگذارید
                </p>

                {/* Star rating */}
                <div>
                  <p className="text-sm font-medium text-foreground mb-2">امتیاز شما</p>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setReviewRating(star)}
                        onMouseEnter={() => setReviewHover(star)}
                        onMouseLeave={() => setReviewHover(0)}
                        className="p-0.5 transition-transform hover:scale-110"
                      >
                        <Star
                          className={cn(
                            "w-8 h-8 transition-colors",
                            star <= (reviewHover || reviewRating)
                              ? "text-yellow-400 fill-yellow-400"
                              : "text-gray-300"
                          )}
                        />
                      </button>
                    ))}
                    {reviewRating > 0 && (
                      <span className="text-sm text-muted mr-2">
                        {toPersianNumber(reviewRating)}/۵
                      </span>
                    )}
                  </div>
                </div>

                {/* Comment */}
                <div>
                  <p className="text-sm font-medium text-foreground mb-2">
                    نظر شما (اختیاری)
                  </p>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="نظر خود را بنویسید..."
                    className="w-full p-3 border border-border rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                    rows={3}
                    maxLength={1000}
                  />
                  {reviewComment.length > 0 && (
                    <p className="text-xs text-muted mt-1 text-left" dir="ltr">
                      {reviewComment.length}/1000
                    </p>
                  )}
                </div>

                {/* Submit */}
                <Button
                  variant="primary"
                  className="w-full"
                  onClick={() => submitReviewMutation.mutate()}
                  isLoading={submitReviewMutation.isPending}
                  disabled={reviewRating === 0}
                  leftIcon={<Send className="w-4 h-4" />}
                >
                  ثبت نظر
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Payment Modal */}
      <Modal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        title="پرداخت کارت به کارت"
        size="md"
      >
        <div className="space-y-6">
          {/* Amount */}
          <div className="text-center p-4 bg-primary-50 rounded-xl">
            <p className="text-sm text-muted mb-1">مبلغ قابل پرداخت</p>
            <p className="text-3xl font-bold text-primary">
              {formatPrice(order.total_price)}
            </p>
          </div>

          {/* Bank card info */}
          <div className="p-4 border border-border rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-muted">شماره کارت</span>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-lg" dir="ltr">
                  {bankInfo.cardNumber}
                </span>
                <button
                  onClick={handleCopyCard}
                  className="p-1.5 hover:bg-accent rounded-lg transition-colors"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-success" />
                  ) : (
                    <Copy className="w-4 h-4 text-muted" />
                  )}
                </button>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted">صاحب حساب</span>
              <span className="font-medium">{bankInfo.cardHolder}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted">بانک</span>
              <span className="font-medium">{bankInfo.bank}</span>
            </div>
          </div>

          {/* Receipt upload */}
          <div>
            <p className="text-sm font-medium text-foreground mb-2">
              آپلود رسید پرداخت
            </p>
            <div
              className={cn(
                "border-2 border-dashed rounded-xl p-6 text-center transition-colors",
                receiptPreview
                  ? "border-success bg-success-light"
                  : "border-border hover:border-primary/30"
              )}
            >
              <input
                type="file"
                id="receipt-file"
                className="hidden"
                accept="image/*"
                onChange={handleFileSelect}
              />
              
              {receiptPreview ? (
                <div className="relative">
                  <Image
                    src={receiptPreview}
                    alt="Receipt preview"
                    width={200}
                    height={200}
                    className="mx-auto rounded-lg object-contain max-h-48"
                  />
                  <button
                    onClick={() => {
                      setReceiptFile(null);
                      setReceiptPreview(null);
                    }}
                    className="absolute top-0 right-0 p-1 bg-danger text-white rounded-full"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <p className="text-sm text-muted mt-2">{receiptFile?.name}</p>
                </div>
              ) : (
                <label htmlFor="receipt-file" className="cursor-pointer">
                  <ImageIcon className="w-12 h-12 mx-auto text-muted mb-2" />
                  <p className="font-medium text-foreground">
                    تصویر رسید را انتخاب کنید
                  </p>
                  <p className="text-sm text-muted mt-1">
                    فرمت‌های مجاز: JPG, PNG
                  </p>
                </label>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              className="flex-1"
              onClick={() => uploadReceiptMutation.mutate()}
              isLoading={uploadReceiptMutation.isPending}
              disabled={!receiptFile}
            >
              ارسال رسید
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowPaymentModal(false)}
            >
              انصراف
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

