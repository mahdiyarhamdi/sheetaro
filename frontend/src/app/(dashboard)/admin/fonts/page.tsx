"use client";

import { useState, useRef, useEffect } from "react";
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
  FileType,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/ui/modal";
import { useAuth } from "@/hooks/useAuth";
import { adminApi, SystemFont, FontCreateData, FontVariant, getErrorMessage } from "@/lib/api";
import toast from "react-hot-toast";

// Get the API base URL for font files
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

interface FontFormData {
  name: string;
  name_fa: string;
  file_url: string;
  file?: File | null;
  sample_text: string;
  variants: FontVariant[];
}

interface VariantFormData {
  weight: number;
  style: string;
  file_url: string;
  file_ttf?: File | null;
  file_woff?: File | null;
  file_woff2?: File | null;
}

export default function AdminFontsPage() {
  const { user, isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const fontFileInputRef = useRef<HTMLInputElement>(null);
  const variantTtfInputRef = useRef<HTMLInputElement>(null);
  const variantWoffInputRef = useRef<HTMLInputElement>(null);
  const variantWoff2InputRef = useRef<HTMLInputElement>(null);

  // Modal states
  const [showFontModal, setShowFontModal] = useState(false);
  const [editingFont, setEditingFont] = useState<SystemFont | null>(null);
  const [fontForm, setFontForm] = useState<FontFormData>({
    name: "",
    name_fa: "",
    file_url: "",
    file: null,
    sample_text: "نمونه متن فارسی - Sample Text 123",
    variants: [],
  });
  const [isUploadingFont, setIsUploadingFont] = useState(false);

  // Variant modal
  const [showVariantModal, setShowVariantModal] = useState(false);
  const [selectedFontId, setSelectedFontId] = useState<string | null>(null);
  const [variantForm, setVariantForm] = useState<VariantFormData>({
    weight: 400,
    style: "normal",
    file_url: "",
    file: null,
  });
  const [isUploadingVariant, setIsUploadingVariant] = useState(false);

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

  // Helper function to construct full font URL
  const getFontUrl = (fileUrl: string | undefined | null): string | null => {
    if (!fileUrl) return null;
    
    // If already absolute URL, return as is
    if (fileUrl.startsWith("http")) return fileUrl;
    
    // Add /api/v1 prefix if not present
    const apiPath = fileUrl.startsWith("/api/v1") ? fileUrl : `/api/v1${fileUrl}`;
    return `${API_BASE_URL}${apiPath}`;
  };

  // Dynamically load fonts using @font-face
  useEffect(() => {
    if (!fonts || fonts.length === 0) return;

    // Create a unique style element for dynamic fonts
    const styleId = "dynamic-fonts-style";
    let styleEl = document.getElementById(styleId) as HTMLStyleElement | null;
    
    if (!styleEl) {
      styleEl = document.createElement("style");
      styleEl.id = styleId;
      document.head.appendChild(styleEl);
    }

    // Build @font-face rules for all fonts and their variants
    const fontFaceRules: string[] = [];

    fonts.forEach((font) => {
      // If font has a main file_url, load it as default
      const mainFontUrl = getFontUrl(font.file_url);
      if (mainFontUrl) {
        const ext = font.file_url?.split('.').pop()?.toLowerCase();
        let format = 'truetype';
        if (ext === 'woff') format = 'woff';
        else if (ext === 'woff2') format = 'woff2';
        
        fontFaceRules.push(`
          @font-face {
            font-family: '${font.name}';
            src: url('${mainFontUrl}') format('${format}');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
          }
        `);
      }

      // Load each variant with its specific weight and style
      if (font.variants && font.variants.length > 0) {
        font.variants.forEach((variant) => {
          const variantUrl = getFontUrl(variant.file_url);
          if (variantUrl) {
            // Detect format from extension
            const ext = variant.file_url?.split('.').pop()?.toLowerCase();
            let format = 'truetype';
            if (ext === 'woff') format = 'woff';
            else if (ext === 'woff2') format = 'woff2';
            else if (ext === 'ttf') format = 'truetype';

            fontFaceRules.push(`
              @font-face {
                font-family: '${font.name}';
                src: url('${variantUrl}') format('${format}');
                font-weight: ${variant.weight};
                font-style: ${variant.style};
                font-display: swap;
              }
            `);
          }
        });
      }
    });

    styleEl.textContent = fontFaceRules.join("\n");

    // Cleanup on unmount
    return () => {
      if (styleEl && styleEl.parentNode) {
        // Don't remove - keep fonts loaded for other components
      }
    };
  }, [fonts]);

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
      file: null,
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
      file: null,
      sample_text: font.sample_text || "نمونه متن فارسی - Sample Text 123",
      variants: font.variants || [],
    });
    setShowFontModal(true);
  };

  const closeFontModal = () => {
    setShowFontModal(false);
    setEditingFont(null);
    if (fontFileInputRef.current) {
      fontFileInputRef.current.value = "";
    }
  };

  const handleFontFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validExtensions = ['.ttf', '.woff', '.woff2'];
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!validExtensions.includes(ext)) {
        toast.error("فرمت فایل مجاز نیست. فقط TTF، WOFF و WOFF2 پشتیبانی می‌شود.");
        return;
      }
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error("حجم فایل بیش از ۱۰ مگابایت است.");
        return;
      }
      setFontForm({ ...fontForm, file });
    }
  };

  const handleFontSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!fontForm.name || !fontForm.name_fa) {
      toast.error("نام فونت الزامی است");
      return;
    }

    try {
      let file_url = fontForm.file_url;

      // Upload file if a new one was selected
      if (fontForm.file) {
        setIsUploadingFont(true);
        const uploadResponse = await adminApi.uploadFontFile(fontForm.file);
        file_url = uploadResponse.data.file_url;
        setIsUploadingFont(false);
      }

      const data: FontCreateData = {
        name: fontForm.name,
        name_fa: fontForm.name_fa,
        file_url: file_url || undefined,
        sample_text: fontForm.sample_text || undefined,
        variants: fontForm.variants.length > 0 ? fontForm.variants : undefined,
      };

      if (editingFont) {
        updateFontMutation.mutate({ id: editingFont.id, data });
      } else {
        createFontMutation.mutate(data);
      }
    } catch (error) {
      setIsUploadingFont(false);
      toast.error(getErrorMessage(error));
    }
  };

  // Variant modal handlers
  const openVariantModal = (fontId: string) => {
    setSelectedFontId(fontId);
    setVariantForm({
      weight: 400,
      style: "normal",
      file_url: "",
      file_ttf: null,
      file_woff: null,
      file_woff2: null,
    });
    setShowVariantModal(true);
  };

  const closeVariantModal = () => {
    setShowVariantModal(false);
    setSelectedFontId(null);
    if (variantTtfInputRef.current) variantTtfInputRef.current.value = "";
    if (variantWoffInputRef.current) variantWoffInputRef.current.value = "";
    if (variantWoff2InputRef.current) variantWoff2InputRef.current.value = "";
  };

  const handleVariantFileChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    format: 'ttf' | 'woff' | 'woff2'
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      const expectedExt = `.${format}`;
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (ext !== expectedExt) {
        toast.error(`لطفاً فایل با فرمت ${format.toUpperCase()} انتخاب کنید.`);
        e.target.value = "";
        return;
      }
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error("حجم فایل بیش از ۱۰ مگابایت است.");
        e.target.value = "";
        return;
      }
      
      if (format === 'ttf') {
        setVariantForm({ ...variantForm, file_ttf: file });
      } else if (format === 'woff') {
        setVariantForm({ ...variantForm, file_woff: file });
      } else {
        setVariantForm({ ...variantForm, file_woff2: file });
      }
    }
  };

  const handleVariantSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFontId) return;

    // At least one file should be selected
    if (!variantForm.file_ttf && !variantForm.file_woff && !variantForm.file_woff2) {
      toast.error("حداقل یک فایل فونت باید انتخاب شود.");
      return;
    }

    try {
      setIsUploadingVariant(true);
      
      // Upload all selected files and collect URLs
      const fileUrls: string[] = [];
      
      if (variantForm.file_ttf) {
        const response = await adminApi.uploadFontFile(variantForm.file_ttf);
        fileUrls.push(response.data.file_url);
      }
      if (variantForm.file_woff) {
        const response = await adminApi.uploadFontFile(variantForm.file_woff);
        fileUrls.push(response.data.file_url);
      }
      if (variantForm.file_woff2) {
        const response = await adminApi.uploadFontFile(variantForm.file_woff2);
        fileUrls.push(response.data.file_url);
      }
      
      setIsUploadingVariant(false);

      // Use first uploaded URL as primary (backend stores one URL per variant)
      addVariantMutation.mutate({
        fontId: selectedFontId,
        weight: variantForm.weight,
        style: variantForm.style,
        fileUrl: fileUrls[0] || undefined,
      });
    } catch (error) {
      setIsUploadingVariant(false);
      toast.error(getErrorMessage(error));
    }
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
                <div className="flex items-center justify-between mb-3">
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
                <div className="space-y-2">
                  {font.variants && font.variants.length > 0 ? (
                    font.variants.map((variant, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500 bg-gray-200 dark:bg-gray-600 px-2 py-0.5 rounded">
                              {fontWeightLabels[variant.weight] || variant.weight}
                              {variant.style === "italic" && " Italic"}
                            </span>
                            <span className="text-xs text-gray-400">
                              وزن {variant.weight}
                            </span>
                          </div>
                          <p
                            className="text-lg leading-relaxed"
                            style={{
                              fontFamily: `'${font.name}'`,
                              fontWeight: variant.weight,
                              fontStyle: variant.style,
                            }}
                          >
                            {previewText}
                          </p>
                        </div>
                        <button
                          onClick={() =>
                            deleteVariantMutation.mutate({
                              fontId: font.id,
                              weight: variant.weight,
                              style: variant.style,
                            })
                          }
                          className="text-red-500 hover:text-red-600 p-2"
                        >
                          <Trash2 className="w-4 h-4" />
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
          
          {/* Font File Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">فایل فونت (اختیاری)</label>
            <div
              onClick={() => fontFileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition-colors"
            >
              {fontForm.file ? (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <FileType className="w-5 h-5" />
                  <span className="text-sm">{fontForm.file.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFontForm({ ...fontForm, file: null });
                      if (fontFileInputRef.current) fontFileInputRef.current.value = "";
                    }}
                    className="text-red-500 hover:text-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : fontForm.file_url ? (
                <div className="flex items-center justify-center gap-2 text-blue-600">
                  <Check className="w-5 h-5" />
                  <span className="text-sm">فایل آپلود شده</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2 text-gray-500">
                  <Upload className="w-6 h-6" />
                  <span className="text-sm">انتخاب فایل فونت</span>
                  <span className="text-xs">TTF, WOFF, WOFF2 - حداکثر ۱۰MB</span>
                </div>
              )}
            </div>
            <input
              ref={fontFileInputRef}
              type="file"
              accept=".ttf,.woff,.woff2"
              onChange={handleFontFileChange}
              className="hidden"
            />
          </div>
          
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
              disabled={isUploadingFont || createFontMutation.isPending || updateFontMutation.isPending}
            >
              {(isUploadingFont || createFontMutation.isPending || updateFontMutation.isPending) ? (
                <Loader2 className="w-4 h-4 animate-spin ml-2" />
              ) : null}
              {isUploadingFont ? "آپلود..." : editingFont ? "به‌روزرسانی" : "ایجاد"}
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
          
          {/* Font Files Upload - Three formats */}
          <div className="space-y-3">
            <label className="block text-sm font-medium">فایل‌های فونت (حداقل یکی الزامی)</label>
            
            {/* TTF Upload */}
            <div
              onClick={() => variantTtfInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-3 text-center cursor-pointer hover:border-blue-500 transition-colors"
            >
              {variantForm.file_ttf ? (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <FileType className="w-4 h-4" />
                  <span className="text-sm">{variantForm.file_ttf.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setVariantForm({ ...variantForm, file_ttf: null });
                      if (variantTtfInputRef.current) variantTtfInputRef.current.value = "";
                    }}
                    className="text-red-500 hover:text-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-gray-500">
                  <Upload className="w-4 h-4" />
                  <span className="text-sm">TTF</span>
                </div>
              )}
            </div>
            <input
              ref={variantTtfInputRef}
              type="file"
              accept=".ttf"
              onChange={(e) => handleVariantFileChange(e, 'ttf')}
              className="hidden"
            />
            
            {/* WOFF Upload */}
            <div
              onClick={() => variantWoffInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-3 text-center cursor-pointer hover:border-blue-500 transition-colors"
            >
              {variantForm.file_woff ? (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <FileType className="w-4 h-4" />
                  <span className="text-sm">{variantForm.file_woff.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setVariantForm({ ...variantForm, file_woff: null });
                      if (variantWoffInputRef.current) variantWoffInputRef.current.value = "";
                    }}
                    className="text-red-500 hover:text-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-gray-500">
                  <Upload className="w-4 h-4" />
                  <span className="text-sm">WOFF</span>
                </div>
              )}
            </div>
            <input
              ref={variantWoffInputRef}
              type="file"
              accept=".woff"
              onChange={(e) => handleVariantFileChange(e, 'woff')}
              className="hidden"
            />
            
            {/* WOFF2 Upload */}
            <div
              onClick={() => variantWoff2InputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-3 text-center cursor-pointer hover:border-blue-500 transition-colors"
            >
              {variantForm.file_woff2 ? (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <FileType className="w-4 h-4" />
                  <span className="text-sm">{variantForm.file_woff2.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setVariantForm({ ...variantForm, file_woff2: null });
                      if (variantWoff2InputRef.current) variantWoff2InputRef.current.value = "";
                    }}
                    className="text-red-500 hover:text-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-gray-500">
                  <Upload className="w-4 h-4" />
                  <span className="text-sm">WOFF2</span>
                </div>
              )}
            </div>
            <input
              ref={variantWoff2InputRef}
              type="file"
              accept=".woff2"
              onChange={(e) => handleVariantFileChange(e, 'woff2')}
              className="hidden"
            />
            
            <p className="text-xs text-gray-500">حداکثر ۱۰ مگابایت برای هر فایل</p>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={closeVariantModal}>
              انصراف
            </Button>
            <Button type="submit" disabled={isUploadingVariant || addVariantMutation.isPending}>
              {(isUploadingVariant || addVariantMutation.isPending) ? (
                <Loader2 className="w-4 h-4 animate-spin ml-2" />
              ) : null}
              {isUploadingVariant ? "آپلود..." : "افزودن"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

