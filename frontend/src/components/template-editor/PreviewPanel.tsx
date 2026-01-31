"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { TemplatePlaceholder, adminApi, PlaceholderPreviewData, TemplatePreviewResponse } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  ImageIcon,
  Type,
  Eye,
  Download,
  Loader2,
  RefreshCw,
  Upload,
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

interface PreviewPanelProps {
  templateId: string;
  placeholders: TemplatePlaceholder[];
  templatePreviewUrl?: string;
}

export default function PreviewPanel({
  templateId,
  placeholders,
  templatePreviewUrl,
}: PreviewPanelProps) {
  // Sample data for each placeholder
  const [sampleData, setSampleData] = useState<Record<string, { image_url?: string; text_value?: string }>>({});
  
  // Preview result
  const [previewResult, setPreviewResult] = useState<TemplatePreviewResponse | null>(null);

  // Generate preview mutation
  const generatePreviewMutation = useMutation({
    mutationFn: async (data: { placeholders: PlaceholderPreviewData[] }) => {
      const response = await adminApi.generateTemplatePreview(templateId, data);
      return response.data;
    },
    onSuccess: (data) => {
      setPreviewResult(data);
      toast.success("پیش‌نمایش ایجاد شد");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "خطا در ایجاد پیش‌نمایش");
    },
  });

  // Handle sample data change
  const handleSampleChange = (placeholderId: string, field: "image_url" | "text_value", value: string) => {
    setSampleData((prev) => ({
      ...prev,
      [placeholderId]: {
        ...prev[placeholderId],
        [field]: value,
      },
    }));
  };

  // Generate preview
  const handleGeneratePreview = () => {
    const placeholderData: PlaceholderPreviewData[] = placeholders
      .filter((p) => p.is_active)
      .map((p) => ({
        placeholder_id: p.id,
        image_url: sampleData[p.id]?.image_url,
        text_value: sampleData[p.id]?.text_value || p.default_value,
      }))
      .filter((d) => d.image_url || d.text_value);

    if (placeholderData.length === 0) {
      toast.error("لطفاً حداقل یک مقدار نمونه وارد کنید");
      return;
    }

    generatePreviewMutation.mutate({ placeholders: placeholderData });
  };

  // Download preview
  const handleDownload = () => {
    if (!previewResult?.preview_url) return;
    
    const link = document.createElement("a");
    link.href = previewResult.preview_url;
    link.download = `preview_${templateId}.png`;
    link.click();
  };

  // Get sorted active placeholders
  const activePlaceholders = placeholders
    .filter((p) => p.is_active)
    .sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-gray-50 dark:bg-gray-800">
        <h3 className="font-semibold flex items-center gap-2">
          <Eye className="w-5 h-5" />
          حالت پیش‌نمایش
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          مقادیر نمونه را وارد کنید تا پیش‌نمایش قالب را ببینید
        </p>
      </div>

      {/* Sample Data Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activePlaceholders.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Type className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">جایگاهی برای پر کردن وجود ندارد</p>
          </div>
        ) : (
          activePlaceholders.map((placeholder) => (
            <div key={placeholder.id} className="space-y-2">
              <div className="flex items-center gap-2">
                {placeholder.type === "IMAGE" ? (
                  <ImageIcon className="w-4 h-4 text-blue-500" />
                ) : (
                  <Type className="w-4 h-4 text-green-500" />
                )}
                <label className="text-sm font-medium">
                  {placeholder.label_fa}
                  {placeholder.is_required && <span className="text-red-500 mr-1">*</span>}
                </label>
              </div>

              {placeholder.type === "IMAGE" ? (
                <div className="space-y-2">
                  <Input
                    value={sampleData[placeholder.id]?.image_url || ""}
                    onChange={(e) => handleSampleChange(placeholder.id, "image_url", e.target.value)}
                    placeholder="https://example.com/image.png"
                    className="text-sm"
                  />
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="text-xs">
                      <Upload className="w-3 h-3 ml-1" />
                      آپلود تصویر
                    </Button>
                    {sampleData[placeholder.id]?.image_url && (
                      <img
                        src={sampleData[placeholder.id].image_url}
                        alt="Preview"
                        className="w-10 h-10 object-cover rounded border"
                        onError={(e) => (e.currentTarget.style.display = "none")}
                      />
                    )}
                  </div>
                </div>
              ) : (
                <Input
                  value={sampleData[placeholder.id]?.text_value || placeholder.default_value || ""}
                  onChange={(e) => handleSampleChange(placeholder.id, "text_value", e.target.value)}
                  placeholder={placeholder.default_value || "متن نمونه..."}
                  style={{
                    fontFamily: placeholder.font_family,
                    fontSize: Math.min(placeholder.font_size || 14, 16),
                  }}
                />
              )}
            </div>
          ))
        )}
      </div>

      {/* Preview Actions */}
      <div className="p-4 border-t space-y-4">
        <Button
          onClick={handleGeneratePreview}
          disabled={generatePreviewMutation.isPending}
          className="w-full"
        >
          {generatePreviewMutation.isPending ? (
            <Loader2 className="w-4 h-4 ml-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 ml-2" />
          )}
          ایجاد پیش‌نمایش
        </Button>

        {/* Preview Result */}
        {previewResult && (
          <div className="space-y-3">
            <div className="relative rounded-lg overflow-hidden border bg-gray-100">
              <img
                src={getFullImageUrl(previewResult.preview_url)}
                alt="Generated Preview"
                className="w-full h-auto"
              />
              <div className="absolute bottom-2 right-2 text-xs bg-black/70 text-white px-2 py-1 rounded">
                {previewResult.width} × {previewResult.height}
              </div>
            </div>

            <Button
              variant="outline"
              onClick={handleDownload}
              className="w-full"
            >
              <Download className="w-4 h-4 ml-2" />
              دانلود پیش‌نمایش
            </Button>
          </div>
        )}

        {/* Original template preview */}
        {!previewResult && templatePreviewUrl && (
          <div className="space-y-2">
            <p className="text-xs text-gray-500">پیش‌نمایش قالب اصلی:</p>
            <div className="rounded-lg overflow-hidden border bg-gray-100">
              <img
                src={getFullImageUrl(templatePreviewUrl)}
                alt="Template Preview"
                className="w-full h-auto opacity-50"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

