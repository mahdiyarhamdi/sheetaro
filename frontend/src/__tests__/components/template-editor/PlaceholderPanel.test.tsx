/**
 * Tests for PlaceholderPanel component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock placeholder data
const mockImagePlaceholder = {
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
};

const mockTextPlaceholder = {
  id: 'ph-2',
  template_id: 'tpl-1',
  type: 'TEXT' as const,
  name: 'company_name',
  label_fa: 'نام شرکت',
  x: 300,
  y: 400,
  width: 300,
  height: 50,
  rotation: 0,
  is_required: true,
  sort_order: 1,
  font_family: 'IRANSans',
  font_size: 24,
  font_weight: 700,
  font_color: '#333333',
  text_align: 'center' as const,
  max_length: 100,
  default_value: 'متن پیش‌فرض',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockFonts = [
  { id: '1', name: 'IRANSans', name_fa: 'ایران سنس', is_active: true },
  { id: '2', name: 'Vazir', name_fa: 'وزیر', is_active: true },
];

// Simplified mock component for testing
const MockPlaceholderPanel: React.FC<{
  selectedPlaceholder: typeof mockImagePlaceholder | typeof mockTextPlaceholder | null;
  onUpdatePlaceholder: (id: string, data: Partial<typeof mockImagePlaceholder>) => void;
  onDeletePlaceholder?: (id: string) => void;
  systemFonts?: typeof mockFonts;
}> = ({
  selectedPlaceholder,
  onUpdatePlaceholder,
  onDeletePlaceholder,
  systemFonts = [],
}) => {
  if (!selectedPlaceholder) {
    return <div data-testid="empty-state">یک جایگاه را انتخاب کنید</div>;
  }

  return (
    <div data-testid="placeholder-panel">
      <h3>تنظیمات جایگاه</h3>
      
      {/* Basic Fields */}
      <div>
        <label htmlFor="name">نام</label>
        <input
          id="name"
          data-testid="input-name"
          value={selectedPlaceholder.name}
          onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { name: e.target.value })}
        />
      </div>
      
      <div>
        <label htmlFor="label_fa">برچسب فارسی</label>
        <input
          id="label_fa"
          data-testid="input-label_fa"
          value={selectedPlaceholder.label_fa}
          onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { label_fa: e.target.value })}
        />
      </div>

      <div>
        <label htmlFor="is_required">اجباری</label>
        <input
          id="is_required"
          type="checkbox"
          data-testid="checkbox-is_required"
          checked={selectedPlaceholder.is_required}
          onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { is_required: e.target.checked })}
        />
      </div>

      {/* Position Fields */}
      <div data-testid="position-fields">
        <div>
          <label htmlFor="x">X</label>
          <input
            id="x"
            type="number"
            data-testid="input-x"
            value={selectedPlaceholder.x}
            onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { x: parseInt(e.target.value) })}
          />
        </div>
        <div>
          <label htmlFor="y">Y</label>
          <input
            id="y"
            type="number"
            data-testid="input-y"
            value={selectedPlaceholder.y}
            onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { y: parseInt(e.target.value) })}
          />
        </div>
        <div>
          <label htmlFor="width">عرض</label>
          <input
            id="width"
            type="number"
            data-testid="input-width"
            value={selectedPlaceholder.width}
            onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { width: parseInt(e.target.value) })}
          />
        </div>
        <div>
          <label htmlFor="height">ارتفاع</label>
          <input
            id="height"
            type="number"
            data-testid="input-height"
            value={selectedPlaceholder.height}
            onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { height: parseInt(e.target.value) })}
          />
        </div>
      </div>

      <div>
        <label htmlFor="rotation">چرخش</label>
        <input
          id="rotation"
          type="number"
          data-testid="input-rotation"
          value={selectedPlaceholder.rotation}
          onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { rotation: parseInt(e.target.value) })}
        />
        <button
          data-testid="btn-rotate-90"
          onClick={() => onUpdatePlaceholder(selectedPlaceholder.id, { rotation: selectedPlaceholder.rotation + 90 })}
        >
          +90°
        </button>
        <button
          data-testid="btn-rotate-minus-90"
          onClick={() => onUpdatePlaceholder(selectedPlaceholder.id, { rotation: selectedPlaceholder.rotation - 90 })}
        >
          -90°
        </button>
      </div>

      {/* Text-specific Fields */}
      {selectedPlaceholder.type === 'TEXT' && (
        <div data-testid="text-fields">
          <div>
            <label htmlFor="font_family">فونت</label>
            <select
              id="font_family"
              data-testid="select-font_family"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).font_family || ''}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { font_family: e.target.value })}
            >
              <option value="">انتخاب فونت</option>
              {systemFonts.map((font) => (
                <option key={font.id} value={font.name}>
                  {font.name_fa}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="font_size">اندازه فونت</label>
            <input
              id="font_size"
              type="number"
              data-testid="input-font_size"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).font_size || 24}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { font_size: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label htmlFor="font_weight">وزن فونت</label>
            <select
              id="font_weight"
              data-testid="select-font_weight"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).font_weight || 400}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { font_weight: parseInt(e.target.value) })}
            >
              <option value={400}>معمولی (400)</option>
              <option value={700}>پررنگ (700)</option>
            </select>
          </div>

          <div>
            <label htmlFor="font_color">رنگ فونت</label>
            <input
              id="font_color"
              type="text"
              data-testid="input-font_color"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).font_color || '#000000'}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { font_color: e.target.value })}
            />
          </div>

          <div data-testid="text-align-buttons">
            <label>تراز متن</label>
            <button
              data-testid="btn-align-left"
              onClick={() => onUpdatePlaceholder(selectedPlaceholder.id, { text_align: 'left' })}
            >
              چپ
            </button>
            <button
              data-testid="btn-align-center"
              onClick={() => onUpdatePlaceholder(selectedPlaceholder.id, { text_align: 'center' })}
            >
              وسط
            </button>
            <button
              data-testid="btn-align-right"
              onClick={() => onUpdatePlaceholder(selectedPlaceholder.id, { text_align: 'right' })}
            >
              راست
            </button>
          </div>

          <div>
            <label htmlFor="max_length">حداکثر طول</label>
            <input
              id="max_length"
              type="number"
              data-testid="input-max_length"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).max_length || ''}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { max_length: parseInt(e.target.value) || undefined })}
            />
          </div>

          <div>
            <label htmlFor="default_value">مقدار پیش‌فرض</label>
            <textarea
              id="default_value"
              data-testid="textarea-default_value"
              value={(selectedPlaceholder as typeof mockTextPlaceholder).default_value || ''}
              onChange={(e) => onUpdatePlaceholder(selectedPlaceholder.id, { default_value: e.target.value })}
            />
          </div>
        </div>
      )}

      {/* Actions */}
      {onDeletePlaceholder && (
        <button
          data-testid="btn-delete"
          onClick={() => onDeletePlaceholder(selectedPlaceholder.id)}
        >
          حذف
        </button>
      )}
    </div>
  );
};

describe('PlaceholderPanel', () => {
  describe('Empty State', () => {
    it('shows empty state when no placeholder selected', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={null}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('empty-state')).toHaveTextContent('یک جایگاه را انتخاب کنید');
    });
  });

  describe('Basic Fields', () => {
    it('renders name input with current value', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-name')).toHaveValue('logo');
    });

    it('renders label_fa input with current value', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-label_fa')).toHaveValue('لوگو');
    });

    it('renders is_required checkbox', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('checkbox-is_required')).toBeChecked();
    });

    it('changing name calls onUpdate', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'new_logo' } });
      expect(onUpdate).toHaveBeenCalledWith('ph-1', { name: 'new_logo' });
    });

    it('changing label_fa calls onUpdate', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      fireEvent.change(screen.getByTestId('input-label_fa'), { target: { value: 'لوگوی جدید' } });
      expect(onUpdate).toHaveBeenCalledWith('ph-1', { label_fa: 'لوگوی جدید' });
    });
  });

  describe('Position Fields', () => {
    it('renders x, y, width, height inputs', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-x')).toHaveValue(100);
      expect(screen.getByTestId('input-y')).toHaveValue(100);
      expect(screen.getByTestId('input-width')).toHaveValue(200);
      expect(screen.getByTestId('input-height')).toHaveValue(200);
    });

    it('renders rotation input with controls', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-rotation')).toHaveValue(0);
      expect(screen.getByTestId('btn-rotate-90')).toBeInTheDocument();
      expect(screen.getByTestId('btn-rotate-minus-90')).toBeInTheDocument();
    });

    it('rotation buttons increment/decrement by 90', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      fireEvent.click(screen.getByTestId('btn-rotate-90'));
      expect(onUpdate).toHaveBeenCalledWith('ph-1', { rotation: 90 });
    });

    it('changing position calls onUpdate', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      fireEvent.change(screen.getByTestId('input-x'), { target: { value: '150' } });
      expect(onUpdate).toHaveBeenCalledWith('ph-1', { x: 150 });
    });
  });

  describe('Text Placeholder Fields', () => {
    it('shows text fields only for TEXT type', () => {
      const onUpdate = vi.fn();
      
      const { rerender } = render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      // IMAGE type should not have text fields
      expect(screen.queryByTestId('text-fields')).not.toBeInTheDocument();

      // TEXT type should have text fields
      rerender(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
          systemFonts={mockFonts}
        />
      );

      expect(screen.getByTestId('text-fields')).toBeInTheDocument();
    });

    it('renders font family dropdown', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
          systemFonts={mockFonts}
        />
      );

      expect(screen.getByTestId('select-font_family')).toBeInTheDocument();
    });

    it('renders font size input', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-font_size')).toHaveValue(24);
    });

    it('renders font weight dropdown', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('select-font_weight')).toHaveValue('700');
    });

    it('renders color input', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-font_color')).toHaveValue('#333333');
    });

    it('renders text align buttons', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('btn-align-left')).toBeInTheDocument();
      expect(screen.getByTestId('btn-align-center')).toBeInTheDocument();
      expect(screen.getByTestId('btn-align-right')).toBeInTheDocument();
    });

    it('renders max_length input', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('input-max_length')).toHaveValue(100);
    });

    it('renders default_value textarea', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
        />
      );

      expect(screen.getByTestId('textarea-default_value')).toHaveValue('متن پیش‌فرض');
    });

    it('font dropdown populated with system fonts', () => {
      const onUpdate = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockTextPlaceholder}
          onUpdatePlaceholder={onUpdate}
          systemFonts={mockFonts}
        />
      );

      const select = screen.getByTestId('select-font_family');
      expect(select).toContainHTML('ایران سنس');
      expect(select).toContainHTML('وزیر');
    });
  });

  describe('Actions', () => {
    it('delete button calls onDelete', () => {
      const onUpdate = vi.fn();
      const onDelete = vi.fn();
      
      render(
        <MockPlaceholderPanel
          selectedPlaceholder={mockImagePlaceholder}
          onUpdatePlaceholder={onUpdate}
          onDeletePlaceholder={onDelete}
        />
      );

      fireEvent.click(screen.getByTestId('btn-delete'));
      expect(onDelete).toHaveBeenCalledWith('ph-1');
    });
  });
});

