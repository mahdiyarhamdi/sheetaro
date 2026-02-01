"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { paymentsApi, getErrorMessage, Payment } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  Modal,
  Textarea,
  PageLoading,
  EmptyState,
} from "@/components/ui";
import {
  CreditCard,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  ArrowRight,
  Package,
  User,
  Calendar,
  Image as ImageIcon,
} from "lucide-react";
import { formatPrice, formatDateTime, toPersianNumber, cn } from "@/lib/utils";
import toast from "react-hot-toast";
import Link from "next/link";

export default function AdminPaymentsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAdmin, isLoadingUser } = useAuth();

  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [page, setPage] = useState(1);

  // Redirect non-admin
  useEffect(() => {
    if (!isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isLoadingUser, isAdmin, router]);

  const { data: paymentsData, isLoading } = useQuery({
    queryKey: ["pendingPayments", page],
    queryFn: async () => {
      const response = await paymentsApi.getPending({ page, page_size: 20 });
      return response.data;
    },
    enabled: isAdmin,
  });

  const approveMutation = useMutation({
    mutationFn: (paymentId: string) => paymentsApi.approve(paymentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pendingPayments"] });
      queryClient.invalidateQueries({ queryKey: ["adminStats"] });
      toast.success("پرداخت تأیید شد");
      setSelectedPayment(null);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ paymentId, reason }: { paymentId: string; reason: string }) =>
      paymentsApi.reject(paymentId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pendingPayments"] });
      queryClient.invalidateQueries({ queryKey: ["adminStats"] });
      toast.success("پرداخت رد شد");
      setSelectedPayment(null);
      setShowRejectModal(false);
      setRejectReason("");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  if (isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const payments = paymentsData?.items ?? [];
  const total = paymentsData?.total ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin">
          <Button variant="ghost" size="sm">
            <ArrowRight className="w-4 h-4 ml-1" />
            بازگشت
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-foreground">پرداخت‌های در انتظار</h1>
          <p className="text-muted mt-1">
            {total > 0
              ? `${toPersianNumber(total)} پرداخت در انتظار بررسی`
              : "همه پرداخت‌ها بررسی شده‌اند"}
          </p>
        </div>
      </div>

      {/* Payments list */}
      {isLoading ? (
        <PageLoading />
      ) : payments.length === 0 ? (
        <EmptyState
          icon={CheckCircle}
          title="همه پرداخت‌ها بررسی شده‌اند"
          description="در حال حاضر پرداختی در انتظار تأیید نیست"
        />
      ) : (
        <div className="space-y-4">
          {payments.map((payment) => (
            <Card key={payment.id} className="hover:border-primary/30 transition-colors">
              <CardContent className="py-4">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Payment info */}
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-warning-light flex items-center justify-center shrink-0">
                      <Clock className="w-6 h-6 text-warning" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-foreground">
                          سفارش #{payment.order_id.slice(0, 8)}
                        </p>
                        <Badge variant="warning" size="sm">
                          در انتظار بررسی
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {formatDateTime(payment.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Amount and actions */}
                  <div className="flex items-center gap-4">
                    <div className="text-left">
                      <p className="text-sm text-muted">مبلغ</p>
                      <p className="text-xl font-bold text-primary">
                        {formatPrice(payment.amount)}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedPayment(payment)}
                        leftIcon={<Eye className="w-4 h-4" />}
                      >
                        بررسی
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Review Modal */}
      <Modal
        isOpen={!!selectedPayment && !showRejectModal}
        onClose={() => setSelectedPayment(null)}
        title="بررسی پرداخت"
        size="lg"
      >
        {selectedPayment && (
          <div className="space-y-6">
            {/* Payment details */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-accent rounded-xl">
              <div>
                <p className="text-sm text-muted">شماره سفارش</p>
                <p className="font-medium">{selectedPayment.order_id.slice(0, 8)}...</p>
              </div>
              <div>
                <p className="text-sm text-muted">مبلغ</p>
                <p className="font-bold text-primary">{formatPrice(selectedPayment.amount)}</p>
              </div>
              <div>
                <p className="text-sm text-muted">تاریخ ارسال</p>
                <p className="font-medium">{formatDateTime(selectedPayment.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-muted">وضعیت</p>
                <Badge variant="warning">در انتظار بررسی</Badge>
              </div>
            </div>

            {/* Receipt image */}
            <div>
              <p className="text-sm font-medium text-foreground mb-2">تصویر رسید</p>
              {selectedPayment.receipt_image_url ? (
                <div className="relative aspect-video bg-accent rounded-xl overflow-hidden">
                  <Image
                    src={selectedPayment.receipt_image_url}
                    alt="Receipt"
                    fill
                    className="object-contain"
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center aspect-video bg-accent rounded-xl">
                  <div className="text-center">
                    <ImageIcon className="w-12 h-12 text-muted mx-auto mb-2" />
                    <p className="text-muted">تصویر رسید موجود نیست</p>
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <Button
                variant="primary"
                className="flex-1"
                onClick={() => approveMutation.mutate(selectedPayment.id)}
                isLoading={approveMutation.isPending}
                leftIcon={<CheckCircle className="w-4 h-4" />}
              >
                تأیید پرداخت
              </Button>
              <Button
                variant="outline"
                className="flex-1 text-danger border-danger hover:bg-danger-light"
                onClick={() => setShowRejectModal(true)}
                leftIcon={<XCircle className="w-4 h-4" />}
              >
                رد پرداخت
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Reject Modal */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => {
          setShowRejectModal(false);
          setRejectReason("");
        }}
        title="رد پرداخت"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-muted">
            لطفاً دلیل رد پرداخت را وارد کنید. این دلیل به کاربر نمایش داده خواهد شد.
          </p>

          <Textarea
            label="دلیل رد"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="مثال: رسید پرداخت نامعتبر است یا مبلغ واریزی مطابقت ندارد"
            rows={4}
          />

          <div className="flex items-center gap-3">
            <Button
              variant="danger"
              className="flex-1"
              onClick={() => {
                if (selectedPayment) {
                  rejectMutation.mutate({
                    paymentId: selectedPayment.id,
                    reason: rejectReason,
                  });
                }
              }}
              isLoading={rejectMutation.isPending}
              disabled={!rejectReason.trim()}
            >
              رد پرداخت
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowRejectModal(false);
                setRejectReason("");
              }}
            >
              انصراف
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

