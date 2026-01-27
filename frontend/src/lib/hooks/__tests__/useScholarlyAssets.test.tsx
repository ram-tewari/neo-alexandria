import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useScholarlyAssets } from '../useScholarlyAssets';
import { scholarlyApi } from '@/lib/api/scholarly';
import type { Equation, Table, Metadata } from '@/types/library';

// Mock the API
vi.mock('@/lib/api/scholarly', () => ({
  scholarlyApi: {
    getEquations: vi.fn(),
    getTables: vi.fn(),
    getMetadata: vi.fn(),
  },
}));

describe('useScholarlyAssets', () => {
  let queryClient: QueryClient;

  const mockEquations: Equation[] = [
    {
      id: '1',
      resource_id: 'resource-1',
      latex: 'E = mc^2',
      page_number: 1,
      position: { x: 10, y: 20 },
    },
    {
      id: '2',
      resource_id: 'resource-1',
      latex: 'F = ma',
      page_number: 2,
      position: { x: 15, y: 25 },
    },
  ];

  const mockTables: Table[] = [
    {
      id: '1',
      resource_id: 'resource-1',
      caption: 'Test Table 1',
      page_number: 3,
      data: [['A', 'B'], ['1', '2']],
    },
  ];

  const mockMetadata: Metadata = {
    resource_id: 'resource-1',
    title: 'Test Paper',
    authors: ['Author 1', 'Author 2'],
    abstract: 'Test abstract',
    publication_date: '2024-01-01',
    completeness_score: 0.85,
  };

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

  describe('fetching assets', () => {
    it('should fetch all assets in parallel', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue(mockEquations);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.equations).toEqual(mockEquations);
      expect(result.current.tables).toEqual(mockTables);
      expect(result.current.metadata).toEqual(mockMetadata);
    });

    it('should not fetch when resourceId is empty', async () => {
      const { result } = renderHook(() => useScholarlyAssets(''), { wrapper });

      // Wait a bit to ensure queries don't start
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(result.current.isLoading).toBe(false);
      expect(result.current.equations).toEqual([]);
      expect(result.current.tables).toEqual([]);
    });

    it('should handle individual loading states', async () => {
      vi.mocked(scholarlyApi.getEquations).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockEquations), 100))
      );
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      expect(result.current.isLoadingEquations).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoadingEquations).toBe(false);
      });
    });

    it('should handle errors', async () => {
      const error = new Error('Failed to fetch equations');
      vi.mocked(scholarlyApi.getEquations).mockRejectedValue(error);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.hasError).toBe(true);
      });

      expect(result.current.equationsError).toBeTruthy();
      expect(result.current.equations).toEqual([]);
    });
  });

  describe('derived states', () => {
    it('should report hasEquations correctly', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue(mockEquations);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue([]);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasEquations).toBe(true);
      expect(result.current.hasTables).toBe(false);
    });

    it('should report hasTables correctly', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue([]);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasEquations).toBe(false);
      expect(result.current.hasTables).toBe(true);
    });

    it('should report hasMetadata correctly', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue([]);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue([]);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasMetadata).toBe(true);
    });

    it('should report hasAnyAssets correctly', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue(mockEquations);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue([]);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(undefined as any);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.hasAnyAssets).toBe(true);
    });
  });

  describe('refetch actions', () => {
    it('should refetch all assets', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue(mockEquations);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      vi.mocked(scholarlyApi.getEquations).mockClear();
      vi.mocked(scholarlyApi.getTables).mockClear();
      vi.mocked(scholarlyApi.getMetadata).mockClear();

      await result.current.refetchAll();

      expect(scholarlyApi.getEquations).toHaveBeenCalled();
      expect(scholarlyApi.getTables).toHaveBeenCalled();
      expect(scholarlyApi.getMetadata).toHaveBeenCalled();
    });

    it('should refetch individual assets', async () => {
      vi.mocked(scholarlyApi.getEquations).mockResolvedValue(mockEquations);
      vi.mocked(scholarlyApi.getTables).mockResolvedValue(mockTables);
      vi.mocked(scholarlyApi.getMetadata).mockResolvedValue(mockMetadata);

      const { result } = renderHook(() => useScholarlyAssets('resource-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const callCountBefore = vi.mocked(scholarlyApi.getEquations).mock.calls.length;

      await result.current.refetchEquations();

      const callCountAfter = vi.mocked(scholarlyApi.getEquations).mock.calls.length;

      expect(callCountAfter).toBeGreaterThan(callCountBefore);
    });
  });
});
