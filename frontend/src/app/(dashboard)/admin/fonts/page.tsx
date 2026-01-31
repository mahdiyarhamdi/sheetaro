"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Type,
  Plus,
  Edit,
  Trash2,
  Eye,
  Loader2,
  Upload,
  Check,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/ui/modal";
import { useAuth } from "@/hooks/useAuth";
import { adminApi, SystemFont, FontCreateData, FontVariant } from "@/lib/api";
import toast from "react-hot-toast";

interface FontFormData {
  name: string;
  name_fa: string;
  file_url: string;
  sample_text: string;
  variants: FontVariant[];
}

interface VariantFormData {
  weight: number;
  style: string;
  file_url: string;
}

export default function AdminFontsPage() {
  const { user, isAdmin } = useAuth();
  const queryClient = useQueryClient();

  // Modal states
  const [showFontModal, setShowFontModal] = useState(false);
  const [editingFont, setEditingFont] = useState<SystemFont | null>(null);
  const [fontForm, setFontForm] = useState<FontFormData>({
    name: "",
    name_fa: "",
    file_url: "",
    sample_text: "نمونه متن فارسی - Sample Text 123",
    variants: [],
  });

  // Variant modal
  const [showVariantModal, setShowVariantModal] = useState(false);
  const [selectedFontId, setSelectedFontId] = useState<string | null>(null);
  const [variantForm, setVariantForm] = useState<VariantFormData>({
    weight: 400,
    style: "normal",
    file_url: "",
  });

  // Preview state
  const [previewText, setPreviewText] = useState("نمونه متن فارسی - Sample Text 123");

  // Fetch fonts
  const { data: fonts, isLoading } = useQuery({
    queryKey: ["fonts"],
    queryFn: async () => {
      const response = await adminApi.getFonts(false);
      return response.data;
    },
    enabled: isAdmin,
  });

  // Mutations
  const createFontMutation = useMutation({
    mutationFn: (data: FontCreateData) => adminApi.createFont(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fonts"] });
      toast.success("فونت با موفقیت ایجاد شد");
      closeFontModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در ایجاد فونت");
    },
  });

  const updateFontMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FontCreateData & { is_active?: boolean }> }) =>
      adminApi.updateFont(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fonts"] });
      toast.success("فونت با موفقیت به‌روزرسانی شد");
      closeFontModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در به‌روزرسانی فونت");
    },
  });

  const deleteFontMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteFont(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fonts"] });
      toast.success("فونت حذف شد");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در حذف فونت");
    },
  });

  const addVariantMutation = useMutation({
    mutationFn: ({ fontId, weight, style, fileUrl }: { fontId: string; weight: number; style: string; fileUrl?: string }) =>
      adminApi.addFontVariant(fontId, weight, style, fileUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fonts"] });
      toast.success("وزن فونت اضافه شد");
      closeVariantModal();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در افزودن وزن فونت");
    },
  });

  const deleteVariantMutation = useMutation({
    mutationFn: ({ fontId, weight, style }: { fontId: string; weight: number; style: string }) =>
      adminApi.deleteFontVariant(fontId, weight, style),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fonts"] });
      toast.success("وزن فونت حذف شد");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در حذف وزن فونت");
    },
  });

  // Modal handlers
  const openCreateFontModal = () => {
    setEditingFont(null);
    setFontForm({
      name: "",
      name_fa: "",
      file_url: "",
      sample_text: "نمونه متن فارسی - Sample Text 123",
      variants: [],
    });
    setShowFontModal(true);
  };

  const openEditFontModal = (font: SystemFont) => {
    setEditingFont(font);
    setFontForm({
      name: font.name,
      name_fa: font.name_fa,
      file_url: font.file_url || "",
      sample_text: font.sample_text || "نمونه متن فارسی - Sample Text 123",
      variants: font.variants || [],
    });
    setShowFontModal(true);
  };

  const closeFontModal = () => {
    setShowFontModal(false);
    setEditingFont(null);
  };

  const handleFontSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!fontForm.name || !fontForm.name_fa) {
      toast.error("نام فونت الزامی است");
      return;
    }

    const data: FontCreateData = {
      name: fontForm.name,
      name_fa: fontForm.name_fa,
      file_url: fontForm.file_url || undefined,
      sample_text: fontForm.sample_text || undefined,
      variants: fontForm.variants.length > 0 ? fontForm.variants : undefined,
    };

    if (editingFont) {
      updateFontMutation.mutate({ id: editingFont.id, data });
    } else {
      createFontMutation.mutate(data);
    }
  };

  // Variant modal handlers
  const openVariantModal = (fontId: string) => {
    setSelectedFontId(fontId);
    setVariantForm({
      weight: 400,
      style: "normal",
      file_url: "",
    });
    setShowVariantModal(true);
  };

  const closeVariantModal = () => {
    setShowVariantModal(false);
    setSelectedFontId(null);
  };

  const handleVariantSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFontId) return;

    addVariantMutation.mutate({
      fontId: selectedFontId,
      weight: variantForm.weight,
      style: variantForm.style,
      fileUrl: variantForm.file_url || undefined,
    });
  };

  // Font weight labels
  const fontWeightLabels: Record<number, string> = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black",
  };

  if (!isAdmin) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">شما به این بخش دسترسی ندارید</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">مدیریت فونت‌ها</h1>
          <p className="text-gray-600 dark:text-gray-400">
            فونت‌های سیستم را مدیریت کنید
          </p>
        </div>
        <Button onClick={openCreateFontModal}>
          <Plus className="w-4 h-4 ml-2" />
          فونت جدید
        </Button>
      </div>

      {/* Preview Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">پیش‌نمایش فونت‌ها</h2>
        <Input
          label="متن پیش‌نمایش"
          value={previewText}
          onChange={(e) => setPreviewText(e.target.value)}
          placeholder="متن خود را وارد کنید..."
        />
      </div>

      {/* Fonts List */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="grid gap-4">
          {fonts?.map((font) => (
            <div
              key={font.id}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                    <Type className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">{font.name_fa}</h3>
                    <p className="text-gray-500 text-sm font-mono">{font.name}</p>
                  </div>
                  {!font.is_active && (
                    <span className="px-2 py-1 text-xs bg-red-100 text-red-600 rounded">
                      غیرفعال
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => openEditFontModal(font)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm("آیا از حذف این فونت مطمئن هستید؟")) {
                        deleteFontMutation.mutate(font.id);
                      }
                    }}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </div>

              {/* Font Preview */}
              <div
                className="text-2xl p-4 bg-gray-50 dark:bg-gray-700 rounded-lg mb-4"
                style={{ fontFamily: font.name }}
              >
                {previewText}
              </div>

              {/* Font Variants */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    وزن‌های فونت
                  </h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openVariantModal(font.id)}
                  >
                    <Plus className="w-3 h-3 ml-1" />
                    افزودن وزن
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {font.variants && font.variants.length > 0 ? (
                    font.variants.map((variant, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg"
                      >
                        <span
                          className="text-sm"
                          style={{
                            fontFamily: font.name,
                            fontWeight: variant.weight,
                            fontStyle: variant.style,
                          }}
                        >
                          {fontWeightLabels[variant.weight] || variant.weight}
                          {variant.style === "italic" && " Italic"}
                        </span>
                        <button
                          onClick={() =>
                            deleteVariantMutation.mutate({
                              fontId: font.id,
                              weight: variant.weight,
                              style: variant.style,
                            })
                          }
                          className="text-red-500 hover:text-red-600"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <span className="text-sm text-gray-500">
                      وزنی تعریف نشده است
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {fonts?.length === 0 && (
            <div className="text-center p-12 bg-white dark:bg-gray-800 rounded-lg">
              <Type className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">فونتی وجود ندارد</h3>
              <p className="text-gray-500 mb-4">
                اولین فونت را اضافه کنید
              </p>
              <Button onClick={openCreateFontModal}>
                <Plus className="w-4 h-4 ml-2" />
                فونت جدید
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Font Modal */}
      <Modal
        isOpen={showFontModal}
        onClose={closeFontModal}
        title={editingFont ? "ویرایش فونت" : "فونت جدید"}
      >
        <form onSubmit={handleFontSubmit} className="space-y-4">
          <Input
            label="نام فونت (انگلیسی)"
            value={fontForm.name}
            onChange={(e) => setFontForm({ ...fontForm, name: e.target.value })}
            placeholder="IRANSans"
            required
          />
          <Input
            label="نام فارسی"
            value={fontForm.name_fa}
            onChange={(e) => setFontForm({ ...fontForm, name_fa: e.target.value })}
            placeholder="ایران سنس"
            required
          />
          <Input
            label="آدرس فایل فونت (اختیاری)"
            value={fontForm.file_url}
            onChange={(e) => setFontForm({ ...fontForm, file_url: e.target.value })}
            placeholder="https://example.com/fonts/IRANSans.ttf"
          />
          <Input
            label="متن نمونه"
            value={fontForm.sample_text}
            onChange={(e) => setFontForm({ ...fontForm, sample_text: e.target.value })}
            placeholder="نمونه متن فارسی - Sample Text 123"
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={closeFontModal}>
              انصراف
            </Button>
            <Button
              type="submit"
              disabled={createFontMutation.isPending || updateFontMutation.isPending}
            >
              {createFontMutation.isPending || updateFontMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin ml-2" />
              ) : null}
              {editingFont ? "به‌روزرسانی" : "ایجاد"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Variant Modal */}
      <Modal
        isOpen={showVariantModal}
        onClose={closeVariantModal}
        title="افزودن وزن فونت"
      >
        <form onSubmit={handleVariantSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">وزن فونت</label>
            <select
              value={variantForm.weight}
              onChange={(e) =>
                setVariantForm({ ...variantForm, weight: Number(e.target.value) })
              }
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            >
              {Object.entries(fontWeightLabels).map(([weight, label]) => (
                <option key={weight} value={weight}>
                  {weight} - {label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">استایل</label>
            <select
              value={variantForm.style}
              onChange={(e) => setVariantForm({ ...variantForm, style: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="normal">Normal</option>
              <option value="italic">Italic</option>
            </select>
          </div>
          <Input
            label="آدرس فایل (اختیاری)"
            value={variantForm.file_url}
            onChange={(e) => setVariantForm({ ...variantForm, file_url: e.target.value })}
            placeholder="https://example.com/fonts/IRANSans-Bold.ttf"
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={closeVariantModal}>
              انصراف
            </Button>
            <Button type="submit" disabled={addVariantMutation.isPending}>
              {addVariantMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin ml-2" />
              ) : null}
              افزودن
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

