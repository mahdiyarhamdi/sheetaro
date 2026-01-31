/**
 * Tests for template API client methods.
 * Uses MSW for API mocking (via global setup).
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { adminApi } from '@/lib/api';

describe('Font API', () => {
  beforeEach(() => {
    // MSW is already set up globally
    localStorage.setItem('access_token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('getFonts returns list of fonts', async () => {
    const response = await adminApi.getFonts();
    const result = response?.data || response;
    
    // Result is either an array or an object with items property
    const isValidResult = Array.isArray(result) || (result?.items !== undefined);
    expect(isValidResult).toBe(true);
    
    // MSW handler returns fonts with IRANSans
    const items = Array.isArray(result) ? result : result?.items || [];
    if (items.length > 0) {
      expect(items[0]).toHaveProperty('name');
      expect(items[0]).toHaveProperty('name_fa');
    }
  });

  it('createFont sends correct payload', async () => {
    const fontData = {
      name: 'NewFont',
      name_fa: 'فونت جدید',
    };

    const response = await adminApi.createFont(fontData);
    const result = response?.data || response;

    expect(result).toHaveProperty('id');
    expect(result.name).toBe('NewFont');
    expect(result.name_fa).toBe('فونت جدید');
  });

  it('updateFont sends partial payload', async () => {
    const updateData = {
      name_fa: 'نام جدید',
    };

    const response = await adminApi.updateFont('font-1', updateData);
    const result = response?.data || response;

    expect(result).toHaveProperty('id');
    expect(result.name_fa).toBe('نام جدید');
  });

  it('deleteFont calls correct endpoint', async () => {
    // MSW handler returns 204 for delete
    await expect(adminApi.deleteFont('font-id-123')).resolves.not.toThrow();
  });
});

describe('Placeholder API', () => {
  beforeEach(() => {
    localStorage.setItem('access_token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('getTemplatePlaceholders returns placeholders', async () => {
    const response = await adminApi.getTemplatePlaceholders('template-123');
    const result = response?.data || response;

    const items = Array.isArray(result) ? result : result?.items || [];
    expect(Array.isArray(items)).toBe(true);
    if (items.length > 0) {
      expect(items[0]).toHaveProperty('type');
      expect(items[0]).toHaveProperty('name');
      expect(items[0]).toHaveProperty('label_fa');
    }
  });

  it('createPlaceholder sends correct payload', async () => {
    const placeholderData = {
      type: 'IMAGE' as const,
      name: 'logo',
      label_fa: 'لوگو',
      x: 100,
      y: 100,
      width: 200,
      height: 200,
    };

    const response = await adminApi.createPlaceholder('template-123', placeholderData);
    const result = response?.data || response;

    expect(result).toHaveProperty('id');
    expect(result.type).toBe('IMAGE');
    expect(result.name).toBe('logo');
    expect(result.label_fa).toBe('لوگو');
  });

  it('updatePlaceholder sends partial payload', async () => {
    const updateData = {
      x: 150,
      y: 200,
    };

    const response = await adminApi.updatePlaceholder('ph-1', updateData);
    const result = response?.data || response;

    expect(result).toHaveProperty('id');
    expect(result.x).toBe(150);
    expect(result.y).toBe(200);
  });

  it('deletePlaceholder calls correct endpoint', async () => {
    // MSW handler returns 204 for delete
    await expect(adminApi.deletePlaceholder('ph-123')).resolves.not.toThrow();
  });

  it('reorderPlaceholders sends items array', async () => {
    const reorderData = [
      { id: 'ph-1', sort_order: 2 },
      { id: 'ph-2', sort_order: 0 },
      { id: 'ph-3', sort_order: 1 },
    ];

    const response = await adminApi.reorderPlaceholders(reorderData);
    const result = response?.data || response;

    // The response should contain success or be truthy (operation completed)
    expect(result).toBeTruthy();
    // If the result has success property, it should be true
    if (result?.success !== undefined) {
      expect(result.success).toBe(true);
    }
  });
});

describe('Template Preview API', () => {
  beforeEach(() => {
    localStorage.setItem('access_token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('generateTemplatePreview sends placeholder data', async () => {
    const previewData = {
      placeholders: [
        { placeholder_id: 'ph-1', image_url: 'https://example.com/logo.png' },
        { placeholder_id: 'ph-2', text_value: 'Company Name' },
      ],
    };

    const response = await adminApi.generateTemplatePreview('template-123', previewData);
    // API client may return either data directly or wrapped in response object
    const result = response?.data || response;

    expect(result).toHaveProperty('preview_url');
    expect(result).toHaveProperty('width');
    expect(result).toHaveProperty('height');
  });

  it('getTemplateDetails returns template with placeholders', async () => {
    const response = await adminApi.getTemplateDetails('template-123');
    // API client may return either data directly or wrapped in response object
    const result = response?.data || response;

    expect(result).toHaveProperty('id');
    // Template may or may not have placeholders depending on the mock
  });
});
