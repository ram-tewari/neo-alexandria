# Phase 3: Living Library - Technical Design

## Architecture Overview

Phase 3 implements a document management system with PDF viewing, scholarly asset extraction, and intelligent linking capabilities. The architecture follows the established patterns from Phase 2.5 with API integration, state management, and comprehensive testing.

## Component Architecture

```
frontend/src/
├── features/library/                    # Library feature components
│   ├── DocumentGrid.tsx                 # Main grid view
│   ├── DocumentCard.tsx                 # Individual document card
│   ├── DocumentUpload.tsx               # Upload interface
│   ├── DocumentFilters.tsx              # Filter controls
│   ├── PDFViewer.tsx                    # PDF viewing component
│   ├── PDFToolbar.tsx                   # Zoom, navigation controls
│   ├── PDFHighlighter.tsx               # Text highlighting
│   ├── EquationDrawer.tsx               # Equation panel
│   ├── TableDrawer.tsx                  # Table panel
│   ├── MetadataPanel.tsx                # Metadata display/edit
│   ├── RelatedCodePanel.tsx             # Auto-linked code files
│   ├── RelatedPapersPanel.tsx           # Auto-linked papers
│   ├── CollectionManager.tsx            # Collection CRUD
│   ├── CollectionPicker.tsx             # Collection selection dialog
│   ├── CollectionStats.tsx              # Statistics dashboard
│   ├── BatchOperations.tsx              # Batch action toolbar
│   └── __tests__/                       # Component tests
├── lib/api/                             # API client layer
│   ├── library.ts                       # Library API functions
│   ├── scholarly.ts                     # Scholarly API functions
│   ├── collections.ts                   # Collections API functions
│   └── __tests__/                       # API tests
├── lib/hooks/                           # Custom React hooks
│   ├── useDocuments.ts                  # Document data hook
│   ├── usePDFViewer.ts                  # PDF viewer hook
│   ├── useScholarlyAssets.ts            # Equations/tables hook
│   ├── useCollections.ts                # Collections hook
│   ├── useAutoLinking.ts                # Auto-linking hook
│   └── __tests__/                       # Hook tests
├── stores/                              # Zustand stores
│   ├── library.ts                       # Library state
│   ├── pdfViewer.ts                     # PDF viewer state
│   ├── collections.ts                   # Collections state
│   └── __tests__/                       # Store tests
└── types/                               # TypeScript types
    └── library.ts                       # Library type definitions
```

## Data Flow

### Document Upload Flow
```
User selects file
  → DocumentUpload component
  → uploadResource() API call
  → POST /resources with multipart/form-data
  → Backend processes file
  → Response with resource ID
  → Optimistic update to library store
  → Redirect to document view
  → Background: scholarly extraction starts
```

### PDF Viewing Flow
```
User clicks document card
  → Navigate to /library/:resourceId
  → PDFViewer component mounts
  → useDocuments() hook fetches resource
  → GET /resources/{resource_id}
  → PDF URL loaded into react-pdf
  → Parallel: fetch equations, tables, metadata
  → Display PDF with overlays
```

### Auto-Linking Flow
```
User opens document
  → useAutoLinking() hook activates
  → Fetch resource embeddings
  → Calculate similarity with other resources
  → Display suggestions in panels
  → User clicks suggestion
  → Navigate to related resource
```

### Collection Management Flow
```
User creates collection
  → CollectionManager form
  → createCollection() API call
  → POST /collections
  → Optimistic update to collections store
  → Success notification
  → Collection appears in list
```

## API Integration Layer

### Library API (`lib/api/library.ts`)

```typescript
import { apiClient } from '@/core/api/client';
import type { Resource, ResourceUpload, ResourceUpdate } from '@/types/library';

export const libraryApi = {
  // Upload resource
  uploadResource: async (file: File, metadata?: Partial<Resource>) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    return apiClient.post<Resource>('/resources', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        // Emit progress events for UI
      }
    });
  },

  // List resources
  listResources: async (params?: {
    type?: string;
    quality_min?: number;
    quality_max?: number;
    limit?: number;
    offset?: number;
  }) => {
    return apiClient.get<{ resources: Resource[]; total: number }>('/resources', {
      params
    });
  },

  // Get resource
  getResource: async (resourceId: string) => {
    return apiClient.get<Resource>(`/resources/${resourceId}`);
  },

  // Update resource
  updateResource: async (resourceId: string, updates: ResourceUpdate) => {
    return apiClient.put<Resource>(`/resources/${resourceId}`, updates);
  },

  // Delete resource
  deleteResource: async (resourceId: string) => {
    return apiClient.delete(`/resources/${resourceId}`);
  },

  // Ingest repository
  ingestRepository: async (repoUrl: string, branch?: string) => {
    return apiClient.post<{ job_id: string; status: string }>('/resources/ingest-repo', {
      repo_url: repoUrl,
      branch
    });
  }
};
```

### Scholarly API (`lib/api/scholarly.ts`)

```typescript
import { apiClient } from '@/core/api/client';
import type { Equation, Table, Metadata, CompletenessStats } from '@/types/library';

export const scholarlyApi = {
  // Get equations
  getEquations: async (resourceId: string) => {
    return apiClient.get<Equation[]>(`/scholarly/resources/${resourceId}/equations`);
  },

  // Get tables
  getTables: async (resourceId: string) => {
    return apiClient.get<Table[]>(`/scholarly/resources/${resourceId}/tables`);
  },

  // Get metadata
  getMetadata: async (resourceId: string) => {
    return apiClient.get<Metadata>(`/scholarly/metadata/${resourceId}`);
  },

  // Get completeness stats
  getCompletenessStats: async () => {
    return apiClient.get<CompletenessStats>('/scholarly/metadata/completeness-stats');
  },

  // Health check
  health: async () => {
    return apiClient.get('/scholarly/health');
  }
};
```

### Collections API (`lib/api/collections.ts`)

```typescript
import { apiClient } from '@/core/api/client';
import type { Collection, CollectionCreate, CollectionUpdate } from '@/types/library';

export const collectionsApi = {
  // Create collection
  createCollection: async (data: CollectionCreate) => {
    return apiClient.post<Collection>('/collections', data);
  },

  // List collections
  listCollections: async (params?: { limit?: number; offset?: number }) => {
    return apiClient.get<{ collections: Collection[]; total: number }>('/collections', {
      params
    });
  },

  // Get collection
  getCollection: async (collectionId: string) => {
    return apiClient.get<Collection>(`/collections/${collectionId}`);
  },

  // Update collection
  updateCollection: async (collectionId: string, updates: CollectionUpdate) => {
    return apiClient.put<Collection>(`/collections/${collectionId}`, updates);
  },

  // Delete collection
  deleteCollection: async (collectionId: string) => {
    return apiClient.delete(`/collections/${collectionId}`);
  },

  // List collection resources
  getCollectionResources: async (collectionId: string, params?: { limit?: number; offset?: number }) => {
    return apiClient.get<{ resources: Resource[]; total: number }>(
      `/collections/${collectionId}/resources`,
      { params }
    );
  },

  // Add resource to collection
  addResourceToCollection: async (collectionId: string, resourceId: string) => {
    return apiClient.put<Collection>(`/collections/${collectionId}/resources`, {
      resource_id: resourceId
    });
  },

  // Find similar collections
  findSimilarCollections: async (collectionId: string, limit?: number) => {
    return apiClient.get<Array<{ collection: Collection; similarity: number }>>(
      `/collections/${collectionId}/similar-collections`,
      { params: { limit } }
    );
  },

  // Batch add resources
  batchAddResources: async (collectionId: string, resourceIds: string[]) => {
    return apiClient.post<{ added: number; failed: string[] }>(
      `/collections/${collectionId}/resources/batch`,
      { resource_ids: resourceIds }
    );
  },

  // Batch remove resources
  batchRemoveResources: async (collectionId: string, resourceIds: string[]) => {
    return apiClient.delete<{ removed: number; failed: string[] }>(
      `/collections/${collectionId}/resources/batch`,
      { data: { resource_ids: resourceIds } }
    );
  },

  // Health check
  health: async () => {
    return apiClient.get('/collections/health');
  }
};
```

## State Management

### Library Store (`stores/library.ts`)

```typescript
import { create } from 'zustand';
import type { Resource } from '@/types/library';

interface LibraryState {
  // State
  resources: Resource[];
  selectedResource: Resource | null;
  filters: {
    type?: string;
    qualityMin?: number;
    qualityMax?: number;
    search?: string;
  };
  sortBy: 'date' | 'title' | 'quality';
  sortOrder: 'asc' | 'desc';
  
  // Actions
  setResources: (resources: Resource[]) => void;
  addResource: (resource: Resource) => void;
  updateResource: (id: string, updates: Partial<Resource>) => void;
  removeResource: (id: string) => void;
  selectResource: (resource: Resource | null) => void;
  setFilters: (filters: Partial<LibraryState['filters']>) => void;
  setSorting: (sortBy: LibraryState['sortBy'], sortOrder: LibraryState['sortOrder']) => void;
  clearFilters: () => void;
}

export const useLibraryStore = create<LibraryState>((set) => ({
  resources: [],
  selectedResource: null,
  filters: {},
  sortBy: 'date',
  sortOrder: 'desc',
  
  setResources: (resources) => set({ resources }),
  
  addResource: (resource) => set((state) => ({
    resources: [resource, ...state.resources]
  })),
  
  updateResource: (id, updates) => set((state) => ({
    resources: state.resources.map((r) =>
      r.id === id ? { ...r, ...updates } : r
    )
  })),
  
  removeResource: (id) => set((state) => ({
    resources: state.resources.filter((r) => r.id !== id)
  })),
  
  selectResource: (resource) => set({ selectedResource: resource }),
  
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),
  
  setSorting: (sortBy, sortOrder) => set({ sortBy, sortOrder }),
  
  clearFilters: () => set({ filters: {} })
}));
```

### PDF Viewer Store (`stores/pdfViewer.ts`)

```typescript
import { create } from 'zustand';

interface PDFViewerState {
  // State
  currentPage: number;
  totalPages: number;
  zoom: number;
  highlights: Array<{
    id: string;
    pageNumber: number;
    position: { x: number; y: number; width: number; height: number };
    color: string;
    text: string;
  }>;
  
  // Actions
  setCurrentPage: (page: number) => void;
  setTotalPages: (total: number) => void;
  setZoom: (zoom: number) => void;
  addHighlight: (highlight: PDFViewerState['highlights'][0]) => void;
  removeHighlight: (id: string) => void;
  clearHighlights: () => void;
}

export const usePDFViewerStore = create<PDFViewerState>((set) => ({
  currentPage: 1,
  totalPages: 0,
  zoom: 1.0,
  highlights: [],
  
  setCurrentPage: (page) => set({ currentPage: page }),
  setTotalPages: (total) => set({ totalPages: total }),
  setZoom: (zoom) => set({ zoom }),
  
  addHighlight: (highlight) => set((state) => ({
    highlights: [...state.highlights, highlight]
  })),
  
  removeHighlight: (id) => set((state) => ({
    highlights: state.highlights.filter((h) => h.id !== id)
  })),
  
  clearHighlights: () => set({ highlights: [] })
}));
```

### Collections Store (`stores/collections.ts`)

```typescript
import { create } from 'zustand';
import type { Collection } from '@/types/library';

interface CollectionsState {
  // State
  collections: Collection[];
  selectedCollection: Collection | null;
  selectedResourceIds: Set<string>;
  
  // Actions
  setCollections: (collections: Collection[]) => void;
  addCollection: (collection: Collection) => void;
  updateCollection: (id: string, updates: Partial<Collection>) => void;
  removeCollection: (id: string) => void;
  selectCollection: (collection: Collection | null) => void;
  toggleResourceSelection: (resourceId: string) => void;
  clearSelection: () => void;
  selectAll: (resourceIds: string[]) => void;
}

export const useCollectionsStore = create<CollectionsState>((set) => ({
  collections: [],
  selectedCollection: null,
  selectedResourceIds: new Set(),
  
  setCollections: (collections) => set({ collections }),
  
  addCollection: (collection) => set((state) => ({
    collections: [collection, ...state.collections]
  })),
  
  updateCollection: (id, updates) => set((state) => ({
    collections: state.collections.map((c) =>
      c.id === id ? { ...c, ...updates } : c
    )
  })),
  
  removeCollection: (id) => set((state) => ({
    collections: state.collections.filter((c) => c.id !== id)
  })),
  
  selectCollection: (collection) => set({ selectedCollection: collection }),
  
  toggleResourceSelection: (resourceId) => set((state) => {
    const newSelection = new Set(state.selectedResourceIds);
    if (newSelection.has(resourceId)) {
      newSelection.delete(resourceId);
    } else {
      newSelection.add(resourceId);
    }
    return { selectedResourceIds: newSelection };
  }),
  
  clearSelection: () => set({ selectedResourceIds: new Set() }),
  
  selectAll: (resourceIds) => set({ selectedResourceIds: new Set(resourceIds) })
}));
```

## Custom Hooks

### useDocuments Hook

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryApi } from '@/lib/api/library';
import { useLibraryStore } from '@/stores/library';

export function useDocuments(params?: {
  type?: string;
  quality_min?: number;
  quality_max?: number;
}) {
  const queryClient = useQueryClient();
  const { setResources, addResource, updateResource, removeResource } = useLibraryStore();
  
  // Fetch documents
  const { data, isLoading, error } = useQuery({
    queryKey: ['documents', params],
    queryFn: () => libraryApi.listResources(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    onSuccess: (data) => {
      setResources(data.resources);
    }
  });
  
  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => libraryApi.uploadResource(file),
    onMutate: async (file) => {
      // Optimistic update
      const tempResource = {
        id: `temp-${Date.now()}`,
        title: file.name,
        type: 'pdf',
        status: 'uploading'
      };
      addResource(tempResource as any);
      return { tempResource };
    },
    onSuccess: (data, variables, context) => {
      // Replace temp with real resource
      removeResource(context.tempResource.id);
      addResource(data);
      queryClient.invalidateQueries(['documents']);
    },
    onError: (error, variables, context) => {
      // Remove temp resource on error
      if (context) {
        removeResource(context.tempResource.id);
      }
    }
  });
  
  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (resourceId: string) => libraryApi.deleteResource(resourceId),
    onMutate: async (resourceId) => {
      // Optimistic update
      const previousResources = queryClient.getQueryData(['documents', params]);
      removeResource(resourceId);
      return { previousResources };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousResources) {
        setResources((context.previousResources as any).resources);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['documents']);
    }
  });
  
  return {
    documents: data?.resources || [],
    total: data?.total || 0,
    isLoading,
    error,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isLoading,
    isDeleting: deleteMutation.isLoading
  };
}
```

### useScholarlyAssets Hook

```typescript
import { useQuery } from '@tanstack/react-query';
import { scholarlyApi } from '@/lib/api/scholarly';

export function useScholarlyAssets(resourceId: string) {
  const equations = useQuery({
    queryKey: ['equations', resourceId],
    queryFn: () => scholarlyApi.getEquations(resourceId),
    staleTime: 30 * 60 * 1000, // 30 minutes
    enabled: !!resourceId
  });
  
  const tables = useQuery({
    queryKey: ['tables', resourceId],
    queryFn: () => scholarlyApi.getTables(resourceId),
    staleTime: 30 * 60 * 1000,
    enabled: !!resourceId
  });
  
  const metadata = useQuery({
    queryKey: ['metadata', resourceId],
    queryFn: () => scholarlyApi.getMetadata(resourceId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!resourceId
  });
  
  return {
    equations: equations.data || [],
    tables: tables.data || [],
    metadata: metadata.data,
    isLoadingEquations: equations.isLoading,
    isLoadingTables: tables.isLoading,
    isLoadingMetadata: metadata.isLoading,
    hasEquations: (equations.data?.length || 0) > 0,
    hasTables: (tables.data?.length || 0) > 0
  };
}
```

### useCollections Hook

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { collectionsApi } from '@/lib/api/collections';
import { useCollectionsStore } from '@/stores/collections';

export function useCollections() {
  const queryClient = useQueryClient();
  const { setCollections, addCollection, updateCollection, removeCollection } = useCollectionsStore();
  
  // Fetch collections
  const { data, isLoading, error } = useQuery({
    queryKey: ['collections'],
    queryFn: () => collectionsApi.listCollections(),
    staleTime: 5 * 60 * 1000,
    onSuccess: (data) => {
      setCollections(data.collections);
    }
  });
  
  // Create mutation
  const createMutation = useMutation({
    mutationFn: collectionsApi.createCollection,
    onMutate: async (newCollection) => {
      const tempCollection = {
        id: `temp-${Date.now()}`,
        ...newCollection,
        resource_count: 0
      };
      addCollection(tempCollection as any);
      return { tempCollection };
    },
    onSuccess: (data, variables, context) => {
      removeCollection(context.tempCollection.id);
      addCollection(data);
      queryClient.invalidateQueries(['collections']);
    },
    onError: (error, variables, context) => {
      if (context) {
        removeCollection(context.tempCollection.id);
      }
    }
  });
  
  // Batch add mutation
  const batchAddMutation = useMutation({
    mutationFn: ({ collectionId, resourceIds }: { collectionId: string; resourceIds: string[] }) =>
      collectionsApi.batchAddResources(collectionId, resourceIds),
    onSuccess: () => {
      queryClient.invalidateQueries(['collections']);
    }
  });
  
  return {
    collections: data?.collections || [],
    total: data?.total || 0,
    isLoading,
    error,
    createCollection: createMutation.mutate,
    batchAddResources: batchAddMutation.mutate,
    isCreating: createMutation.isLoading,
    isBatchAdding: batchAddMutation.isLoading
  };
}
```

## Component Design

### DocumentGrid Component

```typescript
interface DocumentGridProps {
  filters?: {
    type?: string;
    qualityMin?: number;
    qualityMax?: number;
  };
  onDocumentClick?: (resource: Resource) => void;
}

export function DocumentGrid({ filters, onDocumentClick }: DocumentGridProps) {
  const { documents, isLoading, deleteDocument } = useDocuments(filters);
  const { selectedResourceIds, toggleResourceSelection } = useCollectionsStore();
  
  if (isLoading) {
    return <DocumentGridSkeleton />;
  }
  
  if (documents.length === 0) {
    return <EmptyState />;
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          isSelected={selectedResourceIds.has(doc.id)}
          onSelect={() => toggleResourceSelection(doc.id)}
          onClick={() => onDocumentClick?.(doc)}
          onDelete={() => deleteDocument(doc.id)}
        />
      ))}
    </div>
  );
}
```

### PDFViewer Component

```typescript
interface PDFViewerProps {
  resourceId: string;
}

export function PDFViewer({ resourceId }: PDFViewerProps) {
  const { data: resource } = useQuery({
    queryKey: ['resource', resourceId],
    queryFn: () => libraryApi.getResource(resourceId)
  });
  
  const { equations, tables, metadata } = useScholarlyAssets(resourceId);
  const { currentPage, totalPages, zoom, setCurrentPage, setTotalPages, setZoom } = usePDFViewerStore();
  
  return (
    <div className="flex h-screen">
      {/* PDF Canvas */}
      <div className="flex-1 overflow-auto">
        <Document
          file={resource?.url}
          onLoadSuccess={({ numPages }) => setTotalPages(numPages)}
        >
          <Page
            pageNumber={currentPage}
            scale={zoom}
            renderTextLayer
            renderAnnotationLayer
          />
        </Document>
      </div>
      
      {/* Side Panels */}
      <div className="w-80 border-l">
        <Tabs defaultValue="equations">
          <TabsList>
            <TabsTrigger value="equations">Equations ({equations.length})</TabsTrigger>
            <TabsTrigger value="tables">Tables ({tables.length})</TabsTrigger>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>
          
          <TabsContent value="equations">
            <EquationDrawer equations={equations} />
          </TabsContent>
          
          <TabsContent value="tables">
            <TableDrawer tables={tables} />
          </TabsContent>
          
          <TabsContent value="metadata">
            <MetadataPanel metadata={metadata} />
          </TabsContent>
        </Tabs>
      </div>
      
      {/* Toolbar */}
      <PDFToolbar
        currentPage={currentPage}
        totalPages={totalPages}
        zoom={zoom}
        onPageChange={setCurrentPage}
        onZoomChange={setZoom}
      />
    </div>
  );
}
```

## Testing Strategy

### Unit Tests
- API client functions
- Store actions and selectors
- Custom hooks
- Utility functions

### Integration Tests
- Document upload workflow
- PDF viewing with scholarly assets
- Collection management
- Batch operations
- Auto-linking suggestions

### Property-Based Tests
- Optimistic updates consistency
- Cache invalidation correctness
- Filter/sort combinations
- Batch operation atomicity

### E2E Tests
- Complete document lifecycle
- PDF annotation workflow
- Collection organization
- Search and discovery

## Performance Optimizations

1. **Virtual Scrolling**: Use react-window for large document grids
2. **Image Optimization**: Lazy load thumbnails, use WebP format
3. **PDF Rendering**: Render only visible pages, cache rendered pages
4. **Query Caching**: Aggressive caching with TanStack Query
5. **Debouncing**: Search input, filter changes
6. **Code Splitting**: Lazy load PDF viewer and heavy components
7. **Memoization**: React.memo for expensive components

## Error Handling

1. **Upload Errors**: Show progress, handle network failures, retry logic
2. **PDF Loading Errors**: Fallback to download link
3. **API Errors**: Toast notifications, retry with exponential backoff
4. **Validation Errors**: Inline form validation
5. **Network Errors**: Offline mode with cached data

## Accessibility

1. **Keyboard Navigation**: Tab order, arrow keys for grid
2. **Screen Readers**: ARIA labels, live regions for updates
3. **Focus Management**: Focus trapping in modals
4. **Color Contrast**: WCAG AA compliance
5. **Alt Text**: Descriptive text for all images

## Security Considerations

1. **File Upload**: Validate file types, size limits, scan for malware
2. **XSS Prevention**: Sanitize user input, use DOMPurify
3. **CSRF Protection**: CSRF tokens for mutations
4. **Authentication**: JWT tokens, refresh token rotation
5. **Authorization**: Check permissions before operations

## Dependencies

### New Dependencies
- `react-pdf` - PDF rendering
- `pdfjs-dist` - PDF.js library
- `katex` - LaTeX equation rendering
- `react-katex` - React wrapper for KaTeX
- `react-window` - Virtual scrolling
- `react-dropzone` - File upload

### Existing Dependencies
- `@tanstack/react-query` - Data fetching
- `zustand` - State management
- `axios` - HTTP client
- `zod` - Schema validation
- `framer-motion` - Animations

## Migration Path

1. Create API client layer
2. Implement stores
3. Build custom hooks
4. Create base components
5. Integrate with existing workbench
6. Add tests
7. Performance optimization
8. Accessibility audit
