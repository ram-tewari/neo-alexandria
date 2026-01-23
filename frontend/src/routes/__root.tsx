import { Outlet, createRootRoute } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/sonner';
import { ThemeProvider } from '@/app/providers/ThemeProvider';
import { CommandPalette } from '@/components/CommandPalette';
import { useGlobalKeyboard } from '@/lib/hooks/useGlobalKeyboard';

/**
 * Create QueryClient instance with default options
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

/**
 * Root layout component
 * 
 * Provides global providers and layout structure for the entire application.
 * Includes QueryClientProvider for React Query, AuthProvider for authentication,
 * ThemeProvider for theme management, CommandPalette for global keyboard shortcuts,
 * and Toaster for notifications. Also registers global keyboard shortcuts via useGlobalKeyboard hook.
 */
const RootComponent = () => {
  // Register global keyboard shortcuts
  useGlobalKeyboard();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Outlet />
        <CommandPalette />
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

/**
 * Root route definition
 */
export const Route = createRootRoute({
  component: RootComponent,
});
