import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDocuments } from '../useDocuments';
import { libraryApi } from '@/lib/api/library';
import { useLibraryStore } from '@/stores/library';
import type { Resource } from '@/types/library';

// Mock the API
vi.mock('@/lib/api/library', () => ({
  libraryApi: {
    listResources: vi.fn(),
    uploadResource: vi.fn(),
    updateResource: vi.fn(),
    deleteResource: vi.fn(),
  },
}));

// Mock the store
vi.mock('@/stores/library', () => ({
  useLibraryStore: vi.fn(),
}));

describe('useDocuments', () => {
  let queryClient: QueryClient;
  let mockStoreActions: any;

  const mockResources: Resource[] = [
    {
      id: '1',
      title: 'Test Document 1',
      type: 'pdf',
      url: 'https://example.com/doc1.pdf',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      title: 'Test Document 2',
      type: 'html',
      url: 'https://example.com/doc2.html',
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    mockStoreActions = {
      setResources: vi.fn(),
      addResource: vi.fn(),
      updateResource: vi.fn(),
      removeResource: vi.fn(),
    };

    (useLibraryStore as any).mockReturnValue(mockStoreActions);
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('fetching documents', () => {
    it('should fetch documents successfully', async () => {
      vi.mocked(libraryApi.listResources).mockResolvedValue({
        resources: mockResources,
        total: 2,
      });

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.documents).toEqual(mockResources);
      expect(result.current.total).toBe(2);
      expect(mockStoreActions.setResources).toHaveBeenCalledWith(mockResources);
    });

    it('should fetch documents with filters', async () => {
      const params = { type: 'pdf', quality_min: 0.8 };
      vi.mocked(libraryApi.listResources).mockResolvedValue({
        resources: [mockResources[0]],
        total: 1,
      });

      const { result } = renderHook(() => useDocuments(params), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(libraryApi.listResources).toHaveBeenCalledWith(params);
      expect(result.current.documents).toHaveLength(1);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch');
      vi.mocked(libraryApi.listResources).mockRejectedValue(error);

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      expect(result.current.documents).toEqual([]);
    });
  });

  describe('uploading documents', () => {
    it('should upload document with optimistic update', async () => {
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const uploadedResource: Resource = {
        id: '3',
        title: 'test.pdf',
        type: 'pdf',
        url: 'https://example.com/test.pdf',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      };

      vi.mocked(libraryApi.uploadResource).mockResolvedValue(uploadedResource);

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.uploadDocument({ file });

      // Check optimistic update
      await waitFor(() => {
        expect(mockStoreActions.addResource).toHaveBeenCalled();
      }, { timeout: 3000 });

      // Check final update
      await waitFor(() => {
        expect(mockStoreActions.removeResource).toHaveBeenCalled();
      }, { timeout: 3000 });

      expect(mockStoreActions.addResource).toHaveBeenCalledWith(uploadedResource);
    });

    it('should handle upload errors and rollback', async () => {
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const error = new Error('Upload failed');

      vi.mocked(libraryApi.uploadResource).mockRejectedValue(error);

      const { result } = renderHook(() => useDocuments(), { wrapper });

      result.current.uploadDocument({ file });

      await waitFor(() => {
        expect(result.current.uploadError).toBeTruthy();
      });

      // Should remove temp resource
      expect(mockStoreActions.removeResource).toHaveBeenCalled();
    });
  });

  describe('updating documents', () => {
    it('should update document with optimistic update', async () => {
      const updates = { title: 'Updated Title' };
      const updatedResource: Resource = {
        ...mockResources[0],
        ...updates,
      };

      vi.mocked(libraryApi.updateResource).mockResolvedValue(updatedResource);

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.updateDocument({ resourceId: '1', updates });

      // Check optimistic update
      await waitFor(() => {
        expect(mockStoreActions.updateResource).toHaveBeenCalledWith('1', updates);
      }, { timeout: 3000 });
    });

    it('should handle update errors and rollback', async () => {
      const error = new Error('Update failed');
      vi.mocked(libraryApi.updateResource).mockRejectedValue(error);
      vi.mocked(libraryApi.listResources).mockResolvedValue({
        resources: mockResources,
        total: 2,
      });

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.updateDocument({ resourceId: '1', updates: { title: 'New' } });

      await waitFor(() => {
        expect(result.current.updateError).toBeTruthy();
      });

      // Should rollback
      expect(mockStoreActions.setResources).toHaveBeenCalled();
    });
  });

  describe('deleting documents', () => {
    it('should delete document with optimistic update', async () => {
      vi.mocked(libraryApi.deleteResource).mockResolvedValue(undefined);

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.deleteDocument('1');

      // Check optimistic update
      await waitFor(() => {
        expect(mockStoreActions.removeResource).toHaveBeenCalledWith('1');
      }, { timeout: 3000 });
    });

    it('should handle delete errors and rollback', async () => {
      const error = new Error('Delete failed');
      vi.mocked(libraryApi.deleteResource).mockRejectedValue(error);
      vi.mocked(libraryApi.listResources).mockResolvedValue({
        resources: mockResources,
        total: 2,
      });

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.deleteDocument('1');

      await waitFor(() => {
        expect(result.current.deleteError).toBeTruthy();
      });

      // Should rollback
      expect(mockStoreActions.setResources).toHaveBeenCalled();
    });
  });

  describe('refetch', () => {
    it('should refetch documents', async () => {
      vi.mocked(libraryApi.listResources).mockResolvedValue({
        resources: mockResources,
        total: 2,
      });

      const { result } = renderHook(() => useDocuments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      vi.mocked(libraryApi.listResources).mockClear();

      await result.current.refetch();

      expect(libraryApi.listResources).toHaveBeenCalled();
    });
  });
});
