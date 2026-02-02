"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage, ValidationRequest, ValidationStatus } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardContent,
  Button,
  Badge,
  Modal,
  Textarea,
  PageLoading,
  EmptyState,
} from "@/components/ui";
import {
  CheckSquare,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  ArrowRight,
  Calendar,
  Image as ImageIcon,
  User,
  FileText,
  Tag,
} from "lucide-react";
import { formatPrice, formatDateTime, toPersianNumber, cn } from "@/lib/utils";
import toast from "react-hot-toast";
import Link from "next/link";

type FilterStatus = ValidationStatus | "ALL";

export default function AdminValidationsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAdmin, isLoadingUser } = useAuth();

  const [selectedValidation, setSelectedValidation] = useState<ValidationRequest | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectComment, setRejectComment] = useState("");
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<FilterStatus>("PENDING");

  // Redirect non-admin
  useEffect(() => {
    if (!isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isLoadingUser, isAdmin, router]);

  const { data: validationsData, isLoading } = useQuery({
    queryKey: ["validations", page, statusFilter],
    queryFn: async () => {
      const params: { page: number; page_size: number; status?: ValidationStatus } = {
        page,
        page_size: 20,
      };
      if (statusFilter !== "ALL") {
        params.status = statusFilter as ValidationStatus;
      }
      const response = await adminApi.getValidations(params);
      return response.data;
    },
    enabled: isAdmin,
  });

  const approveMutation = useMutation({
    mutationFn: (orderId: string) => adminApi.approveValidation(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["validations"] });
      queryClient.invalidateQueries({ queryKey: ["adminStats"] });
      toast.success("اعتبارسنجی تأیید شد");
      setSelectedValidation(null);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ orderId, comment }: { orderId: string; comment: string }) =>
      adminApi.rejectValidation(orderId, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["validations"] });
      queryClient.invalidateQueries({ queryKey: ["adminStats"] });
      toast.success("اعتبارسنجی رد شد");
      setSelectedValidation(null);
      setShowRejectModal(false);
      setRejectComment("");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  if (isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const validations = validationsData?.items ?? [];
  const total = validationsData?.total ?? 0;

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "PENDING":
        return <Badge variant="warning">در انتظار بررسی</Badge>;
      case "PASSED":
        return <Badge variant="success">تأیید شده</Badge>;
      case "FAILED":
        return <Badge variant="danger">رد شده</Badge>;
      default:
        return <Badge variant="warning">در انتظار بررسی</Badge>;
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case "PASSED":
        return <CheckCircle className="w-6 h-6 text-success" />;
      case "FAILED":
        return <XCircle className="w-6 h-6 text-danger" />;
      default:
        return <Clock className="w-6 h-6 text-warning" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center gap-4">
        <Link href="/admin">
          <Button variant="ghost" size="sm">
            <ArrowRight className="w-4 h-4 ml-1" />
            بازگشت
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-foreground">مدیریت اعتبارسنجی‌ها</h1>
          <p className="text-muted mt-1">
            {total > 0
              ? `${toPersianNumber(total)} درخواست اعتبارسنجی`
              : "هیچ درخواستی موجود نیست"}
          </p>
        </div>
      </div>

      {/* Filter buttons */}
      <div className="flex flex-wrap gap-2">
        {[
          { value: "PENDING" as FilterStatus, label: "در انتظار" },
          { value: "PASSED" as FilterStatus, label: "تأیید شده" },
          { value: "FAILED" as FilterStatus, label: "رد شده" },
          { value: "ALL" as FilterStatus, label: "همه" },
        ].map((filter) => (
          <Button
            key={filter.value}
            variant={statusFilter === filter.value ? "primary" : "outline"}
            size="sm"
            onClick={() => {
              setStatusFilter(filter.value);
              setPage(1);
            }}
          >
            {filter.label}
          </Button>
        ))}
      </div>

      {/* Validations list */}
      {isLoading ? (
        <PageLoading />
      ) : validations.length === 0 ? (
        <EmptyState
          icon={CheckSquare}
          title="درخواستی موجود نیست"
          description={
            statusFilter === "PENDING"
              ? "در حال حاضر درخواست اعتبارسنجی در انتظاری وجود ندارد"
              : "هیچ درخواستی با این فیلتر یافت نشد"
          }
        />
      ) : (
        <div className="space-y-4">
          {validations.map((validation) => (
            <Card key={validation.id} className="hover:border-primary/30 transition-colors">
              <CardContent className="py-4">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Validation info */}
                  <div className="flex items-start gap-4">
                    <div className={cn(
                      "w-12 h-12 rounded-xl flex items-center justify-center shrink-0",
                      validation.validation_status === "PASSED" ? "bg-success-light" :
                      validation.validation_status === "FAILED" ? "bg-danger-light" :
                      "bg-warning-light"
                    )}>
                      {getStatusIcon(validation.validation_status)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-foreground">
                          سفارش #{validation.id.slice(0, 8)}
                        </p>
                        {getStatusBadge(validation.validation_status)}
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-sm text-muted">
                        {validation.user_name && (
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {validation.user_name}
                          </span>
                        )}
                        {validation.category_name && (
                          <span className="flex items-center gap-1">
                            <Tag className="w-4 h-4" />
                            {validation.category_name}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {formatDateTime(validation.created_at)}
                        </span>
                      </div>
                      {validation.plan_name && (
                        <p className="text-sm text-muted mt-1">
                          <FileText className="w-4 h-4 inline ml-1" />
                          پلن: {validation.plan_name}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Amount and actions */}
                  <div className="flex items-center gap-4">
                    <div className="text-left">
                      <p className="text-sm text-muted">هزینه اعتبارسنجی</p>
                      <p className="text-xl font-bold text-primary">
                        {formatPrice(validation.validation_price)}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedValidation(validation)}
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

      {/* Pagination */}
      {total > 20 && (
        <div className="flex justify-center gap-2 mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            قبلی
          </Button>
          <span className="flex items-center px-4 text-sm text-muted">
            صفحه {toPersianNumber(page)} از {toPersianNumber(Math.ceil(total / 20))}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= total}
          >
            بعدی
          </Button>
        </div>
      )}

      {/* Review Modal */}
      <Modal
        isOpen={!!selectedValidation && !showRejectModal}
        onClose={() => setSelectedValidation(null)}
        title="بررسی اعتبارسنجی"
        size="lg"
      >
        {selectedValidation && (
          <div className="space-y-6">
            {/* Validation details */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-accent rounded-xl">
              <div>
                <p className="text-sm text-muted">شماره سفارش</p>
                <p className="font-medium">{selectedValidation.id.slice(0, 8)}...</p>
              </div>
              <div>
                <p className="text-sm text-muted">وضعیت</p>
                {getStatusBadge(selectedValidation.validation_status)}
              </div>
              <div>
                <p className="text-sm text-muted">مشتری</p>
                <p className="font-medium">{selectedValidation.user_name || "ناشناس"}</p>
              </div>
              <div>
                <p className="text-sm text-muted">شماره تماس</p>
                <p className="font-medium">{selectedValidation.user_phone || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted">دسته‌بندی</p>
                <p className="font-medium">{selectedValidation.category_name || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted">پلن طراحی</p>
                <p className="font-medium">{selectedValidation.plan_name || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted">قالب</p>
                <p className="font-medium">{selectedValidation.template_name || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted">هزینه اعتبارسنجی</p>
                <p className="font-bold text-primary">{formatPrice(selectedValidation.validation_price)}</p>
              </div>
              <div>
                <p className="text-sm text-muted">قیمت کل سفارش</p>
                <p className="font-bold text-primary">{formatPrice(selectedValidation.total_price)}</p>
              </div>
              <div>
                <p className="text-sm text-muted">تاریخ ثبت</p>
                <p className="font-medium">{formatDateTime(selectedValidation.created_at)}</p>
              </div>
            </div>

            {/* Design preview */}
            <div>
              <p className="text-sm font-medium text-foreground mb-2">پیش‌نمایش طرح</p>
              {selectedValidation.design_preview_url ? (
                <div className="relative aspect-video bg-accent rounded-xl overflow-hidden">
                  <img
                    src={selectedValidation.design_preview_url.startsWith('http') 
                      ? selectedValidation.design_preview_url 
                      : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005'}${selectedValidation.design_preview_url.startsWith('/api/v1') ? selectedValidation.design_preview_url : '/api/v1' + selectedValidation.design_preview_url}`}
                    alt="Design Preview"
                    className="w-full h-full object-contain"
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center aspect-video bg-accent rounded-xl">
                  <div className="text-center">
                    <ImageIcon className="w-12 h-12 text-muted mx-auto mb-2" />
                    <p className="text-muted">پیش‌نمایش طرح موجود نیست</p>
                  </div>
                </div>
              )}
            </div>

            {/* Actions - only show for pending */}
            {(!selectedValidation.validation_status || selectedValidation.validation_status === "PENDING") && (
              <div className="flex items-center gap-3">
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={() => approveMutation.mutate(selectedValidation.id)}
                  isLoading={approveMutation.isPending}
                  leftIcon={<CheckCircle className="w-4 h-4" />}
                >
                  تأیید اعتبارسنجی
                </Button>
                <Button
                  variant="outline"
                  className="flex-1 text-danger border-danger hover:bg-danger-light"
                  onClick={() => setShowRejectModal(true)}
                  leftIcon={<XCircle className="w-4 h-4" />}
                >
                  رد اعتبارسنجی
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Reject Modal */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => {
          setShowRejectModal(false);
          setRejectComment("");
        }}
        title="رد اعتبارسنجی"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-muted">
            لطفاً دلیل رد اعتبارسنجی و موارد نیاز به اصلاح را وارد کنید.
            این توضیحات به مشتری نمایش داده خواهد شد.
          </p>

          <Textarea
            label="توضیحات اصلاحیه"
            value={rejectComment}
            onChange={(e) => setRejectComment(e.target.value)}
            placeholder="مثال: لطفاً رزولوشن تصویر لوگو را افزایش دهید یا رنگ متن را تغییر دهید"
            rows={4}
          />

          <div className="flex items-center gap-3">
            <Button
              variant="danger"
              className="flex-1"
              onClick={() => {
                if (selectedValidation) {
                  rejectMutation.mutate({
                    orderId: selectedValidation.id,
                    comment: rejectComment,
                  });
                }
              }}
              isLoading={rejectMutation.isPending}
              disabled={!rejectComment.trim()}
            >
              رد اعتبارسنجی
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowRejectModal(false);
                setRejectComment("");
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
