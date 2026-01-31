"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { TemplatePlaceholder, PlaceholderType } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useDynamicFonts } from "@/hooks/useDynamicFonts";
import { ImageIcon, Type, Move, RotateCw, Square } from "lucide-react";

interface TemplateCanvasProps {
  backgroundImage?: string;
  placeholders: TemplatePlaceholder[];
  selectedPlaceholder?: string | null;
  onPlaceholderSelect?: (id: string | null) => void;
  onPlaceholderMove?: (id: string, x: number, y: number) => void;
  onPlaceholderResize?: (id: string, width: number, height: number) => void;
  onPlaceholderRotate?: (id: string, rotation: number) => void;
  canvasWidth?: number;
  canvasHeight?: number;
  scale?: number;
  editable?: boolean;
}

export default function TemplateCanvas({
  backgroundImage,
  placeholders,
  selectedPlaceholder,
  onPlaceholderSelect,
  onPlaceholderMove,
  onPlaceholderResize,
  onPlaceholderRotate,
  canvasWidth = 800,
  canvasHeight = 600,
  scale = 1,
  editable = true,
}: TemplateCanvasProps) {
  // Load fonts dynamically via @font-face so they render correctly in canvas
  useDynamicFonts();
  
  const canvasRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ width: 0, height: 0, x: 0, y: 0 });

  // Handle canvas click to deselect
  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      onPlaceholderSelect?.(null);
    }
  };

  // Handle placeholder selection
  const handlePlaceholderClick = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    onPlaceholderSelect?.(id);
  };

  // Handle drag start
  const handleDragStart = (e: React.MouseEvent, placeholder: TemplatePlaceholder) => {
    if (!editable) return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
    onPlaceholderSelect?.(placeholder.id);
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
      setDragStart({
        x: e.clientX - (placeholder.x * scale),
        y: e.clientY - (placeholder.y * scale),
      });
    }
  };

  // Handle drag
  const handleDrag = useCallback((e: MouseEvent) => {
    if (!isDragging || !selectedPlaceholder || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    let newX = Math.round((e.clientX - dragStart.x) / scale);
    let newY = Math.round((e.clientY - dragStart.y) / scale);
    
    // Constrain to canvas bounds
    newX = Math.max(0, Math.min(newX, canvasWidth - 50));
    newY = Math.max(0, Math.min(newY, canvasHeight - 50));
    
    onPlaceholderMove?.(selectedPlaceholder, newX, newY);
  }, [isDragging, selectedPlaceholder, dragStart, scale, canvasWidth, canvasHeight, onPlaceholderMove]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Handle resize start
  const handleResizeStart = (e: React.MouseEvent, placeholder: TemplatePlaceholder) => {
    if (!editable) return;
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    onPlaceholderSelect?.(placeholder.id);
    
    setResizeStart({
      width: placeholder.width,
      height: placeholder.height,
      x: e.clientX,
      y: e.clientY,
    });
  };

  // Handle resize
  const handleResize = useCallback((e: MouseEvent) => {
    if (!isResizing || !selectedPlaceholder) return;
    
    const deltaX = (e.clientX - resizeStart.x) / scale;
    const deltaY = (e.clientY - resizeStart.y) / scale;
    
    const newWidth = Math.max(50, Math.round(resizeStart.width + deltaX));
    const newHeight = Math.max(50, Math.round(resizeStart.height + deltaY));
    
    onPlaceholderResize?.(selectedPlaceholder, newWidth, newHeight);
  }, [isResizing, selectedPlaceholder, resizeStart, scale, onPlaceholderResize]);

  // Handle resize end
  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Add/remove event listeners
  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleDrag);
      window.addEventListener("mouseup", handleDragEnd);
    }
    if (isResizing) {
      window.addEventListener("mousemove", handleResize);
      window.addEventListener("mouseup", handleResizeEnd);
    }
    
    return () => {
      window.removeEventListener("mousemove", handleDrag);
      window.removeEventListener("mouseup", handleDragEnd);
      window.removeEventListener("mousemove", handleResize);
      window.removeEventListener("mouseup", handleResizeEnd);
    };
  }, [isDragging, isResizing, handleDrag, handleDragEnd, handleResize, handleResizeEnd]);

  // Get placeholder icon
  const getPlaceholderIcon = (type: PlaceholderType) => {
    switch (type) {
      case "IMAGE":
        return <ImageIcon className="w-6 h-6" />;
      case "TEXT":
        return <Type className="w-6 h-6" />;
      default:
        return <Square className="w-6 h-6" />;
    }
  };

  // Get placeholder color - using low opacity for transparency so template shows through
  const getPlaceholderColor = (type: PlaceholderType, isSelected: boolean) => {
    const baseColors = {
      IMAGE: {
        bg: isSelected ? "bg-blue-500/20" : "bg-blue-500/10",
        border: isSelected ? "border-blue-500" : "border-blue-400/70",
        text: "text-blue-600",
      },
      TEXT: {
        bg: isSelected ? "bg-green-500/20" : "bg-green-500/10",
        border: isSelected ? "border-green-500" : "border-green-400/70",
        text: "text-green-600",
      },
    };
    return baseColors[type] || baseColors.IMAGE;
  };

  return (
    <div className="relative overflow-auto bg-gray-100 dark:bg-gray-900 rounded-lg p-4">
      <div
        ref={canvasRef}
        className="relative mx-auto bg-white shadow-lg"
        style={{
          width: canvasWidth * scale,
          height: canvasHeight * scale,
          backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
          backgroundSize: "contain",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "center",
        }}
        onClick={handleCanvasClick}
      >
        {/* No background image placeholder */}
        {!backgroundImage && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
            <ImageIcon className="w-12 h-12 mb-2" />
            <span className="text-sm">تصویر قالب را آپلود کنید</span>
          </div>
        )}

        {/* Placeholders */}
        {placeholders.map((placeholder) => {
          const isSelected = selectedPlaceholder === placeholder.id;
          const colors = getPlaceholderColor(placeholder.type, isSelected);
          
          return (
            <div
              key={placeholder.id}
              className={cn(
                "absolute border-2 border-dashed cursor-move transition-colors",
                colors.bg,
                colors.border,
                isSelected && "ring-2 ring-offset-2 ring-blue-500"
              )}
              style={{
                left: placeholder.x * scale,
                top: placeholder.y * scale,
                width: placeholder.width * scale,
                height: placeholder.height * scale,
                transform: `rotate(${placeholder.rotation || 0}deg)`,
              }}
              onClick={(e) => handlePlaceholderClick(e, placeholder.id)}
              onMouseDown={(e) => handleDragStart(e, placeholder)}
            >
              {/* Placeholder content */}
              <div className={cn(
                "absolute inset-0 flex flex-col items-center justify-center",
                colors.text
              )}>
                {getPlaceholderIcon(placeholder.type)}
                <span className="text-xs mt-1 font-medium truncate max-w-full px-1">
                  {placeholder.label_fa}
                </span>
                {placeholder.type === "TEXT" && placeholder.default_value && (
                  <span
                    className="text-xs mt-1 opacity-60 truncate max-w-full px-1"
                    style={{
                      fontFamily: placeholder.font_family,
                      fontSize: Math.max(8, (placeholder.font_size || 12) * scale * 0.5),
                    }}
                  >
                    {placeholder.default_value}
                  </span>
                )}
              </div>

              {/* Resize handle */}
              {editable && isSelected && (
                <div
                  className="absolute -bottom-2 -left-2 w-4 h-4 bg-blue-500 rounded-full cursor-se-resize border-2 border-white shadow"
                  onMouseDown={(e) => handleResizeStart(e, placeholder)}
                />
              )}

              {/* Move indicator */}
              {editable && isSelected && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white rounded px-1 py-0.5 text-xs flex items-center gap-1 shadow">
                  <Move className="w-3 h-3" />
                  {Math.round(placeholder.x)}, {Math.round(placeholder.y)}
                </div>
              )}

              {/* Size indicator */}
              {editable && isSelected && (
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 bg-gray-700 text-white rounded px-1 py-0.5 text-xs shadow">
                  {Math.round(placeholder.width)} × {Math.round(placeholder.height)}
                </div>
              )}
            </div>
          );
        })}

        {/* Grid overlay when dragging */}
        {(isDragging || isResizing) && (
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: `
                linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)
              `,
              backgroundSize: `${20 * scale}px ${20 * scale}px`,
            }}
          />
        )}
      </div>

      {/* Canvas info */}
      <div className="absolute bottom-2 left-2 text-xs text-gray-500 bg-white/80 px-2 py-1 rounded">
        {canvasWidth} × {canvasHeight} px | {Math.round(scale * 100)}%
      </div>
    </div>
  );
}

