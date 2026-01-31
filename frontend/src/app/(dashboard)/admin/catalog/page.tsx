"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  PageLoading,
  Input,
  Modal,
  Textarea,
  ImageUpload,
} from "@/components/ui";
import {
  Plus,
  Pencil,
  Trash2,
  ArrowRight,
  FolderOpen,
  Tag,
  Layers,
  Package,
  ChevronLeft,
  ChevronDown,
  ChevronUp,
  MoreVertical,
  Eye,
  EyeOff,
  Settings,
  List,
  FileQuestion,
  LayoutTemplate,
  GripVertical,
  Image,
  Type,
  Hash,
  Calendar,
  Palette,
  Upload,
  CircleDot,
  CheckSquare,
  SlidersHorizontal,
  Maximize2,
} from "lucide-react";
import toast from "react-hot-toast";
import { TemplateEditor } from "@/components/template-editor";
import { toPersianNumber, formatPrice } from "@/lib/utils";

type TabType = "categories" | "products" | "plans" | "attributes" | "questionnaire" | "templates";

interface CategoryFormData {
  slug: string;
  name_fa: string;
  description_fa: string;
  is_active: boolean;
}

interface ProductFormData {
  type: "LABEL" | "INVOICE";
  name: string;
  name_fa: string;
  size: string;
  material?: "PAPER" | "VINYL" | "POLYESTER" | "TRANSPARENT";
  base_price: number;
  min_quantity: number;
  description: string;
  is_active: boolean;
  sort_order: number;
}

interface PlanFormData {
  slug: string;
  name: string;
  name_fa: string;
  category_id: string;
  type: "PUBLIC" | "SEMI_PRIVATE" | "PRIVATE";
  price: number;
  max_revisions: number;
  delivery_days: number;
  description_fa: string;
  is_active: boolean;
  // Plan type flags
  has_questionnaire: boolean;
  has_templates: boolean;
  has_file_upload: boolean;
}

type AttributeInputType = "SELECT" | "MULTI_SELECT" | "NUMBER" | "TEXT";

interface AttributeFormData {
  slug: string;
  name_fa: string;
  input_type: AttributeInputType;
  is_required: boolean;
  min_value?: number;
  max_value?: number;
  default_value?: string;
  sort_order: number;
  is_active: boolean;
}

interface AttributeOptionFormData {
  value: string;
  label_fa: string;
  price_modifier: number;
  sort_order: number;
  is_active: boolean;
}

// Questionnaire Types
type QuestionInputType = 
  | "TEXT" 
  | "TEXTAREA" 
  | "NUMBER" 
  | "SINGLE_CHOICE" 
  | "MULTI_CHOICE" 
  | "IMAGE_UPLOAD" 
  | "FILE_UPLOAD" 
  | "COLOR_PICKER" 
  | "DATE_PICKER" 
  | "SCALE";

interface SectionFormData {
  title_fa: string;
  description_fa: string;
  sort_order: number;
  is_active: boolean;
}

interface QuestionFormData {
  question_fa: string;
  input_type: QuestionInputType;
  is_required: boolean;
  placeholder_fa: string;
  help_text_fa: string;
  min_length?: number;
  max_length?: number;
  min_value?: number;
  max_value?: number;
  depends_on_question_id?: string;
  depends_on_values: string[];
  sort_order: number;
  is_active: boolean;
}

interface QuestionOptionFormData {
  value: string;
  label_fa: string;
  price_modifier: number;
  sort_order: number;
  is_active: boolean;
}

// Template Types
interface TemplateFormData {
  name_fa: string;
  description_fa: string;
  preview_url: string;
  file_url: string;
  image_width?: number;
  image_height?: number;
  placeholder_x?: number;
  placeholder_y?: number;
  placeholder_width?: number;
  placeholder_height?: number;
  placeholder_rotation?: number;
  is_active: boolean;
  // New fields for upload flow
  image_file?: File | null;
  image_preview?: string | null;
  image_placeholder_count: number;
  text_placeholder_count: number;
}

export default function CatalogManagementPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("categories");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Modal states
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<any>(null);
  const [categoryForm, setCategoryForm] = useState<CategoryFormData>({
    slug: "",
    name_fa: "",
    description_fa: "",
    is_active: true,
  });

  // Product modal states
  const [showProductModal, setShowProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any>(null);
  const [productForm, setProductForm] = useState<ProductFormData>({
    type: "LABEL",
    name: "",
    name_fa: "",
    size: "",
    material: undefined,
    base_price: 0,
    min_quantity: 1,
    description: "",
    is_active: true,
    sort_order: 0,
  });

  // Plan modal states
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState<any>(null);
  const [planForm, setPlanForm] = useState<PlanFormData>({
    slug: "",
    name: "",
    name_fa: "",
    category_id: "",
    type: "PUBLIC",
    price: 0,
    max_revisions: 3,
    delivery_days: 3,
    description_fa: "",
    is_active: true,
    has_questionnaire: false,
    has_templates: false,
    has_file_upload: false,
  });

  // Attribute modal states
  const [showAttributeModal, setShowAttributeModal] = useState(false);
  const [editingAttribute, setEditingAttribute] = useState<any>(null);
  const [attributeForm, setAttributeForm] = useState<AttributeFormData>({
    slug: "",
    name_fa: "",
    input_type: "SELECT",
    is_required: true,
    min_value: undefined,
    max_value: undefined,
    default_value: "",
    sort_order: 0,
    is_active: true,
  });

  // Attribute Option modal states
  const [showOptionModal, setShowOptionModal] = useState(false);
  const [editingOption, setEditingOption] = useState<any>(null);
  const [selectedAttributeId, setSelectedAttributeId] = useState<string | null>(null);
  const [optionForm, setOptionForm] = useState<AttributeOptionFormData>({
    value: "",
    label_fa: "",
    price_modifier: 0,
    sort_order: 0,
    is_active: true,
  });

  // Expanded attributes (for showing options)
  const [expandedAttributes, setExpandedAttributes] = useState<Set<string>>(new Set());

  // Questionnaire Builder state
  const [selectedPlanForQuestionnaire, setSelectedPlanForQuestionnaire] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [showSectionModal, setShowSectionModal] = useState(false);
  const [editingSection, setEditingSection] = useState<any>(null);
  const [sectionForm, setSectionForm] = useState<SectionFormData>({
    title_fa: "",
    description_fa: "",
    sort_order: 0,
    is_active: true,
  });

  // Question state
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<any>(null);
  const [questionForm, setQuestionForm] = useState<QuestionFormData>({
    question_fa: "",
    input_type: "TEXT",
    is_required: true,
    placeholder_fa: "",
    help_text_fa: "",
    min_length: undefined,
    max_length: undefined,
    min_value: undefined,
    max_value: undefined,
    depends_on_question_id: undefined,
    depends_on_values: [],
    sort_order: 0,
    is_active: true,
  });

  // Question Option state
  const [showQuestionOptionModal, setShowQuestionOptionModal] = useState(false);
  const [editingQuestionOption, setEditingQuestionOption] = useState<any>(null);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null);
  const [questionOptionForm, setQuestionOptionForm] = useState<QuestionOptionFormData>({
    value: "",
    label_fa: "",
    price_modifier: 0,
    sort_order: 0,
    is_active: true,
  });
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set());

  // Template Gallery state
  const [selectedPlanForTemplates, setSelectedPlanForTemplates] = useState<string | null>(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any>(null);
  // Dynamic Template Editor state
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [templateEditorId, setTemplateEditorId] = useState<string | null>(null);
  const [templateForm, setTemplateForm] = useState<TemplateFormData>({
    name_fa: "",
    description_fa: "",
    preview_url: "",
    file_url: "",
    image_width: undefined,
    image_height: undefined,
    placeholder_x: undefined,
    placeholder_y: undefined,
    placeholder_width: undefined,
    placeholder_height: undefined,
    placeholder_rotation: undefined,
    is_active: true,
    image_file: null,
    image_preview: null,
    image_placeholder_count: 1,
    text_placeholder_count: 0,
  });
  const [isUploadingTemplateImage, setIsUploadingTemplateImage] = useState(false);

  // Generate slug from Persian name
  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[آا]/g, "a")
      .replace(/[ب]/g, "b")
      .replace(/[پ]/g, "p")
      .replace(/[ت]/g, "t")
      .replace(/[ث]/g, "s")
      .replace(/[ج]/g, "j")
      .replace(/[چ]/g, "ch")
      .replace(/[ح]/g, "h")
      .replace(/[خ]/g, "kh")
      .replace(/[د]/g, "d")
      .replace(/[ذ]/g, "z")
      .replace(/[ر]/g, "r")
      .replace(/[ز]/g, "z")
      .replace(/[ژ]/g, "zh")
      .replace(/[س]/g, "s")
      .replace(/[ش]/g, "sh")
      .replace(/[ص]/g, "s")
      .replace(/[ض]/g, "z")
      .replace(/[ط]/g, "t")
      .replace(/[ظ]/g, "z")
      .replace(/[ع]/g, "a")
      .replace(/[غ]/g, "gh")
      .replace(/[ف]/g, "f")
      .replace(/[ق]/g, "gh")
      .replace(/[ک]/g, "k")
      .replace(/[گ]/g, "g")
      .replace(/[ل]/g, "l")
      .replace(/[م]/g, "m")
      .replace(/[ن]/g, "n")
      .replace(/[و]/g, "v")
      .replace(/[ه]/g, "h")
      .replace(/[ی]/g, "y")
      .replace(/[ئ]/g, "")
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
  };

  // Wait for initial auth check
  useEffect(() => {
    const timer = setTimeout(() => setIsChecked(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Redirect non-admin users
  useEffect(() => {
    if (isChecked && !isLoadingUser && !isAdmin) {
      router.push("/");
    }
  }, [isChecked, isLoadingUser, isAdmin, router]);

  // Fetch categories
  const { data: categories, isLoading: isLoadingCategories } = useQuery({
    queryKey: ["adminCategories"],
    queryFn: async () => {
      const response = await adminApi.getCategories();
      return response.data;
    },
    enabled: isAdmin,
  });

  // Fetch products
  const { data: productsData, isLoading: isLoadingProducts } = useQuery({
    queryKey: ["adminProducts"],
    queryFn: async () => {
      const response = await adminApi.getProducts({ active_only: false });
      return response.data;
    },
    enabled: isAdmin && activeTab === "products",
  });

  // Fetch plans for selected category
  const { data: plans, isLoading: isLoadingPlans } = useQuery({
    queryKey: ["adminPlans", selectedCategory],
    queryFn: async () => {
      if (!selectedCategory) return [];
      const response = await adminApi.getPlans(selectedCategory);
      return response.data;
    },
    enabled: isAdmin && activeTab === "plans" && !!selectedCategory,
  });

  // Fetch attributes for selected category
  const { data: attributes, isLoading: isLoadingAttributes } = useQuery({
    queryKey: ["categoryAttributes", selectedCategory],
    queryFn: async () => {
      if (!selectedCategory) return [];
      const response = await adminApi.getAttributes(selectedCategory);
      return response.data;
    },
    enabled: isAdmin && activeTab === "attributes" && !!selectedCategory,
  });

  // Fetch sections for selected plan (questionnaire)
  const { data: sections, isLoading: isLoadingSections } = useQuery({
    queryKey: ["planSections", selectedPlanForQuestionnaire],
    queryFn: async () => {
      if (!selectedPlanForQuestionnaire) return [];
      const response = await adminApi.getPlanSections(selectedPlanForQuestionnaire);
      return response.data;
    },
    enabled: isAdmin && activeTab === "questionnaire" && !!selectedPlanForQuestionnaire,
  });

  // Fetch templates for selected plan
  const { data: templates, isLoading: isLoadingTemplates } = useQuery({
    queryKey: ["planTemplates", selectedPlanForTemplates],
    queryFn: async () => {
      if (!selectedPlanForTemplates) return [];
      const response = await adminApi.getPlanTemplates(selectedPlanForTemplates);
      return response.data;
    },
    enabled: isAdmin && activeTab === "templates" && !!selectedPlanForTemplates,
  });

  // Fetch all plans for questionnaire/templates tabs (from all categories)
  const { data: allPlans, isLoading: isLoadingAllPlans } = useQuery({
    queryKey: ["allPlans", categories],
    queryFn: async () => {
      if (!categories?.length) return [];
      // Fetch plans for each category and combine
      const planPromises = categories.map((cat: any) => 
        adminApi.getPlans(cat.id).then(res => 
          res.data.map((plan: any) => ({ ...plan, category: cat }))
        ).catch(() => [])
      );
      const results = await Promise.all(planPromises);
      return results.flat();
    },
    enabled: isAdmin && (activeTab === "questionnaire" || activeTab === "templates") && !!categories?.length,
  });

  // Create category mutation
  const createCategoryMutation = useMutation({
    mutationFn: (data: CategoryFormData) => adminApi.createCategory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminCategories"] });
      toast.success("دسته‌بندی ایجاد شد");
      closeCategoryModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Update category mutation
  const updateCategoryMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CategoryFormData }) =>
      adminApi.updateCategory(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminCategories"] });
      toast.success("دسته‌بندی به‌روزرسانی شد");
      closeCategoryModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Delete category mutation
  const deleteCategoryMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminCategories"] });
      toast.success("دسته‌بندی حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Category modal helpers
  const openCreateCategoryModal = () => {
    setEditingCategory(null);
    setCategoryForm({ slug: "", name_fa: "", description_fa: "", is_active: true });
    setShowCategoryModal(true);
  };

  const openEditCategoryModal = (category: any) => {
    setEditingCategory(category);
    setCategoryForm({
      slug: category.slug || "",
      name_fa: category.name_fa || category.name || "",
      description_fa: category.description_fa || category.description || "",
      is_active: category.is_active,
    });
    setShowCategoryModal(true);
  };

  const closeCategoryModal = () => {
    setShowCategoryModal(false);
    setEditingCategory(null);
    setCategoryForm({ slug: "", name_fa: "", description_fa: "", is_active: true });
  };

  const handleNameChange = (name: string) => {
    setCategoryForm({
      ...categoryForm,
      name_fa: name,
      slug: editingCategory ? categoryForm.slug : generateSlug(name),
    });
  };

  const handleCategorySubmit = () => {
    if (!categoryForm.name_fa.trim()) {
      toast.error("نام دسته‌بندی الزامی است");
      return;
    }
    if (!categoryForm.slug.trim()) {
      toast.error("شناسه (slug) الزامی است");
      return;
    }

    if (editingCategory) {
      updateCategoryMutation.mutate({ id: editingCategory.id, data: categoryForm });
    } else {
      createCategoryMutation.mutate(categoryForm);
    }
  };

  // Delete product mutation
  const deleteProductMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
      toast.success("محصول حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Create product mutation
  const createProductMutation = useMutation({
    mutationFn: (data: ProductFormData) => adminApi.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
      toast.success("محصول ایجاد شد");
      closeProductModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Update product mutation
  const updateProductMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProductFormData }) =>
      adminApi.updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminProducts"] });
      toast.success("محصول به‌روزرسانی شد");
      closeProductModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Product modal helpers
  const openCreateProductModal = () => {
    setEditingProduct(null);
    setProductForm({
      type: "LABEL",
      name: "",
      name_fa: "",
      size: "",
      material: undefined,
      base_price: 0,
      min_quantity: 1,
      description: "",
      is_active: true,
      sort_order: 0,
    });
    setShowProductModal(true);
  };

  const openEditProductModal = (product: any) => {
    setEditingProduct(product);
    setProductForm({
      type: product.type || "LABEL",
      name: product.name || "",
      name_fa: product.name_fa || product.name || "",
      size: product.size || "",
      material: product.material || undefined,
      base_price: product.base_price || 0,
      min_quantity: product.min_quantity || 1,
      description: product.description || "",
      is_active: product.is_active ?? true,
      sort_order: product.sort_order || 0,
    });
    setShowProductModal(true);
  };

  const closeProductModal = () => {
    setShowProductModal(false);
    setEditingProduct(null);
  };

  const handleProductSubmit = () => {
    if (!productForm.name_fa.trim()) {
      toast.error("نام محصول الزامی است");
      return;
    }
    if (!productForm.size.trim()) {
      toast.error("سایز محصول الزامی است");
      return;
    }
    if (productForm.base_price <= 0) {
      toast.error("قیمت محصول باید بیشتر از صفر باشد");
      return;
    }

    const data = {
      ...productForm,
      name: productForm.name || generateSlug(productForm.name_fa),
    };

    if (editingProduct) {
      updateProductMutation.mutate({ id: editingProduct.id, data });
    } else {
      createProductMutation.mutate(data);
    }
  };

  // Create plan mutation
  const createPlanMutation = useMutation({
    mutationFn: (data: PlanFormData) => adminApi.createPlan(data.category_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPlans"] });
      toast.success("پلن ایجاد شد");
      closePlanModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Update plan mutation
  const updatePlanMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PlanFormData }) =>
      adminApi.updatePlan(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPlans"] });
      toast.success("پلن به‌روزرسانی شد");
      closePlanModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Delete plan mutation
  const deletePlanMutation = useMutation({
    mutationFn: (id: string) => adminApi.deletePlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminPlans"] });
      toast.success("پلن حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Create attribute mutation
  const createAttributeMutation = useMutation({
    mutationFn: async (data: AttributeFormData) => {
      if (!selectedCategory) throw new Error("دسته‌بندی انتخاب نشده");
      const response = await adminApi.createAttribute(selectedCategory, data);
      return response.data; // Return the actual data, not the axios response
    },
    onSuccess: (newAttribute) => {
      // Auto-expand the newly created attribute to show options section
      if (newAttribute?.id) {
        setExpandedAttributes(prev => new Set([...prev, newAttribute.id]));
      }
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("ویژگی ایجاد شد - حالا گزینه‌ها را اضافه کنید");
      closeAttributeModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Update attribute mutation
  const updateAttributeMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AttributeFormData> }) =>
      adminApi.updateAttribute(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("ویژگی به‌روزرسانی شد");
      closeAttributeModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Delete attribute mutation
  const deleteAttributeMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteAttribute(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("ویژگی حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Create attribute option mutation
  const createOptionMutation = useMutation({
    mutationFn: ({ attributeId, data }: { attributeId: string; data: AttributeOptionFormData }) =>
      adminApi.createAttributeOption(attributeId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("گزینه ایجاد شد");
      closeOptionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Update attribute option mutation
  const updateOptionMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AttributeOptionFormData> }) =>
      adminApi.updateAttributeOption(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("گزینه به‌روزرسانی شد");
      closeOptionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Delete attribute option mutation
  const deleteOptionMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteAttributeOption(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categoryAttributes", selectedCategory] });
      toast.success("گزینه حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // ============ Section Mutations ============
  const createSectionMutation = useMutation({
    mutationFn: async (data: SectionFormData) => {
      if (!selectedPlanForQuestionnaire) throw new Error("پلن انتخاب نشده");
      const response = await adminApi.createSection(selectedPlanForQuestionnaire, data);
      return response.data;
    },
    onSuccess: (newSection) => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      if (newSection?.id) {
        setExpandedSections(prev => new Set([...prev, newSection.id]));
      }
      toast.success("بخش ایجاد شد - حالا سوالات را اضافه کنید");
      closeSectionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const updateSectionMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<SectionFormData> }) =>
      adminApi.updateSection(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("بخش به‌روزرسانی شد");
      closeSectionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const deleteSectionMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteSection(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("بخش حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // ============ Question Mutations ============
  const createQuestionMutation = useMutation({
    mutationFn: async ({ sectionId, data }: { sectionId: string; data: any }) => {
      const response = await adminApi.createQuestion(sectionId, data);
      return response.data;
    },
    onSuccess: (newQuestion) => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      if (newQuestion?.id && (newQuestion.input_type === "SINGLE_CHOICE" || newQuestion.input_type === "MULTI_CHOICE")) {
        setExpandedQuestions(prev => new Set([...prev, newQuestion.id]));
      }
      toast.success("سوال ایجاد شد");
      closeQuestionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const updateQuestionMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      adminApi.updateQuestion(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("سوال به‌روزرسانی شد");
      closeQuestionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const deleteQuestionMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteQuestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("سوال حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // ============ Question Option Mutations ============
  const createQuestionOptionMutation = useMutation({
    mutationFn: ({ questionId, data }: { questionId: string; data: QuestionOptionFormData }) =>
      adminApi.createQuestionOption(questionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("گزینه ایجاد شد");
      closeQuestionOptionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const updateQuestionOptionMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<QuestionOptionFormData> }) =>
      adminApi.updateQuestionOption(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("گزینه به‌روزرسانی شد");
      closeQuestionOptionModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const deleteQuestionOptionMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteQuestionOption(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planSections", selectedPlanForQuestionnaire] });
      toast.success("گزینه حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // ============ Template Mutations ============
  const createTemplateMutation = useMutation({
    mutationFn: async (data: TemplateFormData) => {
      if (!selectedPlanForTemplates) throw new Error("پلن انتخاب نشده");
      const response = await adminApi.createTemplate(selectedPlanForTemplates, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planTemplates", selectedPlanForTemplates] });
      toast.success("قالب ایجاد شد");
      closeTemplateModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const updateTemplateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TemplateFormData> }) =>
      adminApi.updateTemplate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planTemplates", selectedPlanForTemplates] });
      toast.success("قالب به‌روزرسانی شد");
      closeTemplateModal();
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  const deleteTemplateMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planTemplates", selectedPlanForTemplates] });
      toast.success("قالب حذف شد");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error));
    },
  });

  // Plan modal helpers
  const openCreatePlanModal = () => {
    setEditingPlan(null);
    setPlanForm({
      slug: "",
      name: "",
      name_fa: "",
      category_id: selectedCategory || "",
      type: "PUBLIC",
      price: 0,
      max_revisions: 3,
      delivery_days: 3,
      description_fa: "",
      is_active: true,
      has_questionnaire: false,
      has_templates: true, // Default for PUBLIC
      has_file_upload: false,
    });
    setShowPlanModal(true);
  };

  const openEditPlanModal = (plan: any) => {
    setEditingPlan(plan);
    setPlanForm({
      slug: plan.slug || "",
      name: plan.name || "",
      name_fa: plan.name_fa || plan.name || "",
      category_id: plan.category_id || selectedCategory || "",
      type: plan.type || "PUBLIC",
      price: plan.price || 0,
      max_revisions: plan.max_revisions || 3,
      delivery_days: plan.delivery_days || 3,
      description_fa: plan.description_fa || plan.description || "",
      is_active: plan.is_active,
      has_questionnaire: plan.has_questionnaire ?? false,
      has_templates: plan.has_templates ?? false,
      has_file_upload: plan.has_file_upload ?? false,
    });
    setShowPlanModal(true);
  };

  const closePlanModal = () => {
    setShowPlanModal(false);
    setEditingPlan(null);
  };

  const handlePlanSubmit = () => {
    if (!planForm.name_fa.trim()) {
      toast.error("نام پلن الزامی است");
      return;
    }

    // Auto-generate slug from name_fa if not provided
    const slug = planForm.slug.trim() || generateSlug(planForm.name_fa);
    if (!slug) {
      toast.error("شناسه (slug) الزامی است");
      return;
    }

    const data = {
      ...planForm,
      slug,
      name: planForm.name || generateSlug(planForm.name_fa),
      category_id: selectedCategory || planForm.category_id,
    };

    if (editingPlan) {
      updatePlanMutation.mutate({ id: editingPlan.id, data });
    } else {
      createPlanMutation.mutate(data);
    }
  };

  // Attribute modal helpers
  const openCreateAttributeModal = () => {
    setEditingAttribute(null);
    setAttributeForm({
      slug: "",
      name_fa: "",
      input_type: "SELECT",
      is_required: true,
      min_value: undefined,
      max_value: undefined,
      default_value: "",
      sort_order: 0,
      is_active: true,
    });
    setShowAttributeModal(true);
  };

  const openEditAttributeModal = (attribute: any) => {
    setEditingAttribute(attribute);
    setAttributeForm({
      slug: attribute.slug || "",
      name_fa: attribute.name_fa || "",
      input_type: attribute.input_type || "SELECT",
      is_required: attribute.is_required ?? true,
      min_value: attribute.min_value,
      max_value: attribute.max_value,
      default_value: attribute.default_value || "",
      sort_order: attribute.sort_order || 0,
      is_active: attribute.is_active ?? true,
    });
    setShowAttributeModal(true);
  };

  const closeAttributeModal = () => {
    setShowAttributeModal(false);
    setEditingAttribute(null);
  };

  const handleAttributeNameChange = (name: string) => {
    setAttributeForm({
      ...attributeForm,
      name_fa: name,
      slug: editingAttribute ? attributeForm.slug : generateSlug(name),
    });
  };

  const handleAttributeSubmit = () => {
    if (!attributeForm.name_fa.trim()) {
      toast.error("نام ویژگی الزامی است");
      return;
    }
    if (!attributeForm.slug.trim()) {
      toast.error("شناسه (slug) الزامی است");
      return;
    }

    if (editingAttribute) {
      updateAttributeMutation.mutate({ id: editingAttribute.id, data: attributeForm });
    } else {
      createAttributeMutation.mutate(attributeForm);
    }
  };

  // Option modal helpers
  const openCreateOptionModal = (attributeId: string) => {
    setSelectedAttributeId(attributeId);
    setEditingOption(null);
    setOptionForm({
      value: "",
      label_fa: "",
      price_modifier: 0,
      sort_order: 0,
      is_active: true,
    });
    setShowOptionModal(true);
  };

  const openEditOptionModal = (attributeId: string, option: any) => {
    setSelectedAttributeId(attributeId);
    setEditingOption(option);
    setOptionForm({
      value: option.value || "",
      label_fa: option.label_fa || "",
      price_modifier: option.price_modifier || 0,
      sort_order: option.sort_order || 0,
      is_active: option.is_active ?? true,
    });
    setShowOptionModal(true);
  };

  const closeOptionModal = () => {
    setShowOptionModal(false);
    setEditingOption(null);
    setSelectedAttributeId(null);
  };

  const handleOptionValueChange = (label: string) => {
    setOptionForm({
      ...optionForm,
      label_fa: label,
      value: editingOption ? optionForm.value : generateSlug(label),
    });
  };

  // Get question type label helper
  const getQuestionTypeLabel = (type: QuestionInputType): string => {
    const labels: Record<QuestionInputType, string> = {
      TEXT: "متن کوتاه",
      TEXTAREA: "متن بلند",
      NUMBER: "عدد",
      SINGLE_CHOICE: "تک انتخابی",
      MULTI_CHOICE: "چند انتخابی",
      IMAGE_UPLOAD: "آپلود تصویر",
      FILE_UPLOAD: "آپلود فایل",
      COLOR_PICKER: "انتخاب رنگ",
      DATE_PICKER: "انتخاب تاریخ",
      SCALE: "مقیاس",
    };
    return labels[type] || type;
  };

  const handleOptionSubmit = () => {
    if (!optionForm.label_fa.trim()) {
      toast.error("عنوان گزینه الزامی است");
      return;
    }
    if (!optionForm.value.trim()) {
      toast.error("مقدار گزینه الزامی است");
      return;
    }
    if (!selectedAttributeId) {
      toast.error("ویژگی انتخاب نشده");
      return;
    }

    if (editingOption) {
      updateOptionMutation.mutate({ id: editingOption.id, data: optionForm });
    } else {
      createOptionMutation.mutate({ attributeId: selectedAttributeId, data: optionForm });
    }
  };

  // Toggle attribute expansion
  const toggleAttributeExpansion = (attributeId: string) => {
    setExpandedAttributes(prev => {
      const next = new Set(prev);
      if (next.has(attributeId)) {
        next.delete(attributeId);
      } else {
        next.add(attributeId);
      }
      return next;
    });
  };

  // ============ Section Modal Helpers ============
  const openCreateSectionModal = () => {
    setEditingSection(null);
    setSectionForm({
      title_fa: "",
      description_fa: "",
      sort_order: sections?.length ?? 0,
      is_active: true,
    });
    setShowSectionModal(true);
  };

  const openEditSectionModal = (section: any) => {
    setEditingSection(section);
    setSectionForm({
      title_fa: section.title_fa || "",
      description_fa: section.description_fa || "",
      sort_order: section.sort_order ?? 0,
      is_active: section.is_active ?? true,
    });
    setShowSectionModal(true);
  };

  const closeSectionModal = () => {
    setShowSectionModal(false);
    setEditingSection(null);
  };

  const handleSectionSubmit = () => {
    if (!sectionForm.title_fa.trim()) {
      toast.error("عنوان بخش الزامی است");
      return;
    }
    if (editingSection) {
      updateSectionMutation.mutate({ id: editingSection.id, data: sectionForm });
    } else {
      createSectionMutation.mutate(sectionForm);
    }
  };

  const toggleSectionExpansion = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  };

  // ============ Question Modal Helpers ============
  const openCreateQuestionModal = (sectionId: string) => {
    setSelectedSectionId(sectionId);
    setEditingQuestion(null);
    setQuestionForm({
      question_fa: "",
      input_type: "TEXT",
      is_required: true,
      placeholder_fa: "",
      help_text_fa: "",
      min_length: undefined,
      max_length: undefined,
      min_value: undefined,
      max_value: undefined,
      depends_on_question_id: undefined,
      depends_on_values: [],
      sort_order: 0,
      is_active: true,
    });
    setShowQuestionModal(true);
  };

  const openEditQuestionModal = (sectionId: string, question: any) => {
    setSelectedSectionId(sectionId);
    setEditingQuestion(question);
    setQuestionForm({
      question_fa: question.question_fa || "",
      input_type: question.input_type || "TEXT",
      is_required: question.is_required ?? true,
      placeholder_fa: question.placeholder_fa || "",
      help_text_fa: question.help_text_fa || "",
      min_length: question.validation_rules?.min_length,
      max_length: question.validation_rules?.max_length,
      min_value: question.validation_rules?.min_value,
      max_value: question.validation_rules?.max_value,
      depends_on_question_id: question.depends_on_question_id,
      depends_on_values: question.depends_on_values || [],
      sort_order: question.sort_order ?? 0,
      is_active: question.is_active ?? true,
    });
    setShowQuestionModal(true);
  };

  const closeQuestionModal = () => {
    setShowQuestionModal(false);
    setEditingQuestion(null);
    setSelectedSectionId(null);
  };

  const handleQuestionSubmit = () => {
    if (!questionForm.question_fa.trim()) {
      toast.error("متن سوال الزامی است");
      return;
    }
    if (!selectedSectionId) {
      toast.error("بخش انتخاب نشده");
      return;
    }

    const data: any = {
      question_fa: questionForm.question_fa,
      input_type: questionForm.input_type,
      is_required: questionForm.is_required,
      placeholder_fa: questionForm.placeholder_fa || null,
      help_text_fa: questionForm.help_text_fa || null,
      sort_order: questionForm.sort_order,
      is_active: questionForm.is_active,
    };

    // Add validation rules if any
    const validationRules: any = {};
    if (questionForm.min_length !== undefined) validationRules.min_length = questionForm.min_length;
    if (questionForm.max_length !== undefined) validationRules.max_length = questionForm.max_length;
    if (questionForm.min_value !== undefined) validationRules.min_value = questionForm.min_value;
    if (questionForm.max_value !== undefined) validationRules.max_value = questionForm.max_value;
    if (Object.keys(validationRules).length > 0) {
      data.validation_rules = validationRules;
    }

    // Add conditional logic if any
    if (questionForm.depends_on_question_id) {
      data.depends_on_question_id = questionForm.depends_on_question_id;
      data.depends_on_values = questionForm.depends_on_values;
    }

    if (editingQuestion) {
      updateQuestionMutation.mutate({ id: editingQuestion.id, data });
    } else {
      createQuestionMutation.mutate({ sectionId: selectedSectionId, data });
    }
  };

  const toggleQuestionExpansion = (questionId: string) => {
    setExpandedQuestions(prev => {
      const next = new Set(prev);
      if (next.has(questionId)) {
        next.delete(questionId);
      } else {
        next.add(questionId);
      }
      return next;
    });
  };

  // ============ Question Option Modal Helpers ============
  const openCreateQuestionOptionModal = (questionId: string) => {
    setSelectedQuestionId(questionId);
    setEditingQuestionOption(null);
    setQuestionOptionForm({
      value: "",
      label_fa: "",
      price_modifier: 0,
      sort_order: 0,
      is_active: true,
    });
    setShowQuestionOptionModal(true);
  };

  const openEditQuestionOptionModal = (questionId: string, option: any) => {
    setSelectedQuestionId(questionId);
    setEditingQuestionOption(option);
    setQuestionOptionForm({
      value: option.value || "",
      label_fa: option.label_fa || "",
      price_modifier: option.price_modifier ?? 0,
      sort_order: option.sort_order ?? 0,
      is_active: option.is_active ?? true,
    });
    setShowQuestionOptionModal(true);
  };

  const closeQuestionOptionModal = () => {
    setShowQuestionOptionModal(false);
    setEditingQuestionOption(null);
    setSelectedQuestionId(null);
  };

  const handleQuestionOptionSubmit = () => {
    if (!questionOptionForm.label_fa.trim()) {
      toast.error("عنوان گزینه الزامی است");
      return;
    }
    if (!questionOptionForm.value.trim()) {
      toast.error("مقدار گزینه الزامی است");
      return;
    }
    if (!selectedQuestionId) {
      toast.error("سوال انتخاب نشده");
      return;
    }

    if (editingQuestionOption) {
      updateQuestionOptionMutation.mutate({ id: editingQuestionOption.id, data: questionOptionForm });
    } else {
      createQuestionOptionMutation.mutate({ questionId: selectedQuestionId, data: questionOptionForm });
    }
  };

  // ============ Template Modal Helpers ============
  const openCreateTemplateModal = () => {
    setEditingTemplate(null);
    setTemplateForm({
      name_fa: "",
      description_fa: "",
      preview_url: "",
      file_url: "",
      image_width: undefined,
      image_height: undefined,
      placeholder_x: undefined,
      placeholder_y: undefined,
      placeholder_width: undefined,
      placeholder_height: undefined,
      placeholder_rotation: undefined,
      is_active: true,
      image_file: null,
      image_preview: null,
      image_placeholder_count: 1,
      text_placeholder_count: 0,
    });
    setShowTemplateModal(true);
  };

  const openEditTemplateModal = (template: any) => {
    setEditingTemplate(template);
    setTemplateForm({
      name_fa: template.name_fa || "",
      description_fa: template.description_fa || "",
      preview_url: template.preview_url || "",
      file_url: template.file_url || "",
      image_width: template.image_width,
      image_height: template.image_height,
      placeholder_x: template.placeholder_x,
      placeholder_y: template.placeholder_y,
      placeholder_width: template.placeholder_width,
      placeholder_height: template.placeholder_height,
      placeholder_rotation: template.placeholder_rotation,
      is_active: template.is_active ?? true,
      image_file: null,
      image_preview: template.file_url || template.preview_url || null,
      image_placeholder_count: template.placeholders?.filter((p: any) => p.type === "IMAGE")?.length || 1,
      text_placeholder_count: template.placeholders?.filter((p: any) => p.type === "TEXT")?.length || 0,
    });
    setShowTemplateModal(true);
  };

  const closeTemplateModal = () => {
    setShowTemplateModal(false);
    setEditingTemplate(null);
  };

  const handleTemplateSubmit = async () => {
    if (!templateForm.name_fa.trim()) {
      toast.error("نام قالب الزامی است");
      return;
    }

    // For new templates, image is required
    if (!editingTemplate && !templateForm.image_file && !templateForm.file_url) {
      toast.error("آپلود تصویر قالب الزامی است");
      return;
    }

    try {
      let file_url = templateForm.file_url;
      let preview_url = templateForm.preview_url;
      let image_width = templateForm.image_width;
      let image_height = templateForm.image_height;

      // Upload image if a new file was selected
      if (templateForm.image_file) {
        setIsUploadingTemplateImage(true);
        const uploadResponse = await adminApi.uploadTemplateImage(templateForm.image_file);
        const uploadData = uploadResponse.data;
        file_url = uploadData.file_url;
        preview_url = uploadData.preview_url;
        image_width = uploadData.width;
        image_height = uploadData.height;
        setIsUploadingTemplateImage(false);
      }

      const templateData = {
        name_fa: templateForm.name_fa,
        description_fa: templateForm.description_fa,
        file_url,
        preview_url,
        image_width,
        image_height,
        is_active: templateForm.is_active,
      };

      if (editingTemplate) {
        // Just update the template
        await updateTemplateMutation.mutateAsync({ id: editingTemplate.id, data: templateData });
      } else {
        // Create template
        if (!selectedPlanForTemplates) {
          toast.error("پلن انتخاب نشده");
          return;
        }
        const response = await adminApi.createTemplate(selectedPlanForTemplates, templateData);
        const newTemplate = response.data;

        // Create placeholders based on counts
        const placeholderPromises: Promise<any>[] = [];
        
        // Create image placeholders
        for (let i = 0; i < templateForm.image_placeholder_count; i++) {
          placeholderPromises.push(
            adminApi.createPlaceholder(newTemplate.id, {
              type: "IMAGE",
              name: `image_${i + 1}`,
              label_fa: `تصویر ${i + 1}`,
              x: 50 + (i * 30),
              y: 50 + (i * 30),
              width: 200,
              height: 200,
              rotation: 0,
              sort_order: i,
              is_active: true,
            })
          );
        }
        
        // Create text placeholders
        for (let i = 0; i < templateForm.text_placeholder_count; i++) {
          placeholderPromises.push(
            adminApi.createPlaceholder(newTemplate.id, {
              type: "TEXT",
              name: `text_${i + 1}`,
              label_fa: `متن ${i + 1}`,
              x: 50,
              y: 300 + (i * 60),
              width: 300,
              height: 40,
              rotation: 0,
              font_size: 24,
              font_color: "#000000",
              text_align: "CENTER",
              sort_order: templateForm.image_placeholder_count + i,
              is_active: true,
            })
          );
        }

        if (placeholderPromises.length > 0) {
          await Promise.all(placeholderPromises);
        }

        // Refresh and open editor
        queryClient.invalidateQueries({ queryKey: ["planTemplates", selectedPlanForTemplates] });
        toast.success("قالب ایجاد شد - در حال باز کردن ویرایشگر...");
        closeTemplateModal();
        
        // Open the template editor for positioning
        setTemplateEditorId(newTemplate.id);
        setShowTemplateEditor(true);
      }
    } catch (error) {
      setIsUploadingTemplateImage(false);
      toast.error(getErrorMessage(error));
    }
  };

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const tabs = [
    { id: "categories" as TabType, label: "دسته‌بندی‌ها", icon: FolderOpen, count: categories?.length ?? 0 },
    { id: "products" as TabType, label: "محصولات", icon: Package, count: productsData?.items?.length ?? 0 },
    { id: "plans" as TabType, label: "پلن‌های طراحی", icon: Layers, count: 0 },
    { id: "attributes" as TabType, label: "ویژگی‌ها", icon: Settings, count: attributes?.length ?? 0 },
    { id: "questionnaire" as TabType, label: "پرسشنامه", icon: FileQuestion, count: sections?.length ?? 0 },
    { id: "templates" as TabType, label: "قالب‌ها", icon: LayoutTemplate, count: templates?.length ?? 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/admin"
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-foreground">مدیریت کاتالوگ</h1>
            <p className="text-muted mt-1">
              دسته‌بندی‌ها، محصولات و پلن‌های طراحی
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-primary text-white"
                : "text-muted hover:bg-accent"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
            <span className={`px-2 py-0.5 rounded-full text-xs ${
              activeTab === tab.id ? "bg-white/20" : "bg-accent"
            }`}>
              {toPersianNumber(tab.count)}
            </span>
          </button>
        ))}
      </div>

      {/* Categories Tab */}
      {activeTab === "categories" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FolderOpen className="w-5 h-5" />
              دسته‌بندی‌ها
            </CardTitle>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={openCreateCategoryModal}
            >
              دسته‌بندی جدید
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingCategories ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-accent rounded-lg animate-pulse" />
                ))}
              </div>
            ) : !categories?.length ? (
              <div className="text-center py-12 text-muted">
                <FolderOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">دسته‌بندی‌ای یافت نشد</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={openCreateCategoryModal}
                >
                  ایجاد اولین دسته‌بندی
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {categories.map((category: any) => (
                  <div
                    key={category.id}
                    className="flex items-center justify-between p-4 rounded-xl border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                        <FolderOpen className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{category.name_fa || category.name}</p>
                        <p className="text-sm text-muted">{category.description_fa || category.description || "بدون توضیح"}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        category.is_active 
                          ? "bg-success-light text-success" 
                          : "bg-muted/20 text-muted"
                      }`}>
                        {category.is_active ? "فعال" : "غیرفعال"}
                      </span>
                      <button 
                        onClick={() => openEditCategoryModal(category)}
                        className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => deleteCategoryMutation.mutate(category.id)}
                        className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Products Tab */}
      {activeTab === "products" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              محصولات
            </CardTitle>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={openCreateProductModal}
            >
              محصول جدید
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingProducts ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-16 bg-accent rounded-lg animate-pulse" />
                ))}
              </div>
            ) : !productsData?.items?.length ? (
              <div className="text-center py-12 text-muted">
                <Package className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">محصولی یافت نشد</p>
              </div>
            ) : (
              <div className="space-y-3">
                {productsData.items.map((product: any) => (
                  <div
                    key={product.id}
                    className="flex items-center justify-between p-4 rounded-xl border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                        <Package className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{product.name}</p>
                        <div className="flex items-center gap-3 text-sm text-muted mt-1">
                          <span>{product.type}</span>
                          <span>•</span>
                          <span>{product.size}</span>
                          <span>•</span>
                          <span>{formatPrice(product.base_price)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        product.is_active 
                          ? "bg-success-light text-success" 
                          : "bg-muted/20 text-muted"
                      }`}>
                        {product.is_active ? "فعال" : "غیرفعال"}
                      </span>
                      <button 
                        onClick={() => openEditProductModal(product)}
                        className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => deleteProductMutation.mutate(product.id)}
                        className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Plans Tab */}
      {activeTab === "plans" && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Category selector */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">انتخاب دسته‌بندی</CardTitle>
            </CardHeader>
            <CardContent className="p-2">
              {isLoadingCategories ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-10 bg-accent rounded animate-pulse" />
                  ))}
                </div>
              ) : (
                <div className="space-y-1">
                  {categories?.map((category: any) => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full flex items-center gap-2 p-3 rounded-lg text-sm transition-colors ${
                        selectedCategory === category.id
                          ? "bg-primary text-white"
                          : "hover:bg-accent"
                      }`}
                    >
                      <FolderOpen className="w-4 h-4" />
                      {category.name_fa || category.name}
                      <ChevronLeft className="w-4 h-4 mr-auto" />
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Plans list */}
          <Card className="lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Layers className="w-5 h-5" />
                پلن‌های طراحی
                {selectedCategory && (
                  <span className="text-sm font-normal text-muted">
                    ({categories?.find((c: any) => c.id === selectedCategory)?.name_fa})
                  </span>
                )}
              </CardTitle>
              {selectedCategory && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={openCreatePlanModal}
                >
                  پلن جدید
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {!selectedCategory ? (
                <div className="text-center py-12 text-muted">
                  <Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>یک دسته‌بندی را از سمت راست انتخاب کنید</p>
                </div>
              ) : isLoadingPlans ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-20 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : !plans?.length ? (
                <div className="text-center py-12 text-muted">
                  <Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>پلنی برای این دسته‌بندی یافت نشد</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {plans.map((plan: any) => (
                    <div
                      key={plan.id}
                      className="flex items-center justify-between p-4 rounded-xl border border-border hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          plan.type === "PUBLIC" ? "bg-success-light" :
                          plan.type === "SEMI_PRIVATE" ? "bg-warning-light" :
                          "bg-primary-50"
                        }`}>
                          <Layers className={`w-6 h-6 ${
                            plan.type === "PUBLIC" ? "text-success" :
                            plan.type === "SEMI_PRIVATE" ? "text-warning" :
                            "text-primary"
                          }`} />
                        </div>
                        <div>
                          <p className="font-medium text-foreground">{plan.name}</p>
                          <div className="flex items-center gap-3 text-sm text-muted mt-1">
                            <span>{plan.type}</span>
                            <span>•</span>
                            <span>{formatPrice(plan.price)}</span>
                            {plan.max_revisions && (
                              <>
                                <span>•</span>
                                <span>{toPersianNumber(plan.max_revisions)} اصلاح</span>
                              </>
                            )}
                          </div>
                          {/* Plan type badges */}
                          <div className="flex items-center gap-2 mt-2">
                            {plan.has_questionnaire && (
                              <span className="px-2 py-0.5 rounded text-xs bg-warning-light text-warning">
                                پرسشنامه
                              </span>
                            )}
                            {plan.has_templates && (
                              <span className="px-2 py-0.5 rounded text-xs bg-success-light text-success">
                                قالب‌ها
                              </span>
                            )}
                            {plan.has_file_upload && (
                              <span className="px-2 py-0.5 rounded text-xs bg-primary-50 text-primary">
                                آپلود
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          plan.is_active 
                            ? "bg-success-light text-success" 
                            : "bg-muted/20 text-muted"
                        }`}>
                          {plan.is_active ? "فعال" : "غیرفعال"}
                        </span>
                        <button 
                          onClick={() => openEditPlanModal(plan)}
                          className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => deletePlanMutation.mutate(plan.id)}
                          className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Attributes Tab */}
      {activeTab === "attributes" && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Category selector */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">انتخاب دسته‌بندی</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {isLoadingCategories ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-10 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : !categories?.length ? (
                <p className="text-sm text-muted text-center py-4">
                  دسته‌بندی‌ای یافت نشد
                </p>
              ) : (
                categories.map((cat: any) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`w-full text-right p-3 rounded-lg text-sm transition-colors ${
                      selectedCategory === cat.id
                        ? "bg-primary text-white"
                        : "hover:bg-accent text-foreground"
                    }`}
                  >
                    {cat.name_fa || cat.name}
                  </button>
                ))
              )}
            </CardContent>
          </Card>

          {/* Attributes list */}
          <Card className="lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                ویژگی‌های دسته‌بندی
                {selectedCategory && (
                  <span className="text-sm font-normal text-muted">
                    ({categories?.find((c: any) => c.id === selectedCategory)?.name_fa})
                  </span>
                )}
              </CardTitle>
              {selectedCategory && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={openCreateAttributeModal}
                >
                  ویژگی جدید
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {!selectedCategory ? (
                <div className="text-center py-12 text-muted">
                  <Settings className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>ابتدا یک دسته‌بندی انتخاب کنید</p>
                </div>
              ) : isLoadingAttributes ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-20 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : !attributes?.length ? (
                <div className="text-center py-12 text-muted">
                  <Settings className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">ویژگی‌ای یافت نشد</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    leftIcon={<Plus className="w-4 h-4" />}
                    onClick={openCreateAttributeModal}
                  >
                    ایجاد اولین ویژگی
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Helper text */}
                  <div className="p-3 rounded-lg bg-info-light/30 border border-info/20 text-sm text-info">
                    <p className="font-medium mb-1">راهنما:</p>
                    <p>۱. روی هر ویژگی کلیک کنید تا گزینه‌هایش نمایش داده شود</p>
                    <p>۲. برای ویژگی‌های انتخابی، گزینه‌ها را با قیمت اضافه تعریف کنید</p>
                  </div>
                  {attributes.map((attr: any) => (
                    <div
                      key={attr.id}
                      className="border border-border rounded-xl overflow-hidden"
                    >
                      {/* Attribute header */}
                      <div 
                        className="flex items-center justify-between p-4 bg-accent/30 cursor-pointer hover:bg-accent/50 transition-colors"
                        onClick={() => toggleAttributeExpansion(attr.id)}
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <List className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium text-foreground">{attr.name_fa}</p>
                            <div className="flex items-center gap-2 text-xs text-muted">
                              <span className="px-2 py-0.5 rounded bg-accent">
                                {attr.input_type === "SELECT" ? "انتخابی تکی" : 
                                 attr.input_type === "MULTI_SELECT" ? "چند انتخابی" :
                                 attr.input_type === "NUMBER" ? "عددی" : "متنی"}
                              </span>
                              <span>{attr.is_required ? "الزامی" : "اختیاری"}</span>
                              {attr.options?.length > 0 ? (
                                <span className="text-success">• {toPersianNumber(attr.options.length)} گزینه</span>
                              ) : (attr.input_type === "SELECT" || attr.input_type === "MULTI_SELECT") && (
                                <span className="text-warning animate-pulse">• کلیک کنید و گزینه اضافه کنید</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            attr.is_active 
                              ? "bg-success-light text-success" 
                              : "bg-muted/20 text-muted"
                          }`}>
                            {attr.is_active ? "فعال" : "غیرفعال"}
                          </span>
                          <button
                            onClick={(e) => { e.stopPropagation(); openEditAttributeModal(attr); }}
                            className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); deleteAttributeMutation.mutate(attr.id); }}
                            className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          {expandedAttributes.has(attr.id) ? (
                            <ChevronUp className="w-5 h-5 text-muted" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-muted" />
                          )}
                        </div>
                      </div>

                      {/* Options list (collapsible) */}
                      {expandedAttributes.has(attr.id) && (
                        <div className="p-4 border-t border-border bg-surface">
                          <div className="flex items-center justify-between mb-3">
                            <p className="text-sm font-medium text-muted">گزینه‌ها</p>
                            <Button
                              variant="outline"
                              size="sm"
                              leftIcon={<Plus className="w-3 h-3" />}
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                openCreateOptionModal(attr.id);
                              }}
                            >
                              گزینه جدید
                            </Button>
                          </div>
                          {!attr.options?.length ? (
                            <p className="text-sm text-muted text-center py-4">
                              گزینه‌ای برای این ویژگی تعریف نشده
                            </p>
                          ) : (
                            <div className="space-y-2">
                              {attr.options.map((opt: any) => (
                                <div
                                  key={opt.id}
                                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/30 transition-colors"
                                >
                                  <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded bg-accent flex items-center justify-center text-sm font-medium">
                                      {opt.sort_order + 1}
                                    </div>
                                    <div>
                                      <p className="font-medium text-foreground">{opt.label_fa}</p>
                                      <p className="text-xs text-muted">{opt.value}</p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-3">
                                    {opt.price_modifier !== 0 && (
                                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                                        opt.price_modifier > 0 
                                          ? "bg-success-light text-success" 
                                          : "bg-danger-light text-danger"
                                      }`}>
                                        {opt.price_modifier > 0 ? "+" : ""}{formatPrice(opt.price_modifier)}
                                      </span>
                                    )}
                                    <button
                                      onClick={(e) => { e.stopPropagation(); openEditOptionModal(attr.id, opt); }}
                                      className="p-1.5 rounded hover:bg-accent transition-colors text-muted hover:text-foreground"
                                    >
                                      <Pencil className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); deleteOptionMutation.mutate(opt.id); }}
                                      className="p-1.5 rounded hover:bg-danger-light transition-colors text-muted hover:text-danger"
                                    >
                                      <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ============ Questionnaire Tab ============ */}
      {activeTab === "questionnaire" && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Plan selector */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">انتخاب پلن</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-xs text-muted mb-3">
                پلن‌هایی که پرسشنامه دارند
              </p>
              {isLoadingAllPlans ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-14 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : allPlans?.filter((p: any) => p.has_questionnaire).length ? (
                allPlans.filter((p: any) => p.has_questionnaire).map((plan: any) => (
                  <button
                    key={plan.id}
                    onClick={() => setSelectedPlanForQuestionnaire(plan.id)}
                    className={`w-full p-3 text-right rounded-lg border transition-colors ${
                      selectedPlanForQuestionnaire === plan.id
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border hover:bg-accent/50"
                    }`}
                  >
                    <p className="font-medium text-sm">{plan.name_fa || plan.name}</p>
                    <p className="text-xs text-muted mt-0.5">{plan.category?.name_fa}</p>
                  </button>
                ))
              ) : (
                <p className="text-center text-sm text-muted py-4">
                  پلنی با پرسشنامه یافت نشد
                </p>
              )}
            </CardContent>
          </Card>

          {/* Sections and Questions */}
          <Card className="lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileQuestion className="w-5 h-5" />
                بخش‌ها و سوالات
              </CardTitle>
              {selectedPlanForQuestionnaire && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={openCreateSectionModal}
                >
                  بخش جدید
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {!selectedPlanForQuestionnaire ? (
                <div className="text-center py-12 text-muted">
                  <FileQuestion className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>یک پلن را از سمت راست انتخاب کنید</p>
                </div>
              ) : isLoadingSections ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : !sections?.length ? (
                <div className="text-center py-12 text-muted">
                  <FileQuestion className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>هنوز بخشی برای این پلن تعریف نشده</p>
                  <Button
                    variant="primary"
                    className="mt-4"
                    onClick={openCreateSectionModal}
                  >
                    ایجاد اولین بخش
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {sections.map((section: any, sectionIndex: number) => (
                    <div
                      key={section.id}
                      className="border border-border rounded-xl overflow-hidden"
                    >
                      {/* Section header */}
                      <div 
                        className="flex items-center justify-between p-4 bg-accent/30 cursor-pointer hover:bg-accent/50 transition-colors"
                        onClick={() => toggleSectionExpansion(section.id)}
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <span className="font-bold text-primary">{toPersianNumber(sectionIndex + 1)}</span>
                          </div>
                          <div>
                            <p className="font-medium text-foreground">{section.title_fa}</p>
                            <p className="text-xs text-muted mt-0.5">
                              {section.questions?.length > 0 
                                ? `${toPersianNumber(section.questions.length)} سوال` 
                                : "بدون سوال"}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            section.is_active 
                              ? "bg-success-light text-success" 
                              : "bg-muted/20 text-muted"
                          }`}>
                            {section.is_active ? "فعال" : "غیرفعال"}
                          </span>
                          <button
                            onClick={(e) => { e.stopPropagation(); openEditSectionModal(section); }}
                            className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); deleteSectionMutation.mutate(section.id); }}
                            className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          {expandedSections.has(section.id) ? (
                            <ChevronUp className="w-5 h-5 text-muted" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-muted" />
                          )}
                        </div>
                      </div>

                      {/* Questions list (collapsible) */}
                      {expandedSections.has(section.id) && (
                        <div className="p-4 border-t border-border bg-surface">
                          <div className="flex items-center justify-between mb-3">
                            <p className="text-sm font-medium text-muted">سوالات</p>
                            <Button
                              variant="outline"
                              size="sm"
                              leftIcon={<Plus className="w-3 h-3" />}
                              onClick={(e: React.MouseEvent) => {
                                e.stopPropagation();
                                openCreateQuestionModal(section.id);
                              }}
                            >
                              سوال جدید
                            </Button>
                          </div>
                          {!section.questions?.length ? (
                            <p className="text-sm text-muted text-center py-4">
                              سوالی برای این بخش تعریف نشده
                            </p>
                          ) : (
                            <div className="space-y-3">
                              {section.questions.map((question: any, qIndex: number) => (
                                <div
                                  key={question.id}
                                  className="border border-border rounded-lg overflow-hidden"
                                >
                                  <div 
                                    className="flex items-center justify-between p-3 hover:bg-accent/30 transition-colors cursor-pointer"
                                    onClick={() => toggleQuestionExpansion(question.id)}
                                  >
                                    <div className="flex items-center gap-3">
                                      <span className="text-xs font-medium text-muted w-6 h-6 rounded-full bg-accent flex items-center justify-center">
                                        {toPersianNumber(qIndex + 1)}
                                      </span>
                                      <div>
                                        <p className="text-sm text-foreground">{question.question_fa}</p>
                                        <div className="flex items-center gap-2 mt-1">
                                          <span className="px-1.5 py-0.5 rounded text-xs bg-accent text-muted">
                                            {getQuestionTypeLabel(question.input_type)}
                                          </span>
                                          {question.is_required && (
                                            <span className="text-xs text-warning">الزامی</span>
                                          )}
                                          {(question.input_type === "SINGLE_CHOICE" || question.input_type === "MULTI_CHOICE") && (
                                            <span className="text-xs text-muted">
                                              • {toPersianNumber(question.options?.length || 0)} گزینه
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <button
                                        onClick={(e) => { e.stopPropagation(); openEditQuestionModal(section.id, question); }}
                                        className="p-1.5 rounded hover:bg-accent transition-colors text-muted hover:text-foreground"
                                      >
                                        <Pencil className="w-3.5 h-3.5" />
                                      </button>
                                      <button
                                        onClick={(e) => { e.stopPropagation(); deleteQuestionMutation.mutate(question.id); }}
                                        className="p-1.5 rounded hover:bg-danger-light transition-colors text-muted hover:text-danger"
                                      >
                                        <Trash2 className="w-3.5 h-3.5" />
                                      </button>
                                      {(question.input_type === "SINGLE_CHOICE" || question.input_type === "MULTI_CHOICE") && (
                                        expandedQuestions.has(question.id) ? (
                                          <ChevronUp className="w-4 h-4 text-muted" />
                                        ) : (
                                          <ChevronDown className="w-4 h-4 text-muted" />
                                        )
                                      )}
                                    </div>
                                  </div>
                                  
                                  {/* Question options (for choice types) */}
                                  {(question.input_type === "SINGLE_CHOICE" || question.input_type === "MULTI_CHOICE") && 
                                   expandedQuestions.has(question.id) && (
                                    <div className="p-3 border-t border-border bg-accent/20">
                                      <div className="flex items-center justify-between mb-2">
                                        <p className="text-xs font-medium text-muted">گزینه‌ها</p>
                                        <Button
                                          variant="outline"
                                          size="sm"
                                          leftIcon={<Plus className="w-3 h-3" />}
                                          onClick={(e: React.MouseEvent) => {
                                            e.stopPropagation();
                                            openCreateQuestionOptionModal(question.id);
                                          }}
                                        >
                                          گزینه جدید
                                        </Button>
                                      </div>
                                      {!question.options?.length ? (
                                        <p className="text-xs text-muted text-center py-2">گزینه‌ای تعریف نشده</p>
                                      ) : (
                                        <div className="space-y-1.5">
                                          {question.options.map((opt: any) => (
                                            <div
                                              key={opt.id}
                                              className="flex items-center justify-between p-2 rounded bg-surface border border-border"
                                            >
                                              <div className="flex items-center gap-2">
                                                <span className="text-sm">{opt.label_fa}</span>
                                                {opt.price_modifier !== 0 && (
                                                  <span className={`text-xs ${opt.price_modifier > 0 ? "text-success" : "text-danger"}`}>
                                                    {opt.price_modifier > 0 ? "+" : ""}{formatPrice(opt.price_modifier)}
                                                  </span>
                                                )}
                                              </div>
                                              <div className="flex items-center gap-1">
                                                <button
                                                  onClick={(e) => { e.stopPropagation(); openEditQuestionOptionModal(question.id, opt); }}
                                                  className="p-1 rounded hover:bg-accent transition-colors text-muted hover:text-foreground"
                                                >
                                                  <Pencil className="w-3 h-3" />
                                                </button>
                                                <button
                                                  onClick={(e) => { e.stopPropagation(); deleteQuestionOptionMutation.mutate(opt.id); }}
                                                  className="p-1 rounded hover:bg-danger-light transition-colors text-muted hover:text-danger"
                                                >
                                                  <Trash2 className="w-3 h-3" />
                                                </button>
                                              </div>
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ============ Templates Tab ============ */}
      {activeTab === "templates" && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Plan selector */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-sm">انتخاب پلن</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-xs text-muted mb-3">
                پلن‌هایی که گالری قالب دارند
              </p>
              {isLoadingAllPlans ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-14 bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : allPlans?.filter((p: any) => p.has_templates).length ? (
                allPlans.filter((p: any) => p.has_templates).map((plan: any) => (
                  <button
                    key={plan.id}
                    onClick={() => setSelectedPlanForTemplates(plan.id)}
                    className={`w-full p-3 text-right rounded-lg border transition-colors ${
                      selectedPlanForTemplates === plan.id
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border hover:bg-accent/50"
                    }`}
                  >
                    <p className="font-medium text-sm">{plan.name_fa || plan.name}</p>
                    <p className="text-xs text-muted mt-0.5">{plan.category?.name_fa}</p>
                  </button>
                ))
              ) : (
                <p className="text-center text-sm text-muted py-4">
                  پلنی با گالری قالب یافت نشد
                </p>
              )}
            </CardContent>
          </Card>

          {/* Templates Gallery */}
          <Card className="lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <LayoutTemplate className="w-5 h-5" />
                گالری قالب‌ها
              </CardTitle>
              {selectedPlanForTemplates && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={openCreateTemplateModal}
                >
                  قالب جدید
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {!selectedPlanForTemplates ? (
                <div className="text-center py-12 text-muted">
                  <LayoutTemplate className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>یک پلن را از سمت راست انتخاب کنید</p>
                </div>
              ) : isLoadingTemplates ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div key={i} className="aspect-[3/4] bg-accent rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : !templates?.length ? (
                <div className="text-center py-12 text-muted">
                  <LayoutTemplate className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>هنوز قالبی برای این پلن تعریف نشده</p>
                  <Button
                    variant="primary"
                    className="mt-4"
                    onClick={openCreateTemplateModal}
                  >
                    ایجاد اولین قالب
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {templates.map((template: any) => (
                    <div
                      key={template.id}
                      className="group relative border border-border rounded-xl overflow-hidden hover:border-primary transition-colors"
                    >
                      {/* Preview Image */}
                      <div className="aspect-[3/4] bg-accent relative">
                        {template.preview_url ? (
                          <img
                            src={template.preview_url}
                            alt={template.name_fa}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Image className="w-12 h-12 text-muted/30" />
                          </div>
                        )}
                        
                        {/* Overlay on hover */}
                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                          <button
                            onClick={() => openEditTemplateModal(template)}
                            className="p-2 rounded-full bg-white/90 hover:bg-white transition-colors"
                            title="ویرایش مشخصات"
                          >
                            <Pencil className="w-4 h-4 text-foreground" />
                          </button>
                          <button
                            onClick={() => {
                              setTemplateEditorId(template.id);
                              setShowTemplateEditor(true);
                            }}
                            className="p-2 rounded-full bg-blue-500/90 hover:bg-blue-500 transition-colors"
                            title="ویرایش جایگاه‌ها"
                          >
                            <Maximize2 className="w-4 h-4 text-white" />
                          </button>
                          <button
                            onClick={() => deleteTemplateMutation.mutate(template.id)}
                            className="p-2 rounded-full bg-white/90 hover:bg-danger-light transition-colors"
                            title="حذف"
                          >
                            <Trash2 className="w-4 h-4 text-danger" />
                          </button>
                        </div>
                      </div>
                      
                      {/* Info */}
                      <div className="p-3">
                        <p className="font-medium text-sm truncate">{template.name_fa}</p>
                        <div className="flex items-center justify-between mt-1">
                          <span className={`text-xs ${template.is_active ? "text-success" : "text-muted"}`}>
                            {template.is_active ? "فعال" : "غیرفعال"}
                          </span>
                          {template.placeholder_x !== null && (
                            <span className="text-xs text-muted">
                              با جایگاه لوگو
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Add New Template Card */}
                  <button
                    onClick={openCreateTemplateModal}
                    className="aspect-[3/4] border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center gap-2 text-muted hover:border-primary hover:text-primary transition-colors"
                  >
                    <Plus className="w-8 h-8" />
                    <span className="text-sm">قالب جدید</span>
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Category Create/Edit Modal */}
      <Modal
        isOpen={showCategoryModal}
        onClose={closeCategoryModal}
        title={editingCategory ? "ویرایش دسته‌بندی" : "ایجاد دسته‌بندی جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="نام دسته‌بندی (فارسی)"
            placeholder="مثال: کارت ویزیت"
            value={categoryForm.name_fa}
            onChange={(e) => handleNameChange(e.target.value)}
          />

          <Input
            label="شناسه (Slug)"
            placeholder="مثال: business-card"
            value={categoryForm.slug}
            onChange={(e) => setCategoryForm({ ...categoryForm, slug: e.target.value })}
            dir="ltr"
            hint="این شناسه در URL استفاده می‌شود (فقط حروف انگلیسی و خط تیره)"
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[100px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیح مختصر درباره این دسته‌بندی..."
              value={categoryForm.description_fa}
              onChange={(e) => setCategoryForm({ ...categoryForm, description_fa: e.target.value })}
            />
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={categoryForm.is_active}
              onChange={(e) => setCategoryForm({ ...categoryForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleCategorySubmit}
              isLoading={createCategoryMutation.isPending || updateCategoryMutation.isPending}
            >
              {editingCategory ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeCategoryModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* Product Create/Edit Modal */}
      <Modal
        isOpen={showProductModal}
        onClose={closeProductModal}
        title={editingProduct ? "ویرایش محصول" : "ایجاد محصول جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="نام محصول (فارسی)"
            placeholder="مثال: کارت ویزیت سلفون مات"
            value={productForm.name_fa}
            onChange={(e) => setProductForm({ ...productForm, name_fa: e.target.value })}
          />

          <Input
            label="شناسه محصول (انگلیسی)"
            placeholder="مثال: matte-business-card"
            value={productForm.name}
            onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
            dir="ltr"
            hint="اختیاری - اگر خالی باشد از نام فارسی ساخته می‌شود"
          />

          <div className="grid grid-cols-2 gap-3">
            <div className="w-full">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                نوع محصول *
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                value={productForm.type}
                onChange={(e) => setProductForm({ ...productForm, type: e.target.value as "LABEL" | "INVOICE" })}
              >
                <option value="LABEL">لیبل (LABEL)</option>
                <option value="INVOICE">فاکتور (INVOICE)</option>
              </select>
            </div>

            <Input
              label="سایز محصول *"
              placeholder="مثال: 5x5cm یا A5"
              value={productForm.size}
              onChange={(e) => setProductForm({ ...productForm, size: e.target.value })}
              dir="ltr"
            />
          </div>

          {productForm.type === "LABEL" && (
            <div className="w-full">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                جنس مواد
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                value={productForm.material || ""}
                onChange={(e) => setProductForm({ ...productForm, material: e.target.value as any || undefined })}
              >
                <option value="">انتخاب کنید...</option>
                <option value="PAPER">کاغذی (PAPER)</option>
                <option value="VINYL">وینیل (VINYL)</option>
                <option value="POLYESTER">پلی‌استر (POLYESTER)</option>
                <option value="TRANSPARENT">شفاف (TRANSPARENT)</option>
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="قیمت پایه (تومان) *"
              type="number"
              placeholder="50000"
              value={productForm.base_price || ""}
              onChange={(e) => setProductForm({ ...productForm, base_price: parseInt(e.target.value) || 0 })}
              dir="ltr"
            />
            <Input
              label="حداقل تعداد سفارش"
              type="number"
              placeholder="1"
              value={productForm.min_quantity || ""}
              onChange={(e) => setProductForm({ ...productForm, min_quantity: parseInt(e.target.value) || 1 })}
              dir="ltr"
            />
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیح مختصر درباره این محصول..."
              value={productForm.description}
              onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
            />
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={productForm.is_active}
              onChange={(e) => setProductForm({ ...productForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleProductSubmit}
              isLoading={createProductMutation.isPending || updateProductMutation.isPending}
            >
              {editingProduct ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeProductModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* Plan Create/Edit Modal */}
      <Modal
        isOpen={showPlanModal}
        onClose={closePlanModal}
        title={editingPlan ? "ویرایش پلن طراحی" : "ایجاد پلن طراحی جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="نام پلن (فارسی)"
            placeholder="مثال: طراحی عمومی"
            value={planForm.name_fa}
            onChange={(e) => {
              const name_fa = e.target.value;
              setPlanForm({ 
                ...planForm, 
                name_fa,
                // Auto-generate slug when creating (not editing)
                slug: editingPlan ? planForm.slug : generateSlug(name_fa),
              });
            }}
          />

          <Input
            label="شناسه (Slug)"
            placeholder="مثال: public-design"
            value={planForm.slug}
            onChange={(e) => setPlanForm({ ...planForm, slug: e.target.value })}
            dir="ltr"
            hint="این شناسه در URL استفاده می‌شود (فقط حروف انگلیسی و خط تیره)"
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              نوع پلن
            </label>
            <select
              className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              value={planForm.type}
              onChange={(e) => setPlanForm({ ...planForm, type: e.target.value as any })}
            >
              <option value="PUBLIC">عمومی (PUBLIC)</option>
              <option value="SEMI_PRIVATE">نیمه خصوصی (SEMI_PRIVATE)</option>
              <option value="PRIVATE">خصوصی (PRIVATE)</option>
            </select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="قیمت (تومان)"
              type="number"
              placeholder="50000"
              value={planForm.price || ""}
              onChange={(e) => setPlanForm({ ...planForm, price: parseInt(e.target.value) || 0 })}
              dir="ltr"
            />
            <Input
              label="تعداد اصلاح"
              type="number"
              placeholder="3"
              value={planForm.max_revisions || ""}
              onChange={(e) => setPlanForm({ ...planForm, max_revisions: parseInt(e.target.value) || 0 })}
              dir="ltr"
            />
            <Input
              label="روز تحویل"
              type="number"
              placeholder="3"
              value={planForm.delivery_days || ""}
              onChange={(e) => setPlanForm({ ...planForm, delivery_days: parseInt(e.target.value) || 0 })}
              dir="ltr"
            />
          </div>

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیح مختصر درباره این پلن..."
              value={planForm.description_fa}
              onChange={(e) => setPlanForm({ ...planForm, description_fa: e.target.value })}
            />
          </div>

          {/* Plan Type Features */}
          <div className="p-4 rounded-lg bg-accent/30 space-y-3">
            <p className="text-sm font-medium text-foreground mb-2">قابلیت‌های پلن:</p>
            
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={planForm.has_questionnaire}
                onChange={(e) => setPlanForm({ ...planForm, has_questionnaire: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <div>
                <span className="text-sm text-foreground">پرسشنامه</span>
                <p className="text-xs text-muted">کاربر فرم سوالات را پر می‌کند (برای پلن نیمه‌خصوصی و خصوصی)</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={planForm.has_templates}
                onChange={(e) => setPlanForm({ ...planForm, has_templates: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <div>
                <span className="text-sm text-foreground">گالری قالب‌ها</span>
                <p className="text-xs text-muted">کاربر از بین قالب‌های آماده انتخاب می‌کند (برای پلن عمومی)</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={planForm.has_file_upload}
                onChange={(e) => setPlanForm({ ...planForm, has_file_upload: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <div>
                <span className="text-sm text-foreground">آپلود فایل</span>
                <p className="text-xs text-muted">کاربر طرح خود را آپلود می‌کند (برای پلن خصوصی)</p>
              </div>
            </label>
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={planForm.is_active}
              onChange={(e) => setPlanForm({ ...planForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handlePlanSubmit}
              isLoading={createPlanMutation.isPending || updatePlanMutation.isPending}
            >
              {editingPlan ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closePlanModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* Attribute Create/Edit Modal */}
      <Modal
        isOpen={showAttributeModal}
        onClose={closeAttributeModal}
        title={editingAttribute ? "ویرایش ویژگی" : "ایجاد ویژگی جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="نام ویژگی (فارسی)"
            placeholder="مثال: جنس"
            value={attributeForm.name_fa}
            onChange={(e) => handleAttributeNameChange(e.target.value)}
          />

          <Input
            label="شناسه (Slug)"
            placeholder="مثال: material"
            value={attributeForm.slug}
            onChange={(e) => setAttributeForm({ ...attributeForm, slug: e.target.value })}
            dir="ltr"
            hint="این شناسه برای شناسایی ویژگی در سیستم استفاده می‌شود"
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              نوع ورودی
            </label>
            <select
              className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              value={attributeForm.input_type}
              onChange={(e) => setAttributeForm({ ...attributeForm, input_type: e.target.value as AttributeInputType })}
            >
              <option value="SELECT">انتخابی تکی (SELECT)</option>
              <option value="MULTI_SELECT">چند انتخابی (MULTI_SELECT)</option>
              <option value="NUMBER">عددی (NUMBER)</option>
              <option value="TEXT">متنی (TEXT)</option>
            </select>
          </div>

          {attributeForm.input_type === "NUMBER" && (
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="حداقل مقدار"
                type="number"
                placeholder="0"
                value={attributeForm.min_value ?? ""}
                onChange={(e) => setAttributeForm({ ...attributeForm, min_value: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
              <Input
                label="حداکثر مقدار"
                type="number"
                placeholder="100"
                value={attributeForm.max_value ?? ""}
                onChange={(e) => setAttributeForm({ ...attributeForm, max_value: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
            </div>
          )}

          <Input
            label="مقدار پیش‌فرض (اختیاری)"
            placeholder="مقدار پیش‌فرض"
            value={attributeForm.default_value || ""}
            onChange={(e) => setAttributeForm({ ...attributeForm, default_value: e.target.value })}
          />

          <div className="flex items-center gap-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={attributeForm.is_required}
                onChange={(e) => setAttributeForm({ ...attributeForm, is_required: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">الزامی باشد</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={attributeForm.is_active}
                onChange={(e) => setAttributeForm({ ...attributeForm, is_active: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">فعال باشد</span>
            </label>
          </div>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleAttributeSubmit}
              isLoading={createAttributeMutation.isPending || updateAttributeMutation.isPending}
            >
              {editingAttribute ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeAttributeModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* Attribute Option Create/Edit Modal */}
      <Modal
        isOpen={showOptionModal}
        onClose={closeOptionModal}
        title={editingOption ? "ویرایش گزینه" : "ایجاد گزینه جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="عنوان گزینه (فارسی)"
            placeholder="مثال: کاغذی"
            value={optionForm.label_fa}
            onChange={(e) => handleOptionValueChange(e.target.value)}
          />

          <Input
            label="مقدار (انگلیسی)"
            placeholder="مثال: paper"
            value={optionForm.value}
            onChange={(e) => setOptionForm({ ...optionForm, value: e.target.value })}
            dir="ltr"
            hint="این مقدار برای پردازش سیستمی استفاده می‌شود"
          />

          <Input
            label="تغییر قیمت (تومان)"
            type="number"
            placeholder="0"
            value={optionForm.price_modifier || ""}
            onChange={(e) => setOptionForm({ ...optionForm, price_modifier: parseInt(e.target.value) || 0 })}
            dir="ltr"
            hint="مقدار مثبت به قیمت پایه اضافه و مقدار منفی از آن کم می‌شود"
          />

          <Input
            label="ترتیب نمایش"
            type="number"
            placeholder="0"
            value={optionForm.sort_order || ""}
            onChange={(e) => setOptionForm({ ...optionForm, sort_order: parseInt(e.target.value) || 0 })}
            dir="ltr"
          />

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={optionForm.is_active}
              onChange={(e) => setOptionForm({ ...optionForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleOptionSubmit}
              isLoading={createOptionMutation.isPending || updateOptionMutation.isPending}
            >
              {editingOption ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeOptionModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* ============ Section Modal ============ */}
      <Modal
        isOpen={showSectionModal}
        onClose={closeSectionModal}
        title={editingSection ? "ویرایش بخش" : "ایجاد بخش جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="عنوان بخش"
            placeholder="مثال: اطلاعات شرکت"
            value={sectionForm.title_fa}
            onChange={(e) => setSectionForm({ ...sectionForm, title_fa: e.target.value })}
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیحاتی که بالای بخش نمایش داده می‌شود..."
              value={sectionForm.description_fa}
              onChange={(e) => setSectionForm({ ...sectionForm, description_fa: e.target.value })}
            />
          </div>

          <Input
            label="ترتیب نمایش"
            type="number"
            placeholder="0"
            value={sectionForm.sort_order || ""}
            onChange={(e) => setSectionForm({ ...sectionForm, sort_order: parseInt(e.target.value) || 0 })}
            dir="ltr"
          />

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={sectionForm.is_active}
              onChange={(e) => setSectionForm({ ...sectionForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleSectionSubmit}
              isLoading={createSectionMutation.isPending || updateSectionMutation.isPending}
            >
              {editingSection ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeSectionModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* ============ Question Modal ============ */}
      <Modal
        isOpen={showQuestionModal}
        onClose={closeQuestionModal}
        title={editingQuestion ? "ویرایش سوال" : "ایجاد سوال جدید"}
        size="lg"
      >
        <div className="space-y-4 max-h-[70vh] overflow-y-auto">
          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              متن سوال *
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="سوالی که از کاربر پرسیده می‌شود..."
              value={questionForm.question_fa}
              onChange={(e) => setQuestionForm({ ...questionForm, question_fa: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="w-full">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                نوع ورودی *
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                value={questionForm.input_type}
                onChange={(e) => setQuestionForm({ ...questionForm, input_type: e.target.value as QuestionInputType })}
              >
                <option value="TEXT">متن کوتاه</option>
                <option value="TEXTAREA">متن بلند</option>
                <option value="NUMBER">عدد</option>
                <option value="SINGLE_CHOICE">تک انتخابی</option>
                <option value="MULTI_CHOICE">چند انتخابی</option>
                <option value="IMAGE_UPLOAD">آپلود تصویر</option>
                <option value="FILE_UPLOAD">آپلود فایل</option>
                <option value="COLOR_PICKER">انتخاب رنگ</option>
                <option value="DATE_PICKER">انتخاب تاریخ</option>
                <option value="SCALE">مقیاس (۱ تا ۵)</option>
              </select>
            </div>
            
            <Input
              label="ترتیب نمایش"
              type="number"
              placeholder="0"
              value={questionForm.sort_order || ""}
              onChange={(e) => setQuestionForm({ ...questionForm, sort_order: parseInt(e.target.value) || 0 })}
              dir="ltr"
            />
          </div>

          <Input
            label="متن راهنما (placeholder)"
            placeholder="مثال: نام شرکت را وارد کنید"
            value={questionForm.placeholder_fa}
            onChange={(e) => setQuestionForm({ ...questionForm, placeholder_fa: e.target.value })}
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات کمکی (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[60px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیحات بیشتر برای کمک به کاربر..."
              value={questionForm.help_text_fa}
              onChange={(e) => setQuestionForm({ ...questionForm, help_text_fa: e.target.value })}
            />
          </div>

          {/* Validation rules for text/number inputs */}
          {(questionForm.input_type === "TEXT" || questionForm.input_type === "TEXTAREA") && (
            <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-accent/30">
              <Input
                label="حداقل کاراکتر"
                type="number"
                placeholder="بدون محدودیت"
                value={questionForm.min_length ?? ""}
                onChange={(e) => setQuestionForm({ ...questionForm, min_length: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
              <Input
                label="حداکثر کاراکتر"
                type="number"
                placeholder="بدون محدودیت"
                value={questionForm.max_length ?? ""}
                onChange={(e) => setQuestionForm({ ...questionForm, max_length: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
            </div>
          )}

          {questionForm.input_type === "NUMBER" && (
            <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-accent/30">
              <Input
                label="حداقل مقدار"
                type="number"
                placeholder="بدون محدودیت"
                value={questionForm.min_value ?? ""}
                onChange={(e) => setQuestionForm({ ...questionForm, min_value: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
              <Input
                label="حداکثر مقدار"
                type="number"
                placeholder="بدون محدودیت"
                value={questionForm.max_value ?? ""}
                onChange={(e) => setQuestionForm({ ...questionForm, max_value: e.target.value ? parseInt(e.target.value) : undefined })}
                dir="ltr"
              />
            </div>
          )}

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={questionForm.is_required}
                onChange={(e) => setQuestionForm({ ...questionForm, is_required: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">الزامی باشد</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={questionForm.is_active}
                onChange={(e) => setQuestionForm({ ...questionForm, is_active: e.target.checked })}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">فعال باشد</span>
            </label>
          </div>

          {(questionForm.input_type === "SINGLE_CHOICE" || questionForm.input_type === "MULTI_CHOICE") && (
            <div className="p-3 rounded-lg bg-warning-light/30 border border-warning/30">
              <p className="text-sm text-warning">
                <strong>توجه:</strong> برای اضافه کردن گزینه‌ها، ابتدا سوال را ایجاد کنید، سپس روی سوال کلیک کرده و گزینه‌ها را اضافه کنید.
              </p>
            </div>
          )}

          {/* Conditional Logic */}
          <div className="p-4 rounded-lg bg-accent/30 space-y-3">
            <p className="text-sm font-medium text-foreground mb-2">نمایش شرطی (اختیاری):</p>
            <p className="text-xs text-muted mb-3">
              این سوال فقط زمانی نمایش داده می‌شود که کاربر به سوال انتخابی پاسخ مشخصی داده باشد.
            </p>
            
            <div className="w-full">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                وابسته به سوال
              </label>
              <select
                className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                value={questionForm.depends_on_question_id || ""}
                onChange={(e) => setQuestionForm({ 
                  ...questionForm, 
                  depends_on_question_id: e.target.value || undefined,
                  depends_on_values: [] 
                })}
              >
                <option value="">بدون وابستگی</option>
                {sections?.flatMap((section: any) => 
                  section.questions?.filter((q: any) => 
                    q.id !== editingQuestion?.id && 
                    (q.input_type === "SINGLE_CHOICE" || q.input_type === "MULTI_CHOICE")
                  ).map((q: any) => (
                    <option key={q.id} value={q.id}>
                      {section.title_fa}: {q.question_fa.substring(0, 50)}...
                    </option>
                  ))
                )}
              </select>
            </div>

            {questionForm.depends_on_question_id && (
              <div className="w-full">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  نمایش داده شود اگر پاسخ یکی از این‌ها باشد:
                </label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {sections?.flatMap((section: any) => 
                    section.questions?.filter((q: any) => q.id === questionForm.depends_on_question_id)
                  )?.[0]?.options?.map((opt: any) => (
                    <label key={opt.id} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={questionForm.depends_on_values.includes(opt.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setQuestionForm({
                              ...questionForm,
                              depends_on_values: [...questionForm.depends_on_values, opt.value]
                            });
                          } else {
                            setQuestionForm({
                              ...questionForm,
                              depends_on_values: questionForm.depends_on_values.filter(v => v !== opt.value)
                            });
                          }
                        }}
                        className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                      />
                      <span className="text-sm">{opt.label_fa}</span>
                    </label>
                  )) || (
                    <p className="text-xs text-muted">سوال انتخابی گزینه‌ای ندارد</p>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleQuestionSubmit}
              isLoading={createQuestionMutation.isPending || updateQuestionMutation.isPending}
            >
              {editingQuestion ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeQuestionModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* ============ Question Option Modal ============ */}
      <Modal
        isOpen={showQuestionOptionModal}
        onClose={closeQuestionOptionModal}
        title={editingQuestionOption ? "ویرایش گزینه" : "ایجاد گزینه جدید"}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="عنوان گزینه (فارسی)"
            placeholder="مثال: بله"
            value={questionOptionForm.label_fa}
            onChange={(e) => {
              const label = e.target.value;
              setQuestionOptionForm({
                ...questionOptionForm,
                label_fa: label,
                value: editingQuestionOption ? questionOptionForm.value : generateSlug(label),
              });
            }}
          />

          <Input
            label="مقدار (انگلیسی)"
            placeholder="مثال: yes"
            value={questionOptionForm.value}
            onChange={(e) => setQuestionOptionForm({ ...questionOptionForm, value: e.target.value })}
            dir="ltr"
            hint="این مقدار برای پردازش سیستمی استفاده می‌شود"
          />

          <Input
            label="تغییر قیمت (تومان)"
            type="number"
            placeholder="0"
            value={questionOptionForm.price_modifier || ""}
            onChange={(e) => setQuestionOptionForm({ ...questionOptionForm, price_modifier: parseInt(e.target.value) || 0 })}
            dir="ltr"
            hint="مقدار مثبت به قیمت پایه اضافه و مقدار منفی از آن کم می‌شود"
          />

          <Input
            label="ترتیب نمایش"
            type="number"
            placeholder="0"
            value={questionOptionForm.sort_order || ""}
            onChange={(e) => setQuestionOptionForm({ ...questionOptionForm, sort_order: parseInt(e.target.value) || 0 })}
            dir="ltr"
          />

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={questionOptionForm.is_active}
              onChange={(e) => setQuestionOptionForm({ ...questionOptionForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleQuestionOptionSubmit}
              isLoading={createQuestionOptionMutation.isPending || updateQuestionOptionMutation.isPending}
            >
              {editingQuestionOption ? "به‌روزرسانی" : "ایجاد"}
            </Button>
            <Button variant="outline" onClick={closeQuestionOptionModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* ============ Template Modal ============ */}
      <Modal
        isOpen={showTemplateModal}
        onClose={closeTemplateModal}
        title={editingTemplate ? "ویرایش قالب" : "ایجاد قالب جدید"}
        size="lg"
      >
        <div className="space-y-4 max-h-[70vh] overflow-y-auto">
          <Input
            label="نام قالب *"
            placeholder="مثال: قالب کلاسیک"
            value={templateForm.name_fa}
            onChange={(e) => setTemplateForm({ ...templateForm, name_fa: e.target.value })}
          />

          <div className="w-full">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              توضیحات (اختیاری)
            </label>
            <textarea
              className="w-full min-h-[60px] px-3 py-2 rounded-lg border border-border bg-surface text-foreground placeholder:text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              placeholder="توضیحات مختصر درباره این قالب..."
              value={templateForm.description_fa}
              onChange={(e) => setTemplateForm({ ...templateForm, description_fa: e.target.value })}
            />
          </div>

          {/* Image Upload Section */}
          <ImageUpload
            label="تصویر قالب *"
            hint="تصویر قالب را آپلود کنید"
            value={templateForm.image_preview}
            isUploading={isUploadingTemplateImage}
            onChange={(file, preview) => {
              setTemplateForm({
                ...templateForm,
                image_file: file,
                image_preview: preview,
              });
            }}
            maxSizeMB={20}
          />

          {/* Placeholder Count Configuration - Only for new templates */}
          {!editingTemplate && (
            <div className="p-4 rounded-lg bg-accent/30 space-y-4">
              <p className="text-sm font-medium text-foreground">تعداد جایگاه‌ها:</p>
              <p className="text-xs text-muted">
                مشخص کنید چند جایگاه تصویر و متن نیاز دارید. پس از ایجاد قالب، ویرایشگر باز می‌شود تا جایگاه‌ها را روی تصویر تنظیم کنید.
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    تعداد جایگاه تصویر
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setTemplateForm({
                        ...templateForm,
                        image_placeholder_count: Math.max(0, templateForm.image_placeholder_count - 1)
                      })}
                      className="w-10 h-10 rounded-lg border border-border bg-surface hover:bg-accent flex items-center justify-center"
                    >
                      -
                    </button>
                    <div className="flex-1 text-center text-lg font-medium">
                      {toPersianNumber(templateForm.image_placeholder_count)}
                    </div>
                    <button
                      type="button"
                      onClick={() => setTemplateForm({
                        ...templateForm,
                        image_placeholder_count: templateForm.image_placeholder_count + 1
                      })}
                      className="w-10 h-10 rounded-lg border border-border bg-surface hover:bg-accent flex items-center justify-center"
                    >
                      +
                    </button>
                  </div>
                  <p className="text-xs text-muted mt-1 flex items-center gap-1">
                    <Image className="w-3 h-3" />
                    برای لوگو، تصویر محصول و...
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    تعداد جایگاه متن
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setTemplateForm({
                        ...templateForm,
                        text_placeholder_count: Math.max(0, templateForm.text_placeholder_count - 1)
                      })}
                      className="w-10 h-10 rounded-lg border border-border bg-surface hover:bg-accent flex items-center justify-center"
                    >
                      -
                    </button>
                    <div className="flex-1 text-center text-lg font-medium">
                      {toPersianNumber(templateForm.text_placeholder_count)}
                    </div>
                    <button
                      type="button"
                      onClick={() => setTemplateForm({
                        ...templateForm,
                        text_placeholder_count: templateForm.text_placeholder_count + 1
                      })}
                      className="w-10 h-10 rounded-lg border border-border bg-surface hover:bg-accent flex items-center justify-center"
                    >
                      +
                    </button>
                  </div>
                  <p className="text-xs text-muted mt-1 flex items-center gap-1">
                    <Type className="w-3 h-3" />
                    برای عنوان، شماره و...
                  </p>
                </div>
              </div>
            </div>
          )}

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={templateForm.is_active}
              onChange={(e) => setTemplateForm({ ...templateForm, is_active: e.target.checked })}
              className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm text-foreground">فعال باشد</span>
          </label>

          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              className="flex-1"
              onClick={handleTemplateSubmit}
              isLoading={isUploadingTemplateImage || createTemplateMutation.isPending || updateTemplateMutation.isPending}
            >
              {editingTemplate ? "به‌روزرسانی" : "ایجاد و ویرایش"}
            </Button>
            <Button variant="outline" onClick={closeTemplateModal}>
              انصراف
            </Button>
          </div>
        </div>
      </Modal>

      {/* ============ Dynamic Template Editor Modal ============ */}
      <Modal
        isOpen={showTemplateEditor}
        onClose={() => {
          setShowTemplateEditor(false);
          setTemplateEditorId(null);
        }}
        title="ویرایشگر قالب داینامیک"
        size="full"
      >
        {templateEditorId && (
          <TemplateEditor
            templateId={templateEditorId}
            onClose={() => {
              setShowTemplateEditor(false);
              setTemplateEditorId(null);
            }}
          />
        )}
      </Modal>
    </div>
  );
}
