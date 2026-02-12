"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, ordersApi, getErrorMessage, DesignRevision, ChatMessage } from "@/lib/api";
import { ImagePreview } from "@/components/ui/image-preview";
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
} from "@/components/ui";
import {
  ArrowRight,
  Package,
  User,
  Upload,
  CheckCircle,
  XCircle,
  History,
  MessageSquare,
  Send,
  FileText,
  ChevronDown,
  ChevronUp,
  Palette,
  Loader2,
  Image as ImageIcon,
} from "lucide-react";
import {
  formatPrice,
  formatDateTime,
  orderStatusLabels,
  toPersianNumber,
  cn,
} from "@/lib/utils";
import toast from "react-hot-toast";
import { getUser } from "@/lib/auth";
import Link from "next/link";

export default function DesignerOrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const orderId = params.orderId as string;
  const currentUser = typeof window !== "undefined" ? getUser() : null;

  // States
  const [designFile, setDesignFile] = useState<File | null>(null);
  const [designPreview, setDesignPreview] = useState<string | null>(null);
  const [showRevisionHistory, setShowRevisionHistory] = useState(false);
  const [chatMessage, setChatMessage] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch order detail
  const { data: order, isLoading, error } = useQuery({
    queryKey: ["designerOrder", orderId],
    queryFn: async () => {
      const response = await adminApi.getDesignerOrderDetail(orderId);
      return response.data;
    },
  });

  // Fetch revisions
  const { data: revisionsData } = useQuery({
    queryKey: ["designerRevisions", orderId],
    queryFn: async () => {
      const response = await adminApi.getDesignerRevisions(orderId);
      return response.data;
    },
    enabled: !!order,
  });

  // Fetch messages (PRIVATE only)
  const { data: messagesData, refetch: refetchMessages } = useQuery({
    queryKey: ["designerMessages", orderId],
    queryFn: async () => {
      const response = await ordersApi.getMessages(orderId, { page: 1, page_size: 100 });
      return response.data;
    },
    enabled: !!order && order.design_plan === "PRIVATE" && order.status === "DESIGNING",
    refetchInterval: 5000,
  });

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messagesData?.items?.length]);

  // Upload design mutation
  const uploadDesignMutation = useMutation({
    mutationFn: async () => {
      if (!designFile) throw new Error("فایل طرح انتخاب نشده");
      return adminApi.designerUploadDesign(orderId, designFile);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["designerOrder", orderId] });
      queryClient.invalidateQueries({ queryKey: ["designerRevisions", orderId] });
      setDesignFile(null);
      setDesignPreview(null);
      toast.success("طرح با موفقیت آپلود شد");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  // Accept order mutation (for PENDING_DESIGNER status)
  const acceptOrderMutation = useMutation({
    mutationFn: async () => {
      return adminApi.designerAcceptOrder(orderId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["designerOrder", orderId] });
      queryClient.invalidateQueries({ queryKey: ["designerQueue"] });
      queryClient.invalidateQueries({ queryKey: ["designerStats"] });
      queryClient.invalidateQueries({ queryKey: ["designerOrders"] });
      toast.success("سفارش با موفقیت پذیرفته شد");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async () => {
      if (!chatMessage.trim()) throw new Error("پیام خالی");
      return ordersApi.sendMessage(orderId, { content: chatMessage.trim() });
    },
    onSuccess: () => {
      setChatMessage("");
      refetchMessages();
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  // File handlers
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDesignFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setDesignPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setDesignFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setDesignPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  }, []);

  if (isLoading) return <PageLoading />;

  if (error || !order) {
    return (
      <EmptyState
        icon={Package}
        title="سفارش یافت نشد"
        description="سفارش مورد نظر پیدا نشد یا به شما اختصاص داده نشده است"
        action={{
          label: "بازگشت",
          onClick: () => router.push("/designer/orders"),
        }}
      />
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/designer/orders">
          <Button variant="ghost" size="sm">
            <ArrowRight className="w-4 h-4 ml-1" />
            بازگشت
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-foreground">جزئیات سفارش</h1>
          <p className="text-sm text-muted">شناسه: {orderId.slice(0, 8)}...</p>
        </div>
        <Badge
          variant={order.status === "PENDING_DESIGNER" ? "warning" : order.status === "DESIGNING" ? "primary" : "success"}
          size="md"
        >
          {orderStatusLabels[order.status] || order.status}
        </Badge>
      </div>

      {/* Accept Banner (for PENDING_DESIGNER) */}
      {order.status === "PENDING_DESIGNER" && (
        <Card className="border-2 border-yellow-400 bg-yellow-50">
          <CardContent className="py-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-foreground text-lg">
                  این سفارش در صف انتظار طراحی است
                </h3>
                <p className="text-sm text-muted mt-1">
                  برای شروع کار روی این سفارش، آن را پذیرش کنید
                </p>
              </div>
              <Button
                variant="primary"
                size="md"
                onClick={() => acceptOrderMutation.mutate()}
                isLoading={acceptOrderMutation.isPending}
              >
                پذیرش سفارش
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Order Info */}
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
              <p className="font-medium">
                {order.category_icon && <span className="ml-1">{order.category_icon}</span>}
                {order.category_name || "-"}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted">نوع طراحی</p>
              <p className="font-medium">{order.design_plan_label || "-"}</p>
            </div>
            <div>
              <p className="text-sm text-muted">تعداد</p>
              <p className="font-medium">{toPersianNumber(order.quantity)}</p>
            </div>
            {order.customer_name && (
              <div>
                <p className="text-sm text-muted">مشتری</p>
                <p className="font-medium flex items-center gap-1">
                  <User className="w-4 h-4" />
                  {order.customer_name}
                </p>
              </div>
            )}
          </div>

          {/* Print specs */}
          {order.enriched_attributes && order.enriched_attributes.length > 0 && (
            <div className="pt-4 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-2">مشخصات چاپ:</p>
              <div className="flex flex-wrap gap-2">
                {order.enriched_attributes.map((attr: { attribute_name: string; value_name: string }, idx: number) => (
                  <Badge key={idx} variant="outline">
                    {attr.attribute_name}: {attr.value_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Customer notes */}
          {order.customer_notes && (
            <div className="pt-4 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-1">یادداشت مشتری:</p>
              <p className="text-sm text-muted bg-accent/50 rounded-lg p-3">{order.customer_notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Design Section */}
      {order.status === "DESIGNING" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary" />
              آپلود طرح جدید
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center transition-colors",
                isDragging ? "border-primary bg-primary-50" : "border-border hover:border-primary/30",
                designPreview && "border-success bg-success-light"
              )}
            >
              <input
                type="file"
                id="design-upload"
                className="hidden"
                accept="image/*"
                onChange={handleFileSelect}
              />

              {designPreview ? (
                <div className="space-y-3">
                  <img
                    src={designPreview}
                    alt="پیش‌نمایش طرح"
                    className="mx-auto max-h-64 rounded-lg object-contain"
                  />
                  <p className="text-sm text-muted">{designFile?.name}</p>
                  <button
                    onClick={() => { setDesignFile(null); setDesignPreview(null); }}
                    className="text-sm text-danger hover:underline"
                  >
                    حذف و انتخاب دوباره
                  </button>
                </div>
              ) : (
                <label htmlFor="design-upload" className="cursor-pointer">
                  <ImageIcon className="w-12 h-12 mx-auto text-muted mb-2" />
                  <p className="font-medium text-foreground">
                    فایل طرح را بکشید و رها کنید یا کلیک کنید
                  </p>
                  <p className="text-sm text-muted mt-1">فرمت‌های مجاز: JPG, PNG, PDF</p>
                </label>
              )}
            </div>
          </CardContent>
          {designFile && (
            <CardFooter>
              <Button
                variant="primary"
                className="w-full"
                onClick={() => uploadDesignMutation.mutate()}
                isLoading={uploadDesignMutation.isPending}
                leftIcon={<Upload className="w-4 h-4" />}
              >
                ارسال طرح
              </Button>
            </CardFooter>
          )}
        </Card>
      )}

      {/* Revision History */}
      {revisionsData && revisionsData.items.length > 0 && (
        <Card>
          <CardHeader
            className="cursor-pointer"
            onClick={() => setShowRevisionHistory(!showRevisionHistory)}
          >
            <CardTitle className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-primary" />
                تاریخچه ریویژن‌ها ({toPersianNumber(revisionsData.items.length)})
              </div>
              {showRevisionHistory ? (
                <ChevronUp className="w-5 h-5 text-muted" />
              ) : (
                <ChevronDown className="w-5 h-5 text-muted" />
              )}
            </CardTitle>
          </CardHeader>
          {showRevisionHistory && (
            <CardContent className="space-y-4">
              {revisionsData.items.map((rev: DesignRevision) => (
                <div
                  key={rev.id}
                  className="p-4 border border-border rounded-lg space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">ریویژن {toPersianNumber(rev.version)}</span>
                    <Badge
                      variant={
                        rev.status === "APPROVED"
                          ? "success"
                          : rev.status === "REJECTED"
                          ? "danger"
                          : "warning"
                      }
                      size="sm"
                    >
                      {rev.status === "APPROVED"
                        ? "تایید شده"
                        : rev.status === "REJECTED"
                        ? "رد شده"
                        : "در انتظار بررسی"}
                    </Badge>
                  </div>
                  {rev.design_file_url && (
                    <ImagePreview
                      src={rev.design_file_url}
                      alt={`ریویژن ${rev.version}`}
                      className="w-32 h-32 rounded-lg"
                      aspectRatio="aspect-square"
                      thumbnailSize={200}
                      showExpand={true}
                    />
                  )}
                  {rev.customer_feedback && (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                      <p className="text-xs text-orange-600 mb-1 font-medium">بازخورد مشتری:</p>
                      <p className="text-sm">{rev.customer_feedback}</p>
                    </div>
                  )}
                  <p className="text-xs text-muted">{formatDateTime(rev.created_at)}</p>
                </div>
              ))}
            </CardContent>
          )}
        </Card>
      )}

      {/* Chat Section (PRIVATE only) */}
      {order.design_plan === "PRIVATE" && order.status === "DESIGNING" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-primary" />
              چت با مشتری
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Messages */}
            <div className="max-h-96 overflow-y-auto space-y-3 p-2">
              {(!messagesData?.items || messagesData.items.length === 0) && (
                <p className="text-center text-sm text-muted py-8">
                  هنوز پیامی ارسال نشده
                </p>
              )}
              {messagesData?.items?.map((msg: ChatMessage) => {
                const isMe = msg.sender_id === currentUser?.id;
                return (
                  <div
                    key={msg.id}
                    className={cn("flex", isMe ? "justify-end" : "justify-start")}
                  >
                    <div
                      className={cn(
                        "max-w-[75%] rounded-2xl px-4 py-2",
                        isMe
                          ? "bg-primary text-white rounded-br-sm"
                          : "bg-accent rounded-bl-sm"
                      )}
                    >
                      {!isMe && msg.sender_name && (
                        <p className="text-xs font-medium mb-1 opacity-70">
                          {msg.sender_name}
                        </p>
                      )}
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      {msg.file_url && (
                        <a
                          href={msg.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={cn(
                            "text-xs underline mt-1 inline-block",
                            isMe ? "text-white/80" : "text-primary"
                          )}
                        >
                          فایل پیوست
                        </a>
                      )}
                      <p
                        className={cn(
                          "text-[10px] mt-1",
                          isMe ? "text-white/60 text-left" : "text-muted text-left"
                        )}
                        dir="ltr"
                      >
                        {new Date(msg.created_at).toLocaleTimeString("fa-IR", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                );
              })}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <textarea
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="پیام خود را بنویسید..."
                className="flex-1 p-3 border border-border rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    if (chatMessage.trim()) sendMessageMutation.mutate();
                  }
                }}
              />
              <Button
                variant="primary"
                onClick={() => sendMessageMutation.mutate()}
                isLoading={sendMessageMutation.isPending}
                disabled={!chatMessage.trim()}
                className="self-end"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
