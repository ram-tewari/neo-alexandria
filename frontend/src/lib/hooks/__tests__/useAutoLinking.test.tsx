import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAutoLinking } from '../useAutoLinking';
import { apiClient } from '@/core/api/client';
import type { Resource } from '@/types/library';

// Mock the API client
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('useAutoLinking', () => {
  let queryClient: QueryClient;

  const mockCodeResource: Resource = {
    id: 'code-1',
    title: 'utils.ts',
    type: 'code',
    url: 'https://example.com/code/utils.ts',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockPaperResource: Resource = {
    id: 'paper-1',
    title: 'Research Paper',
    type: 'pdf',
    url: 'https://example.com/paper.pdf',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  };

  const mockRelatedCode = [
    {
      resource: mockCodeResource,
      similarity: 0.85,
      relationship_type: 'code_reference' as const,
    },
    {
      resource: { ...mockCodeResource, id: 'code-2', title: 'helpers.ts' },
      similarity: 0.72,
      relationship_type: 'semantic' as const,
    },
  ];

  const mockRelatedPapers = [
    {
      resource: mockPaperResource,
      similarity: 0.91,
      relationship_type: 'citation' as const,
    },
    {
      resource: { ...mockPaperResource, id: 'paper-2', title: 'Related Paper' },
      similarity: 0.68,
      relationship_type: 'semantic' as const,
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('fetching related resources', () => {
    it('should fetch related code and papers', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: mockRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.relatedCode).toEqual(mockRelatedCode);
      expect(result.current.relatedPapers).toEqual(mockRelatedPapers);
    });

    it('should not fetch when resourceId is empty', async () => {
      const { result } = renderHook(() => useAutoLinking(''), { wrapper });

      // Wait a bit to ensure queries don't start
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(result.current.isLoading).toBe(false);
      expect(result.current.relatedCode).toEqual([]);
      expect(result.current.relatedPapers).toEqual([]);
    });

    it('should handle individual loading states', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return new Promise((resolve) =>
            setTimeout(() => resolve({ data: mockRelatedCode }), 100)
          );
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      expect(result.current.isLoadingCode).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoadingCode).toBe(false);
      });
    });

    it('should handle errors', async () => {
      const error = new Error('Failed to fetch related code');
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.reject(error);
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.hasError).toBe(true);
      });

      expect(result.current.codeError).toBeTruthy();
      expect(result.current.relatedCode).toEqual([]);
    });
  });

  describe('derived states', () => {
    it('should report hasRelatedCode correctly', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: mockRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasRelatedCode).toBe(true);
      expect(result.current.hasRelatedPapers).toBe(false);
    });

    it('should report hasRelatedPapers correctly', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: [] });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasRelatedCode).toBe(false);
      expect(result.current.hasRelatedPapers).toBe(true);
    });

    it('should report hasAnySuggestions correctly', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: mockRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasAnySuggestions).toBe(true);
    });
  });

  describe('similarity scoring', () => {
    it('should get top related code by similarity', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: mockRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const topCode = result.current.getTopRelatedCode(1);

      expect(topCode).toHaveLength(1);
      expect(topCode[0].similarity).toBe(0.85);
    });

    it('should get top related papers by similarity', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: [] });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const topPapers = result.current.getTopRelatedPapers(1);

      expect(topPapers).toHaveLength(1);
      expect(topPapers[0].similarity).toBe(0.91);
    });

    it('should limit results correctly', async () => {
      const manyRelatedCode = Array.from({ length: 10 }, (_, i) => ({
        resource: { ...mockCodeResource, id: `code-${i}` },
        similarity: 0.9 - i * 0.05,
        relationship_type: 'semantic' as const,
      }));

      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: manyRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const top3 = result.current.getTopRelatedCode(3);

      expect(top3).toHaveLength(3);
      expect(top3[0].similarity).toBeGreaterThan(top3[1].similarity);
      expect(top3[1].similarity).toBeGreaterThan(top3[2].similarity);
    });
  });

  describe('refresh suggestions', () => {
    it('should refresh all suggestions', async () => {
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url.includes('related-code')) {
          return Promise.resolve({ data: mockRelatedCode });
        }
        if (url.includes('related-papers')) {
          return Promise.resolve({ data: mockRelatedPapers });
        }
        return Promise.reject(new Error('Unknown endpoint'));
      });

      const { result } = renderHook(() => useAutoLinking('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      vi.mocked(apiClient.get).mockClear();

      await result.current.refreshSuggestions();

      expect(apiClient.get).toHaveBeenCalledTimes(2);
    });
  });
});
