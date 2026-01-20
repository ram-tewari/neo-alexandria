import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import ResourcesPage from '@/routes/_auth.resources';
import * as api from '../api';
import type { Resource } from '@/core/types/resource';

// Mock the API
vi.mock('../api');

// Mock toast
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));

describe('Integration: Pagination Flow', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
    vi.clearAllMocks();
  });

  const renderPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ResourcesPage />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  const createMockResource = (id: number): Resource => ({
    id: `resource-${id}`,
    title: `Resource ${id}`,
    url: `https://example.com/resource-${id}`,
    ingestion_status: 'completed',
    quality_score: 0.8,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    classification_code: 'CS.AI'
  });

  it('completes full pagination flow', async () => {
    const user = userEvent.setup();

    // Step 1: Load initial page (page 1)
    const page1Resources = Array.from({ length: 25 }, (_, i) => createMockResource(i + 1));
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: page1Resources,
      total: 75 // 3 pages total
    });

    renderPage();

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Resource 1')).toBeInTheDocument();
    });

    // Verify API called with correct params for page 1
    expect(api.fetchResources).toHaveBeenCalledWith({
      page: 1,
      limit: 25,
      sort: 'created_at:desc'
    });

    // Verify pagination shows page 1 of 3
    expect(screen.getByText(/page 1 of 3/i)).toBeInTheDocument();
    expect(screen.getByText(/75 total resources/i)).toBeInTheDocument();

    // Verify "Previous" is disabled on first page
    const previousButton = screen.getByRole('button', { name: /previous/i });
    expect(previousButton).toBeDisabled();

    // Step 2: Click "Next"
    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).not.toBeDisabled();

    const page2Resources = Array.from({ length: 25 }, (_, i) => createMockResource(i + 26));
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: page2Resources,
      total: 75
    });

    await user.click(nextButton);

    // Step 3: Verify API called with correct offset for page 2
    await waitFor(() => {
      expect(api.fetchResources).toHaveBeenCalledWith({
        page: 2,
        limit: 25,
        sort: 'created_at:desc'
      });
    });

    // Step 4: Verify table updates with page 2 data
    await waitFor(() => {
      expect(screen.getByText('Resource 26')).toBeInTheDocument();
    });

    // Verify pagination shows page 2 of 3
    expect(screen.getByText(/page 2 of 3/i)).toBeInTheDocument();

    // Step 5: Verify "Previous" is now enabled
    expect(previousButton).not.toBeDisabled();

    // Step 6: Navigate to last page (page 3)
    const page3Resources = Array.from({ length: 25 }, (_, i) => createMockResource(i + 51));
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: page3Resources,
      total: 75
    });

    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Resource 51')).toBeInTheDocument();
    });

    // Step 7: Verify "Next" is disabled on last page
    expect(screen.getByText(/page 3 of 3/i)).toBeInTheDocument();
    expect(nextButton).toBeDisabled();

    // Step 8: Navigate back to page 2
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: page2Resources,
      total: 75
    });

    await user.click(previousButton);

    await waitFor(() => {
      expect(screen.getByText('Resource 26')).toBeInTheDocument();
    });

    expect(screen.getByText(/page 2 of 3/i)).toBeInTheDocument();
  });

  it('handles empty pages correctly', async () => {
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: [],
      total: 0
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No resources found')).toBeInTheDocument();
    });

    // Both buttons should be disabled
    const previousButton = screen.getByRole('button', { name: /previous/i });
    const nextButton = screen.getByRole('button', { name: /next/i });

    expect(previousButton).toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  it('handles single page correctly', async () => {
    const resources = Array.from({ length: 10 }, (_, i) => createMockResource(i + 1));
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: resources,
      total: 10
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Resource 1')).toBeInTheDocument();
    });

    expect(screen.getByText(/page 1 of 1/i)).toBeInTheDocument();

    // Both buttons should be disabled on single page
    const previousButton = screen.getByRole('button', { name: /previous/i });
    const nextButton = screen.getByRole('button', { name: /next/i });

    expect(previousButton).toBeDisabled();
    expect(nextButton).toBeDisabled();
  });
});
