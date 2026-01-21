"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useCategories, useCategoryAttributes, useCategoryPlans, usePlanTemplates, usePlanQuestionnaire } from "@/hooks/useCatalog";
import { useOrders } from "@/hooks/useOrders";
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
  ChevronDown,
} from "lucide-react";
import { cn, formatPrice, toPersianNumber } from "@/lib/utils";
import toast from "react-hot-toast";

type OrderStep = "category" | "attributes" | "plan" | "design" | "summary";

interface OrderData {
  category_id: string;
  attributes: Record<string, string>;
  plan_id: string;
  template_id?: string;
  questionnaire_answers?: Record<string, string>;
  design_file?: File;
}

const steps: { id: OrderStep; label: string; icon: React.ElementType }[] = [
  { id: "category", label: "انتخاب محصول", icon: Package },
  { id: "attributes", label: "ویژگی‌ها", icon: Palette },
  { id: "plan", label: "نوع طراحی", icon: FileText },
  { id: "design", label: "طراحی", icon: ImageIcon },
  { id: "summary", label: "تأیید نهایی", icon: CreditCard },
];

export default function NewOrderPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<OrderStep>("category");
  const [orderData, setOrderData] = useState<OrderData>({
    category_id: "",
    attributes: {},
    plan_id: "",
  });

  // Fetch data
  const { data: categories, isLoading: isLoadingCategories } = useCategories();
  const { data: attributes, isLoading: isLoadingAttributes } = useCategoryAttributes(orderData.category_id);
  const { data: plans, isLoading: isLoadingPlans } = useCategoryPlans(orderData.category_id);
  const { data: templates, isLoading: isLoadingTemplates } = usePlanTemplates(orderData.plan_id);
  const { data: questionnaire, isLoading: isLoadingQuestionnaire } = usePlanQuestionnaire(orderData.plan_id);
  
  const { createOrder, isCreatingOrder } = useOrders();

  const selectedCategory = categories?.find((c) => c.id === orderData.category_id);
  const selectedPlan = plans?.find((p) => p.id === orderData.plan_id);
  const selectedTemplate = templates?.find((t) => t.id === orderData.template_id);

  // Calculate total price
  const totalPrice = useMemo(() => {
    let price = selectedCategory?.base_price || 0;
    
    // Add plan price
    if (selectedPlan) {
      price += selectedPlan.price;
    }
    
    // Add attribute options prices
    if (attributes) {
      attributes.forEach((attr) => {
        const selectedValue = orderData.attributes[attr.id];
        if (selectedValue && attr.options) {
          const option = attr.options.find((o) => o.value === selectedValue);
          if (option) {
            price += option.extra_price;
          }
        }
      });
    }
    
    return price;
  }, [selectedCategory, selectedPlan, attributes, orderData.attributes]);

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  const canProceed = () => {
    switch (currentStep) {
      case "category":
        return !!orderData.category_id;
      case "attributes":
        if (!attributes) return true;
        // Check if all required attributes are filled
        return attributes.every((attr) => !!orderData.attributes[attr.id]);
      case "plan":
        return !!orderData.plan_id;
      case "design":
        if (selectedPlan?.plan_type === "public") {
          return !!orderData.template_id;
        }
        if (selectedPlan?.plan_type === "private") {
          return !!orderData.design_file;
        }
        // Semi-private: questionnaire answers
        if (questionnaire?.sections) {
          const allQuestions = questionnaire.sections.flatMap((s) => s.questions);
          const requiredAnswered = allQuestions
            .filter((q) => q.is_required)
            .every((q) => !!orderData.questionnaire_answers?.[q.id]);
          return requiredAnswered;
        }
        return true;
      case "summary":
        return true;
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

  const handleSubmit = () => {
    createOrder({
      category_id: orderData.category_id,
      plan_id: orderData.plan_id,
      attributes: orderData.attributes,
      questionnaire_answers: orderData.questionnaire_answers,
      template_id: orderData.template_id,
    }, {
      onSuccess: (data) => {
        router.push(`/orders/${data.data.id}`);
      },
    });
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
                    onClick={() => setOrderData({ ...orderData, category_id: category.id, plan_id: "", attributes: {} })}
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
                      {attr.options.map((option) => (
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
                          {option.extra_price > 0 && (
                            <span className="text-xs text-muted">
                              +{formatPrice(option.extra_price)}
                            </span>
                          )}
                        </button>
                      ))}
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
                    onClick={() => setOrderData({ ...orderData, plan_id: plan.id, template_id: undefined, questionnaire_answers: {} })}
                  >
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-foreground">{plan.name_fa}</h3>
                          <p className="text-sm text-muted mt-1">
                            {plan.plan_type === "public" && "انتخاب از قالب‌های آماده"}
                            {plan.plan_type === "semi_private" && "طراحی بر اساس اطلاعات شما"}
                            {plan.plan_type === "private" && "آپلود طرح اختصاصی شما"}
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

      case "design":
        if (!selectedPlan) return null;

        if (selectedPlan.plan_type === "public") {
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
                      onClick={() => setOrderData({ ...orderData, template_id: template.id })}
                    >
                      <div className="aspect-square relative bg-accent">
                        {template.preview_url ? (
                          <Image
                            src={template.preview_url}
                            alt={template.name_fa}
                            fill
                            className="object-cover"
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
        }

        if (selectedPlan.plan_type === "semi_private") {
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
                            {question.text_fa}
                            {question.is_required && (
                              <span className="text-danger mr-1">*</span>
                            )}
                          </label>
                          {question.input_type === "textarea" ? (
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
                              placeholder={`${question.text_fa} را وارد کنید`}
                            />
                          ) : question.input_type === "select" && question.options ? (
                            <Select
                              options={question.options.map((o) => ({ value: o, label: o }))}
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
                              placeholder="انتخاب کنید"
                            />
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
                              placeholder={`${question.text_fa} را وارد کنید`}
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
        }

        // Private plan - file upload
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

                <div className="flex items-center justify-between py-2 text-lg">
                  <span className="font-semibold">مبلغ کل</span>
                  <span className="font-bold text-primary">{formatPrice(totalPrice)}</span>
                </div>
              </CardContent>
            </Card>
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
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
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
                  "w-full h-1 mx-2",
                  index < currentStepIndex ? "bg-primary" : "bg-accent"
                )}
                style={{ width: "40px" }}
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
          {steps[currentStepIndex].label}
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
            {totalPrice > 0 && (
              <span className="text-sm text-muted hidden sm:block">
                مبلغ: <strong className="text-primary">{formatPrice(totalPrice)}</strong>
              </span>
            )}
            
            {currentStep === "summary" ? (
              <Button
                variant="primary"
                onClick={handleSubmit}
                isLoading={isCreatingOrder}
                rightIcon={<Check className="w-4 h-4" />}
              >
                ثبت سفارش
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

