import { Outlet, createRootRoute } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/sonner';

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
 * Includes QueryClientProvider for React Query and Toaster for notifications.
 */
const RootComponent = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
      <Toaster />
    </QueryClientProvider>
  );
};

/**
 * Root route definition
 */
export const Route = createRootRoute({
  component: RootComponent,
});
