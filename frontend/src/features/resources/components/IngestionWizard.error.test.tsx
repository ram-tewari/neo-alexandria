import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IngestionWizard } from './IngestionWizard';
import * as useIngestResourceModule from '../hooks/useIngestResource';

// Mock the toast hook
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: mockToast
  })
}));

describe('IngestionWizard - Error Handling', () => {
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

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <IngestionWizard />
      </QueryClientProvider>
    );
  };

  it('handles network errors with appropriate toast', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      const networkError = new Error('Network Error');
      callbacks?.onError?.(networkError);
    });
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      isSuccess: false,
      error: null,
      data: undefined,
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isIdle: true,
      isPaused: false,
      status: 'idle',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Network Error',
        description: 'Network error. Please check your connection.',
        variant: 'destructive'
      });
    });
  });

  it('handles 429 rate limit errors with retry-after message', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      const rateLimitError = {
        response: {
          status: 429,
          headers: { 'retry-after': '30' },
          data: { detail: 'Rate limit exceeded' }
        }
      };
      callbacks?.onError?.(rateLimitError);
    });
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      isSuccess: false,
      error: null,
      data: undefined,
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isIdle: true,
      isPaused: false,
      status: 'idle',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Rate Limit Exceeded',
        description: 'Rate limit exceeded. Please try again in 30 seconds.',
        variant: 'destructive'
      });
    });
  });

  it('handles 500 server errors with generic message', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
      };
      callbacks?.onError?.(serverError);
    });
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      isSuccess: false,
      error: null,
      data: undefined,
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isIdle: true,
      isPaused: false,
      status: 'idle',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Server Error',
        description: 'Server error. Please try again later.',
        variant: 'destructive'
      });
    });
  });

  it('handles 400 validation errors with backend message', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      const validationError = {
        response: {
          status: 400,
          data: { detail: 'Invalid URL format' }
        }
      };
      callbacks?.onError?.(validationError);
    });
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      isSuccess: false,
      error: null,
      data: undefined,
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isIdle: true,
      isPaused: false,
      status: 'idle',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Ingestion Failed',
        description: 'Invalid URL format',
        variant: 'destructive'
      });
    });
  });

  it('logs errors to console', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      const error = new Error('Test error');
      callbacks?.onError?.(error);
    });
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      isSuccess: false,
      error: null,
      data: undefined,
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isIdle: true,
      isPaused: false,
      status: 'idle',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'https://example.com/article');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Ingestion error:', expect.any(Error));
    });
    
    consoleErrorSpy.mockRestore();
  });
});
