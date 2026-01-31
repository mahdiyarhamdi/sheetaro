/**
 * CRUD Test Template
 * 
 * این فایل الگوهای استاندارد برای تست عملیات CRUD فراهم می‌کند.
 * از این الگوها برای نوشتن تست‌های یکنواخت در تمام پروژه استفاده کنید.
 * 
 * استفاده:
 * 1. این فایل را import کنید
 * 2. از توابع کمکی برای ساخت تست‌های CRUD استفاده کنید
 * 3. تست‌ها را برای entity خاص خود customize کنید
 */

import { describe, test, expect, vi, beforeEach, Mock } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// ============================================
// Types
// ============================================

export interface CrudTestConfig<T> {
  /** Name of the entity (e.g., 'category', 'product') */
  entityName: string;
  
  /** Persian name for UI assertions */
  entityNamePersian: string;
  
  /** The page component to test */
  PageComponent: React.ComponentType;
  
  /** API mock functions */
  api: {
    list: Mock;
    create: Mock;
    update: Mock;
    delete: Mock;
  };
  
  /** Sample data for testing */
  sampleData: {
    list: T[];
    createPayload: Partial<T>;
    updatePayload: Partial<T>;
  };
  
  /** UI element selectors/names */
  ui: {
    /** Text on "new" button */
    newButtonText: string | RegExp;
    /** Modal title when creating */
    createModalTitle: string | RegExp;
    /** Modal title when editing */
    editModalTitle: string | RegExp;
    /** Primary field input label */
    primaryFieldLabel: string | RegExp;
    /** Submit button text */
    submitButtonText: string | RegExp;
    /** Cancel button text */
    cancelButtonText: string | RegExp;
    /** Success message after create */
    createSuccessMessage: string | RegExp;
    /** Success message after update */
    updateSuccessMessage: string | RegExp;
    /** Success message after delete */
    deleteSuccessMessage: string | RegExp;
  };
}

// ============================================
// Helper Functions
// ============================================

/**
 * Create a test wrapper with QueryClient
 */
export const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

/**
 * Setup common mocks for Next.js
 */
export const setupNextMocks = () => {
  vi.mock('next/navigation', () => ({
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      back: vi.fn(),
    }),
    useSearchParams: () => new URLSearchParams(),
    usePathname: () => '/',
  }));
};

/**
 * Setup auth mock for admin
 */
export const setupAdminAuthMock = () => {
  vi.mock('@/hooks/useAuth', () => ({
    useAuth: () => ({
      user: { id: '1', is_admin: true },
      isLoadingUser: false,
      isAdmin: true,
      isAuthenticated: true,
    }),
  }));
};

// ============================================
// Test Templates
// ============================================

/**
 * Generate CREATE operation tests
 */
export function generateCreateTests<T>(config: CrudTestConfig<T>) {
  return describe(`CREATE ${config.entityName}`, () => {
    beforeEach(() => {
      vi.resetAllMocks();
      config.api.list.mockResolvedValue({ data: [] });
      config.api.create.mockResolvedValue({ data: { id: 'new-id', ...config.sampleData.createPayload } });
    });

    test(`"${config.ui.newButtonText}" button opens modal`, async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: config.ui.newButtonText })).toBeInTheDocument();
      });

      const newButton = screen.getByRole('button', { name: config.ui.newButtonText });
      await user.click(newButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(config.ui.createModalTitle)).toBeInTheDocument();
    });

    test('form validates required fields', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: config.ui.newButtonText })).toBeInTheDocument();
      });

      // Open modal
      await user.click(screen.getByRole('button', { name: config.ui.newButtonText }));

      // Try to submit empty form
      const submitButton = screen.getByRole('button', { name: config.ui.submitButtonText });
      await user.click(submitButton);

      // API should NOT be called
      expect(config.api.create).not.toHaveBeenCalled();
    });

    test('successful submission calls API with correct data', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: config.ui.newButtonText })).toBeInTheDocument();
      });

      // Open modal
      await user.click(screen.getByRole('button', { name: config.ui.newButtonText }));

      // Fill form (this needs to be customized per entity)
      const primaryInput = screen.getByLabelText(config.ui.primaryFieldLabel);
      await user.type(primaryInput, 'Test Value');

      // Submit
      await user.click(screen.getByRole('button', { name: config.ui.submitButtonText }));

      await waitFor(() => {
        expect(config.api.create).toHaveBeenCalled();
      });
    });

    test('cancel button closes modal without submission', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: config.ui.newButtonText })).toBeInTheDocument();
      });

      // Open modal
      await user.click(screen.getByRole('button', { name: config.ui.newButtonText }));
      expect(screen.getByRole('dialog')).toBeInTheDocument();

      // Cancel
      await user.click(screen.getByRole('button', { name: config.ui.cancelButtonText }));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
      expect(config.api.create).not.toHaveBeenCalled();
    });

    test('API error shows error message', async () => {
      config.api.create.mockRejectedValue(new Error('API Error'));
      
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: config.ui.newButtonText })).toBeInTheDocument();
      });

      // Open modal and fill form
      await user.click(screen.getByRole('button', { name: config.ui.newButtonText }));
      const primaryInput = screen.getByLabelText(config.ui.primaryFieldLabel);
      await user.type(primaryInput, 'Test Value');

      // Submit
      await user.click(screen.getByRole('button', { name: config.ui.submitButtonText }));

      // Should show error (via toast or inline)
      // The exact assertion depends on implementation
    });
  });
}

/**
 * Generate READ (list) operation tests
 */
export function generateReadTests<T>(config: CrudTestConfig<T>) {
  return describe(`READ ${config.entityName} list`, () => {
    test('renders list of items', async () => {
      config.api.list.mockResolvedValue({ data: config.sampleData.list });
      
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        // Verify items are rendered
        config.sampleData.list.forEach((item: any) => {
          // This needs to be customized based on what fields are displayed
        });
      });
    });

    test('shows empty state when no items', async () => {
      config.api.list.mockResolvedValue({ data: [] });
      
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        // Should show empty state message
        expect(screen.queryByText(/یافت نشد/i) || screen.queryByText(/خالی/i)).toBeInTheDocument();
      });
    });

    test('shows loading state while fetching', async () => {
      config.api.list.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      // Should show loading indicator
      expect(
        screen.queryByRole('progressbar') || 
        screen.queryByTestId('loading') ||
        screen.queryByText(/در حال/i)
      ).toBeInTheDocument();
    });

    test('handles API error gracefully', async () => {
      config.api.list.mockRejectedValue(new Error('API Error'));
      
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        // Should show error state or message
      });
    });
  });
}

/**
 * Generate UPDATE operation tests
 */
export function generateUpdateTests<T>(config: CrudTestConfig<T>) {
  return describe(`UPDATE ${config.entityName}`, () => {
    beforeEach(() => {
      config.api.list.mockResolvedValue({ data: config.sampleData.list });
      config.api.update.mockResolvedValue({ data: { ...config.sampleData.list[0], ...config.sampleData.updatePayload } });
    });

    test('edit button opens modal with existing data', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(config.api.list).toHaveBeenCalled();
      });

      // Find and click edit button
      const editButtons = screen.getAllByRole('button', { name: /ویرایش/i }) ||
                          screen.getAllByLabelText(/ویرایش/i);
      
      if (editButtons.length > 0) {
        await user.click(editButtons[0]);
        
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        expect(screen.getByText(config.ui.editModalTitle)).toBeInTheDocument();
        
        // Form should be pre-filled with existing data
      }
    });

    test('update submission calls API with correct data', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(config.api.list).toHaveBeenCalled();
      });

      const editButtons = screen.getAllByRole('button', { name: /ویرایش/i }) ||
                          screen.getAllByLabelText(/ویرایش/i);
      
      if (editButtons.length > 0) {
        await user.click(editButtons[0]);
        
        // Modify data
        const primaryInput = screen.getByLabelText(config.ui.primaryFieldLabel);
        await user.clear(primaryInput);
        await user.type(primaryInput, 'Updated Value');
        
        // Submit
        await user.click(screen.getByRole('button', { name: config.ui.submitButtonText }));
        
        await waitFor(() => {
          expect(config.api.update).toHaveBeenCalled();
        });
      }
    });
  });
}

/**
 * Generate DELETE operation tests
 */
export function generateDeleteTests<T>(config: CrudTestConfig<T>) {
  return describe(`DELETE ${config.entityName}`, () => {
    beforeEach(() => {
      config.api.list.mockResolvedValue({ data: config.sampleData.list });
      config.api.delete.mockResolvedValue({});
    });

    test('delete button triggers deletion', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(config.api.list).toHaveBeenCalled();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /حذف/i }) ||
                            screen.getAllByLabelText(/حذف/i);
      
      if (deleteButtons.length > 0) {
        await user.click(deleteButtons[0]);
        
        // May show confirmation dialog
        const confirmButton = screen.queryByRole('button', { name: /تأیید|بله/i });
        if (confirmButton) {
          await user.click(confirmButton);
        }
        
        await waitFor(() => {
          expect(config.api.delete).toHaveBeenCalled();
        });
      }
    });

    test('delete can be cancelled', async () => {
      const user = userEvent.setup();
      render(<config.PageComponent />, { wrapper: createTestWrapper() });

      await waitFor(() => {
        expect(config.api.list).toHaveBeenCalled();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /حذف/i }) ||
                            screen.getAllByLabelText(/حذف/i);
      
      if (deleteButtons.length > 0) {
        await user.click(deleteButtons[0]);
        
        // If there's a confirmation dialog, cancel it
        const cancelButton = screen.queryByRole('button', { name: /انصراف|خیر|لغو/i });
        if (cancelButton) {
          await user.click(cancelButton);
          expect(config.api.delete).not.toHaveBeenCalled();
        }
      }
    });
  });
}

/**
 * Generate all CRUD tests for an entity
 */
export function generateAllCrudTests<T>(config: CrudTestConfig<T>) {
  return describe(`${config.entityNamePersian} CRUD Operations`, () => {
    generateCreateTests(config);
    generateReadTests(config);
    generateUpdateTests(config);
    generateDeleteTests(config);
  });
}

// ============================================
// Example Usage
// ============================================

/*
import { generateAllCrudTests, CrudTestConfig } from '@/__tests__/templates/crud.template';
import CatalogPage from '@/app/(dashboard)/admin/catalog/page';
import { adminApi } from '@/lib/api';

const categoryConfig: CrudTestConfig<Category> = {
  entityName: 'category',
  entityNamePersian: 'دسته‌بندی',
  PageComponent: CatalogPage,
  api: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  sampleData: {
    list: [
      { id: '1', name_fa: 'کارت ویزیت', slug: 'business-card', is_active: true },
    ],
    createPayload: { name_fa: 'تست', slug: 'test', is_active: true },
    updatePayload: { name_fa: 'ویرایش شده' },
  },
  ui: {
    newButtonText: /دسته‌بندی جدید/i,
    createModalTitle: /ایجاد دسته‌بندی/i,
    editModalTitle: /ویرایش دسته‌بندی/i,
    primaryFieldLabel: /نام دسته‌بندی/i,
    submitButtonText: /ایجاد|به‌روزرسانی/i,
    cancelButtonText: /انصراف/i,
    createSuccessMessage: /ایجاد شد/i,
    updateSuccessMessage: /به‌روزرسانی شد/i,
    deleteSuccessMessage: /حذف شد/i,
  },
};

generateAllCrudTests(categoryConfig);
*/

export default {
  createTestWrapper,
  setupNextMocks,
  setupAdminAuthMock,
  generateCreateTests,
  generateReadTests,
  generateUpdateTests,
  generateDeleteTests,
  generateAllCrudTests,
};

