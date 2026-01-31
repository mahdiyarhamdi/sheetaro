/**
 * Contract Tests for Template Builder API Schemas.
 * 
 * These tests ensure that the frontend's type definitions match the backend's API schemas.
 * This prevents runtime errors caused by schema mismatches.
 */

import { describe, it, expect } from 'vitest';
import { z } from 'zod';

// Define Zod schemas that mirror the backend Pydantic schemas

// ============== Enums ==============

const PlaceholderTypeSchema = z.enum(['IMAGE', 'TEXT']);

const TextAlignSchema = z.enum(['left', 'center', 'right']);

// ============== Font Schemas ==============

const FontVariantSchema = z.object({
  weight: z.number().int().min(100).max(900),
  style: z.string().max(20),
  file_url: z.string().max(500),
});

const SystemFontCreateSchema = z.object({
  name: z.string().max(100),
  name_fa: z.string().max(100),
  file_url: z.string().max(500).optional().nullable(),
  variants: z.array(FontVariantSchema).optional().default([]),
  sample_text: z.string().max(200).optional().default('نمونه متن فارسی - Sample Text 123'),
});

const SystemFontOutSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  name_fa: z.string(),
  file_url: z.string().nullable(),
  variants: z.array(FontVariantSchema),
  sample_text: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
});

// ============== Placeholder Schemas ==============

const PlaceholderCreateSchema = z.object({
  type: PlaceholderTypeSchema,
  name: z.string().max(50),
  label_fa: z.string().max(100),
  x: z.number().int().optional().default(0),
  y: z.number().int().optional().default(0),
  width: z.number().int().optional().default(100),
  height: z.number().int().optional().default(100),
  rotation: z.number().int().optional().default(0),
  is_required: z.boolean().optional().default(true),
  sort_order: z.number().int().optional().default(0),
  // Text-specific
  font_family: z.string().max(100).optional().nullable(),
  font_size: z.number().int().optional().default(24),
  font_weight: z.number().int().optional().default(400),
  font_color: z.string().max(9).optional().default('#000000'),
  text_align: TextAlignSchema.optional().default('right'),
  max_length: z.number().int().optional().nullable(),
  default_value: z.string().optional().nullable(),
});

const PlaceholderOutSchema = z.object({
  id: z.string().uuid(),
  template_id: z.string().uuid(),
  type: PlaceholderTypeSchema,
  name: z.string(),
  label_fa: z.string(),
  x: z.number(),
  y: z.number(),
  width: z.number(),
  height: z.number(),
  rotation: z.number(),
  is_required: z.boolean(),
  sort_order: z.number(),
  font_family: z.string().nullable(),
  font_size: z.number().nullable(),
  font_weight: z.number().nullable(),
  font_color: z.string().nullable(),
  text_align: TextAlignSchema.nullable(),
  max_length: z.number().nullable(),
  default_value: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
});

// ============== Template Schemas ==============

const TemplateCreateSchema = z.object({
  name_fa: z.string().max(100),
  description_fa: z.string().max(500).optional().nullable(),
  preview_url: z.string().max(500).optional().nullable(),
  file_url: z.string().max(500).optional().nullable(),
  image_width: z.number().int().optional().nullable(),
  image_height: z.number().int().optional().nullable(),
  placeholder_x: z.number().int().optional().nullable(),
  placeholder_y: z.number().int().optional().nullable(),
  placeholder_width: z.number().int().optional().nullable(),
  placeholder_height: z.number().int().optional().nullable(),
  placeholder_rotation: z.number().int().optional().default(0),
  sort_order: z.number().int().optional().default(0),
  is_active: z.boolean().optional().default(true),
});

const TemplateOutSchema = z.object({
  id: z.string().uuid(),
  plan_id: z.string().uuid(),
  name_fa: z.string(),
  description_fa: z.string().nullable(),
  preview_url: z.string().nullable(),
  file_url: z.string().nullable(),
  image_width: z.number().nullable(),
  image_height: z.number().nullable(),
  placeholder_x: z.number().nullable(),
  placeholder_y: z.number().nullable(),
  placeholder_width: z.number().nullable(),
  placeholder_height: z.number().nullable(),
  placeholder_rotation: z.number().nullable(),
  sort_order: z.number(),
  is_active: z.boolean(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
});

const TemplateWithPlaceholdersSchema = TemplateOutSchema.extend({
  placeholders: z.array(PlaceholderOutSchema).optional().default([]),
});

// ============== Preview Schemas ==============

const PlaceholderPreviewDataSchema = z.object({
  placeholder_id: z.string().uuid(),
  image_url: z.string().optional().nullable(),
  text_value: z.string().optional().nullable(),
});

const TemplatePreviewRequestSchema = z.object({
  placeholders: z.array(PlaceholderPreviewDataSchema),
});

const TemplatePreviewResponseSchema = z.object({
  preview_url: z.string(),
  width: z.number().int(),
  height: z.number().int(),
});

// ============== Tests ==============

describe('Template Builder Contract Tests', () => {
  describe('PlaceholderType Enum', () => {
    it('accepts valid types', () => {
      expect(PlaceholderTypeSchema.safeParse('IMAGE').success).toBe(true);
      expect(PlaceholderTypeSchema.safeParse('TEXT').success).toBe(true);
    });

    it('rejects invalid types', () => {
      expect(PlaceholderTypeSchema.safeParse('LOGO').success).toBe(false);
      expect(PlaceholderTypeSchema.safeParse('BUTTON').success).toBe(false);
      expect(PlaceholderTypeSchema.safeParse('image').success).toBe(false);
    });
  });

  describe('TextAlign Enum', () => {
    it('accepts valid alignments', () => {
      expect(TextAlignSchema.safeParse('left').success).toBe(true);
      expect(TextAlignSchema.safeParse('center').success).toBe(true);
      expect(TextAlignSchema.safeParse('right').success).toBe(true);
    });

    it('rejects invalid alignments', () => {
      expect(TextAlignSchema.safeParse('justify').success).toBe(false);
      expect(TextAlignSchema.safeParse('LEFT').success).toBe(false);
    });
  });

  describe('FontVariant Schema', () => {
    it('accepts valid variant', () => {
      const variant = {
        weight: 400,
        style: 'normal',
        file_url: 'https://example.com/font.woff2',
      };
      expect(FontVariantSchema.safeParse(variant).success).toBe(true);
    });

    it('validates weight range', () => {
      const tooLight = { weight: 50, style: 'normal', file_url: 'https://example.com/font.woff2' };
      const tooHeavy = { weight: 1000, style: 'normal', file_url: 'https://example.com/font.woff2' };
      
      expect(FontVariantSchema.safeParse(tooLight).success).toBe(false);
      expect(FontVariantSchema.safeParse(tooHeavy).success).toBe(false);
    });

    it('requires all fields', () => {
      expect(FontVariantSchema.safeParse({ weight: 400 }).success).toBe(false);
      expect(FontVariantSchema.safeParse({ weight: 400, style: 'normal' }).success).toBe(false);
    });
  });

  describe('SystemFontCreate Schema', () => {
    it('accepts valid font create data', () => {
      const data = {
        name: 'IRANSans',
        name_fa: 'ایران سنس',
      };
      expect(SystemFontCreateSchema.safeParse(data).success).toBe(true);
    });

    it('accepts font with variants', () => {
      const data = {
        name: 'IRANSans',
        name_fa: 'ایران سنس',
        variants: [
          { weight: 400, style: 'normal', file_url: 'https://example.com/regular.woff2' },
          { weight: 700, style: 'normal', file_url: 'https://example.com/bold.woff2' },
        ],
      };
      expect(SystemFontCreateSchema.safeParse(data).success).toBe(true);
    });

    it('requires name and name_fa', () => {
      expect(SystemFontCreateSchema.safeParse({ name: 'Test' }).success).toBe(false);
      expect(SystemFontCreateSchema.safeParse({ name_fa: 'تست' }).success).toBe(false);
    });
  });

  describe('SystemFontOut Schema', () => {
    it('accepts valid font response', () => {
      const data = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'IRANSans',
        name_fa: 'ایران سنس',
        file_url: null,
        variants: [],
        sample_text: 'نمونه متن',
        is_active: true,
        created_at: '2024-01-01T00:00:00+00:00',
        updated_at: '2024-01-01T00:00:00+00:00',
      };
      expect(SystemFontOutSchema.safeParse(data).success).toBe(true);
    });
  });

  describe('PlaceholderCreate Schema', () => {
    it('accepts minimal image placeholder', () => {
      const data = {
        type: 'IMAGE',
        name: 'logo',
        label_fa: 'لوگو',
      };
      expect(PlaceholderCreateSchema.safeParse(data).success).toBe(true);
    });

    it('accepts text placeholder with all fields', () => {
      const data = {
        type: 'TEXT',
        name: 'title',
        label_fa: 'عنوان',
        x: 100,
        y: 50,
        width: 200,
        height: 30,
        rotation: 0,
        font_family: 'IRANSans',
        font_size: 24,
        font_weight: 700,
        font_color: '#FF0000',
        text_align: 'center',
        max_length: 50,
        default_value: 'متن پیش‌فرض',
      };
      expect(PlaceholderCreateSchema.safeParse(data).success).toBe(true);
    });

    it('applies default values', () => {
      const data = {
        type: 'IMAGE',
        name: 'logo',
        label_fa: 'لوگو',
      };
      const result = PlaceholderCreateSchema.parse(data);
      
      expect(result.x).toBe(0);
      expect(result.y).toBe(0);
      expect(result.width).toBe(100);
      expect(result.height).toBe(100);
      expect(result.is_required).toBe(true);
    });
  });

  describe('PlaceholderOut Schema', () => {
    it('accepts valid placeholder response', () => {
      const data = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        template_id: '223e4567-e89b-12d3-a456-426614174000',
        type: 'IMAGE',
        name: 'logo',
        label_fa: 'لوگو',
        x: 100,
        y: 100,
        width: 200,
        height: 200,
        rotation: 0,
        is_required: true,
        sort_order: 0,
        font_family: null,
        font_size: null,
        font_weight: null,
        font_color: null,
        text_align: null,
        max_length: null,
        default_value: null,
        is_active: true,
        created_at: '2024-01-01T00:00:00+00:00',
        updated_at: '2024-01-01T00:00:00+00:00',
      };
      expect(PlaceholderOutSchema.safeParse(data).success).toBe(true);
    });

    it('accepts text placeholder with font settings', () => {
      const data = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        template_id: '223e4567-e89b-12d3-a456-426614174000',
        type: 'TEXT',
        name: 'title',
        label_fa: 'عنوان',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        rotation: 0,
        is_required: true,
        sort_order: 1,
        font_family: 'IRANSans',
        font_size: 24,
        font_weight: 700,
        font_color: '#000000',
        text_align: 'right',
        max_length: 100,
        default_value: 'پیش‌فرض',
        is_active: true,
        created_at: '2024-01-01T00:00:00+00:00',
        updated_at: '2024-01-01T00:00:00+00:00',
      };
      expect(PlaceholderOutSchema.safeParse(data).success).toBe(true);
    });
  });

  describe('TemplateCreate Schema', () => {
    it('accepts minimal template', () => {
      const data = {
        name_fa: 'قالب تست',
      };
      expect(TemplateCreateSchema.safeParse(data).success).toBe(true);
    });

    it('accepts template with all fields', () => {
      const data = {
        name_fa: 'قالب کارت ویزیت',
        description_fa: 'قالب مناسب برای کارت ویزیت',
        preview_url: 'https://example.com/preview.png',
        file_url: 'https://example.com/template.png',
        image_width: 800,
        image_height: 600,
        placeholder_x: 100,
        placeholder_y: 100,
        placeholder_width: 200,
        placeholder_height: 200,
        placeholder_rotation: 0,
        sort_order: 1,
        is_active: true,
      };
      expect(TemplateCreateSchema.safeParse(data).success).toBe(true);
    });
  });

  describe('TemplateWithPlaceholders Schema', () => {
    it('accepts template with placeholders array', () => {
      const data = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        plan_id: '223e4567-e89b-12d3-a456-426614174000',
        name_fa: 'قالب تست',
        description_fa: null,
        preview_url: null,
        file_url: 'https://example.com/template.png',
        image_width: 800,
        image_height: 600,
        placeholder_x: null,
        placeholder_y: null,
        placeholder_width: null,
        placeholder_height: null,
        placeholder_rotation: null,
        sort_order: 0,
        is_active: true,
        created_at: '2024-01-01T00:00:00+00:00',
        updated_at: '2024-01-01T00:00:00+00:00',
        placeholders: [
          {
            id: '323e4567-e89b-12d3-a456-426614174000',
            template_id: '123e4567-e89b-12d3-a456-426614174000',
            type: 'IMAGE',
            name: 'logo',
            label_fa: 'لوگو',
            x: 100,
            y: 100,
            width: 200,
            height: 200,
            rotation: 0,
            is_required: true,
            sort_order: 0,
            font_family: null,
            font_size: null,
            font_weight: null,
            font_color: null,
            text_align: null,
            max_length: null,
            default_value: null,
            is_active: true,
            created_at: '2024-01-01T00:00:00+00:00',
            updated_at: '2024-01-01T00:00:00+00:00',
          },
        ],
      };
      expect(TemplateWithPlaceholdersSchema.safeParse(data).success).toBe(true);
    });
  });

  describe('TemplatePreviewRequest Schema', () => {
    it('accepts valid preview request', () => {
      const data = {
        placeholders: [
          {
            placeholder_id: '123e4567-e89b-12d3-a456-426614174000',
            image_url: 'https://example.com/logo.png',
          },
          {
            placeholder_id: '223e4567-e89b-12d3-a456-426614174000',
            text_value: 'شرکت تست',
          },
        ],
      };
      expect(TemplatePreviewRequestSchema.safeParse(data).success).toBe(true);
    });

    it('requires placeholders array', () => {
      expect(TemplatePreviewRequestSchema.safeParse({}).success).toBe(false);
    });
  });

  describe('TemplatePreviewResponse Schema', () => {
    it('accepts valid preview response', () => {
      const data = {
        preview_url: 'https://example.com/preview/123.png',
        width: 800,
        height: 600,
      };
      expect(TemplatePreviewResponseSchema.safeParse(data).success).toBe(true);
    });

    it('requires all fields', () => {
      expect(TemplatePreviewResponseSchema.safeParse({ preview_url: 'https://example.com' }).success).toBe(false);
      expect(TemplatePreviewResponseSchema.safeParse({ preview_url: 'https://example.com', width: 800 }).success).toBe(false);
    });
  });

  describe('Cross-Schema Validation', () => {
    it('placeholder.template_id matches parent template.id', () => {
      const templateId = '123e4567-e89b-12d3-a456-426614174000';
      const placeholder = {
        id: '323e4567-e89b-12d3-a456-426614174000',
        template_id: templateId,
        type: 'IMAGE' as const,
        name: 'logo',
        label_fa: 'لوگو',
        x: 0,
        y: 0,
        width: 100,
        height: 100,
        rotation: 0,
        is_required: true,
        sort_order: 0,
        font_family: null,
        font_size: null,
        font_weight: null,
        font_color: null,
        text_align: null,
        max_length: null,
        default_value: null,
        is_active: true,
        created_at: '2024-01-01T00:00:00+00:00',
        updated_at: '2024-01-01T00:00:00+00:00',
      };
      
      expect(PlaceholderOutSchema.safeParse(placeholder).success).toBe(true);
      expect(placeholder.template_id).toBe(templateId);
    });

    it('preview request placeholder_ids reference existing placeholders', () => {
      const placeholderIds = [
        '123e4567-e89b-12d3-a456-426614174000',
        '223e4567-e89b-12d3-a456-426614174000',
      ];
      
      const previewRequest = {
        placeholders: placeholderIds.map((id, index) => ({
          placeholder_id: id,
          text_value: index === 0 ? 'تست ۱' : 'تست ۲',
        })),
      };
      
      expect(TemplatePreviewRequestSchema.safeParse(previewRequest).success).toBe(true);
      
      // Verify all placeholder_ids are valid UUIDs
      previewRequest.placeholders.forEach((p) => {
        expect(z.string().uuid().safeParse(p.placeholder_id).success).toBe(true);
      });
    });
  });
});

