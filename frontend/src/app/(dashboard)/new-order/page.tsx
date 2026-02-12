"use client";

import { useState, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import { OptimizedImage } from "@/components/ui";
import { ImagePreview } from "@/components/ui/image-preview";
import { useCategories, useCategoryAttributes, useCategoryPlans, usePlanTemplates, usePlanQuestionnaire, useTemplatePlaceholders, useTemplatePreview } from "@/hooks/useCatalog";
import { useOrders } from "@/hooks/useOrders";
import { useAuth } from "@/hooks/useAuth";
import { filesApi, paymentsApi, ordersApi, PlaceholderImageUploadResponse } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
  Button,
  Input,
  Textarea,
  Select,
  Badge,
  PageLoading,
  EmptyState,
} from "@/components/ui";
import {
  ArrowRight,
  ArrowLeft,
  Check,
  Package,
  Palette,
  FileText,
  CreditCard,
  Upload,
  Image as ImageIcon,
  Type,
  LayoutTemplate,
  ShieldCheck,
  AlertTriangle,
  Copy,
  X,
} from "lucide-react";
import { cn, formatPrice, toPersianNumber } from "@/lib/utils";
import { getImageUrl } from "@/lib/image-utils";
import toast from "react-hot-toast";

// Step types for different plan flows
type BaseStep = "category" | "attributes" | "plan";
type PublicPlanStep = "template" | "placeholders" | "validation";
type SemiPrivateStep = "questionnaire" | "validation";
type PrivateStep = "upload" | "validation";
type PaymentStep = "payment";
type FinalStep = "summary";

type OrderStep = BaseStep | PublicPlanStep | SemiPrivateStep | PrivateStep | PaymentStep | FinalStep;

interface PlaceholderValue {
  type: "IMAGE" | "TEXT";
  value: string;
}

interface OrderData {
  category_id: string;
  attributes: Record<string, string>;
  plan_id: string;
  template_id?: string;
  questionnaire_answers?: Record<string, string>;
  design_file?: File;
  placeholder_values: Record<string, PlaceholderValue>;
  wants_validation: boolean;
  quantity: number;
}

const VALIDATION_PRICE = 50000; // 50,000 Toman

export default function NewOrderPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<OrderStep>("category");
  const [orderData, setOrderData] = useState<OrderData>({
    category_id: "",
    attributes: {},
    plan_id: "",
    placeholder_values: {},
    wants_validation: false,
    quantity: 1,
  });
  const [uploadingImage, setUploadingImage] = useState<string | null>(null);
  
  // Payment receipt state
  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Bank card info (should come from API/settings)
  const bankInfo = {
    cardNumber: "6037-9979-1234-5678",
    cardHolder: "شرکت شیتارو",
    bank: "بانک ملی",
  };

  // Fetch data
  const { data: categories, isLoading: isLoadingCategories } = useCategories();
  const { data: attributes, isLoading: isLoadingAttributes } = useCategoryAttributes(orderData.category_id);
  const { data: plans, isLoading: isLoadingPlans } = useCategoryPlans(orderData.category_id);
  const { data: templates, isLoading: isLoadingTemplates } = usePlanTemplates(orderData.plan_id);
  const { data: questionnaire, isLoading: isLoadingQuestionnaire } = usePlanQuestionnaire(orderData.plan_id);
  const { data: placeholders, isLoading: isLoadingPlaceholders } = useTemplatePlaceholders(orderData.template_id || "");
  
  const previewMutation = useTemplatePreview();
  const { createOrder, isCreatingOrder } = useOrders();
  const { user } = useAuth();

  const selectedCategory = categories?.find((c) => c.id === orderData.category_id);
  const selectedPlan = plans?.find((p) => p.id === orderData.plan_id);
  const selectedTemplate = templates?.find((t) => t.id === orderData.template_id);

  // Generate preview when placeholder values change
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  useEffect(() => {
    if (orderData.template_id && placeholders && Object.keys(orderData.placeholder_values).length > 0) {
      const placeholderData = placeholders.map(p => ({
        placeholder_id: p.id,
        image_url: orderData.placeholder_values[p.id]?.type === "IMAGE" ? orderData.placeholder_values[p.id]?.value : undefined,
        text_value: orderData.placeholder_values[p.id]?.type === "TEXT" ? orderData.placeholder_values[p.id]?.value : undefined,
      }));
      
      previewMutation.mutate(
        { templateId: orderData.template_id, placeholders: placeholderData },
        {
          onSuccess: (data) => {
            setPreviewUrl(data.preview_url);
          },
        }
      );
    }
  }, [orderData.template_id, orderData.placeholder_values, placeholders]);

  // Dynamic steps based on plan type
  const getStepsForPlanType = () => {
    const baseSteps = [
      { id: "category" as OrderStep, label: "انتخاب محصول", icon: Package },
      { id: "attributes" as OrderStep, label: "ویژگی‌ها", icon: Palette },
      { id: "plan" as OrderStep, label: "نوع طراحی", icon: FileText },
    ];

    if (!selectedPlan) {
      return [
        ...baseSteps,
        { id: "summary" as OrderStep, label: "خلاصه سفارش", icon: FileText },
        { id: "payment" as OrderStep, label: "پرداخت", icon: CreditCard },
      ];
    }

    let planSpecificSteps: { id: OrderStep; label: string; icon: React.ElementType }[] = [];

    if (selectedPlan.has_templates) {
      // PUBLIC plan: template + placeholders + optional validation
      planSpecificSteps = [
        { id: "template", label: "انتخاب قالب", icon: LayoutTemplate },
        { id: "placeholders", label: "محتوای طرح", icon: Type },
        { id: "validation", label: "اعتبارسنجی", icon: ShieldCheck },
      ];
    } else if (selectedPlan.has_questionnaire) {
      // SEMI_PRIVATE / PRIVATE: questionnaire only, no validation step
      // (design is created by designer, not uploaded by customer)
      planSpecificSteps = [
        { id: "questionnaire", label: "اطلاعات طراحی", icon: FileText },
      ];
    } else if (selectedPlan.has_file_upload) {
      // OWN_DESIGN: customer uploads their file + optional validation
      planSpecificSteps = [
        { id: "upload", label: "آپلود طرح", icon: Upload },
        { id: "validation", label: "اعتبارسنجی", icon: ShieldCheck },
      ];
    }

    return [
      ...baseSteps,
      ...planSpecificSteps,
      { id: "summary" as OrderStep, label: "خلاصه سفارش", icon: FileText },
      { id: "payment" as OrderStep, label: "پرداخت", icon: CreditCard },
    ];
  };

  const steps = getStepsForPlanType();
  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  // Calculate total price
  // Calculate unit price (price per item)
  // Calculate price breakdown
  const basePrice = useMemo(() => {
    return Number(selectedCategory?.base_price) || 0;
  }, [selectedCategory]);

  const planPrice = useMemo(() => {
    return Number(selectedPlan?.price) || 0;
  }, [selectedPlan]);

  // Calculate attributes price based on price_type (FIXED vs MULTIPLIER)
  const { fixedAttributesPrice, multiplierTotal } = useMemo(() => {
    let fixedPrice = 0;
    let multiplier = 1; // Start with base multiplier of 1
    
    if (attributes) {
      attributes.forEach((attr) => {
        const selectedValue = orderData.attributes[attr.id];
        if (selectedValue && attr.options) {
          const option = attr.options.find((o) => o.value === selectedValue);
          if (option) {
            const modifier = Number(option.price_modifier) || 0;
            if (attr.price_type === "MULTIPLIER") {
              // Multiply the multiplier (e.g., 1.5 = 150%)
              multiplier *= modifier;
            } else {
              // FIXED: add to fixed price
              fixedPrice += modifier;
            }
          }
        }
      });
    }
    return { fixedAttributesPrice: fixedPrice, multiplierTotal: multiplier };
  }, [attributes, orderData.attributes]);
  
  // For backward compatibility
  const attributesPrice = fixedAttributesPrice;

  // Calculate unit price (price per item)
  // Formula: (base_price × multiplier) + fixed_attributes
  const unitPrice = useMemo(() => {
    const multipliedBase = Math.round(basePrice * multiplierTotal);
    return multipliedBase + fixedAttributesPrice;
  }, [basePrice, multiplierTotal, fixedAttributesPrice]);

  // Calculate total price:
  // (unit price × quantity) + design price (once) + validation fee (once, if requested)
  const totalPrice = useMemo(() => {
    let total = unitPrice * orderData.quantity;
    // Design price is added once (not multiplied by quantity)
    total += planPrice;
    // Validation fee is added once (not multiplied by quantity)
    if (orderData.wants_validation) {
      total += VALIDATION_PRICE;
    }
    return total;
  }, [unitPrice, orderData.quantity, planPrice, orderData.wants_validation]);

  const canProceed = () => {
    switch (currentStep) {
      case "category":
        return !!orderData.category_id;
      case "attributes":
        if (!attributes || attributes.length === 0) return true;
        return attributes.every((attr) => !!orderData.attributes[attr.id]);
      case "plan":
        return !!orderData.plan_id;
      case "template":
          return !!orderData.template_id;
      case "placeholders":
        if (!placeholders) return true;
        const requiredPlaceholders = placeholders.filter(p => p.is_required);
        return requiredPlaceholders.every(p => !!orderData.placeholder_values[p.id]?.value);
      case "questionnaire":
        if (questionnaire?.sections) {
          const allQuestions = questionnaire.sections.flatMap((s) => s.questions);
          return allQuestions
            .filter((q) => q.is_required)
            .every((q) => !!orderData.questionnaire_answers?.[q.id]);
        }
        return true;
      case "upload":
        return !!orderData.design_file;
      case "validation":
        return true; // Always can proceed from validation step
      case "summary":
        return true;
      case "payment":
        return !!receiptFile; // Must upload receipt to proceed
      default:
        return true;
    }
  };

  const handleNext = () => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < steps.length) {
      setCurrentStep(steps[nextIndex].id);
    }
  };

  const handleBack = () => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(steps[prevIndex].id);
    }
  };

  const handleImageUpload = async (placeholderId: string, file: File) => {
    setUploadingImage(placeholderId);
    try {
      const response = await filesApi.uploadPlaceholderImage(file);
      const imageUrl = response.data.file_url;
      setOrderData({
        ...orderData,
        placeholder_values: {
          ...orderData.placeholder_values,
          [placeholderId]: { type: "IMAGE", value: imageUrl },
        },
      });
      toast.success("تصویر با موفقیت آپلود شد");
    } catch (error) {
      toast.error("خطا در آپلود تصویر");
    } finally {
      setUploadingImage(null);
    }
  };

  const handleReceiptSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
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

  const handleSubmit = async () => {
    if (!user?.id) {
      toast.error("لطفاً ابتدا وارد شوید");
      return;
    }

    if (!receiptFile) {
      toast.error("لطفاً فیش واریزی را آپلود کنید");
      return;
    }

    setIsSubmitting(true);

    try {
      // Map plan characteristics to design_plan enum
      let designPlan: "PUBLIC" | "SEMI_PRIVATE" | "PRIVATE" | "OWN_DESIGN" = "PUBLIC";
      if (selectedPlan) {
        if (selectedPlan.has_templates) {
          designPlan = "PUBLIC";
        } else if (selectedPlan.has_questionnaire) {
          designPlan = "SEMI_PRIVATE";
        } else if (selectedPlan.has_file_upload) {
          designPlan = "PRIVATE";
        }
      }

      // SEMI_PRIVATE and PRIVATE plans don't support validation
      // (design is created by designer, not customer)
      const validationRequested = (designPlan === "SEMI_PRIVATE" || designPlan === "PRIVATE")
        ? false
        : orderData.wants_validation;

      // Convert attributes to the backend format
      const selectedAttributes = Object.entries(orderData.attributes).map(([attrId, optionValue]) => {
        const attr = attributes?.find(a => a.id === attrId);
        const option = attr?.options?.find(o => o.value === optionValue);
        return {
          attribute_id: attrId,
          option_id: option?.id || optionValue,
        };
      });

      // Step 1: Create order
      const orderResponse = await new Promise<{ data: { id: string } }>((resolve, reject) => {
        createOrder({
          data: {
            category_id: orderData.category_id,
            design_plan: designPlan,
            plan_id: orderData.plan_id, // Send actual plan_id to get correct price from database
            selected_attributes: selectedAttributes,
            quantity: orderData.quantity,
            validation_requested: validationRequested,
            template_id: orderData.template_id,
          },
          userId: user.id,
        }, {
          onSuccess: resolve,
          onError: reject,
        });
      });

      const orderId = orderResponse.data.id;

      // Step 2a: Submit questionnaire answers (for SEMI_PRIVATE / PRIVATE plans)
      if (orderData.questionnaire_answers && Object.keys(orderData.questionnaire_answers).length > 0) {
        // Build a lookup of question input types from the loaded questionnaire
        const questionTypeMap: Record<string, string> = {};
        if (questionnaire?.sections) {
          for (const section of questionnaire.sections) {
            for (const q of section.questions) {
              questionTypeMap[q.id] = q.input_type;
            }
          }
        }

        const answers = Object.entries(orderData.questionnaire_answers)
          .filter(([, value]) => value) // skip empty answers
          .map(([questionId, value]) => {
            const inputType = questionTypeMap[questionId] || "TEXT";

            // Map to the correct field based on question type
            if (inputType === "IMAGE_UPLOAD" || inputType === "FILE_UPLOAD") {
              return {
                question_id: questionId,
                answer_file_url: value,
              };
            } else if (inputType === "MULTI_CHOICE") {
              return {
                question_id: questionId,
                answer_values: value.split(",").filter(Boolean),
              };
            } else {
              return {
                question_id: questionId,
                answer_text: value,
              };
            }
          });

        if (answers.length > 0) {
          await ordersApi.submitAnswers(orderId, answers);
        }
      }

      // Step 2b: Save design with placeholder values (if template-based order)
      if (orderData.template_id && Object.keys(orderData.placeholder_values).length > 0) {
        const placeholderValues = Object.entries(orderData.placeholder_values).map(
          ([placeholderId, value]) => ({
            placeholder_id: placeholderId,
            image_url: value.type === "IMAGE" ? value.value : undefined,
            text_value: value.type === "TEXT" ? value.value : undefined,
          })
        );

        await ordersApi.saveDesign(orderId, {
          template_id: orderData.template_id,
          placeholder_values: placeholderValues,
        });
      }

      // Step 3: Initiate payment
      const paymentResponse = await paymentsApi.initiate(orderId);
      const paymentId = paymentResponse.data.id;

      // Step 4: Upload receipt
      await paymentsApi.uploadReceipt(paymentId, receiptFile);

      toast.success("سفارش با موفقیت ثبت شد. رسید پرداخت در حال بررسی است.");
      router.push(`/orders/${orderId}`);
    } catch (error: any) {
      console.error("Error submitting order:", error);
      // Show backend validation errors if available
      const detail = error?.response?.data?.detail;
      if (detail && typeof detail === "object" && !Array.isArray(detail)) {
        // Questionnaire validation errors: { question_id: error_message }
        const messages = Object.values(detail) as string[];
        toast.error(messages.join("\n"), { duration: 6000 });
      } else if (typeof detail === "string") {
        toast.error(detail);
      } else {
        toast.error("خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case "category":
        return (
          <div className="space-y-4">
            <p className="text-muted">محصول مورد نظر خود را انتخاب کنید:</p>
            
            {isLoadingCategories ? (
              <PageLoading />
            ) : categories && categories.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {categories.map((category) => (
                  <Card
                    key={category.id}
                    variant={orderData.category_id === category.id ? "bordered" : "default"}
                    className={cn(
                      "cursor-pointer transition-all hover:border-primary/30",
                      orderData.category_id === category.id && "border-primary border-2 bg-primary-50"
                    )}
                    onClick={() => setOrderData({ 
                      ...orderData, 
                      category_id: category.id, 
                      plan_id: "", 
                      attributes: {},
                      template_id: undefined,
                      placeholder_values: {},
                    })}
                  >
                    <CardContent className="pt-4 text-center">
                      <div className="text-4xl mb-3">{category.icon || "📦"}</div>
                      <h3 className="font-semibold text-foreground mb-1">{category.name_fa}</h3>
                      <p className="text-sm text-muted mb-2">قیمت پایه: {formatPrice(category.base_price)}</p>
                      {orderData.category_id === category.id && (
                        <Badge variant="success">
                          <Check className="w-3 h-3 ml-1" />
                          انتخاب شده
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Package}
                title="محصولی یافت نشد"
                description="در حال حاضر محصولی برای سفارش موجود نیست"
              />
            )}
          </div>
        );

      case "attributes":
        return (
          <div className="space-y-6">
            <p className="text-muted">ویژگی‌های محصول را انتخاب کنید:</p>
            
            {isLoadingAttributes ? (
              <PageLoading />
            ) : attributes && attributes.length > 0 ? (
              attributes.map((attr) => (
                <div key={attr.id}>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    {attr.name_fa}
                  </label>
                  {attr.options && attr.options.length > 0 ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {attr.options.map((option) => {
                        const modifier = Number(option.price_modifier) || 0;
                        const isMultiplier = attr.price_type === "MULTIPLIER";
                        return (
                        <button
                          key={option.id}
                          type="button"
                          onClick={() =>
                            setOrderData({
                              ...orderData,
                              attributes: { ...orderData.attributes, [attr.id]: option.value },
                            })
                          }
                          className={cn(
                            "p-3 rounded-lg border text-sm text-right transition-all",
                            orderData.attributes[attr.id] === option.value
                              ? "border-primary bg-primary-50 text-primary"
                              : "border-border hover:border-primary/30"
                          )}
                        >
                          <span className="block font-medium">{option.label_fa}</span>
                          {modifier > 0 && (
                            <Badge variant={isMultiplier ? "warning" : "success"} className="mt-1 text-xs">
                              {isMultiplier 
                                ? `×${toPersianNumber(modifier.toFixed(2))}` 
                                : `+${formatPrice(modifier)}`}
                            </Badge>
                          )}
                        </button>
                        );
                      })}
                    </div>
                  ) : (
                    <Input
                      value={orderData.attributes[attr.id] || ""}
                      onChange={(e) =>
                        setOrderData({
                          ...orderData,
                          attributes: { ...orderData.attributes, [attr.id]: e.target.value },
                        })
                      }
                      placeholder={`${attr.name_fa} را وارد کنید`}
                    />
                  )}
                </div>
              ))
            ) : (
              <p className="text-center text-muted py-8">
                این محصول نیازی به انتخاب ویژگی ندارد
              </p>
            )}
          </div>
        );

      case "plan":
        return (
          <div className="space-y-4">
            <p className="text-muted">نوع طراحی را انتخاب کنید:</p>
            
            {isLoadingPlans ? (
              <PageLoading />
            ) : plans && plans.length > 0 ? (
              <div className="space-y-4">
                {plans.map((plan) => (
                  <Card
                    key={plan.id}
                    variant={orderData.plan_id === plan.id ? "bordered" : "default"}
                    className={cn(
                      "cursor-pointer transition-all hover:border-primary/30",
                      orderData.plan_id === plan.id && "border-primary border-2 bg-primary-50"
                    )}
                    onClick={() => setOrderData({ 
                      ...orderData, 
                      plan_id: plan.id, 
                      template_id: undefined, 
                      questionnaire_answers: {},
                      placeholder_values: {},
                    })}
                  >
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-foreground">{plan.name_fa}</h3>
                          <p className="text-sm text-muted mt-1">
                            {plan.has_templates && "انتخاب از قالب‌های آماده"}
                            {plan.has_questionnaire && "طراحی بر اساس اطلاعات شما"}
                            {plan.has_file_upload && "آپلود طرح اختصاصی شما"}
                          </p>
                        </div>
                        <div className="text-left">
                          <p className="font-semibold text-primary">{formatPrice(plan.price)}</p>
                          {orderData.plan_id === plan.id && (
                            <Badge variant="success" size="sm" className="mt-1">
                              <Check className="w-3 h-3 ml-1" />
                              انتخاب شده
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Palette}
                title="پلنی یافت نشد"
                description="برای این محصول پلن طراحی تعریف نشده است"
              />
            )}
          </div>
        );

      case "template":
          return (
            <div className="space-y-4">
              <p className="text-muted">یک قالب را انتخاب کنید:</p>
              
              {isLoadingTemplates ? (
                <PageLoading />
              ) : templates && templates.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {templates.map((template) => (
                    <Card
                      key={template.id}
                      variant={orderData.template_id === template.id ? "bordered" : "default"}
                      className={cn(
                        "cursor-pointer transition-all hover:border-primary/30 overflow-hidden",
                        orderData.template_id === template.id && "border-primary border-2"
                      )}
                    onClick={() => setOrderData({ 
                      ...orderData, 
                      template_id: template.id,
                      placeholder_values: {},
                    })}
                    >
                      <div className="aspect-square relative bg-accent">
                        {template.preview_url ? (
                          <ImagePreview
                            src={template.preview_url}
                            alt={template.name_fa}
                            className="w-full h-full"
                            aspectRatio="aspect-square"
                            imageClassName="object-cover"
                            thumbnailSize={300}
                            showDownload={false}
                            downloadFilename={template.name_fa}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <ImageIcon className="w-12 h-12 text-muted" />
                          </div>
                        )}
                        {orderData.template_id === template.id && (
                          <div className="absolute top-2 right-2">
                            <Badge variant="success">
                              <Check className="w-3 h-3" />
                            </Badge>
                          </div>
                        )}
                      </div>
                      <CardContent className="py-3 text-center">
                        <p className="text-sm font-medium">{template.name_fa}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={ImageIcon}
                  title="قالبی یافت نشد"
                  description="برای این پلن قالبی تعریف نشده است"
                />
              )}
            </div>
          );

      case "placeholders":
        return (
          <div className="space-y-6">
            <p className="text-muted">محتوای طرح خود را وارد کنید:</p>
            
            {isLoadingPlaceholders ? (
              <PageLoading />
            ) : placeholders && placeholders.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Preview Section */}
                <div className="order-2 lg:order-1">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">پیش‌نمایش</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="aspect-square relative bg-accent rounded-lg overflow-hidden">
                        {previewUrl ? (
                          <ImagePreview
                            src={previewUrl}
                            alt="پیش‌نمایش طرح نهایی"
                            className="w-full h-full"
                            aspectRatio="aspect-square"
                            imageClassName="object-contain"
                            thumbnailSize={600}
                            showDownload={true}
                            downloadFilename="design-preview"
                          />
                        ) : selectedTemplate?.preview_url ? (
                          <ImagePreview
                            src={selectedTemplate.preview_url}
                            alt={selectedTemplate.name_fa}
                            className="w-full h-full"
                            aspectRatio="aspect-square"
                            imageClassName="object-contain"
                            thumbnailSize={600}
                            showDownload={false}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <div className="text-center text-muted">
                              <ImageIcon className="w-12 h-12 mx-auto mb-2" />
                              <p className="text-sm">پیش‌نمایش پس از تکمیل فیلدها</p>
                            </div>
                          </div>
                        )}
                        {previewMutation.isPending && (
                          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                            <div className="text-white text-sm">در حال ساخت پیش‌نمایش...</div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Form Section */}
                <div className="order-1 lg:order-2 space-y-4">
                  {placeholders
                    .sort((a, b) => a.sort_order - b.sort_order)
                    .map((placeholder) => (
                    <div key={placeholder.id} className="space-y-2">
                      <label className="block text-sm font-medium text-foreground">
                        {placeholder.label_fa}
                        {placeholder.is_required && (
                          <span className="text-danger mr-1">*</span>
                        )}
                      </label>
                      
                      {placeholder.type === "IMAGE" ? (
                        <div
                          className={cn(
                            "border-2 border-dashed rounded-lg p-4 text-center transition-colors",
                            orderData.placeholder_values[placeholder.id]?.value
                              ? "border-success bg-success-light"
                              : "border-border hover:border-primary/30"
                          )}
                        >
                          <input
                            type="file"
                            id={`placeholder-${placeholder.id}`}
                            className="hidden"
                            accept="image/*"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) {
                                handleImageUpload(placeholder.id, file);
                              }
                            }}
                          />
                          <label htmlFor={`placeholder-${placeholder.id}`} className="cursor-pointer block">
                            {uploadingImage === placeholder.id ? (
                              <div className="py-2">
                                <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
                                <p className="text-sm text-muted mt-2">در حال آپلود...</p>
                              </div>
                            ) : orderData.placeholder_values[placeholder.id]?.value ? (
                              <div className="relative">
                                <ImagePreview
                                  src={orderData.placeholder_values[placeholder.id].value}
                                  alt={placeholder.label_fa}
                                  className="w-[100px] h-[100px] mx-auto"
                                  aspectRatio="aspect-square"
                                  thumbnailSize={200}
                                  showDownload={false}
                                  showExpand={true}
                                />
                                <p className="text-xs text-muted mt-2">برای تغییر کلیک کنید</p>
                              </div>
                            ) : (
                              <>
                                <Upload className="w-8 h-8 mx-auto text-muted" />
                                <p className="text-sm text-muted mt-2">آپلود تصویر</p>
                              </>
                            )}
                          </label>
                        </div>
                      ) : (
                        <Input
                          value={orderData.placeholder_values[placeholder.id]?.value || ""}
                          onChange={(e) =>
                            setOrderData({
                              ...orderData,
                              placeholder_values: {
                                ...orderData.placeholder_values,
                                [placeholder.id]: { type: "TEXT", value: e.target.value },
                              },
                            })
                          }
                          placeholder={placeholder.default_value || `${placeholder.label_fa} را وارد کنید`}
                          maxLength={placeholder.max_length || undefined}
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-center text-muted py-8">
                این قالب نیازی به ورود اطلاعات ندارد
              </p>
            )}
          </div>
        );

      case "questionnaire":
          return (
            <div className="space-y-6">
              <p className="text-muted">اطلاعات طراحی را وارد کنید:</p>
              
              {isLoadingQuestionnaire ? (
                <PageLoading />
              ) : questionnaire?.sections && questionnaire.sections.length > 0 ? (
                questionnaire.sections.map((section) => (
                  <Card key={section.id}>
                    <CardHeader>
                      <CardTitle>{section.title_fa}</CardTitle>
                      {section.description_fa && (
                        <p className="text-sm text-muted">{section.description_fa}</p>
                      )}
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {section.questions.map((question) => (
                        <div key={question.id}>
                          <label className="block text-sm font-medium text-foreground mb-2">
                            {question.question_fa}
                            {question.is_required && (
                              <span className="text-danger mr-1">*</span>
                            )}
                          </label>
                          {question.help_text_fa && (
                            <p className="text-xs text-muted mb-1">{question.help_text_fa}</p>
                          )}
                          {question.input_type === "TEXTAREA" ? (
                            <Textarea
                              value={orderData.questionnaire_answers?.[question.id] || ""}
                              onChange={(e) =>
                                setOrderData({
                                  ...orderData,
                                  questionnaire_answers: {
                                    ...orderData.questionnaire_answers,
                                    [question.id]: e.target.value,
                                  },
                                })
                              }
                              placeholder={question.placeholder_fa || `${question.question_fa} را وارد کنید`}
                            />
                          ) : question.input_type === "SINGLE_CHOICE" && question.options?.length > 0 ? (
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                              {question.options.map((option) => (
                                <button
                                  key={option.id}
                                  type="button"
                                  onClick={() =>
                                    setOrderData({
                                      ...orderData,
                                      questionnaire_answers: {
                                        ...orderData.questionnaire_answers,
                                        [question.id]: option.value,
                                      },
                                    })
                                  }
                                  className={cn(
                                    "p-3 rounded-lg border text-sm text-right transition-all",
                                    orderData.questionnaire_answers?.[question.id] === option.value
                                      ? "border-primary bg-primary-50 text-primary"
                                      : "border-border hover:border-primary/30"
                                  )}
                                >
                                  {option.image_url && (
                                    <OptimizedImage
                                      src={getImageUrl(option.image_url) || option.image_url}
                                      alt={option.label_fa}
                                      width={60}
                                      height={60}
                                      className="mx-auto mb-2 rounded"
                                    />
                                  )}
                                  <span className="block font-medium">{option.label_fa}</span>
                                </button>
                              ))}
                            </div>
                          ) : question.input_type === "MULTI_CHOICE" && question.options?.length > 0 ? (
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                              {question.options.map((option) => {
                                const selected = (orderData.questionnaire_answers?.[question.id] || "").split(",").filter(Boolean);
                                const isSelected = selected.includes(option.value);
                                return (
                                  <button
                                    key={option.id}
                                    type="button"
                                    onClick={() => {
                                      const newValues = isSelected
                                        ? selected.filter((v) => v !== option.value)
                                        : [...selected, option.value];
                                      setOrderData({
                                        ...orderData,
                                        questionnaire_answers: {
                                          ...orderData.questionnaire_answers,
                                          [question.id]: newValues.join(","),
                                        },
                                      });
                                    }}
                                    className={cn(
                                      "p-3 rounded-lg border text-sm text-right transition-all",
                                      isSelected
                                        ? "border-primary bg-primary-50 text-primary"
                                        : "border-border hover:border-primary/30"
                                    )}
                                  >
                                    <span className="block font-medium">{option.label_fa}</span>
                                    {isSelected && <Check className="w-4 h-4 text-primary mt-1" />}
                                  </button>
                                );
                              })}
                            </div>
                          ) : question.input_type === "NUMBER" ? (
                            <Input
                              type="number"
                              value={orderData.questionnaire_answers?.[question.id] || ""}
                              onChange={(e) =>
                                setOrderData({
                                  ...orderData,
                                  questionnaire_answers: {
                                    ...orderData.questionnaire_answers,
                                    [question.id]: e.target.value,
                                  },
                                })
                              }
                              placeholder={question.placeholder_fa || `${question.question_fa} را وارد کنید`}
                            />
                          ) : question.input_type === "COLOR_PICKER" ? (
                            <div className="flex items-center gap-3">
                              <input
                                type="color"
                                value={orderData.questionnaire_answers?.[question.id] || "#000000"}
                                onChange={(e) =>
                                  setOrderData({
                                    ...orderData,
                                    questionnaire_answers: {
                                      ...orderData.questionnaire_answers,
                                      [question.id]: e.target.value,
                                    },
                                  })
                                }
                                className="w-12 h-12 border border-border rounded-lg cursor-pointer"
                              />
                              <span className="text-sm text-muted font-mono" dir="ltr">
                                {orderData.questionnaire_answers?.[question.id] || "#000000"}
                              </span>
                            </div>
                          ) : question.input_type === "IMAGE_UPLOAD" ? (
                            <div
                              className={cn(
                                "border-2 border-dashed rounded-lg p-4 text-center transition-colors",
                                orderData.questionnaire_answers?.[question.id]
                                  ? "border-success bg-success-light"
                                  : "border-border hover:border-primary/30"
                              )}
                            >
                              <input
                                type="file"
                                id={`q-upload-${question.id}`}
                                className="hidden"
                                accept="image/*"
                                onChange={async (e) => {
                                  const file = e.target.files?.[0];
                                  if (file) {
                                    try {
                                      const response = await filesApi.uploadPlaceholderImage(file);
                                      setOrderData({
                                        ...orderData,
                                        questionnaire_answers: {
                                          ...orderData.questionnaire_answers,
                                          [question.id]: response.data.file_url,
                                        },
                                      });
                                      toast.success("تصویر آپلود شد");
                                    } catch {
                                      toast.error("خطا در آپلود تصویر");
                                    }
                                  }
                                }}
                              />
                              <label htmlFor={`q-upload-${question.id}`} className="cursor-pointer block">
                                {orderData.questionnaire_answers?.[question.id] ? (
                                  <div>
                                    <ImagePreview
                                      src={orderData.questionnaire_answers[question.id]}
                                      alt={question.question_fa}
                                      className="w-[100px] h-[100px] mx-auto"
                                      aspectRatio="aspect-square"
                                      thumbnailSize={200}
                                      showDownload={false}
                                    />
                                    <p className="text-xs text-muted mt-2">برای تغییر کلیک کنید</p>
                                  </div>
                                ) : (
                                  <>
                                    <Upload className="w-8 h-8 mx-auto text-muted" />
                                    <p className="text-sm text-muted mt-2">آپلود تصویر</p>
                                  </>
                                )}
                              </label>
                            </div>
                          ) : (
                            <Input
                              value={orderData.questionnaire_answers?.[question.id] || ""}
                              onChange={(e) =>
                                setOrderData({
                                  ...orderData,
                                  questionnaire_answers: {
                                    ...orderData.questionnaire_answers,
                                    [question.id]: e.target.value,
                                  },
                                })
                              }
                              placeholder={question.placeholder_fa || `${question.question_fa} را وارد کنید`}
                            />
                          )}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ))
              ) : (
                <p className="text-center text-muted py-8">
                  پرسشنامه‌ای برای این پلن تعریف نشده است
                </p>
              )}
            </div>
          );

      case "upload":
        return (
          <div className="space-y-4">
            <p className="text-muted">فایل طراحی خود را آپلود کنید:</p>
            
            <div
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center transition-colors",
                orderData.design_file
                  ? "border-success bg-success-light"
                  : "border-border hover:border-primary/30"
              )}
            >
              <input
                type="file"
                id="design-file"
                className="hidden"
                accept=".pdf,.ai,.psd,.eps,.svg,.png,.jpg,.jpeg"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setOrderData({ ...orderData, design_file: file });
                  }
                }}
              />
              <label htmlFor="design-file" className="cursor-pointer">
                <Upload className={cn(
                  "w-12 h-12 mx-auto mb-4",
                  orderData.design_file ? "text-success" : "text-muted"
                )} />
                {orderData.design_file ? (
                  <>
                    <p className="font-medium text-foreground">{orderData.design_file.name}</p>
                    <p className="text-sm text-muted mt-1">برای تغییر کلیک کنید</p>
                  </>
                ) : (
                  <>
                    <p className="font-medium text-foreground">فایل را انتخاب کنید یا اینجا رها کنید</p>
                    <p className="text-sm text-muted mt-1">
                      فرمت‌های مجاز: PDF, AI, PSD, EPS, SVG, PNG, JPG
                    </p>
                  </>
                )}
              </label>
            </div>
          </div>
        );

      case "validation":
        return (
          <div className="space-y-6">
            <p className="text-muted">آیا می‌خواهید طرح شما توسط تیم ما اعتبارسنجی شود؟</p>
            
            <div className="space-y-4">
              {/* Yes Option */}
              <Card
                variant={orderData.wants_validation ? "bordered" : "default"}
                className={cn(
                  "cursor-pointer transition-all hover:border-primary/30",
                  orderData.wants_validation && "border-primary border-2 bg-primary-50"
                )}
                onClick={() => setOrderData({ ...orderData, wants_validation: true })}
              >
                <CardContent className="py-4">
                  <div className="flex items-start gap-4">
                    <div className={cn(
                      "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5",
                      orderData.wants_validation ? "border-primary bg-primary" : "border-border"
                    )}>
                      {orderData.wants_validation && <Check className="w-4 h-4 text-white" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-foreground">بله، اعتبارسنجی شود</h3>
                        <Badge variant="primary">+{formatPrice(VALIDATION_PRICE)}</Badge>
                      </div>
                      <ul className="mt-2 space-y-1 text-sm text-muted">
                        <li className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-success" />
                          بررسی توسط تیم متخصص
                        </li>
                        <li className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-success" />
                          اطمینان از کیفیت چاپ
                        </li>
                        <li className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-success" />
                          رفع مشکلات احتمالی قبل از چاپ
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* No Option */}
              <Card
                variant={!orderData.wants_validation ? "bordered" : "default"}
                className={cn(
                  "cursor-pointer transition-all hover:border-primary/30",
                  !orderData.wants_validation && "border-warning border-2 bg-warning-light"
                )}
                onClick={() => setOrderData({ ...orderData, wants_validation: false })}
              >
                <CardContent className="py-4">
                  <div className="flex items-start gap-4">
                    <div className={cn(
                      "w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5",
                      !orderData.wants_validation ? "border-warning bg-warning" : "border-border"
                    )}>
                      {!orderData.wants_validation && <Check className="w-4 h-4 text-white" />}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground">خیر، نیازی نیست</h3>
                      <div className="mt-3 p-3 bg-warning/10 rounded-lg border border-warning/20">
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-foreground">
                            <strong>توجه:</strong> در صورت عدم اعتبارسنجی، مسئولیت کیفیت چاپ و هرگونه مشکل احتمالی به عهده شماست.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      case "summary":
        return (
          <div className="space-y-6">
            <p className="text-muted">جزئیات سفارش خود را بررسی کنید:</p>
            
            <Card>
              <CardContent className="py-4 space-y-4">
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-muted">محصول</span>
                  <span className="font-medium">{selectedCategory?.name_fa}</span>
                </div>
                
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-muted">نوع طراحی</span>
                  <span className="font-medium">{selectedPlan?.name_fa}</span>
                </div>

                {selectedTemplate && (
                  <div className="flex items-center justify-between py-2 border-b border-border">
                    <span className="text-muted">قالب انتخابی</span>
                    <span className="font-medium">{selectedTemplate.name_fa}</span>
                  </div>
                )}

                {attributes && attributes.length > 0 && (
                  <div className="py-2 border-b border-border">
                    <p className="text-muted mb-2">ویژگی‌ها:</p>
                    <div className="space-y-1">
                      {attributes.map((attr) => {
                        const value = orderData.attributes[attr.id];
                        if (!value) return null;
                        const option = attr.options?.find((o) => o.value === value);
                        return (
                          <div key={attr.id} className="flex items-center justify-between text-sm">
                            <span>{attr.name_fa}</span>
                            <span className="font-medium">{option?.label_fa || value}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-muted">اعتبارسنجی</span>
                  <span className={cn("font-medium", orderData.wants_validation ? "text-success" : "text-warning")}>
                    {orderData.wants_validation ? "بله" : "خیر"}
                    {orderData.wants_validation && ` (+${formatPrice(VALIDATION_PRICE)})`}
                  </span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-muted">تعداد</span>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      className="w-8 h-8 flex items-center justify-center rounded-md border border-border hover:bg-muted transition-colors"
                      onClick={() => setOrderData(prev => ({ ...prev, quantity: Math.max(1, prev.quantity - 1) }))}
                      disabled={orderData.quantity <= 1}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                      </svg>
                    </button>
                    <input
                      type="number"
                      min="1"
                      max="1000"
                      value={orderData.quantity}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 1;
                        setOrderData(prev => ({ ...prev, quantity: Math.max(1, Math.min(1000, val)) }));
                      }}
                      className="w-16 text-center border border-border rounded-md py-1 px-2 bg-background"
                    />
                    <button
                      type="button"
                      className="w-8 h-8 flex items-center justify-center rounded-md border border-border hover:bg-muted transition-colors"
                      onClick={() => setOrderData(prev => ({ ...prev, quantity: Math.min(1000, prev.quantity + 1) }))}
                      disabled={orderData.quantity >= 1000}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Price Breakdown */}
                <div className="py-2 border-b border-border space-y-2">
                  <p className="text-muted font-medium mb-3">ریز قیمت واحد:</p>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted">قیمت پایه محصول</span>
                    <span>{formatPrice(basePrice)}</span>
                  </div>
                  
                  {multiplierTotal !== 1 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">ضریب ویژگی‌ها</span>
                      <span>×{toPersianNumber(multiplierTotal.toFixed(2))}</span>
                    </div>
                  )}
                  
                  {multiplierTotal !== 1 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">قیمت پایه × ضریب</span>
                      <span>{formatPrice(Math.round(basePrice * multiplierTotal))}</span>
                    </div>
                  )}
                  
                  {fixedAttributesPrice > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">هزینه ثابت ویژگی‌ها</span>
                      <span>+{formatPrice(fixedAttributesPrice)}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between pt-2 border-t border-dashed border-border">
                    <span className="font-medium">قیمت واحد</span>
                    <span className="font-medium">{formatPrice(unitPrice)}</span>
                  </div>
                </div>

                {/* Total Calculation */}
                <div className="py-2 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted">جمع چاپ ({orderData.quantity} عدد × {formatPrice(unitPrice)})</span>
                    <span>{formatPrice(unitPrice * orderData.quantity)}</span>
                  </div>
                  
                  {planPrice > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">هزینه طراحی ({selectedPlan?.name_fa})</span>
                      <span>{formatPrice(planPrice)}</span>
                    </div>
                  )}
                  
                  {orderData.wants_validation && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">هزینه اعتبارسنجی</span>
                      <span>{formatPrice(VALIDATION_PRICE)}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between pt-2 border-t border-border text-lg">
                  <span className="font-semibold">مبلغ کل</span>
                  <span className="font-bold text-primary">{formatPrice(totalPrice)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case "payment":
        return (
          <div className="space-y-6">
            <p className="text-muted">لطفاً مبلغ سفارش را به شماره کارت زیر واریز کرده و رسید را آپلود کنید:</p>
            
            {/* Amount */}
            <div className="text-center p-4 bg-primary-50 rounded-xl">
              <p className="text-sm text-muted mb-1">مبلغ قابل پرداخت</p>
              <p className="text-3xl font-bold text-primary">
                {formatPrice(totalPrice)}
              </p>
            </div>

            {/* Bank card info */}
            <Card>
              <CardContent className="py-4 space-y-3">
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
              </CardContent>
            </Card>

            {/* Receipt upload */}
            <div>
              <p className="text-sm font-medium text-foreground mb-2">
                آپلود رسید پرداخت <span className="text-danger">*</span>
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
                  onChange={handleReceiptSelect}
                />
                
                {receiptPreview ? (
                  <div className="relative">
                    <OptimizedImage
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
                      className="absolute top-0 right-1/2 translate-x-[100px] p-1 bg-danger text-white rounded-full"
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

            {/* Warning */}
            <div className="p-4 bg-warning-light rounded-xl">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">توجه</p>
                  <p className="text-sm text-muted mt-1">
                    پس از آپلود رسید، سفارش شما ثبت شده و رسید توسط تیم ما بررسی خواهد شد.
                    نتیجه بررسی از طریق پیامک اطلاع‌رسانی می‌شود.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">سفارش جدید</h1>
        <p className="text-muted mt-1">در چند مرحله ساده سفارش خود را ثبت کنید</p>
      </div>

      {/* Progress steps */}
      <div className="flex items-center justify-between overflow-x-auto pb-2">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-shrink-0">
            <div
              className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center transition-colors",
                index <= currentStepIndex
                  ? "bg-primary text-white"
                  : "bg-accent text-muted"
              )}
            >
              {index < currentStepIndex ? (
                <Check className="w-5 h-5" />
              ) : (
                <step.icon className="w-5 h-5" />
              )}
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "w-8 sm:w-12 h-1 mx-1 sm:mx-2",
                  index < currentStepIndex ? "bg-primary" : "bg-accent"
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step title */}
      <div className="text-center">
        <Badge variant="default" size="md">
          مرحله {toPersianNumber(currentStepIndex + 1)} از {toPersianNumber(steps.length)}
        </Badge>
        <h2 className="text-xl font-semibold text-foreground mt-2">
          {steps[currentStepIndex]?.label}
        </h2>
      </div>

      {/* Step content */}
      <Card>
        <CardContent className="py-6">{renderStepContent()}</CardContent>
        <CardFooter className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStepIndex === 0}
            leftIcon={<ArrowRight className="w-4 h-4" />}
          >
            مرحله قبل
          </Button>

          <div className="flex items-center gap-2">
            {unitPrice > 0 && currentStep !== "payment" && (
              <span className="text-sm text-muted hidden sm:block">
                {orderData.quantity > 1 && `${orderData.quantity} عدد × `}
                مبلغ: <strong className="text-primary">{formatPrice(totalPrice)}</strong>
              </span>
            )}
            
            {currentStep === "payment" ? (
              <Button
                variant="primary"
                onClick={handleSubmit}
                isLoading={isSubmitting || isCreatingOrder}
                disabled={!receiptFile}
                rightIcon={<Check className="w-4 h-4" />}
              >
                ثبت سفارش و ارسال رسید
              </Button>
            ) : (
              <Button
                variant="primary"
                onClick={handleNext}
                disabled={!canProceed()}
                rightIcon={<ArrowLeft className="w-4 h-4" />}
              >
                مرحله بعد
              </Button>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
