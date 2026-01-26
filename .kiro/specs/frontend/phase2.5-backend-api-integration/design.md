# Design Document: Phase 2.5 - Backend API Integration

## Overview

Phase 2.5 integrates the frontend components from Phase 1 and Phase 2 with the live backend API. This design focuses on creating a robust API client layer, updating Zustand stores to fetch real data, implementing proper error handling, and ensuring type safety across the frontend-backend boundary.

**Key Design Principles:**
- **Type Safety**: All API interactions are fully typed with TypeScript
- **Error Resilience**: Graceful degradation with retry logic and fallbacks
- **Performance**: Intelligent caching and request deduplication
- **Developer Experience**: Clear error messages and debugging tools
- **Testability**: Comprehensive mocks and integration tests

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Components                        │
│  (WorkbenchLayout, MonacoEditor, AnnotationPanel, etc.)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Zustand Stores                            │
│  (editor, annotation, chunk, quality, workbench, etc.)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  TanStack Query Layer                       │
│         (useQuery, useMutation, queryClient)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Client Layer                         │
│  (axios instance, interceptors, retry logic)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend API (pharos.onrender.com)              │
│  (FastAPI, 90+ endpoints, JWT auth, rate limiting)         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Patterns

**Pattern 1: Simple Read (GET)**
```
Component → useQuery → API Client → Backend → Cache → Component
```

**Pattern 2: Mutation with Optimistic Update (POST/PUT/DELETE)**
```
Component → useMutation → Optimistic Update → API Client → Backend
                                                    ↓
                                              Success/Failure
                                                    ↓
                                          Confirm or Revert Update
```

**Pattern 3: Polling (Status Checks)**
```
Component → useQuery (refetchInterval) → API Client → Backend → Component
```



## Components and Interfaces

### 1. API Client Core (`frontend/src/core/api/client.ts`)

**Purpose**: Central axios instance with interceptors and configuration

**Interface**:
```typescript
// Configuration
interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

// Axios instance with interceptors
export const apiClient: AxiosInstance;

// Helper functions
export function setAuthToken(token: string): void;
export function clearAuthToken(): void;
export function getAuthToken(): string | null;
```

**Key Features**:
- Base URL from environment variable (`VITE_API_BASE_URL`)
- Request interceptor adds JWT token to Authorization header
- Response interceptor handles common errors (401, 403, 429, 500)
- Retry logic with exponential backoff (3 attempts, 1s → 2s → 4s)
- Request/response logging in development mode

### 2. API Client Modules

**Phase 1 API Client** (`frontend/src/lib/api/workbench.ts`):
```typescript
export const workbenchApi = {
  // Auth endpoints
  getCurrentUser: () => Promise<User>,
  getRateLimit: () => Promise<RateLimitStatus>,
  
  // Resource endpoints
  getResources: (params?: ResourceListParams) => Promise<Resource[]>,
  
  // Health endpoints
  getSystemHealth: () => Promise<HealthStatus>,
  getAuthHealth: () => Promise<ModuleHealth>,
  getResourcesHealth: () => Promise<ModuleHealth>,
};
```

**Phase 2 API Client** (`frontend/src/lib/api/editor.ts`):
```typescript
export const editorApi = {
  // Resource content
  getResource: (resourceId: string) => Promise<Resource>,
  getResourceStatus: (resourceId: string) => Promise<ProcessingStatus>,
  
  // Chunks
  getChunks: (resourceId: string) => Promise<SemanticChunk[]>,
  getChunk: (chunkId: string) => Promise<SemanticChunk>,
  triggerChunking: (resourceId: string) => Promise<ChunkingTask>,
  
  // Annotations
  createAnnotation: (resourceId: string, data: AnnotationCreate) => Promise<Annotation>,
  getAnnotations: (resourceId: string) => Promise<Annotation[]>,
  updateAnnotation: (annotationId: string, data: AnnotationUpdate) => Promise<Annotation>,
  deleteAnnotation: (annotationId: string) => Promise<void>,
  searchAnnotationsFulltext: (params: SearchParams) => Promise<Annotation[]>,
  searchAnnotationsSemantic: (params: SearchParams) => Promise<Annotation[]>,
  searchAnnotationsByTags: (tags: string[]) => Promise<Annotation[]>,
  exportAnnotationsMarkdown: (resourceId?: string) => Promise<string>,
  exportAnnotationsJSON: (resourceId?: string) => Promise<AnnotationExport>,
  
  // Quality
  recalculateQuality: (resourceId: string) => Promise<QualityDetails>,
  getQualityOutliers: (params?: PaginationParams) => Promise<QualityOutlier[]>,
  getQualityDegradation: (days: number) => Promise<QualityDegradation>,
  getQualityDistribution: (bins: number) => Promise<QualityDistribution>,
  getQualityTrends: (granularity: 'daily' | 'weekly' | 'monthly') => Promise<QualityTrend[]>,
  getQualityDimensions: () => Promise<QualityDimensionScores>,
  getQualityReviewQueue: (params?: PaginationParams) => Promise<ReviewQueueItem[]>,
  
  // Graph/Hover
  getHoverInfo: (params: HoverParams) => Promise<HoverInfo>,
};
```

### 3. TanStack Query Hooks

**Workbench Hooks** (`frontend/src/lib/hooks/useWorkbenchData.ts`):
```typescript
export function useCurrentUser() {
  return useQuery({
    queryKey: ['user', 'current'],
    queryFn: workbenchApi.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useResources(params?: ResourceListParams) {
  return useQuery({
    queryKey: ['resources', params],
    queryFn: () => workbenchApi.getResources(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['health', 'system'],
    queryFn: workbenchApi.getSystemHealth,
    refetchInterval: 30 * 1000, // Poll every 30 seconds
  });
}
```

**Editor Hooks** (`frontend/src/lib/hooks/useEditorData.ts`):
```typescript
export function useResource(resourceId: string) {
  return useQuery({
    queryKey: ['resource', resourceId],
    queryFn: () => editorApi.getResource(resourceId),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useChunks(resourceId: string) {
  return useQuery({
    queryKey: ['chunks', resourceId],
    queryFn: () => editorApi.getChunks(resourceId),
    staleTime: 10 * 60 * 1000,
  });
}

export function useAnnotations(resourceId: string) {
  return useQuery({
    queryKey: ['annotations', resourceId],
    queryFn: () => editorApi.getAnnotations(resourceId),
    staleTime: 5 * 60 * 1000,
  });
}

// Mutations
export function useCreateAnnotation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ resourceId, data }: { resourceId: string; data: AnnotationCreate }) =>
      editorApi.createAnnotation(resourceId, data),
    onMutate: async ({ resourceId, data }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['annotations', resourceId] });
      const previous = queryClient.getQueryData(['annotations', resourceId]);
      
      queryClient.setQueryData(['annotations', resourceId], (old: Annotation[]) => [
        ...old,
        { ...data, id: 'temp-' + Date.now(), created_at: new Date().toISOString() },
      ]);
      
      return { previous };
    },
    onError: (err, variables, context) => {
      // Revert optimistic update
      queryClient.setQueryData(['annotations', variables.resourceId], context?.previous);
    },
    onSettled: (data, error, variables) => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['annotations', variables.resourceId] });
    },
  });
}
```

### 4. Zustand Store Updates

**Editor Store** (`frontend/src/stores/editor.ts`):
```typescript
interface EditorStore {
  // State
  currentResourceId: string | null;
  content: string | null;
  isLoading: boolean;
  error: Error | null;
  
  // Actions
  loadResource: (resourceId: string) => Promise<void>;
  clearResource: () => void;
  setError: (error: Error | null) => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  currentResourceId: null,
  content: null,
  isLoading: false,
  error: null,
  
  loadResource: async (resourceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const resource = await editorApi.getResource(resourceId);
      set({
        currentResourceId: resourceId,
        content: resource.content,
        isLoading: false,
      });
    } catch (error) {
      set({ error: error as Error, isLoading: false });
    }
  },
  
  clearResource: () => set({ currentResourceId: null, content: null }),
  setError: (error) => set({ error }),
}));
```

**Annotation Store** (`frontend/src/stores/annotation.ts`):
```typescript
interface AnnotationStore {
  // State
  annotations: Map<string, Annotation>;
  selectedAnnotationId: string | null;
  isCreating: boolean;
  
  // Actions (now use TanStack Query mutations)
  selectAnnotation: (id: string | null) => void;
  clearAnnotations: () => void;
}

// Note: CRUD operations moved to TanStack Query hooks
export const useAnnotationStore = create<AnnotationStore>((set) => ({
  annotations: new Map(),
  selectedAnnotationId: null,
  isCreating: false,
  
  selectAnnotation: (id) => set({ selectedAnnotationId: id }),
  clearAnnotations: () => set({ annotations: new Map(), selectedAnnotationId: null }),
}));
```

### 5. TypeScript Type Definitions

**API Types** (`frontend/src/types/api.ts`):
```typescript
// User types
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_premium: boolean;
  tier: 'free' | 'premium' | 'admin';
  created_at: string;
}

// Resource types
export interface Resource {
  id: string;
  title: string;
  content: string;
  content_type: 'code' | 'pdf' | 'markdown' | 'text';
  language?: string;
  file_path?: string;
  url?: string;
  created_at: string;
  updated_at: string;
  quality_overall?: number;
  quality_dimensions?: QualityDimensions;
}

// Annotation types
export interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];
  created_at: string;
  updated_at: string;
}

// Chunk types
export interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: ChunkMetadata;
  embedding_id?: string;
  created_at: string;
}

export interface ChunkMetadata {
  function_name?: string;
  class_name?: string;
  start_line: number;
  end_line: number;
  language: string;
  node_type?: string;
}

// Quality types
export interface QualityDimensions {
  accuracy: number;
  completeness: number;
  consistency: number;
  timeliness: number;
  relevance: number;
}

export interface QualityDetails {
  resource_id: string;
  quality_dimensions: QualityDimensions;
  quality_overall: number;
  quality_weights: QualityDimensions;
  quality_last_computed: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
}

// Error types
export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'VALIDATION_ERROR';

export interface ApiError {
  code: ApiErrorCode;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}
```

