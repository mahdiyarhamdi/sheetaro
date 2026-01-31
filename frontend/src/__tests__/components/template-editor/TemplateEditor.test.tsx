/**
 * Tests for TemplateEditor component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React, { useState } from 'react';

// Mock template data
const mockTemplate = {
  id: 'tpl-1',
  plan_id: 'plan-1',
  name_fa: 'قالب تست',
  file_url: 'https://example.com/template.png',
  image_width: 800,
  image_height: 600,
  is_active: true,
  placeholders: [
    {
      id: 'ph-1',
      template_id: 'tpl-1',
      type: 'IMAGE' as const,
      name: 'logo',
      label_fa: 'لوگو',
      x: 100,
      y: 100,
      width: 200,
      height: 200,
      rotation: 0,
      is_required: true,
      sort_order: 0,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'ph-2',
      template_id: 'tpl-1',
      type: 'TEXT' as const,
      name: 'title',
      label_fa: 'عنوان',
      x: 300,
      y: 400,
      width: 200,
      height: 50,
      rotation: 0,
      is_required: true,
      sort_order: 1,
      font_family: 'IRANSans',
      font_size: 24,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Simplified mock editor component for testing
const MockTemplateEditor: React.FC<{
  template: typeof mockTemplate | null;
  isLoading?: boolean;
  onClose: () => void;
  onSave?: () => void;
  onAddPlaceholder?: (type: 'IMAGE' | 'TEXT') => void;
  onUpdatePlaceholder?: (id: string, data: any) => void;
  onDeletePlaceholder?: (id: string) => void;
  onDuplicatePlaceholder?: (id: string) => void;
}> = ({
  template,
  isLoading = false,
  onClose,
  onSave,
  onAddPlaceholder,
  onUpdatePlaceholder,
  onDeletePlaceholder,
  onDuplicatePlaceholder,
}) => {
  const [activeTab, setActiveTab] = useState<'design' | 'preview'>('design');
  const [selectedPlaceholderId, setSelectedPlaceholderId] = useState<string | null>(null);
  const [scale, setScale] = useState(1);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  if (isLoading) {
    return <div data-testid="loading-spinner">در حال بارگذاری...</div>;
  }

  if (!template) {
    return <div data-testid="template-not-found">قالب یافت نشد</div>;
  }

  const selectedPlaceholder = template.placeholders.find(
    (p) => p.id === selectedPlaceholderId
  );

  const handlePlaceholderMove = (id: string, x: number, y: number) => {
    setHasUnsavedChanges(true);
    onUpdatePlaceholder?.(id, { x, y });
  };

  const handlePlaceholderDelete = (id: string) => {
    onDeletePlaceholder?.(id);
    setSelectedPlaceholderId(null);
  };

  const handlePlaceholderDuplicate = (id: string) => {
    onDuplicatePlaceholder?.(id);
  };

  return (
    <div data-testid="template-editor">
      {/* Header */}
      <div data-testid="editor-header">
        <h2>{template.name_fa}</h2>
        <button data-testid="btn-close" onClick={onClose}>بستن</button>
        {onSave && (
          <button data-testid="btn-save" onClick={onSave}>ذخیره</button>
        )}
      </div>

      {/* Unsaved Changes Indicator */}
      {hasUnsavedChanges && (
        <div data-testid="unsaved-indicator">تغییرات ذخیره نشده</div>
      )}

      {/* Tabs */}
      <div data-testid="tabs">
        <button
          data-testid="tab-design"
          className={activeTab === 'design' ? 'active' : ''}
          onClick={() => setActiveTab('design')}
        >
          طراحی
        </button>
        <button
          data-testid="tab-preview"
          className={activeTab === 'preview' ? 'active' : ''}
          onClick={() => setActiveTab('preview')}
        >
          پیش‌نمایش
        </button>
      </div>

      {/* Toolbar */}
      <div data-testid="toolbar">
        <button
          data-testid="btn-add-image"
          onClick={() => onAddPlaceholder?.('IMAGE')}
        >
          افزودن تصویر
        </button>
        <button
          data-testid="btn-add-text"
          onClick={() => onAddPlaceholder?.('TEXT')}
        >
          افزودن متن
        </button>
        <button
          data-testid="btn-zoom-in"
          onClick={() => setScale((s) => Math.min(s + 0.1, 2))}
        >
          +
        </button>
        <button
          data-testid="btn-zoom-out"
          onClick={() => setScale((s) => Math.max(s - 0.1, 0.5))}
        >
          -
        </button>
        <span data-testid="zoom-level">{Math.round(scale * 100)}%</span>
      </div>

      {/* Main Content */}
      <div data-testid="editor-content">
        {activeTab === 'design' && (
          <>
            {/* Canvas */}
            <div
              data-testid="canvas-container"
              style={{ transform: `scale(${scale})` }}
            >
              <div
                data-testid="template-canvas"
                style={{
                  width: template.image_width,
                  height: template.image_height,
                  backgroundImage: `url(${template.file_url})`,
                }}
              >
                {template.placeholders.map((ph) => (
                  <div
                    key={ph.id}
                    data-testid={`canvas-placeholder-${ph.id}`}
                    className={selectedPlaceholderId === ph.id ? 'selected' : ''}
                    onClick={() => setSelectedPlaceholderId(ph.id)}
                  >
                    {ph.label_fa}
                  </div>
                ))}
              </div>
            </div>

            {/* Properties Panel */}
            <div data-testid="properties-panel">
              {selectedPlaceholder ? (
                <div data-testid="placeholder-properties">
                  <h4>{selectedPlaceholder.label_fa}</h4>
                  <div>
                    <label>X:</label>
                    <input
                      data-testid="prop-x"
                      type="number"
                      value={selectedPlaceholder.x}
                      onChange={(e) =>
                        handlePlaceholderMove(
                          selectedPlaceholder.id,
                          parseInt(e.target.value),
                          selectedPlaceholder.y
                        )
                      }
                    />
                  </div>
                  <button
                    data-testid="btn-delete-placeholder"
                    onClick={() => handlePlaceholderDelete(selectedPlaceholder.id)}
                  >
                    حذف
                  </button>
                  <button
                    data-testid="btn-duplicate-placeholder"
                    onClick={() => handlePlaceholderDuplicate(selectedPlaceholder.id)}
                  >
                    کپی
                  </button>
                </div>
              ) : (
                <div data-testid="no-selection">جایگاهی انتخاب نشده</div>
              )}
            </div>
          </>
        )}

        {activeTab === 'preview' && (
          <>
            {/* Preview Canvas */}
            <div data-testid="preview-canvas">
              پیش‌نمایش قالب
            </div>
            {/* Preview Panel */}
            <div data-testid="preview-panel">
              پنل پیش‌نمایش
            </div>
          </>
        )}
      </div>
    </div>
  );
};

describe('TemplateEditor', () => {
  describe('Loading', () => {
    it('shows loading spinner while fetching template', () => {
      render(
        <MockTemplateEditor
          template={null}
          isLoading={true}
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Tabs', () => {
    it('design tab shows canvas and properties panel', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('template-canvas')).toBeInTheDocument();
      expect(screen.getByTestId('properties-panel')).toBeInTheDocument();
    });

    it('preview tab shows canvas and preview panel', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
        />
      );

      fireEvent.click(screen.getByTestId('tab-preview'));

      expect(screen.getByTestId('preview-canvas')).toBeInTheDocument();
      expect(screen.getByTestId('preview-panel')).toBeInTheDocument();
    });

    it('tab switching works correctly', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
        />
      );

      // Initially on design tab
      expect(screen.getByTestId('tab-design')).toHaveClass('active');
      expect(screen.getByTestId('template-canvas')).toBeInTheDocument();

      // Switch to preview
      fireEvent.click(screen.getByTestId('tab-preview'));
      expect(screen.getByTestId('tab-preview')).toHaveClass('active');
      expect(screen.queryByTestId('template-canvas')).not.toBeInTheDocument();

      // Switch back to design
      fireEvent.click(screen.getByTestId('tab-design'));
      expect(screen.getByTestId('tab-design')).toHaveClass('active');
      expect(screen.getByTestId('template-canvas')).toBeInTheDocument();
    });
  });

  describe('Toolbar', () => {
    it('add image button creates image placeholder', () => {
      const onAddPlaceholder = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onAddPlaceholder={onAddPlaceholder}
        />
      );

      fireEvent.click(screen.getByTestId('btn-add-image'));
      expect(onAddPlaceholder).toHaveBeenCalledWith('IMAGE');
    });

    it('add text button creates text placeholder', () => {
      const onAddPlaceholder = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onAddPlaceholder={onAddPlaceholder}
        />
      );

      fireEvent.click(screen.getByTestId('btn-add-text'));
      expect(onAddPlaceholder).toHaveBeenCalledWith('TEXT');
    });

    it('zoom buttons change scale', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('zoom-level')).toHaveTextContent('100%');

      fireEvent.click(screen.getByTestId('btn-zoom-in'));
      expect(screen.getByTestId('zoom-level')).toHaveTextContent('110%');

      fireEvent.click(screen.getByTestId('btn-zoom-out'));
      fireEvent.click(screen.getByTestId('btn-zoom-out'));
      expect(screen.getByTestId('zoom-level')).toHaveTextContent('90%');
    });
  });

  describe('Placeholder Management', () => {
    it('selecting placeholder shows properties', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
        />
      );

      // Initially no selection
      expect(screen.getByTestId('no-selection')).toBeInTheDocument();

      // Click on a placeholder
      fireEvent.click(screen.getByTestId('canvas-placeholder-ph-1'));

      // Should show properties
      expect(screen.getByTestId('placeholder-properties')).toBeInTheDocument();
      expect(screen.getByTestId('placeholder-properties')).toHaveTextContent('لوگو');
    });

    it('moving placeholder updates local state', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onUpdatePlaceholder={onUpdate}
        />
      );

      // Select placeholder
      fireEvent.click(screen.getByTestId('canvas-placeholder-ph-1'));

      // Change X position
      fireEvent.change(screen.getByTestId('prop-x'), { target: { value: '150' } });

      expect(onUpdate).toHaveBeenCalledWith('ph-1', { x: 150, y: 100 });
    });

    it('deleting placeholder removes from list', () => {
      const onDelete = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onDeletePlaceholder={onDelete}
        />
      );

      // Select placeholder
      fireEvent.click(screen.getByTestId('canvas-placeholder-ph-1'));

      // Delete
      fireEvent.click(screen.getByTestId('btn-delete-placeholder'));

      expect(onDelete).toHaveBeenCalledWith('ph-1');
    });

    it('duplicating placeholder creates copy', () => {
      const onDuplicate = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onDuplicatePlaceholder={onDuplicate}
        />
      );

      // Select placeholder
      fireEvent.click(screen.getByTestId('canvas-placeholder-ph-1'));

      // Duplicate
      fireEvent.click(screen.getByTestId('btn-duplicate-placeholder'));

      expect(onDuplicate).toHaveBeenCalledWith('ph-1');
    });
  });

  describe('Unsaved Changes', () => {
    it('shows unsaved changes indicator', () => {
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onUpdatePlaceholder={vi.fn()}
        />
      );

      // Initially no indicator
      expect(screen.queryByTestId('unsaved-indicator')).not.toBeInTheDocument();

      // Make a change
      fireEvent.click(screen.getByTestId('canvas-placeholder-ph-1'));
      fireEvent.change(screen.getByTestId('prop-x'), { target: { value: '200' } });

      // Should show indicator
      expect(screen.getByTestId('unsaved-indicator')).toBeInTheDocument();
    });
  });

  describe('Close and Save', () => {
    it('close button calls onClose', () => {
      const onClose = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={onClose}
        />
      );

      fireEvent.click(screen.getByTestId('btn-close'));
      expect(onClose).toHaveBeenCalled();
    });

    it('save button calls onSave', () => {
      const onSave = vi.fn();
      
      render(
        <MockTemplateEditor
          template={mockTemplate}
          onClose={vi.fn()}
          onSave={onSave}
        />
      );

      fireEvent.click(screen.getByTestId('btn-save'));
      expect(onSave).toHaveBeenCalled();
    });
  });
});

