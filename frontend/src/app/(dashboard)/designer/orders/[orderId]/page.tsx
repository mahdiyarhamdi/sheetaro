"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, ordersApi, plansApi, filesApi, getErrorMessage, DesignRevision, ChatMessage, Question, QuestionnaireSection } from "@/lib/api";
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
  Paperclip,
  X,
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
import { getImageUrl } from "@/lib/image-utils";
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
  const [chatFile, setChatFile] = useState<File | null>(null);
  const [chatFilePreview, setChatFilePreview] = useState<string | null>(null);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatFileInputRef = useRef<HTMLInputElement>(null);

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

  // Fetch questionnaire answers
  const { data: answersData } = useQuery({
    queryKey: ["orderAnswers", orderId],
    queryFn: async () => {
      const response = await ordersApi.getAnswers(orderId);
      return response.data;
    },
    enabled: !!order && (order.design_plan === "SEMI_PRIVATE" || order.design_plan === "PRIVATE"),
  });

  // Fetch questionnaire structure (question texts) from the plan
  const { data: questionnaireData } = useQuery({
    queryKey: ["planQuestionnaire", order?.design_plan_id],
    queryFn: async () => {
      const response = await plansApi.getPlanQuestionnaire(order!.design_plan_id!);
      return response.data;
    },
    enabled: !!order?.design_plan_id && !!answersData && answersData.length > 0,
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

  // Send message mutation (with optional file)
  const sendMessageMutation = useMutation({
    mutationFn: async () => {
      const hasText = chatMessage.trim().length > 0;
      const hasFile = !!chatFile;
      if (!hasText && !hasFile) throw new Error("پیام یا فایل الزامی است");

      let fileUrl: string | undefined;
      if (hasFile) {
        setIsUploadingFile(true);
        try {
          const uploadRes = await filesApi.uploadPlaceholderImage(chatFile!);
          fileUrl = uploadRes.data.file_url;
        } finally {
          setIsUploadingFile(false);
        }
      }

      return ordersApi.sendMessage(orderId, {
        content: chatMessage.trim(),
        file_url: fileUrl,
      });
    },
    onSuccess: () => {
      setChatMessage("");
      setChatFile(null);
      setChatFilePreview(null);
      refetchMessages();
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  // Chat file selection handler
  const handleChatFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setChatFile(file);
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onloadend = () => setChatFilePreview(reader.result as string);
        reader.readAsDataURL(file);
      } else {
        setChatFilePreview(null);
      }
    }
    e.target.value = "";
  };

  const removeChatFile = () => {
    setChatFile(null);
    setChatFilePreview(null);
  };

  // Design file handlers
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

      {/* Questionnaire Answers Section */}
      {answersData && answersData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              پاسخ‌های پرسشنامه مشتری
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {(() => {
              // Build a question map from questionnaire data
              const questionMap: Record<string, { text: string; type: string; options: Array<{ value: string; label_fa: string }> }> = {};
              if (questionnaireData?.sections) {
                for (const section of questionnaireData.sections) {
                  for (const q of section.questions) {
                    questionMap[q.id] = {
                      text: q.question_fa,
                      type: q.input_type,
                      options: q.options || [],
                    };
                  }
                }
              }

              return answersData.map((answer: any, idx: number) => {
                const question = questionMap[answer.question_id];
                const questionText = question?.text || `سوال ${toPersianNumber(idx + 1)}`;
                const inputType = question?.type || "TEXT";

                return (
                  <div
                    key={answer.id}
                    className="border border-border rounded-lg p-4"
                  >
                    <p className="text-sm font-medium text-foreground mb-2">
                      {questionText}
                      {inputType === "IMAGE_UPLOAD" || inputType === "FILE_UPLOAD" ? (
                        <Badge variant="outline" size="sm" className="mr-2">فایل</Badge>
                      ) : null}
                    </p>

                    {/* Text answers */}
                    {answer.answer_text && !answer.answer_file_url && (
                      <div className="bg-accent/50 rounded-lg p-3">
                        {inputType === "SINGLE_CHOICE" && question?.options ? (
                          <p className="text-sm text-foreground">
                            {question.options.find(o => o.value === answer.answer_text)?.label_fa || answer.answer_text}
                          </p>
                        ) : (
                          <p className="text-sm text-foreground whitespace-pre-wrap">
                            {answer.answer_text}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Multi-choice answers */}
                    {answer.answer_values && answer.answer_values.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {answer.answer_values.map((val: string, vIdx: number) => {
                          const optionLabel = question?.options?.find(o => o.value === val)?.label_fa || val;
                          return (
                            <Badge key={vIdx} variant="primary" size="sm">
                              {optionLabel}
                            </Badge>
                          );
                        })}
                      </div>
                    )}

                    {/* File/Image answers */}
                    {answer.answer_file_url && (
                      <div className="mt-1">
                        {(inputType === "IMAGE_UPLOAD" || answer.answer_file_url.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)) ? (
                          <a
                            href={getImageUrl(answer.answer_file_url) || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block"
                          >
                            <img
                              src={getImageUrl(answer.answer_file_url) || ""}
                              alt={questionText}
                              className="max-h-48 rounded-lg border border-border object-contain hover:opacity-80 transition-opacity"
                            />
                          </a>
                        ) : (
                          <a
                            href={getImageUrl(answer.answer_file_url) || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline flex items-center gap-1"
                          >
                            <FileText className="w-4 h-4" />
                            دانلود فایل
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                );
              });
            })()}
          </CardContent>
        </Card>
      )}

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
                const isImageFile = msg.file_url?.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i);
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
                        <p className={cn("text-xs font-medium mb-1", isMe ? "text-white/70" : "text-foreground/70")}>
                          {msg.sender_name}
                        </p>
                      )}
                      {/* File attachment */}
                      {msg.file_url && (
                        isImageFile ? (
                          <a
                            href={getImageUrl(msg.file_url) || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block mb-2"
                          >
                            <img
                              src={getImageUrl(msg.file_url) || ""}
                              alt="تصویر پیوست"
                              className="max-w-full max-h-48 rounded-lg object-contain hover:opacity-80 transition-opacity"
                            />
                          </a>
                        ) : (
                          <a
                            href={getImageUrl(msg.file_url) || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={cn(
                              "flex items-center gap-2 mb-2 p-2 rounded-lg text-sm",
                              isMe ? "bg-white/10 text-white" : "bg-white text-foreground"
                            )}
                          >
                            <FileText className="w-4 h-4 shrink-0" />
                            <span className="truncate">فایل پیوست</span>
                          </a>
                        )
                      )}
                      {/* Text content */}
                      {msg.content && (
                        <p className={cn("text-sm whitespace-pre-wrap", isMe ? "text-white" : "text-foreground")}>
                          {msg.content}
                        </p>
                      )}
                      <p
                        className={cn(
                          "text-[10px] mt-1",
                          isMe ? "text-white/60 text-left" : "text-foreground/40 text-left"
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

            {/* File preview (when file is selected) */}
            {chatFile && (
              <div className="flex items-center gap-3 p-3 bg-accent/50 rounded-lg border border-border">
                {chatFilePreview ? (
                  <img src={chatFilePreview} alt="پیش‌نمایش" className="w-14 h-14 rounded-lg object-cover" />
                ) : (
                  <div className="w-14 h-14 rounded-lg bg-accent flex items-center justify-center">
                    <FileText className="w-6 h-6 text-muted" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{chatFile.name}</p>
                  <p className="text-xs text-muted">{(chatFile.size / 1024).toFixed(0)} KB</p>
                </div>
                <button
                  onClick={removeChatFile}
                  className="text-muted hover:text-danger transition-colors p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Input */}
            <div className="flex items-end gap-2">
              <input
                type="file"
                ref={chatFileInputRef}
                className="hidden"
                accept="image/*,.pdf,.doc,.docx,.ai,.psd,.svg"
                onChange={handleChatFileSelect}
              />
              <button
                type="button"
                onClick={() => chatFileInputRef.current?.click()}
                className="p-3 text-muted hover:text-primary transition-colors rounded-lg hover:bg-accent"
                title="پیوست فایل"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <textarea
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="پیام خود را بنویسید..."
                className="flex-1 p-3 border border-border rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    if (chatMessage.trim() || chatFile) sendMessageMutation.mutate();
                  }
                }}
              />
              <Button
                variant="primary"
                onClick={() => sendMessageMutation.mutate()}
                isLoading={sendMessageMutation.isPending || isUploadingFile}
                disabled={!chatMessage.trim() && !chatFile}
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
