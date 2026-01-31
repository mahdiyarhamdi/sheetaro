"use client";

import { useState, useRef, useCallback, DragEvent, ChangeEvent } from "react";
import { Upload, X, Loader2, Image as ImageIcon, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ImageUploadProps {
  value?: string | null;
  onChange: (file: File | null, previewUrl: string | null) => void;
  onUploadComplete?: (response: {
    file_url: string;
    preview_url: string;
    width: number;
    height: number;
  }) => void;
  accept?: string;
  maxSizeMB?: number;
  label?: string;
  hint?: string;
  error?: string;
  disabled?: boolean;
  isUploading?: boolean;
  className?: string;
  previewClassName?: string;
}

export function ImageUpload({
  value,
  onChange,
  onUploadComplete,
  accept = "image/png,image/jpeg,image/webp",
  maxSizeMB = 20,
  label = "آپلود تصویر",
  hint = "فایل را اینجا بکشید یا کلیک کنید",
  error,
  disabled = false,
  isUploading = false,
  className,
  previewClassName,
}: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(value || null);
  const inputRef = useRef<HTMLInputElement>(null);

  const displayError = error || localError;

  const validateFile = useCallback(
    (file: File): boolean => {
      setLocalError(null);

      // Check file type
      const acceptedTypes = accept.split(",").map((t) => t.trim());
      const isValidType = acceptedTypes.some(
        (type) =>
          file.type === type ||
          (type.includes("*") && file.type.startsWith(type.split("/*")[0]))
      );

      if (!isValidType) {
        setLocalError("فرمت فایل مجاز نیست");
        return false;
      }

      // Check file size
      const maxSizeBytes = maxSizeMB * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        setLocalError(`حجم فایل بیش از ${maxSizeMB} مگابایت است`);
        return false;
      }

      return true;
    },
    [accept, maxSizeMB]
  );

  const handleFile = useCallback(
    (file: File) => {
      if (!validateFile(file)) return;

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        const preview = reader.result as string;
        setPreviewUrl(preview);
        onChange(file, preview);
      };
      reader.readAsDataURL(file);
    },
    [validateFile, onChange]
  );

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled || isUploading) return;

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    },
    [disabled, isUploading, handleFile]
  );

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  const handleClick = useCallback(() => {
    if (!disabled && !isUploading && inputRef.current) {
      inputRef.current.click();
    }
  }, [disabled, isUploading]);

  const handleRemove = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setPreviewUrl(null);
      setLocalError(null);
      onChange(null, null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    },
    [onChange]
  );

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <label className="block text-sm font-medium text-foreground">
          {label}
        </label>
      )}

      <div
        onClick={handleClick}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-xl transition-all cursor-pointer",
          "hover:border-primary hover:bg-primary/5",
          isDragging && "border-primary bg-primary/10",
          displayError && "border-danger",
          disabled && "opacity-50 cursor-not-allowed",
          !previewUrl && "min-h-[160px]",
          className
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          disabled={disabled || isUploading}
          className="hidden"
        />

        {isUploading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <span className="text-sm">در حال آپلود...</span>
          </div>
        ) : previewUrl ? (
          <div className="relative group">
            <img
              src={previewUrl}
              alt="Preview"
              className={cn(
                "w-full h-auto rounded-lg object-contain max-h-[300px]",
                previewClassName
              )}
            />
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-4">
              <button
                onClick={handleRemove}
                className="p-2 rounded-full bg-danger text-white hover:bg-danger/80 transition-colors"
                title="حذف تصویر"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-muted p-4">
            <div className="p-3 rounded-full bg-primary/10">
              <Upload className="w-6 h-6 text-primary" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">{hint}</p>
              <p className="text-xs text-muted mt-1">
                PNG, JPG, WEBP - حداکثر {maxSizeMB} مگابایت
              </p>
            </div>
          </div>
        )}
      </div>

      {displayError && (
        <p className="text-sm text-danger flex items-center gap-1">
          <AlertCircle className="w-4 h-4" />
          {displayError}
        </p>
      )}
    </div>
  );
}

export default ImageUpload;

