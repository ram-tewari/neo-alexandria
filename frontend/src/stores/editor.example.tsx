/**
 * Example Usage: Editor Store with Real Resource Data
 * 
 * This file demonstrates how to use the updated editor store
 * with the useResource hook for real backend integration.
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 5.3 Update editor store to use real resource data
 */

import { useEffect } from 'react';
import { useEditorStore, resourceToCodeFile } from './editor';
import { useResource } from '@/lib/hooks/useEditorData';

// ============================================================================
// Example 1: Basic Resource Loading
// ============================================================================

/**
 * Basic pattern for loading a resource into the editor
 * 
 * Flow:
 * 1. Set active resource ID in store
 * 2. useResource hook fetches data
 * 3. Convert Resource to CodeFile
 * 4. Set active file in store
 */
export function EditorBasicExample({ resourceId }: { resourceId: string }) {
  const { setActiveResource, setActiveFile, activeFile, isLoading, error } = useEditorStore();
  
  // Fetch resource data using TanStack Query hook
  const { data: resource } = useResource(resourceId);
  
  // Set active resource on mount
  useEffect(() => {
    setActiveResource(resourceId);
  }, [resourceId, setActiveResource]);
  
  // Convert and set file when resource loads
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      setActiveFile(codeFile);
    }
  }, [resource, setActiveFile]);
  
  // Render based on state
  if (isLoading) {
    return <div className="editor-loading">Loading resource...</div>;
  }
  
  if (error) {
    return (
      <div className="editor-error">
        <p>Error: {error.message}</p>
      </div>
    );
  }
  
  if (!activeFile) {
    return <div className="editor-empty">No file loaded</div>;
  }
  
  return (
    <div className="editor-container">
      <h3>{activeFile.name}</h3>
      <pre>{activeFile.content}</pre>
    </div>
  );
}

// ============================================================================
// Example 2: With Error Handling and Retry
// ============================================================================

/**
 * Pattern with comprehensive error handling and retry logic
 * 
 * Features:
 * - Syncs hook error to store
 * - Provides retry button
 * - Shows error details
 */
export function EditorWithErrorHandling({ resourceId }: { resourceId: string }) {
  const { setError, setLoading, error, isLoading } = useEditorStore();
  
  // Hook provides error and refetch function
  const { 
    data: resource, 
    error: hookError, 
    isLoading: hookLoading,
    refetch 
  } = useResource(resourceId);
  
  // Sync hook states to store
  useEffect(() => {
    setLoading(hookLoading);
  }, [hookLoading, setLoading]);
  
  useEffect(() => {
    setError(hookError);
  }, [hookError, setError]);
  
  if (error) {
    return (
      <div className="error-container">
        <h3>Failed to Load Resource</h3>
        <p className="error-message">{error.message}</p>
        <button 
          onClick={() => refetch()}
          className="retry-button"
        >
          Retry
        </button>
      </div>
    );
  }
  
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading resource...</p>
      </div>
    );
  }
  
  return (
    <div className="editor-container">
      <pre>{resource?.content}</pre>
    </div>
  );
}

// ============================================================================
// Example 3: Resource Selector with Store Integration
// ============================================================================

/**
 * Pattern for resource selection that triggers loading
 * 
 * Flow:
 * 1. User clicks resource
 * 2. setActiveResource() sets ID and loading state
 * 3. Editor component (separate) uses useResource() to fetch
 */
export function ResourceSelector({ resources }: { resources: Array<{ id: string; title: string }> }) {
  const { setActiveResource, activeResourceId } = useEditorStore();
  
  const handleSelect = (resourceId: string) => {
    // Store automatically sets loading state
    setActiveResource(resourceId);
  };
  
  return (
    <div className="resource-list">
      {resources.map(resource => (
        <button
          key={resource.id}
          onClick={() => handleSelect(resource.id)}
          className={activeResourceId === resource.id ? 'active' : ''}
        >
          {resource.title}
        </button>
      ))}
    </div>
  );
}

// ============================================================================
// Example 4: Editor with Loading Skeleton
// ============================================================================

/**
 * Pattern with skeleton loader for better UX
 * 
 * Features:
 * - Shows skeleton while loading
 * - Smooth transition to content
 * - Maintains layout during load
 */
export function EditorWithSkeleton({ resourceId }: { resourceId: string }) {
  const { activeFile, isLoading } = useEditorStore();
  const { data: resource } = useResource(resourceId);
  
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      useEditorStore.getState().setActiveFile(codeFile);
    }
  }, [resource]);
  
  if (isLoading) {
    return (
      <div className="editor-skeleton">
        <div className="skeleton-header" />
        <div className="skeleton-line" />
        <div className="skeleton-line" />
        <div className="skeleton-line" />
      </div>
    );
  }
  
  return (
    <div className="editor-content">
      {activeFile && (
        <>
          <div className="editor-header">
            <span className="file-name">{activeFile.name}</span>
            <span className="file-language">{activeFile.language}</span>
          </div>
          <pre className="editor-code">{activeFile.content}</pre>
        </>
      )}
    </div>
  );
}

// ============================================================================
// Example 5: Clear Editor on Unmount
// ============================================================================

/**
 * Pattern for cleaning up editor state when component unmounts
 * 
 * Use case: Navigating away from editor page
 */
export function EditorPage() {
  const { clearEditor } = useEditorStore();
  
  // Clear editor state when leaving page
  useEffect(() => {
    return () => {
      clearEditor();
    };
  }, [clearEditor]);
  
  return (
    <div className="editor-page">
      <EditorBasicExample resourceId="resource-1" />
    </div>
  );
}

// ============================================================================
// Example 6: Multiple Resources with Tabs
// ============================================================================

/**
 * Pattern for managing multiple open resources
 * 
 * Features:
 * - Tab-based interface
 * - Preserves scroll position per file
 * - Switches between resources
 */
export function EditorWithTabs({ resourceIds }: { resourceIds: string[] }) {
  const { activeResourceId, setActiveResource, activeFile } = useEditorStore();
  
  const handleTabClick = (resourceId: string) => {
    setActiveResource(resourceId);
  };
  
  return (
    <div className="editor-with-tabs">
      <div className="tabs">
        {resourceIds.map(id => (
          <button
            key={id}
            onClick={() => handleTabClick(id)}
            className={activeResourceId === id ? 'active' : ''}
          >
            Resource {id}
          </button>
        ))}
      </div>
      
      <div className="editor-content">
        {activeResourceId && (
          <EditorBasicExample resourceId={activeResourceId} />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Example 7: Resource Sync Effect (Reusable Component)
// ============================================================================

/**
 * Reusable component that syncs resource data to store
 * 
 * Use case: Separate data fetching from UI rendering
 */
export function ResourceSyncEffect({ resourceId }: { resourceId: string }) {
  const { setActiveFile, setLoading, setError } = useEditorStore();
  const { data: resource, isLoading, error } = useResource(resourceId);
  
  // Sync loading state
  useEffect(() => {
    setLoading(isLoading);
  }, [isLoading, setLoading]);
  
  // Sync error state
  useEffect(() => {
    setError(error);
  }, [error, setError]);
  
  // Sync resource data
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      setActiveFile(codeFile);
    }
  }, [resource, setActiveFile]);
  
  return null; // This component doesn't render anything
}

// Usage:
export function EditorWithSyncEffect({ resourceId }: { resourceId: string }) {
  const { activeFile, isLoading, error } = useEditorStore();
  
  return (
    <>
      <ResourceSyncEffect resourceId={resourceId} />
      
      {isLoading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}
      {activeFile && <pre>{activeFile.content}</pre>}
    </>
  );
}

// ============================================================================
// Example 8: Custom Hook for Editor Integration
// ============================================================================

/**
 * Custom hook that combines store and data fetching
 * 
 * Benefits:
 * - Encapsulates integration logic
 * - Reusable across components
 * - Clean component code
 */
export function useEditorResource(resourceId: string) {
  const { 
    setActiveResource, 
    setActiveFile, 
    setLoading, 
    setError,
    activeFile,
    isLoading,
    error 
  } = useEditorStore();
  
  const { data: resource, error: hookError, isLoading: hookLoading } = useResource(resourceId);
  
  // Set active resource on mount
  useEffect(() => {
    setActiveResource(resourceId);
  }, [resourceId, setActiveResource]);
  
  // Sync hook states to store
  useEffect(() => {
    setLoading(hookLoading);
  }, [hookLoading, setLoading]);
  
  useEffect(() => {
    setError(hookError);
  }, [hookError, setError]);
  
  // Convert and set file when resource loads
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      setActiveFile(codeFile);
    }
  }, [resource, setActiveFile]);
  
  return {
    activeFile,
    isLoading,
    error,
    resource,
  };
}

// Usage:
export function EditorWithCustomHook({ resourceId }: { resourceId: string }) {
  const { activeFile, isLoading, error } = useEditorResource(resourceId);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!activeFile) return <div>No file</div>;
  
  return <pre>{activeFile.content}</pre>;
}

