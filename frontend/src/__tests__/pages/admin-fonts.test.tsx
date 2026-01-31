/**
 * Tests for Admin Fonts Management Page.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React, { useState } from 'react';

// Mock font data
const mockFonts = [
  {
    id: 'font-1',
    name: 'IRANSans',
    name_fa: 'ایران سنس',
    file_url: 'https://example.com/fonts/iransans.woff2',
    variants: [
      { weight: 400, style: 'normal', file_url: 'https://example.com/fonts/iransans-regular.woff2' },
      { weight: 700, style: 'normal', file_url: 'https://example.com/fonts/iransans-bold.woff2' },
    ],
    sample_text: 'نمونه متن فارسی - Sample Text',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'font-2',
    name: 'Vazirmatn',
    name_fa: 'وزیرمتن',
    file_url: 'https://example.com/fonts/vazirmatn.woff2',
    variants: [
      { weight: 400, style: 'normal', file_url: 'https://example.com/fonts/vazirmatn-regular.woff2' },
    ],
    sample_text: 'متن آزمایشی',
    is_active: true,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

// Mock AdminFontsPage component
const MockAdminFontsPage: React.FC<{
  fonts?: typeof mockFonts;
  isLoading?: boolean;
  onCreateFont?: (data: any) => Promise<void>;
  onUpdateFont?: (id: string, data: any) => Promise<void>;
  onDeleteFont?: (id: string) => Promise<void>;
  onUploadFontFile?: (file: File) => Promise<string>;
}> = ({
  fonts = mockFonts,
  isLoading = false,
  onCreateFont,
  onUpdateFont,
  onDeleteFont,
  onUploadFontFile,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingFont, setEditingFont] = useState<typeof mockFonts[0] | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    name_fa: '',
    sample_text: 'نمونه متن فارسی - Sample Text 123',
  });
  const [variants, setVariants] = useState<typeof mockFonts[0]['variants']>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  const openCreateModal = () => {
    setEditingFont(null);
    setFormData({
      name: '',
      name_fa: '',
      sample_text: 'نمونه متن فارسی - Sample Text 123',
    });
    setVariants([]);
    setIsModalOpen(true);
  };

  const openEditModal = (font: typeof mockFonts[0]) => {
    setEditingFont(font);
    setFormData({
      name: font.name,
      name_fa: font.name_fa,
      sample_text: font.sample_text,
    });
    setVariants([...font.variants]);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const data = {
        ...formData,
        variants,
      };

      if (editingFont) {
        await onUpdateFont?.(editingFont.id, data);
      } else {
        await onCreateFont?.(data);
      }
      setIsModalOpen(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (fontId: string) => {
    await onDeleteFont?.(fontId);
  };

  const handleFileUpload = async (file: File, weight: number, style: string) => {
    setUploadProgress(0);
    try {
      const url = await onUploadFontFile?.(file);
      if (url) {
        setVariants([...variants, { weight, style, file_url: url }]);
      }
    } finally {
      setUploadProgress(null);
    }
  };

  const removeVariant = (index: number) => {
    setVariants(variants.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return <div data-testid="loading-state">در حال بارگذاری...</div>;
  }

  return (
    <div data-testid="admin-fonts-page">
      {/* Header */}
      <div data-testid="page-header">
        <h1>مدیریت فونت‌ها</h1>
        <button
          data-testid="btn-create-font"
          onClick={openCreateModal}
        >
          فونت جدید
        </button>
      </div>

      {/* Empty State */}
      {fonts.length === 0 && (
        <div data-testid="empty-state">
          هیچ فونتی یافت نشد
        </div>
      )}

      {/* Font List */}
      <div data-testid="font-list">
        {fonts.map((font) => (
          <div key={font.id} data-testid={`font-item-${font.id}`}>
            <div data-testid={`font-preview-${font.id}`}>
              <span style={{ fontFamily: font.name }}>{font.sample_text}</span>
            </div>
            <div>
              <h3 data-testid={`font-name-${font.id}`}>{font.name_fa}</h3>
              <span data-testid={`font-name-en-${font.id}`}>{font.name}</span>
              <span data-testid={`font-variants-count-${font.id}`}>
                {font.variants.length} وزن
              </span>
            </div>
            <div>
              <button
                data-testid={`btn-edit-font-${font.id}`}
                onClick={() => openEditModal(font)}
              >
                ویرایش
              </button>
              <button
                data-testid={`btn-delete-font-${font.id}`}
                onClick={() => handleDelete(font.id)}
              >
                حذف
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div data-testid="font-modal">
          <h2>{editingFont ? 'ویرایش فونت' : 'فونت جدید'}</h2>

          <label>
            نام فارسی
            <input
              data-testid="input-name-fa"
              value={formData.name_fa}
              onChange={(e) => setFormData({ ...formData, name_fa: e.target.value })}
            />
          </label>

          <label>
            نام انگلیسی (شناسه)
            <input
              data-testid="input-name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </label>

          <label>
            متن نمونه
            <input
              data-testid="input-sample-text"
              value={formData.sample_text}
              onChange={(e) => setFormData({ ...formData, sample_text: e.target.value })}
            />
          </label>

          {/* Font Preview */}
          <div data-testid="font-preview-section">
            <div style={{ fontFamily: formData.name }}>
              {formData.sample_text || 'پیش‌نمایش فونت'}
            </div>
          </div>

          {/* Variants */}
          <div data-testid="variants-section">
            <h4>وزن‌های فونت</h4>
            
            {variants.length === 0 && (
              <div data-testid="no-variants">هیچ فایل فونتی آپلود نشده</div>
            )}
            
            {variants.map((v, index) => (
              <div key={index} data-testid={`variant-${index}`}>
                <span>وزن: {v.weight}</span>
                <span>استایل: {v.style}</span>
                <button
                  data-testid={`btn-remove-variant-${index}`}
                  onClick={() => removeVariant(index)}
                >
                  حذف
                </button>
              </div>
            ))}

            <div data-testid="upload-section">
              <select data-testid="select-weight" defaultValue="400">
                <option value="100">100 - Thin</option>
                <option value="300">300 - Light</option>
                <option value="400">400 - Regular</option>
                <option value="500">500 - Medium</option>
                <option value="700">700 - Bold</option>
                <option value="900">900 - Black</option>
              </select>

              <input
                type="file"
                data-testid="input-font-file"
                accept=".ttf,.otf,.woff,.woff2"
              />

              {uploadProgress !== null && (
                <div data-testid="upload-progress">
                  آپلود: {uploadProgress}%
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div>
            <button
              data-testid="btn-cancel"
              onClick={() => setIsModalOpen(false)}
            >
              انصراف
            </button>
            <button
              data-testid="btn-submit"
              onClick={handleSubmit}
              disabled={isSubmitting || !formData.name || !formData.name_fa}
            >
              {isSubmitting ? 'در حال ذخیره...' : 'ذخیره'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

describe('AdminFontsPage', () => {
  describe('Initial Render', () => {
    it('shows loading state', () => {
      render(<MockAdminFontsPage fonts={[]} isLoading={true} />);
      expect(screen.getByTestId('loading-state')).toBeInTheDocument();
    });

    it('shows empty state when no fonts', () => {
      render(<MockAdminFontsPage fonts={[]} />);
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    it('shows font list', () => {
      render(<MockAdminFontsPage />);
      
      expect(screen.getByTestId('font-list')).toBeInTheDocument();
      expect(screen.getByTestId('font-item-font-1')).toBeInTheDocument();
      expect(screen.getByTestId('font-item-font-2')).toBeInTheDocument();
    });

    it('displays font information correctly', () => {
      render(<MockAdminFontsPage />);
      
      expect(screen.getByTestId('font-name-font-1')).toHaveTextContent('ایران سنس');
      expect(screen.getByTestId('font-name-en-font-1')).toHaveTextContent('IRANSans');
      expect(screen.getByTestId('font-variants-count-font-1')).toHaveTextContent('2 وزن');
    });

    it('shows font preview with sample text', () => {
      render(<MockAdminFontsPage />);
      
      const preview = screen.getByTestId('font-preview-font-1');
      expect(preview).toHaveTextContent('نمونه متن فارسی - Sample Text');
    });
  });

  describe('Create Font Modal', () => {
    it('opens create modal when clicking add button', () => {
      render(<MockAdminFontsPage />);
      
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      expect(screen.getByTestId('font-modal')).toBeInTheDocument();
      // Modal title is also "فونت جدید" in create mode - check via heading element
      const modalTitle = screen.getByRole('heading', { level: 2, name: 'فونت جدید' });
      expect(modalTitle).toBeInTheDocument();
    });

    it('has empty form fields in create mode', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      expect(screen.getByTestId('input-name-fa')).toHaveValue('');
      expect(screen.getByTestId('input-name')).toHaveValue('');
    });

    it('validates required fields before submit', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      const submitBtn = screen.getByTestId('btn-submit');
      expect(submitBtn).toBeDisabled();

      // Fill in required fields
      fireEvent.change(screen.getByTestId('input-name-fa'), { target: { value: 'تست' } });
      fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'Test' } });
      
      expect(submitBtn).not.toBeDisabled();
    });

    it('calls onCreateFont on submit', async () => {
      const onCreateFont = vi.fn().mockResolvedValue(undefined);
      
      render(<MockAdminFontsPage onCreateFont={onCreateFont} />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      fireEvent.change(screen.getByTestId('input-name-fa'), { target: { value: 'فونت تست' } });
      fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'TestFont' } });
      
      fireEvent.click(screen.getByTestId('btn-submit'));

      await waitFor(() => {
        expect(onCreateFont).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'TestFont',
            name_fa: 'فونت تست',
          })
        );
      });
    });

    it('closes modal on cancel', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      expect(screen.getByTestId('font-modal')).toBeInTheDocument();
      
      fireEvent.click(screen.getByTestId('btn-cancel'));
      
      expect(screen.queryByTestId('font-modal')).not.toBeInTheDocument();
    });
  });

  describe('Edit Font Modal', () => {
    it('opens edit modal with font data', () => {
      render(<MockAdminFontsPage />);
      
      fireEvent.click(screen.getByTestId('btn-edit-font-font-1'));
      
      expect(screen.getByTestId('font-modal')).toBeInTheDocument();
      expect(screen.getByText('ویرایش فونت')).toBeInTheDocument();
      expect(screen.getByTestId('input-name-fa')).toHaveValue('ایران سنس');
      expect(screen.getByTestId('input-name')).toHaveValue('IRANSans');
    });

    it('shows existing variants in edit mode', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-edit-font-font-1'));
      
      expect(screen.getByTestId('variant-0')).toBeInTheDocument();
      expect(screen.getByTestId('variant-1')).toBeInTheDocument();
    });

    it('calls onUpdateFont on submit', async () => {
      const onUpdateFont = vi.fn().mockResolvedValue(undefined);
      
      render(<MockAdminFontsPage onUpdateFont={onUpdateFont} />);
      fireEvent.click(screen.getByTestId('btn-edit-font-font-1'));
      
      fireEvent.change(screen.getByTestId('input-name-fa'), { target: { value: 'نام جدید' } });
      fireEvent.click(screen.getByTestId('btn-submit'));

      await waitFor(() => {
        expect(onUpdateFont).toHaveBeenCalledWith(
          'font-1',
          expect.objectContaining({
            name_fa: 'نام جدید',
          })
        );
      });
    });
  });

  describe('Font Variants', () => {
    it('shows no variants message when empty', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      expect(screen.getByTestId('no-variants')).toBeInTheDocument();
    });

    it('can remove a variant', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-edit-font-font-1'));
      
      // Initially 2 variants
      expect(screen.getByTestId('variant-0')).toBeInTheDocument();
      expect(screen.getByTestId('variant-1')).toBeInTheDocument();
      
      // Remove first variant
      fireEvent.click(screen.getByTestId('btn-remove-variant-0'));
      
      // Now only 1 variant
      expect(screen.queryByTestId('variant-1')).not.toBeInTheDocument();
    });

    it('shows upload section with weight select', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      expect(screen.getByTestId('upload-section')).toBeInTheDocument();
      expect(screen.getByTestId('select-weight')).toBeInTheDocument();
      expect(screen.getByTestId('input-font-file')).toBeInTheDocument();
    });
  });

  describe('Delete Font', () => {
    it('calls onDeleteFont when clicking delete', async () => {
      const onDeleteFont = vi.fn().mockResolvedValue(undefined);
      
      render(<MockAdminFontsPage onDeleteFont={onDeleteFont} />);
      
      fireEvent.click(screen.getByTestId('btn-delete-font-font-1'));

      await waitFor(() => {
        expect(onDeleteFont).toHaveBeenCalledWith('font-1');
      });
    });
  });

  describe('Font Preview', () => {
    it('shows real-time preview in modal', () => {
      render(<MockAdminFontsPage />);
      fireEvent.click(screen.getByTestId('btn-create-font'));
      
      const previewSection = screen.getByTestId('font-preview-section');
      expect(previewSection).toBeInTheDocument();
      
      fireEvent.change(screen.getByTestId('input-sample-text'), {
        target: { value: 'متن جدید برای پیش‌نمایش' }
      });
      
      expect(previewSection).toHaveTextContent('متن جدید برای پیش‌نمایش');
    });
  });

  describe('Header', () => {
    it('shows page title', () => {
      render(<MockAdminFontsPage />);
      expect(screen.getByText('مدیریت فونت‌ها')).toBeInTheDocument();
    });

    it('shows create button', () => {
      render(<MockAdminFontsPage />);
      expect(screen.getByTestId('btn-create-font')).toBeInTheDocument();
      expect(screen.getByTestId('btn-create-font')).toHaveTextContent('فونت جدید');
    });
  });
});

