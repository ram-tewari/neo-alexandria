import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IngestionWizard } from './IngestionWizard';
import * as useIngestResourceModule from '../hooks/useIngestResource';

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));

describe('IngestionWizard', () => {
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

  it('renders trigger button', () => {
    renderComponent();
    expect(screen.getByRole('button', { name: /add resource/i })).toBeInTheDocument();
  });

  it('opens dialog when trigger is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Choose a method to add resources to your library.')).toBeInTheDocument();
  });

  it('renders three tabs', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    expect(screen.getByRole('tab', { name: /single url/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /file upload/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /batch paste/i })).toBeInTheDocument();
  });

  it('shows Single URL tab by default', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    expect(screen.getByLabelText(/resource url/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title \(optional\)/i)).toBeInTheDocument();
  });

  it('validates URL format - requires http/https', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const urlInput = screen.getByLabelText(/resource url/i);
    await user.type(urlInput, 'invalid-url');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/url must start with http/i)).toBeInTheDocument();
    });
  });

  it('validates URL is required', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/url is required/i)).toBeInTheDocument();
    });
  });

  it('disables submit button during loading', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn();
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: true,
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
      isIdle: false,
      isPaused: false,
      status: 'pending',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    expect(submitButton).toBeDisabled();
  });

  it('shows loading spinner during submission', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn();
    
    vi.spyOn(useIngestResourceModule, 'useIngestResource').mockReturnValue({
      mutate: mockMutate,
      isPending: true,
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
      isIdle: false,
      isPaused: false,
      status: 'pending',
      submittedAt: 0
    });
    
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    expect(screen.getByRole('button', { name: /ingest/i }).querySelector('svg.animate-spin')).toBeInTheDocument();
  });

  it('submits form with valid URL', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      callbacks?.onSuccess?.();
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
      expect(mockMutate).toHaveBeenCalledWith(
        { url: 'https://example.com/article', title: undefined },
        expect.any(Object)
      );
    });
  });

  it('submits form with URL and title', async () => {
    const user = userEvent.setup();
    const mockMutate = vi.fn((payload, callbacks) => {
      callbacks?.onSuccess?.();
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
    const titleInput = screen.getByLabelText(/title \(optional\)/i);
    
    await user.type(urlInput, 'https://example.com/article');
    await user.type(titleInput, 'My Custom Title');
    
    const submitButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        { url: 'https://example.com/article', title: 'My Custom Title' },
        expect.any(Object)
      );
    });
  });

  it('marks File Upload and Batch Paste tabs as disabled', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    await user.click(screen.getByRole('button', { name: /add resource/i }));
    
    const fileTab = screen.getByRole('tab', { name: /file upload/i });
    const batchTab = screen.getByRole('tab', { name: /batch paste/i });
    
    expect(fileTab).toBeDisabled();
    expect(batchTab).toBeDisabled();
  });
});
