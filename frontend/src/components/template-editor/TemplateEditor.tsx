"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Template,
  TemplatePlaceholder,
  PlaceholderType,
  PlaceholderCreateData,
  adminApi,
  getErrorMessage,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Modal from "@/components/ui/modal";
import TemplateCanvas from "./TemplateCanvas";
import PlaceholderPanel from "./PlaceholderPanel";
import PreviewPanel from "./PreviewPanel";
import {
  ImageIcon,
  Type,
  Plus,
  Save,
  Eye,
  Settings,
  Loader2,
  Upload,
  ZoomIn,
  ZoomOut,
  Layers,
  RefreshCw,
} from "lucide-react";
import toast from "react-hot-toast";

// API base URL for constructing full image URLs
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3005";

// Helper to construct full image URL from relative path
const getFullImageUrl = (url?: string): string | undefined => {
  if (!url) return undefined;
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}/api/v1${url}`;
};

interface TemplateEditorProps {
  templateId: string;
  onClose: () => void;
}

type EditorTab = "design" | "preview";

export default function TemplateEditor({ templateId, onClose }: TemplateEditorProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Editor state
  const [activeTab, setActiveTab] = useState<EditorTab>("design");
  const [selectedPlaceholder, setSelectedPlaceholder] = useState<string | null>(null);
  const [scale, setScale] = useState(0.5);
  const [localPlaceholders, setLocalPlaceholders] = useState<TemplatePlaceholder[]>([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Fetch template with placeholders
  const { data: template, isLoading } = useQuery({
    queryKey: ["template-details", templateId],
    queryFn: async () => {
      const response = await adminApi.getTemplateDetails(templateId);
      return response.data;
    },
  });
  
  // Sync local placeholders with fetched data
  useEffect(() => {
    if (template?.placeholders) {
      setLocalPlaceholders(template.placeholders);
    }
  }, [template?.placeholders]);

  // Mutations
  const createPlaceholderMutation = useMutation({
    mutationFn: (data: PlaceholderCreateData) =>
      adminApi.createPlaceholder(templateId, data),
    onSuccess: (response) => {
      const newPlaceholder = response.data;
      setLocalPlaceholders((prev) => [...prev, newPlaceholder]);
      setSelectedPlaceholder(newPlaceholder.id);
      setHasUnsavedChanges(false);
      toast.success("جایگاه جدید ایجاد شد");
      queryClient.invalidateQueries({ queryKey: ["template-details", templateId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در ایجاد جایگاه");
    },
  });

  const updatePlaceholderMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PlaceholderCreateData> }) =>
      adminApi.updatePlaceholder(id, data),
    onSuccess: (response) => {
      // Update local state directly instead of invalidating query
      // This prevents race conditions when saving multiple placeholders
      const updatedPlaceholder = response.data;
      setLocalPlaceholders((prev) =>
        prev.map((p) => (p.id === updatedPlaceholder.id ? updatedPlaceholder : p))
      );
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در به‌روزرسانی");
    },
  });

  const deletePlaceholderMutation = useMutation({
    mutationFn: (id: string) => adminApi.deletePlaceholder(id),
    onSuccess: () => {
      setLocalPlaceholders((prev) => prev.filter((p) => p.id !== selectedPlaceholder));
      setSelectedPlaceholder(null);
      toast.success("جایگاه حذف شد");
      queryClient.invalidateQueries({ queryKey: ["template-details", templateId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در حذف");
    },
  });

  // Handle placeholder selection
  const handlePlaceholderSelect = useCallback((id: string | null) => {
    // Save pending changes before switching
    if (selectedPlaceholder && hasUnsavedChanges) {
      const placeholder = localPlaceholders.find((p) => p.id === selectedPlaceholder);
      if (placeholder) {
        updatePlaceholderMutation.mutate({
          id: selectedPlaceholder,
          data: {
            x: placeholder.x,
            y: placeholder.y,
            width: placeholder.width,
            height: placeholder.height,
            rotation: placeholder.rotation,
          },
        });
      }
    }
    setSelectedPlaceholder(id);
    setHasUnsavedChanges(false);
  }, [selectedPlaceholder, hasUnsavedChanges, localPlaceholders, updatePlaceholderMutation]);

  // Handle placeholder move
  const handlePlaceholderMove = useCallback((id: string, x: number, y: number) => {
    setLocalPlaceholders((prev) =>
      prev.map((p) => (p.id === id ? { ...p, x, y } : p))
    );
    setHasUnsavedChanges(true);
  }, []);

  // Handle placeholder resize
  const handlePlaceholderResize = useCallback((id: string, width: number, height: number) => {
    setLocalPlaceholders((prev) =>
      prev.map((p) => (p.id === id ? { ...p, width, height } : p))
    );
    setHasUnsavedChanges(true);
  }, []);

  // Handle placeholder update from panel
  const handlePlaceholderUpdate = useCallback((data: Partial<TemplatePlaceholder>) => {
    if (!selectedPlaceholder) return;

    setLocalPlaceholders((prev) =>
      prev.map((p) => (p.id === selectedPlaceholder ? { ...p, ...data } : p))
    );

    // Debounced save to server
    updatePlaceholderMutation.mutate({
      id: selectedPlaceholder,
      data: data as Partial<PlaceholderCreateData>,
    });
  }, [selectedPlaceholder, updatePlaceholderMutation]);

  // Add new placeholder
  const addPlaceholder = (type: PlaceholderType) => {
    const count = localPlaceholders.filter((p) => p.type === type).length + 1;
    const name = type === "IMAGE" ? `image_${count}` : `text_${count}`;
    const label = type === "IMAGE" ? `تصویر ${count}` : `متن ${count}`;

    createPlaceholderMutation.mutate({
      type,
      name,
      label_fa: label,
      x: 50 + (count - 1) * 20,
      y: 50 + (count - 1) * 20,
      width: type === "IMAGE" ? 150 : 200,
      height: type === "IMAGE" ? 150 : 50,
      is_required: false,
      sort_order: localPlaceholders.length,
      ...(type === "TEXT" && {
        font_size: 24,
        font_weight: 400,
        font_color: "#000000",
        text_align: "right" as const,
      }),
    });
  };

  // Delete selected placeholder
  const handleDeletePlaceholder = () => {
    if (!selectedPlaceholder) return;
    if (!confirm("آیا از حذف این جایگاه مطمئن هستید؟")) return;
    deletePlaceholderMutation.mutate(selectedPlaceholder);
  };

  // Save all pending changes
  const handleSaveAll = async () => {
    if (hasUnsavedChanges && selectedPlaceholder) {
      const placeholder = localPlaceholders.find((p) => p.id === selectedPlaceholder);
      if (placeholder) {
        try {
          await updatePlaceholderMutation.mutateAsync({
            id: selectedPlaceholder,
            data: {
              x: placeholder.x,
              y: placeholder.y,
              width: placeholder.width,
              height: placeholder.height,
              rotation: placeholder.rotation,
            },
          });
          setHasUnsavedChanges(false);
        } catch (error) {
          // Error already handled by mutation
        }
      }
    }
  };

  // Handle close with save - saves all placeholders before closing
  const handleClose = async () => {
    // Save all placeholder positions before closing
    try {
      const savePromises = localPlaceholders.map(async (placeholder) => {
        try {
          await adminApi.updatePlaceholder(placeholder.id, {
            x: placeholder.x,
            y: placeholder.y,
            width: placeholder.width,
            height: placeholder.height,
            rotation: placeholder.rotation,
          });
        } catch (error) {
          console.error(`Failed to save placeholder ${placeholder.id}:`, error);
        }
      });
      await Promise.all(savePromises);
      // Invalidate queries so next open gets fresh data
      queryClient.invalidateQueries({ queryKey: ["template-details", templateId] });
    } catch (error) {
      console.error("Error saving placeholders on close:", error);
    }
    onClose();
  };

  // Duplicate selected placeholder
  const handleDuplicatePlaceholder = () => {
    if (!selectedPlaceholder) return;
    const placeholder = localPlaceholders.find((p) => p.id === selectedPlaceholder);
    if (!placeholder) return;

    createPlaceholderMutation.mutate({
      type: placeholder.type,
      name: `${placeholder.name}_copy`,
      label_fa: `${placeholder.label_fa} (کپی)`,
      x: placeholder.x + 20,
      y: placeholder.y + 20,
      width: placeholder.width,
      height: placeholder.height,
      rotation: placeholder.rotation,
      is_required: placeholder.is_required,
      sort_order: localPlaceholders.length,
      font_family: placeholder.font_family,
      font_size: placeholder.font_size,
      font_weight: placeholder.font_weight,
      font_color: placeholder.font_color,
      text_align: placeholder.text_align,
      max_length: placeholder.max_length,
      default_value: placeholder.default_value,
    });
  };

  // Handle template image change
  const handleImageChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ["image/png", "image/jpeg", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      toast.error("فرمت فایل مجاز نیست. فقط PNG، JPG و WEBP پشتیبانی می‌شود.");
      return;
    }

    // Validate file size (20MB max)
    if (file.size > 20 * 1024 * 1024) {
      toast.error("حجم فایل بیش از ۲۰ مگابایت است.");
      return;
    }

    try {
      setIsUploadingImage(true);
      
      // Upload the image
      const uploadResponse = await adminApi.uploadTemplateImage(file);
      const uploadData = uploadResponse.data;

      // Update the template with the new image
      await adminApi.updateTemplate(templateId, {
        file_url: uploadData.file_url,
        preview_url: uploadData.preview_url,
        image_width: uploadData.width,
        image_height: uploadData.height,
      });

      // Invalidate queries to refresh the template
      queryClient.invalidateQueries({ queryKey: ["template-details", templateId] });
      toast.success("تصویر قالب با موفقیت تغییر کرد");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsUploadingImage(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // Get selected placeholder object
  const selectedPlaceholderObj = localPlaceholders.find((p) => p.id === selectedPlaceholder) || null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="h-[85vh] flex flex-col bg-gray-50 dark:bg-gray-900 -m-6">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-800 border-b">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold">{template?.name_fa}</h2>
          {hasUnsavedChanges && (
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded">
              تغییرات ذخیره نشده
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Tab buttons */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setActiveTab("design")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "design"
                  ? "bg-white dark:bg-gray-600 shadow"
                  : "hover:bg-gray-200 dark:hover:bg-gray-600"
              }`}
            >
              <Settings className="w-4 h-4 inline-block ml-1" />
              طراحی
            </button>
            <button
              onClick={() => setActiveTab("preview")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "preview"
                  ? "bg-white dark:bg-gray-600 shadow"
                  : "hover:bg-gray-200 dark:hover:bg-gray-600"
              }`}
            >
              <Eye className="w-4 h-4 inline-block ml-1" />
              پیش‌نمایش
            </button>
          </div>

          {/* Save Button - Always enabled to save any position changes */}
          <Button 
            variant="primary"
            onClick={async () => {
              if (isSaving) return;
              setIsSaving(true);
              
              try {
                // Save all placeholder positions to server in parallel
                let savedCount = 0;
                const savePromises = localPlaceholders.map(async (placeholder) => {
                  try {
                    await adminApi.updatePlaceholder(placeholder.id, {
                      x: placeholder.x,
                      y: placeholder.y,
                      width: placeholder.width,
                      height: placeholder.height,
                      rotation: placeholder.rotation,
                    });
                    savedCount++;
                  } catch (error) {
                    console.error(`Failed to save placeholder ${placeholder.id}:`, error);
                  }
                });
                
                await Promise.all(savePromises);
                setHasUnsavedChanges(false);
                
                // Invalidate queries once after all saves complete
                queryClient.invalidateQueries({ queryKey: ["template-details", templateId] });
                
                if (savedCount > 0) {
                  toast.success(`${savedCount} جایگاه ذخیره شد`);
                } else {
                  toast.success("تغییرات ذخیره شد");
                }
              } finally {
                setIsSaving(false);
              }
            }}
            disabled={isSaving}
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 ml-1 animate-spin" />
            ) : (
              <Save className="w-4 h-4 ml-1" />
            )}
            ذخیره تغییرات
          </Button>

          {/* Close Button */}
          <Button 
            variant="outline" 
            onClick={handleClose}
            disabled={isSaving}
          >
            بستن
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === "design" ? (
          <>
            {/* Left Panel - Canvas */}
            <div className="flex-1 flex flex-col">
              {/* Toolbar */}
              <div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => addPlaceholder("IMAGE")}
                  >
                    <ImageIcon className="w-4 h-4 ml-1" />
                    تصویر
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => addPlaceholder("TEXT")}
                  >
                    <Type className="w-4 h-4 ml-1" />
                    متن
                  </Button>
                  
                  <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />
                  
                  {/* Change Template Image Button */}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploadingImage}
                  >
                    {isUploadingImage ? (
                      <Loader2 className="w-4 h-4 ml-1 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4 ml-1" />
                    )}
                    {isUploadingImage ? "در حال آپلود..." : "تغییر تصویر قالب"}
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setScale((s) => Math.max(0.25, s - 0.25))}
                  >
                    <ZoomOut className="w-4 h-4" />
                  </Button>
                  <span className="text-sm w-16 text-center">
                    {Math.round(scale * 100)}%
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setScale((s) => Math.min(2, s + 0.25))}
                  >
                    <ZoomIn className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Canvas */}
              <div className="flex-1 overflow-auto p-4">
                <TemplateCanvas
                  backgroundImage={getFullImageUrl(template?.file_url || template?.preview_url)}
                  placeholders={localPlaceholders}
                  selectedPlaceholder={selectedPlaceholder}
                  onPlaceholderSelect={handlePlaceholderSelect}
                  onPlaceholderMove={handlePlaceholderMove}
                  onPlaceholderResize={handlePlaceholderResize}
                  canvasWidth={template?.image_width || 800}
                  canvasHeight={template?.image_height || 600}
                  scale={scale}
                />
              </div>

              {/* Placeholders List */}
              <div className="h-32 border-t bg-white dark:bg-gray-800 overflow-x-auto">
                <div className="flex items-center gap-2 p-3">
                  <span className="text-sm font-medium text-gray-500 flex items-center gap-1 flex-shrink-0">
                    <Layers className="w-4 h-4" />
                    جایگاه‌ها:
                  </span>
                  {localPlaceholders.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedPlaceholder(p.id)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors flex-shrink-0 ${
                        selectedPlaceholder === p.id
                          ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {p.type === "IMAGE" ? (
                        <ImageIcon className="w-4 h-4 text-blue-500" />
                      ) : (
                        <Type className="w-4 h-4 text-green-500" />
                      )}
                      <span className="text-sm">{p.label_fa}</span>
                    </button>
                  ))}
                  {localPlaceholders.length === 0 && (
                    <span className="text-sm text-gray-400">
                      هنوز جایگاهی اضافه نشده است. از دکمه‌های بالا استفاده کنید.
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Right Panel - Properties */}
            <div className="w-80 bg-white dark:bg-gray-800 border-r overflow-y-auto">
              <PlaceholderPanel
                placeholder={selectedPlaceholderObj}
                onUpdate={handlePlaceholderUpdate}
                onDelete={handleDeletePlaceholder}
                onDuplicate={handleDuplicatePlaceholder}
              />
            </div>
          </>
        ) : (
          /* Preview Tab */
          <div className="flex-1 flex">
            <div className="flex-1 overflow-auto p-4">
              <TemplateCanvas
                backgroundImage={getFullImageUrl(template?.file_url || template?.preview_url)}
                placeholders={localPlaceholders}
                canvasWidth={template?.image_width || 800}
                canvasHeight={template?.image_height || 600}
                scale={scale}
                editable={false}
              />
            </div>
            <div className="w-96 bg-white dark:bg-gray-800 border-r">
              <PreviewPanel
                templateId={templateId}
                placeholders={localPlaceholders}
                templatePreviewUrl={template?.preview_url}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

