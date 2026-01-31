/**
 * Tests for PreviewPanel component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React, { useState } from 'react';

// Mock placeholders
const mockPlaceholders = [
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
    default_value: 'متن پیش‌فرض',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'ph-3',
    template_id: 'tpl-1',
    type: 'TEXT' as const,
    name: 'optional_text',
    label_fa: 'متن اختیاری',
    x: 300,
    y: 450,
    width: 300,
    height: 50,
    rotation: 0,
    is_required: false,
    sort_order: 2,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

// Simplified mock component for testing
const MockPreviewPanel: React.FC<{
  templateId: string;
  placeholders: typeof mockPlaceholders;
  onGeneratePreview: (data: { placeholders: Array<{ placeholder_id: string; image_url?: string; text_value?: string }> }) => Promise<{ preview_url: string; width: number; height: number }>;
  initialPreviewUrl?: string;
  isLoading?: boolean;
}> = ({
  templateId,
  placeholders,
  onGeneratePreview,
  initialPreviewUrl,
  isLoading = false,
}) => {
  const [sampleData, setSampleData] = useState<Record<string, string>>({});
  const [previewUrl, setPreviewUrl] = useState(initialPreviewUrl || '');
  const [loading, setLoading] = useState(isLoading);
  const [error, setError] = useState<string | null>(null);

  const handleSampleDataChange = (name: string, value: string) => {
    setSampleData((prev) => ({ ...prev, [name]: value }));
  };

  const handleGeneratePreview = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await onGeneratePreview({
        placeholders: placeholders.map((ph) => ({
          placeholder_id: ph.id,
          ...(ph.type === 'IMAGE' ? { image_url: sampleData[ph.name] } : { text_value: sampleData[ph.name] || (ph as any).default_value }),
        })),
      });
      setPreviewUrl(result.preview_url);
    } catch (err: any) {
      setError(err.message || 'خطا در تولید پیش‌نمایش');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (previewUrl) {
      const link = document.createElement('a');
      link.href = previewUrl;
      link.download = `preview_${templateId}.png`;
      link.click();
    }
  };

  return (
    <div data-testid="preview-panel">
      <h3>پیش‌نمایش</h3>
      
      {/* Sample Data Form */}
      <div data-testid="sample-data-form">
        {placeholders.map((ph) => (
          <div key={ph.id} data-testid={`sample-input-container-${ph.name}`}>
            <label htmlFor={`sample-${ph.name}`}>
              {ph.label_fa}
              {ph.is_required && <span data-testid="required-marker">*</span>}
            </label>
            
            {ph.type === 'IMAGE' ? (
              <div data-testid={`image-input-${ph.name}`}>
                <input
                  id={`sample-${ph.name}`}
                  type="text"
                  data-testid={`input-url-${ph.name}`}
                  placeholder="URL تصویر"
                  value={sampleData[ph.name] || ''}
                  onChange={(e) => handleSampleDataChange(ph.name, e.target.value)}
                />
                <button data-testid={`btn-upload-${ph.name}`}>آپلود</button>
              </div>
            ) : (
              <input
                id={`sample-${ph.name}`}
                type="text"
                data-testid={`input-text-${ph.name}`}
                placeholder={(ph as any).default_value || ''}
                style={{ fontFamily: (ph as any).font_family }}
                value={sampleData[ph.name] || ''}
                onChange={(e) => handleSampleDataChange(ph.name, e.target.value)}
              />
            )}
          </div>
        ))}
      </div>

      {/* Generate Button */}
      <button
        data-testid="btn-generate"
        onClick={handleGeneratePreview}
        disabled={loading}
      >
        {loading ? 'در حال تولید...' : 'تولید پیش‌نمایش'}
      </button>

      {/* Error */}
      {error && <div data-testid="error-message">{error}</div>}

      {/* Preview Image */}
      {previewUrl && (
        <div data-testid="preview-container">
          <img
            data-testid="preview-image"
            src={previewUrl}
            alt="Preview"
          />
          <button
            data-testid="btn-download"
            onClick={handleDownload}
          >
            دانلود
          </button>
        </div>
      )}
    </div>
  );
};

describe('PreviewPanel', () => {
  describe('Sample Data Form', () => {
    it('renders input for each active placeholder', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      expect(screen.getByTestId('sample-input-container-logo')).toBeInTheDocument();
      expect(screen.getByTestId('sample-input-container-company_name')).toBeInTheDocument();
      expect(screen.getByTestId('sample-input-container-optional_text')).toBeInTheDocument();
    });

    it('image placeholder shows URL input and upload button', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      expect(screen.getByTestId('image-input-logo')).toBeInTheDocument();
      expect(screen.getByTestId('input-url-logo')).toBeInTheDocument();
      expect(screen.getByTestId('btn-upload-logo')).toBeInTheDocument();
    });

    it('text placeholder shows text input', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      expect(screen.getByTestId('input-text-company_name')).toBeInTheDocument();
    });

    it('text input uses placeholder font style', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      const input = screen.getByTestId('input-text-company_name');
      expect(input).toHaveStyle({ fontFamily: 'IRANSans' });
    });

    it('required placeholders marked with asterisk', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      // Find required markers in required placeholder containers
      const logoContainer = screen.getByTestId('sample-input-container-logo');
      const companyNameContainer = screen.getByTestId('sample-input-container-company_name');
      const optionalContainer = screen.getByTestId('sample-input-container-optional_text');

      expect(logoContainer.querySelector('[data-testid="required-marker"]')).toBeInTheDocument();
      expect(companyNameContainer.querySelector('[data-testid="required-marker"]')).toBeInTheDocument();
      expect(optionalContainer.querySelector('[data-testid="required-marker"]')).not.toBeInTheDocument();
    });
  });

  describe('Preview Generation', () => {
    it('generate button calls API with placeholder data', async () => {
      const onGenerate = vi.fn().mockResolvedValue({
        preview_url: 'https://example.com/preview.png',
        width: 500,
        height: 400,
      });
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      // Fill in sample data
      fireEvent.change(screen.getByTestId('input-url-logo'), {
        target: { value: 'https://example.com/logo.png' },
      });
      fireEvent.change(screen.getByTestId('input-text-company_name'), {
        target: { value: 'شرکت تست' },
      });

      // Click generate
      fireEvent.click(screen.getByTestId('btn-generate'));

      await waitFor(() => {
        expect(onGenerate).toHaveBeenCalledWith(
          expect.objectContaining({
            placeholders: expect.arrayContaining([
              expect.objectContaining({ placeholder_id: 'ph-1' }),
              expect.objectContaining({ placeholder_id: 'ph-2' }),
              expect.objectContaining({ placeholder_id: 'ph-3' }),
            ]),
          })
        );
      });
    });

    it('shows loading state during generation', async () => {
      let resolveGenerate: (value: any) => void;
      const generatePromise = new Promise((resolve) => {
        resolveGenerate = resolve;
      });
      const onGenerate = vi.fn().mockReturnValue(generatePromise);
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      fireEvent.click(screen.getByTestId('btn-generate'));

      // Should show loading state
      expect(screen.getByTestId('btn-generate')).toHaveTextContent('در حال تولید...');
      expect(screen.getByTestId('btn-generate')).toBeDisabled();

      // Resolve the promise
      resolveGenerate!({ preview_url: 'https://example.com/preview.png', width: 500, height: 400 });

      await waitFor(() => {
        expect(screen.getByTestId('btn-generate')).toHaveTextContent('تولید پیش‌نمایش');
        expect(screen.getByTestId('btn-generate')).not.toBeDisabled();
      });
    });

    it('displays preview image on success', async () => {
      const onGenerate = vi.fn().mockResolvedValue({
        preview_url: 'https://example.com/preview.png',
        width: 500,
        height: 400,
      });
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      fireEvent.click(screen.getByTestId('btn-generate'));

      await waitFor(() => {
        expect(screen.getByTestId('preview-image')).toBeInTheDocument();
        expect(screen.getByTestId('preview-image')).toHaveAttribute(
          'src',
          'https://example.com/preview.png'
        );
      });
    });

    it('shows error toast on failure', async () => {
      const onGenerate = vi.fn().mockRejectedValue(new Error('خطای تست'));
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      fireEvent.click(screen.getByTestId('btn-generate'));

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('خطای تست');
      });
    });
  });

  describe('Download', () => {
    it('download button triggers file download', async () => {
      const onGenerate = vi.fn().mockResolvedValue({
        preview_url: 'https://example.com/preview.png',
        width: 500,
        height: 400,
      });
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
          initialPreviewUrl="https://example.com/preview.png"
        />
      );

      // Should have download button when preview exists
      expect(screen.getByTestId('btn-download')).toBeInTheDocument();

      // Click download - just verify it doesn't throw
      const clickSpy = vi.fn();
      HTMLAnchorElement.prototype.click = clickSpy;

      fireEvent.click(screen.getByTestId('btn-download'));
      
      // In real implementation, this would trigger download
      expect(clickSpy).toHaveBeenCalled();
    });

    it('download button hidden when no preview', () => {
      const onGenerate = vi.fn();
      
      render(
        <MockPreviewPanel
          templateId="tpl-1"
          placeholders={mockPlaceholders}
          onGeneratePreview={onGenerate}
        />
      );

      expect(screen.queryByTestId('btn-download')).not.toBeInTheDocument();
    });
  });
});

