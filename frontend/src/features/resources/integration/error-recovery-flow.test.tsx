import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import ResourcesPage from '@/routes/_auth.resources';
import * as api from '../api';

// Mock the API
vi.mock('../api');

// Mock toast
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: mockToast
  })
}));

describe('Integration: Error Recovery Flow', () => {
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

  it('recovers from validation error and successfully submits', async () => {
    const user = userEvent.setup();

    // Mock initial empty list
    vi.mocked(api.fetchResources).mockResolvedValue({
      items: [],
      total: 0
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No resources found')).toBeInTheDocument();
    });

    // Step 1: Open wizard
    const addButton = screen.getByRole('button', { name: /add resource/i });
    await user.click(addButton);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    // Step 2: Submit invalid URL (validation error)
    vi.mocked(api.ingestResource).mockRejectedValue({
      response: {
        status: 400,
        data: { detail: 'Invalid URL format' }
      }
    });

    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://invalid-url');

    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);

    // Step 3: Verify error toast
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Ingestion Failed',
        description: 'Invalid URL format',
        variant: 'destructive'
      });
    });

    // Dialog should remain open
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    // Step 4: Correct URL
    await user.clear(urlInput);
    await user.type(urlInput, 'https://example.com/valid-article');

    // Step 5: Resubmit with valid URL
    vi.mocked(api.ingestResource).mockResolvedValue({
      id: 'test-resource-id',
      status: 'pending',
      title: 'Valid Article',
      ingestion_status: 'pending'
    });

    await user.click(submitButton);

    // Step 6: Verify success
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Ingestion Started',
        description: 'Your resource is being processed.'
      });
    });

    // Dialog should close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('recovers from network error', async () => {
    const user = userEvent.setup();

    vi.mocked(api.fetchResources).mockResolvedValue({
      items: [],
      total: 0
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No resources found')).toBeInTheDocument();
    });

    // Open wizard
    const addButton = screen.getByRole('button', { name: /add resource/i });
    await user.click(addButton);

    // Submit with network error
    vi.mocked(api.ingestResource).mockRejectedValue(new Error('Network Error'));

    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');

    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);

    // Verify network error toast
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Network Error',
        description: 'Network error. Please check your connection.',
        variant: 'destructive'
      });
    });

    // Dialog remains open for retry
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    // Retry with successful submission
    vi.mocked(api.ingestResource).mockResolvedValue({
      id: 'test-resource-id',
      status: 'pending',
      title: 'Article',
      ingestion_status: 'pending'
    });

    await user.click(submitButton);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Ingestion Started',
        description: 'Your resource is being processed.'
      });
    });
  });

  it('recovers from rate limit error', async () => {
    const user = userEvent.setup();

    vi.mocked(api.fetchResources).mockResolvedValue({
      items: [],
      total: 0
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No resources found')).toBeInTheDocument();
    });

    // Open wizard
    const addButton = screen.getByRole('button', { name: /add resource/i });
    await user.click(addButton);

    // Submit with rate limit error
    vi.mocked(api.ingestResource).mockRejectedValue({
      response: {
        status: 429,
        headers: { 'retry-after': '60' },
        data: { detail: 'Rate limit exceeded' }
      }
    });

    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');

    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);

    // Verify rate limit toast
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Rate Limit Exceeded',
        description: 'Rate limit exceeded. Please try again in 60 seconds.',
        variant: 'destructive'
      });
    });

    // Dialog remains open
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('recovers from server error', async () => {
    const user = userEvent.setup();

    vi.mocked(api.fetchResources).mockResolvedValue({
      items: [],
      total: 0
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No resources found')).toBeInTheDocument();
    });

    // Open wizard
    const addButton = screen.getByRole('button', { name: /add resource/i });
    await user.click(addButton);

    // Submit with server error
    vi.mocked(api.ingestResource).mockRejectedValue({
      response: {
        status: 500,
        data: { detail: 'Internal server error' }
      }
    });

    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');

    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);

    // Verify server error toast
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Server Error',
        description: 'Server error. Please try again later.',
        variant: 'destructive'
      });
    });

    // Dialog remains open for retry
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    // Retry with success
    vi.mocked(api.ingestResource).mockResolvedValue({
      id: 'test-resource-id',
      status: 'pending',
      title: 'Article',
      ingestion_status: 'pending'
    });

    await user.click(submitButton);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Ingestion Started',
        description: 'Your resource is being processed.'
      });
    });
  });
});
