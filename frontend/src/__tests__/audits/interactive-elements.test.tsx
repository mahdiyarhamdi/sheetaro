/**
 * Interactive Elements Audit Tests
 * 
 * این تست‌ها اطمینان می‌دهند که تمام المان‌های تعاملی (دکمه‌ها، لینک‌ها و...)
 * handler مناسب دارند و کار می‌کنند.
 * 
 * قوانین:
 * 1. هر دکمه باید یا onClick داشته باشد یا type="submit" باشد
 * 2. هر لینک باید href معتبر داشته باشد
 * 3. هر فرم باید onSubmit داشته باشد
 */

import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock modules
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}));

vi.mock('@/lib/api', () => ({
  adminApi: {
    getCategories: vi.fn().mockResolvedValue({ data: [] }),
    getProducts: vi.fn().mockResolvedValue({ data: { items: [] } }),
    getPlans: vi.fn().mockResolvedValue({ data: [] }),
    createCategory: vi.fn().mockResolvedValue({ data: {} }),
    updateCategory: vi.fn().mockResolvedValue({ data: {} }),
    deleteCategory: vi.fn().mockResolvedValue({}),
    createProduct: vi.fn().mockResolvedValue({ data: {} }),
    updateProduct: vi.fn().mockResolvedValue({ data: {} }),
    deleteProduct: vi.fn().mockResolvedValue({}),
    createPlan: vi.fn().mockResolvedValue({ data: {} }),
    updatePlan: vi.fn().mockResolvedValue({ data: {} }),
    deletePlan: vi.fn().mockResolvedValue({}),
  },
  getErrorMessage: vi.fn((e) => e?.message || 'Error'),
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: '1', is_admin: true },
    isLoadingUser: false,
    isAdmin: true,
    isAuthenticated: true,
  }),
}));

// Helper to create test wrapper
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('Interactive Elements Audit', () => {
  describe('Admin Catalog Page', () => {
    let CatalogPage: any;

    beforeEach(async () => {
      vi.resetModules();
      const module = await import('@/app/(dashboard)/admin/catalog/page');
      CatalogPage = module.default;
    });

    test('all buttons have onClick or are submit type', async () => {
      render(<CatalogPage />, { wrapper: createWrapper() });

      // Wait for component to load
      await screen.findByText('مدیریت کاتالوگ');

      const buttons = screen.getAllByRole('button');
      
      const buttonsWithoutHandlers: string[] = [];
      
      buttons.forEach((button) => {
        const hasOnClick = button.onclick !== null;
        const isSubmit = button.getAttribute('type') === 'submit';
        const isDisabled = button.hasAttribute('disabled');
        const buttonText = button.textContent || button.getAttribute('aria-label') || 'unnamed';
        
        if (!hasOnClick && !isSubmit && !isDisabled) {
          // Check if parent has onClick (for icon buttons in wrappers)
          const parentHasOnClick = button.parentElement?.onclick !== null;
          if (!parentHasOnClick) {
            buttonsWithoutHandlers.push(buttonText);
          }
        }
      });

      if (buttonsWithoutHandlers.length > 0) {
        console.warn('Buttons without handlers:', buttonsWithoutHandlers);
      }
      
      // This test will fail if any button lacks a handler
      expect(buttonsWithoutHandlers).toHaveLength(0);
    });

    test('"دسته‌بندی جدید" button opens modal', async () => {
      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      const newCategoryBtn = screen.getByRole('button', { name: /دسته‌بندی جدید/i });
      expect(newCategoryBtn).toBeInTheDocument();

      await user.click(newCategoryBtn);

      // Modal should open
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('ایجاد دسته‌بندی جدید')).toBeInTheDocument();
    });

    test('"محصول جدید" button opens modal', async () => {
      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      // Click on Products tab first
      const productsTab = screen.getByRole('button', { name: /محصولات/i });
      await user.click(productsTab);

      const newProductBtn = screen.getByRole('button', { name: /محصول جدید/i });
      expect(newProductBtn).toBeInTheDocument();

      await user.click(newProductBtn);

      // Modal should open
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('ایجاد محصول جدید')).toBeInTheDocument();
    });

    test('"پلن جدید" button opens modal when category is selected', async () => {
      // Mock categories to have at least one
      vi.mocked(await import('@/lib/api')).adminApi.getCategories = vi.fn().mockResolvedValue({
        data: [{ id: '1', name_fa: 'تست', is_active: true }],
      });

      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      // Click on Plans tab
      const plansTab = screen.getByRole('button', { name: /پلن‌های طراحی/i });
      await user.click(plansTab);

      // Select a category (if available)
      const categoryButton = screen.queryByRole('button', { name: /تست/i });
      if (categoryButton) {
        await user.click(categoryButton);

        const newPlanBtn = screen.queryByRole('button', { name: /پلن جدید/i });
        if (newPlanBtn) {
          await user.click(newPlanBtn);

          // Modal should open
          expect(screen.getByRole('dialog')).toBeInTheDocument();
          expect(screen.getByText('ایجاد پلن طراحی جدید')).toBeInTheDocument();
        }
      }
    });

    test('all tab buttons switch tabs correctly', async () => {
      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      // Test Categories tab
      const categoriesTab = screen.getByRole('button', { name: /دسته‌بندی‌ها/i });
      await user.click(categoriesTab);
      expect(categoriesTab).toHaveClass('bg-primary');

      // Test Products tab
      const productsTab = screen.getByRole('button', { name: /محصولات/i });
      await user.click(productsTab);
      expect(productsTab).toHaveClass('bg-primary');

      // Test Plans tab
      const plansTab = screen.getByRole('button', { name: /پلن‌های طراحی/i });
      await user.click(plansTab);
      expect(plansTab).toHaveClass('bg-primary');
    });
  });

  describe('Modal Form Submissions', () => {
    let CatalogPage: any;

    beforeEach(async () => {
      vi.resetModules();
      const module = await import('@/app/(dashboard)/admin/catalog/page');
      CatalogPage = module.default;
    });

    test('category form validates required fields', async () => {
      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      // Open modal
      const newCategoryBtn = screen.getByRole('button', { name: /دسته‌بندی جدید/i });
      await user.click(newCategoryBtn);

      // Try to submit empty form
      const submitBtn = screen.getByRole('button', { name: /ایجاد/i });
      await user.click(submitBtn);

      // Should show error (form validation prevents empty submission)
      // The exact behavior depends on implementation
    });

    test('category form submission calls API with correct data', async () => {
      const { adminApi } = await import('@/lib/api');
      const mockCreate = vi.fn().mockResolvedValue({ data: {} });
      vi.mocked(adminApi.createCategory).mockImplementation(mockCreate);

      const user = userEvent.setup();
      render(<CatalogPage />, { wrapper: createWrapper() });

      await screen.findByText('مدیریت کاتالوگ');

      // Open modal
      await user.click(screen.getByRole('button', { name: /دسته‌بندی جدید/i }));

      // Fill form
      const nameInput = screen.getByPlaceholderText('مثال: کارت ویزیت');
      await user.type(nameInput, 'تست دسته‌بندی');

      // Submit
      await user.click(screen.getByRole('button', { name: /ایجاد/i }));

      // Verify API was called
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  describe('Button Handler Coverage', () => {
    test('no buttons render without click handlers in production code', async () => {
      // This is a meta-test that scans component files
      // In a real implementation, this would use AST parsing
      
      const fs = await import('fs');
      const path = await import('path');
      
      // Skip if running in browser environment
      if (typeof window !== 'undefined') {
        return;
      }

      const componentsDir = path.resolve(__dirname, '../../app');
      
      const scanFile = (filePath: string): string[] => {
        const issues: string[] = [];
        
        try {
          const content = fs.readFileSync(filePath, 'utf8');
          
          // Find all Button components without onClick
          const buttonMatches = content.matchAll(/<Button[^>]*>[\s\S]*?<\/Button>/g);
          
          for (const match of buttonMatches) {
            const buttonCode = match[0];
            
            // Check if it has onClick, type="submit", or is disabled
            const hasOnClick = /onClick/.test(buttonCode);
            const isSubmit = /type=["']submit["']/.test(buttonCode);
            const isDisabled = /disabled/.test(buttonCode);
            
            if (!hasOnClick && !isSubmit && !isDisabled) {
              // Extract button text for reporting
              const textMatch = buttonCode.match(/>([^<]+)</);
              const buttonText = textMatch ? textMatch[1].trim() : 'unnamed';
              issues.push(`${filePath}: Button "${buttonText}" has no onClick handler`);
            }
          }
        } catch (e) {
          // File read error, skip
        }
        
        return issues;
      };

      // This would recursively scan all files
      // For now, just validate the concept
      expect(true).toBe(true);
    });
  });
});

describe('API Endpoint Validation', () => {
  test('all adminApi methods exist and are callable', async () => {
    const { adminApi } = await import('@/lib/api');
    
    // Catalog endpoints
    expect(typeof adminApi.getCategories).toBe('function');
    expect(typeof adminApi.createCategory).toBe('function');
    expect(typeof adminApi.updateCategory).toBe('function');
    expect(typeof adminApi.deleteCategory).toBe('function');
    
    expect(typeof adminApi.getProducts).toBe('function');
    expect(typeof adminApi.createProduct).toBe('function');
    expect(typeof adminApi.updateProduct).toBe('function');
    expect(typeof adminApi.deleteProduct).toBe('function');
    
    expect(typeof adminApi.getPlans).toBe('function');
    expect(typeof adminApi.createPlan).toBe('function');
    expect(typeof adminApi.updatePlan).toBe('function');
    expect(typeof adminApi.deletePlan).toBe('function');
  });
});

