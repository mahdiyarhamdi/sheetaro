"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useState } from "react";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: "var(--color-surface)",
            color: "var(--color-text-primary)",
            borderRadius: "0.75rem",
            boxShadow: "var(--shadow-medium)",
            border: "1px solid var(--color-border)",
            padding: "12px 16px",
            fontFamily: "IRANYekan, sans-serif",
          },
          success: {
            iconTheme: {
              primary: "var(--color-success)",
              secondary: "white",
            },
          },
          error: {
            iconTheme: {
              primary: "var(--color-danger)",
              secondary: "white",
            },
          },
        }}
      />
    </QueryClientProvider>
  );
}

