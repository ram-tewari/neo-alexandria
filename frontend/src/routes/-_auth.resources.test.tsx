import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ResourcesPage from './_auth.resources';
import * as useResourceListModule from '@/features/resources/hooks/useResourceList';

// Mock the hooks
vi.mock('@/features/resources/hooks/useResourceList');
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));

describe('ResourcesPage Route', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
    vi.clearAllMocks();
    
    // Mock useResourceList to return empty data
    vi.spyOn(useResourceListModule, 'useResourceList').mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      isFetching: false,
      isSuccess: true,
      status: 'success',
      dataUpdatedAt: 0,
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      errorUpdateCount: 0,
      isInitialLoading: false,
      isLoadingError: false,
      isPaused: false,
      isPlaceholderData: false,
      isPreviousData: false,
      isRefetchError: false,
      isRefetching: false,
      isStale: false,
      remove: vi.fn()
    });
  });

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<ResourcesPage />} />
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders page title and description', () => {
    renderComponent();
    
    expect(screen.getByText('Resource Library')).toBeInTheDocument();
    expect(screen.getByText('Manage and browse your knowledge base')).toBeInTheDocument();
  });

  it('renders IngestionWizard button', () => {
    renderComponent();
    
    expect(screen.getByRole('button', { name: /add resource/i })).toBeInTheDocument();
  });

  it('renders ResourceDataTable', () => {
    renderComponent();
    
    // Table should be rendered (check for pagination controls)
    expect(screen.getByText(/page/i)).toBeInTheDocument();
  });

  it('initializes with default state', () => {
    renderComponent();
    
    // Should show page 1
    expect(screen.getByText(/page 1/i)).toBeInTheDocument();
    
    // Should call useResourceList with correct params
    expect(useResourceListModule.useResourceList).toHaveBeenCalledWith({
      page: 1,
      limit: 25,
      sort: 'created_at:desc'
    });
  });
});
