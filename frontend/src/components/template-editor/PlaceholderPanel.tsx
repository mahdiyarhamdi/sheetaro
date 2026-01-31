"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { TemplatePlaceholder, PlaceholderType, TextAlign, SystemFont, adminApi } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  ImageIcon,
  Type,
  Trash2,
  RotateCw,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Bold,
  Copy,
} from "lucide-react";

interface PlaceholderPanelProps {
  placeholder: TemplatePlaceholder | null;
  onUpdate: (data: Partial<TemplatePlaceholder>) => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

const fontWeightOptions = [
  { value: 100, label: "Thin (100)" },
  { value: 200, label: "ExtraLight (200)" },
  { value: 300, label: "Light (300)" },
  { value: 400, label: "Regular (400)" },
  { value: 500, label: "Medium (500)" },
  { value: 600, label: "SemiBold (600)" },
  { value: 700, label: "Bold (700)" },
  { value: 800, label: "ExtraBold (800)" },
  { value: 900, label: "Black (900)" },
];

export default function PlaceholderPanel({
  placeholder,
  onUpdate,
  onDelete,
  onDuplicate,
}: PlaceholderPanelProps) {
  // Local state for form values
  const [formData, setFormData] = useState<Partial<TemplatePlaceholder>>({});

  // Fetch system fonts
  const { data: fonts } = useQuery({
    queryKey: ["fonts-active"],
    queryFn: async () => {
      const response = await adminApi.getFonts(true);
      return response.data;
    },
  });

  // Sync local state with placeholder prop
  useEffect(() => {
    if (placeholder) {
      setFormData({ ...placeholder });
    } else {
      setFormData({});
    }
  }, [placeholder]);

  // Handle field change
  const handleChange = (field: keyof TemplatePlaceholder, value: any) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onUpdate({ [field]: value });
  };

  if (!placeholder) {
    return (
      <div className="p-4 text-center text-gray-500">
        <div className="p-8 border-2 border-dashed border-gray-200 rounded-lg">
          <Type className="w-8 h-8 mx-auto mb-2 text-gray-300" />
          <p className="text-sm">یک جایگاه را برای ویرایش انتخاب کنید</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div className="flex items-center gap-2">
          {placeholder.type === "IMAGE" ? (
            <div className="p-2 bg-blue-100 rounded-lg">
              <ImageIcon className="w-5 h-5 text-blue-600" />
            </div>
          ) : (
            <div className="p-2 bg-green-100 rounded-lg">
              <Type className="w-5 h-5 text-green-600" />
            </div>
          )}
          <div>
            <h3 className="font-semibold">{placeholder.label_fa}</h3>
            <p className="text-xs text-gray-500">{placeholder.type === "IMAGE" ? "تصویر" : "متن"}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={onDuplicate} title="کپی">
            <Copy className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={onDelete} title="حذف" className="text-red-500 hover:text-red-600">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700">مشخصات</h4>
        
        <Input
          label="نام (slug)"
          value={formData.name || ""}
          onChange={(e) => handleChange("name", e.target.value)}
          placeholder="logo"
          className="font-mono text-sm"
        />
        
        <Input
          label="عنوان فارسی"
          value={formData.label_fa || ""}
          onChange={(e) => handleChange("label_fa", e.target.value)}
          placeholder="لوگوی شرکت"
        />

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.is_required ?? true}
              onChange={(e) => handleChange("is_required", e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm">اجباری</span>
          </label>
        </div>
      </div>

      {/* Position & Size */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700">موقعیت و اندازه</h4>
        
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="X"
            type="number"
            value={formData.x ?? 0}
            onChange={(e) => handleChange("x", parseInt(e.target.value) || 0)}
          />
          <Input
            label="Y"
            type="number"
            value={formData.y ?? 0}
            onChange={(e) => handleChange("y", parseInt(e.target.value) || 0)}
          />
          <Input
            label="عرض"
            type="number"
            value={formData.width ?? 100}
            onChange={(e) => handleChange("width", parseInt(e.target.value) || 100)}
          />
          <Input
            label="ارتفاع"
            type="number"
            value={formData.height ?? 100}
            onChange={(e) => handleChange("height", parseInt(e.target.value) || 100)}
          />
        </div>

        <div className="flex items-center gap-3">
          <Input
            label="چرخش"
            type="number"
            value={formData.rotation ?? 0}
            onChange={(e) => handleChange("rotation", parseInt(e.target.value) || 0)}
            className="flex-1"
          />
          <div className="flex items-center gap-1 mt-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleChange("rotation", ((formData.rotation || 0) - 90 + 360) % 360)}
            >
              <RotateCw className="w-4 h-4 rotate-180" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleChange("rotation", ((formData.rotation || 0) + 90) % 360)}
            >
              <RotateCw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Text-specific options */}
      {placeholder.type === "TEXT" && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">تنظیمات متن</h4>
          
          {/* Font Family */}
          <div>
            <label className="block text-sm font-medium mb-1">فونت</label>
            <select
              value={formData.font_family || ""}
              onChange={(e) => handleChange("font_family", e.target.value)}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="">انتخاب فونت...</option>
              {fonts?.map((font) => (
                <option key={font.id} value={font.name}>
                  {font.name_fa} ({font.name})
                </option>
              ))}
            </select>
          </div>

          {/* Font Size & Weight */}
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="اندازه (px)"
              type="number"
              value={formData.font_size ?? 24}
              onChange={(e) => handleChange("font_size", parseInt(e.target.value) || 24)}
            />
            <div>
              <label className="block text-sm font-medium mb-1">وزن</label>
              <select
                value={formData.font_weight ?? 400}
                onChange={(e) => handleChange("font_weight", parseInt(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
              >
                {fontWeightOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Font Color */}
          <div>
            <label className="block text-sm font-medium mb-1">رنگ</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={formData.font_color || "#000000"}
                onChange={(e) => handleChange("font_color", e.target.value)}
                className="w-10 h-10 rounded border cursor-pointer"
              />
              <input
                type="text"
                value={formData.font_color || "#000000"}
                onChange={(e) => handleChange("font_color", e.target.value)}
                className="flex-1 px-3 py-2 border rounded-lg font-mono text-sm dark:bg-gray-700 dark:border-gray-600"
                placeholder="#000000"
              />
            </div>
          </div>

          {/* Text Align */}
          <div>
            <label className="block text-sm font-medium mb-1">تراز</label>
            <div className="flex gap-1">
              {[
                { value: "right", icon: AlignRight, label: "راست" },
                { value: "center", icon: AlignCenter, label: "وسط" },
                { value: "left", icon: AlignLeft, label: "چپ" },
              ].map((align) => (
                <Button
                  key={align.value}
                  variant={formData.text_align === align.value ? "primary" : "outline"}
                  size="sm"
                  onClick={() => handleChange("text_align", align.value as TextAlign)}
                  title={align.label}
                  className="flex-1"
                >
                  <align.icon className="w-4 h-4" />
                </Button>
              ))}
            </div>
          </div>

          {/* Max Length */}
          <Input
            label="حداکثر طول"
            type="number"
            value={formData.max_length ?? ""}
            onChange={(e) => handleChange("max_length", e.target.value ? parseInt(e.target.value) : null)}
            placeholder="بدون محدودیت"
          />

          {/* Default Value */}
          <div>
            <label className="block text-sm font-medium mb-1">مقدار پیش‌فرض</label>
            <textarea
              value={formData.default_value || ""}
              onChange={(e) => handleChange("default_value", e.target.value)}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
              rows={2}
              placeholder="متن نمونه..."
              style={{
                fontFamily: formData.font_family,
                fontSize: Math.min(formData.font_size || 14, 16),
                fontWeight: formData.font_weight,
                color: formData.font_color,
              }}
            />
          </div>
        </div>
      )}

      {/* Sort Order */}
      <div className="pt-4 border-t">
        <Input
          label="ترتیب نمایش"
          type="number"
          value={formData.sort_order ?? 0}
          onChange={(e) => handleChange("sort_order", parseInt(e.target.value) || 0)}
        />
      </div>
    </div>
  );
}

