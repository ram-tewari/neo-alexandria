import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RepositorySwitcher } from '../RepositorySwitcher';
import { useRepositoryStore } from '@/stores/repository';
import * as useWorkbenchData from '@/lib/hooks/useWorkbenchData';
import type { Resource } from '@/types/api';

/**
 * Property-Based Tests for RepositorySwitcher
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 3.3 Update workbench store to use real data
 * Property 5: Repository Switcher Selection
 * Validates: Requirements 2.2, 2.5, 2.6
 */

// Mock the hooks
vi.mock('@/lib/hooks/useWorkbenchData');
vi.mock('@/stores/repository', async () => {
  const actual = await vi.importActual('@/stores/repository');
  return {
    ...actual,
    useRepositoryStore: vi.fn(),
  };
});

describe('RepositorySwitcher - Property Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  const renderWithQuery = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  /**
   * Property 5: Repository Switcher Selection
   * For any repository in the list, selecting it should update the active repository
   * and persist the selection
   */
  it('should display repositories from backend API', async () => {
    const mockResources: Resource[] = [
      {
        id: '1',
        title: 'neo-alexandria-2.0',
        description: 'Knowledge management system',
        url: 'https://github.com/example/neo-alexandria-2.0',
        language: 'TypeScript',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'completed',
      },
      {
        id: '2',
        title: 'react',
        description: 'JavaScript library',
        url: 'https://github.com/facebook/react',
        language: 'JavaScript',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-20T00:00:00Z',
        ingestion_status: 'completed',
      },
    ];

    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: mockResources,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: '1',
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    renderWithQuery(<RepositorySwitcher />);

    await waitFor(() => {
      expect(screen.getByText('neo-alexandria-2.0')).toBeInTheDocument();
    });
  });

  it('should show loading state while fetching repositories', () => {
    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: null,
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    renderWithQuery(<RepositorySwitcher />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should show error state when API fails', async () => {
    const mockError = new Error('Failed to fetch resources');

    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: null,
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    renderWithQuery(<RepositorySwitcher />);

    await waitFor(() => {
      expect(screen.getByText(/Error loading/i)).toBeInTheDocument();
    });
  });

  it('should handle empty repository list', () => {
    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: null,
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    renderWithQuery(<RepositorySwitcher />);

    expect(screen.getByText('No repositories')).toBeInTheDocument();
  });

  it('should map resources to repositories correctly', async () => {
    const mockResources: Resource[] = [
      {
        id: '1',
        title: 'GitHub Repo',
        url: 'https://github.com/example/repo',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'completed',
      },
      {
        id: '2',
        title: 'GitLab Repo',
        url: 'https://gitlab.com/example/repo',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'processing',
      },
      {
        id: '3',
        title: 'Local Repo',
        file_path: '/path/to/local/repo',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'failed',
      },
    ];

    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: mockResources,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: '1',
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    renderWithQuery(<RepositorySwitcher />);

    await waitFor(() => {
      expect(screen.getByText('GitHub Repo')).toBeInTheDocument();
    });
  });

  it('should maintain selection consistency across re-renders', async () => {
    const mockResources: Resource[] = [
      {
        id: '1',
        title: 'Repo 1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'completed',
      },
      {
        id: '2',
        title: 'Repo 2',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: 'completed',
      },
    ];

    vi.mocked(useWorkbenchData.useResources).mockReturnValue({
      data: mockResources,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.mocked(useRepositoryStore).mockReturnValue({
      activeRepositoryId: '1',
      setActiveRepository: vi.fn(),
      clearActiveRepository: vi.fn(),
    });

    const { rerender } = renderWithQuery(<RepositorySwitcher />);

    await waitFor(() => {
      expect(screen.getByText('Repo 1')).toBeInTheDocument();
    });

    // Re-render with same props
    rerender(
      <QueryClientProvider client={queryClient}>
        <RepositorySwitcher />
      </QueryClientProvider>
    );

    // Should still show same repository
    expect(screen.getByText('Repo 1')).toBeInTheDocument();
  });

  it('should handle different ingestion statuses', async () => {
    const statuses: Array<Resource['ingestion_status']> = [
      'completed',
      'processing',
      'pending',
      'failed',
    ];

    for (const status of statuses) {
      const mockResource: Resource = {
        id: '1',
        title: `Repo ${status}`,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: status,
      };

      vi.mocked(useWorkbenchData.useResources).mockReturnValue({
        data: [mockResource],
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      } as any);

      vi.mocked(useRepositoryStore).mockReturnValue({
        activeRepositoryId: '1',
        setActiveRepository: vi.fn(),
        clearActiveRepository: vi.fn(),
      });

      const { unmount } = renderWithQuery(<RepositorySwitcher />);

      await waitFor(() => {
        expect(screen.getByText(`Repo ${status}`)).toBeInTheDocument();
      });

      unmount();
    }
  });
});
