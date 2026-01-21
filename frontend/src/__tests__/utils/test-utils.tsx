/**
 * Test utilities and wrapper components
 */

import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import userEvent from "@testing-library/user-event";

// Create a new QueryClient for each test
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// Providers wrapper for tests
interface ProvidersProps {
  children: React.ReactNode;
}

function TestProviders({ children }: ProvidersProps) {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// Custom render function with providers
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) {
  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: TestProviders, ...options }),
  };
}

// Re-export everything from testing-library
export * from "@testing-library/react";

// Override render with custom render
export { customRender as render };

// Helper to wait for loading states
export async function waitForLoadingToFinish() {
  // Wait a tick for React Query to start loading
  await new Promise((resolve) => setTimeout(resolve, 0));
}

// Helper to create mock router
export function createMockRouter(overrides = {}) {
  return {
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
    ...overrides,
  };
}

// Helper to mock localStorage
export function mockLocalStorage(initialData: Record<string, string> = {}) {
  const store = { ...initialData };
  
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach((key) => delete store[key]);
    }),
    getStore: () => store,
  };
}

