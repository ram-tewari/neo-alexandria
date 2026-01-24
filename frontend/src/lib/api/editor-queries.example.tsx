/**
 * TanStack Query Hooks Usage Examples
 * 
 * This file demonstrates how to use the editor query hooks for optimal caching,
 * prefetching, and request deduplication.
 */

import { useEffect } from 'react';
import {
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
  useChunks,
  useQualityDetails,
  usePrefetchChunks,
  usePrefetchQualityDetails,
  usePrefetchEditorData,
  useInvalidateEditorData,
} from './editor-queries';

// ============================================================================
// Example 1: Basic Query Usage with Automatic Caching
// ============================================================================

function AnnotationList({ resourceId }: { resourceId: string }) {
  // This hook automatically:
  // - Caches data for 5 minutes (staleTime)
  // - Keeps cache for 10 minutes (gcTime)
  // - Deduplicates requests (multiple components calling this share one request)
  // - Refetches in background when stale
  const { data: annotations, isLoading, error } = useAnnotations(resourceId);

  if (isLoading) return <div>Loading annotations...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {annotations?.map((annotation) => (
        <li key={annotation.id}>{annotation.highlighted_text}</li>
      ))}
    </ul>
  );
}

// ============================================================================
// Example 2: Request Deduplication
// ============================================================================

function EditorView({ resourceId }: { resourceId: string }) {
  // Both components call useAnnotations with the same resourceId
  // TanStack Query automatically deduplicates these requests into ONE API call
  return (
    <div>
      <AnnotationGutter resourceId={resourceId} />
      <AnnotationPanel resourceId={resourceId} />
    </div>
  );
}

function AnnotationGutter({ resourceId }: { resourceId: string }) {
  const { data: annotations } = useAnnotations(resourceId);
  return <div>Gutter with {annotations?.length} annotations</div>;
}

function AnnotationPanel({ resourceId }: { resourceId: string }) {
  const { data: annotations } = useAnnotations(resourceId);
  return <div>Panel with {annotations?.length} annotations</div>;
}

// ============================================================================
// Example 3: Mutations with Optimistic Updates
// ============================================================================

function CreateAnnotationButton({ resourceId }: { resourceId: string }) {
  const createAnnotation = useCreateAnnotation();

  const handleCreate = async () => {
    try {
      // This mutation:
      // 1. Immediately updates the UI (optimistic update)
      // 2. Sends request to backend
      // 3. Replaces optimistic data with real data on success
      // 4. Rolls back on error
      await createAnnotation.mutateAsync({
        resourceId,
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'Example text',
          note: 'Example note',
        },
      });
    } catch (error) {
      console.error('Failed to create annotation:', error);
    }
  };

  return (
    <button onClick={handleCreate} disabled={createAnnotation.isPending}>
      {createAnnotation.isPending ? 'Creating...' : 'Create Annotation'}
    </button>
  );
}

// ============================================================================
// Example 4: Prefetching for Better Performance
// ============================================================================

function FileTreeItem({ 
  resourceId, 
  fileName 
}: { 
  resourceId: string; 
  fileName: string; 
}) {
  const prefetchChunks = usePrefetchChunks();
  const prefetchQuality = usePrefetchQualityDetails();

  // Prefetch data when user hovers over file
  // This makes the editor feel instant when they click
  const handleMouseEnter = () => {
    prefetchChunks(resourceId);
    prefetchQuality(resourceId);
  };

  return (
    <div onMouseEnter={handleMouseEnter}>
      {fileName}
    </div>
  );
}

// ============================================================================
// Example 5: Prefetch All Editor Data on File Open
// ============================================================================

function CodeEditor({ resourceId }: { resourceId: string }) {
  const prefetchEditorData = usePrefetchEditorData();

  useEffect(() => {
    // Prefetch all editor data in parallel when file opens
    // This loads annotations, chunks, and quality data simultaneously
    prefetchEditorData(resourceId);
  }, [resourceId, prefetchEditorData]);

  // Now when components mount, data is already cached
  const { data: annotations } = useAnnotations(resourceId);
  const { data: chunks } = useChunks(resourceId);
  const { data: quality } = useQualityDetails(resourceId);

  return (
    <div>
      <div>Annotations: {annotations?.length}</div>
      <div>Chunks: {chunks?.length}</div>
      <div>Quality: {quality?.quality_overall}</div>
    </div>
  );
}

// ============================================================================
// Example 6: Conditional Queries (Lazy Loading)
// ============================================================================

function QualityBadges({ resourceId, visible }: { 
  resourceId: string; 
  visible: boolean;
}) {
  // Only fetch quality data when badges are visible
  // This saves bandwidth and API calls
  const { data: quality } = useQualityDetails(resourceId, {
    enabled: visible, // Only run query when visible is true
  });

  if (!visible) return null;

  return (
    <div>
      Quality Score: {quality?.quality_overall}
    </div>
  );
}

// ============================================================================
// Example 7: Error Handling with Fallback
// ============================================================================

function AnnotationsWithFallback({ resourceId }: { resourceId: string }) {
  const { data: annotations, error, isLoading } = useAnnotations(resourceId, {
    // Retry failed requests once
    retry: 1,
    // Show stale data while refetching
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <div>Loading...</div>;

  if (error) {
    // TanStack Query keeps the last successful data in cache
    // So we can show stale data with a warning
    if (annotations) {
      return (
        <div>
          <div className="warning">
            Unable to fetch latest data. Showing cached annotations.
          </div>
          <AnnotationList annotations={annotations} />
        </div>
      );
    }
    return <div>Error: {error.message}</div>;
  }

  return <AnnotationList annotations={annotations || []} />;
}

function AnnotationList({ annotations }: { annotations: any[] }) {
  return <ul>{/* render annotations */}</ul>;
}

// ============================================================================
// Example 8: Manual Cache Invalidation
// ============================================================================

function RefreshButton({ resourceId }: { resourceId: string }) {
  const invalidateEditorData = useInvalidateEditorData();

  const handleRefresh = () => {
    // Force refetch of all editor data
    // Useful after major updates or when user explicitly requests refresh
    invalidateEditorData(resourceId);
  };

  return (
    <button onClick={handleRefresh}>
      Refresh All Data
    </button>
  );
}

// ============================================================================
// Example 9: Combining Multiple Queries
// ============================================================================

function EditorSidebar({ resourceId }: { resourceId: string }) {
  // All three queries run in parallel
  // TanStack Query automatically manages loading states
  const annotationsQuery = useAnnotations(resourceId);
  const chunksQuery = useChunks(resourceId);
  const qualityQuery = useQualityDetails(resourceId);

  // Check if any query is loading
  const isLoading = 
    annotationsQuery.isLoading || 
    chunksQuery.isLoading || 
    qualityQuery.isLoading;

  // Check if any query has error
  const hasError = 
    annotationsQuery.error || 
    chunksQuery.error || 
    qualityQuery.error;

  if (isLoading) return <div>Loading editor data...</div>;
  if (hasError) return <div>Error loading editor data</div>;

  return (
    <div>
      <div>Annotations: {annotationsQuery.data?.length}</div>
      <div>Chunks: {chunksQuery.data?.length}</div>
      <div>Quality: {qualityQuery.data?.quality_overall}</div>
    </div>
  );
}

// ============================================================================
// Example 10: Update and Delete with Optimistic Updates
// ============================================================================

function AnnotationEditor({ 
  annotationId, 
  resourceId 
}: { 
  annotationId: string; 
  resourceId: string;
}) {
  const updateAnnotation = useUpdateAnnotation();
  const deleteAnnotation = useDeleteAnnotation();

  const handleUpdate = async (note: string) => {
    try {
      await updateAnnotation.mutateAsync({
        annotationId,
        data: { note },
      });
    } catch (error) {
      console.error('Failed to update:', error);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteAnnotation.mutateAsync(annotationId);
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  return (
    <div>
      <button onClick={() => handleUpdate('Updated note')}>
        Update
      </button>
      <button onClick={handleDelete}>
        Delete
      </button>
    </div>
  );
}

// ============================================================================
// Performance Benefits Summary
// ============================================================================

/**
 * Benefits of TanStack Query Caching:
 * 
 * 1. **Automatic Request Deduplication**
 *    - Multiple components requesting same data = ONE API call
 *    - Saves bandwidth and reduces server load
 * 
 * 2. **Smart Caching**
 *    - Data cached for configured time (5-30 minutes depending on type)
 *    - Stale data shown immediately while refetching in background
 *    - No loading spinners for cached data
 * 
 * 3. **Optimistic Updates**
 *    - UI updates immediately before API responds
 *    - Automatic rollback on error
 *    - Better perceived performance
 * 
 * 4. **Prefetching**
 *    - Load data before it's needed (on hover, on route change)
 *    - Makes UI feel instant
 *    - Parallel data loading
 * 
 * 5. **Background Refetching**
 *    - Stale data refetched automatically in background
 *    - Always shows latest data without blocking UI
 *    - Configurable staleness per query type
 * 
 * 6. **Memory Management**
 *    - Unused cache automatically garbage collected
 *    - Configurable cache retention time
 *    - No memory leaks
 * 
 * 7. **Error Handling**
 *    - Automatic retries with exponential backoff
 *    - Stale data available during errors
 *    - Graceful degradation
 */
