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
  MoreVertical,
  Eye,
  EyeOff,
} from "lucide-react";
import toast from "react-hot-toast";
import { toPersianNumber, formatPrice } from "@/lib/utils";

type TabType = "categories" | "products" | "plans";

export default function CatalogManagementPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isLoadingUser, isAdmin } = useAuth();
  const [isChecked, setIsChecked] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("categories");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

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

  if (!isChecked || isLoadingUser || !isAdmin) {
    return <PageLoading />;
  }

  const tabs = [
    { id: "categories" as TabType, label: "دسته‌بندی‌ها", icon: FolderOpen, count: categories?.length ?? 0 },
    { id: "products" as TabType, label: "محصولات", icon: Package, count: productsData?.items?.length ?? 0 },
    { id: "plans" as TabType, label: "پلن‌های طراحی", icon: Layers, count: 0 },
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
                        <p className="font-medium text-foreground">{category.name}</p>
                        <p className="text-sm text-muted">{category.description || "بدون توضیح"}</p>
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
                      <button className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground">
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
                      <button className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground">
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
                      {category.name}
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
                    ({categories?.find((c: any) => c.id === selectedCategory)?.name})
                  </span>
                )}
              </CardTitle>
              {selectedCategory && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
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
                        <button className="p-2 rounded-lg hover:bg-accent transition-colors text-muted hover:text-foreground">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button className="p-2 rounded-lg hover:bg-danger-light transition-colors text-muted hover:text-danger">
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
    </div>
  );
}
