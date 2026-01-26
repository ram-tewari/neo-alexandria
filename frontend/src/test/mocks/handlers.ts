/**
 * MSW Request Handlers
 * 
 * Mock API handlers for testing
 */

import { http, HttpResponse } from 'msw';
import type {
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
  SemanticChunk,
  QualityDetails,
  Node2VecSummary,
  GraphConnection,
} from '@/lib/api/editor';
import type {
  Resource,
  ProcessingStatus,
  ChunkingRequest,
  User,
} from '@/types/api';

// Use the production API URL to match the .env file
const API_BASE_URL = 'https://pharos.onrender.com';

// ============================================================================
// Mock Data
// ============================================================================

export const mockUser = {
  id: 'user-123',
  username: 'testuser',
  email: 'test@example.com',
  tier: 'premium' as const,
  is_active: true,
};

export const mockRateLimitStatus = {
  tier: 'premium' as const,
  limit: 1000,
  remaining: 950,
  reset: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
};

export const mockHealthStatus = {
  status: 'healthy' as const,
  message: 'All systems operational',
  timestamp: new Date().toISOString(),
  components: {
    database: { status: 'healthy' as const },
    cache: { status: 'healthy' as const },
    event_bus: { status: 'healthy' as const },
  },
  modules: {
    resources: 'healthy' as const,
    annotations: 'healthy' as const,
    quality: 'healthy' as const,
    search: 'healthy' as const,
    graph: 'healthy' as const,
  },
};

export const mockAnnotations: Annotation[] = [
  {
    id: 'ann-1',
    resource_id: 'resource-1',
    user_id: 'user-123',
    start_offset: 0,
    end_offset: 50,
    highlighted_text: 'function example() {',
    note: 'This is a test annotation',
    tags: ['important', 'review'],
    color: '#ff0000',
    is_shared: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'ann-2',
    resource_id: 'resource-1',
    user_id: 'user-123',
    start_offset: 100,
    end_offset: 150,
    highlighted_text: 'const value = 42;',
    note: 'Magic number',
    tags: ['refactor'],
    color: '#00ff00',
    is_shared: true,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

export const mockChunks: SemanticChunk[] = [
  {
    id: 'chunk-1',
    resource_id: 'resource-1',
    content: 'function example() { return 42; }',
    chunk_index: 0,
    chunk_metadata: {
      function_name: 'example',
      start_line: 1,
      end_line: 3,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'chunk-2',
    resource_id: 'resource-1',
    content: 'class MyClass { constructor() {} }',
    chunk_index: 1,
    chunk_metadata: {
      class_name: 'MyClass',
      start_line: 5,
      end_line: 7,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  },
];

export const mockQualityDetails: QualityDetails = {
  resource_id: 'resource-1',
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.85,
    consistency: 0.95,
    timeliness: 0.8,
    relevance: 0.88,
  },
  quality_overall: 0.876,
  quality_weights: {
    accuracy: 0.3,
    completeness: 0.25,
    consistency: 0.2,
    timeliness: 0.15,
    relevance: 0.1,
  },
  quality_last_computed: '2024-01-01T00:00:00Z',
  is_quality_outlier: false,
  needs_quality_review: false,
};

export const mockNode2VecSummary: Node2VecSummary = {
  symbol: 'example',
  summary: 'A function that returns the answer to everything',
  metadata: {
    type: 'function',
    file: 'example.ts',
  },
};

export const mockGraphConnections: GraphConnection[] = [
  {
    name: 'helper',
    type: 'function',
    relationship: 'calls',
    file: 'utils.ts',
    line: 10,
  },
  {
    name: 'MyClass',
    type: 'class',
    relationship: 'uses',
    file: 'example.ts',
    line: 5,
  },
];

export const mockResource: Resource = {
  id: 'resource-1',
  title: 'example.ts',
  description: 'Example TypeScript file',
  content: `function example() {
  return 42;
}

class MyClass {
  constructor() {}
}`,
  content_type: 'code',
  language: 'typescript',
  file_path: '/src/example.ts',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ingestion_status: 'completed',
  ingestion_started_at: '2024-01-01T00:00:00Z',
  ingestion_completed_at: '2024-01-01T00:00:01Z',
  read_status: 'unread',
  quality_score: 0.876,
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.85,
    consistency: 0.95,
    timeliness: 0.8,
    relevance: 0.88,
  },
};

export const mockProcessingStatus: ProcessingStatus = {
  id: 'resource-1',
  ingestion_status: 'completed',
  ingestion_started_at: '2024-01-01T00:00:00Z',
  ingestion_completed_at: '2024-01-01T00:00:01Z',
};

export const mockResources: Resource[] = [
  mockResource,
  {
    id: 'resource-2',
    title: 'utils.ts',
    description: 'Utility functions',
    content_type: 'code',
    language: 'typescript',
    file_path: '/src/utils.ts',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    ingestion_status: 'completed',
    read_status: 'in_progress',
    quality_score: 0.92,
  },
];

// ============================================================================
// Request Handlers
// ============================================================================

export const handlers = [
  // ==========================================================================
  // Authentication
  // ==========================================================================

  // Get current user
  http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.json(mockUser);
  }),

  // Get rate limit status
  http.get(`${API_BASE_URL}/api/auth/rate-limit`, () => {
    return HttpResponse.json(mockRateLimitStatus);
  }),

  // ==========================================================================
  // Health & Monitoring
  // ==========================================================================

  // Get system health
  http.get(`${API_BASE_URL}/health`, () => {
    return HttpResponse.json(mockHealthStatus);
  }),

  // Get module health
  http.get(`${API_BASE_URL}/health/:module`, ({ params }) => {
    const { module } = params;
    const moduleHealth = mockHealthStatus.modules[module as string] || 'healthy';
    return HttpResponse.json({ status: moduleHealth });
  }),

  // ==========================================================================
  // Resources
  // ==========================================================================

  // List resources
  http.get(`${API_BASE_URL}/resources`, ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    const q = url.searchParams.get('q');
    
    let filtered = [...mockResources];
    
    // Apply search filter
    if (q) {
      filtered = filtered.filter(r => 
        r.title.toLowerCase().includes(q.toLowerCase()) ||
        r.description?.toLowerCase().includes(q.toLowerCase())
      );
    }
    
    const paginated = filtered.slice(offset, offset + limit);
    
    return HttpResponse.json({
      items: paginated,
      total: filtered.length,
    });
  }),

  // Get resource
  http.get(`${API_BASE_URL}/resources/:resourceId`, ({ params }) => {
    const { resourceId } = params;
    
    const resource = mockResources.find(r => r.id === resourceId);
    
    if (!resource) {
      return HttpResponse.json(
        { detail: 'Resource not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(resource);
  }),

  // Get resource status
  http.get(`${API_BASE_URL}/resources/:resourceId/status`, ({ params }) => {
    const { resourceId } = params;
    
    if (resourceId === 'resource-1') {
      return HttpResponse.json(mockProcessingStatus);
    }
    
    return HttpResponse.json(
      { detail: 'Status not found' },
      { status: 404 }
    );
  }),

  // ==========================================================================
  // Annotations
  // ==========================================================================

  // Create annotation
  http.post(`${API_BASE_URL}/annotations`, async ({ request }) => {
    const body = await request.json() as AnnotationCreate & { resource_id: string };
    
    const newAnnotation: Annotation = {
      id: `ann-${Date.now()}`,
      resource_id: body.resource_id,
      user_id: mockUser.id,
      start_offset: body.start_offset,
      end_offset: body.end_offset,
      highlighted_text: body.highlighted_text,
      note: body.note,
      tags: body.tags,
      color: body.color || '#ffeb3b',
      is_shared: false,
      collection_ids: body.collection_ids,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(newAnnotation, { status: 201 });
  }),

  // Get annotations by resource_id
  http.get(`${API_BASE_URL}/annotations`, ({ request }) => {
    const url = new URL(request.url);
    const resourceId = url.searchParams.get('resource_id');
    
    if (!resourceId) {
      return HttpResponse.json({
        items: mockAnnotations,
        total: mockAnnotations.length,
      });
    }
    
    const filtered = mockAnnotations.filter(a => a.resource_id === resourceId);
    return HttpResponse.json({
      items: filtered,
      total: filtered.length,
    });
  }),

  // Legacy: Get annotations for a resource (old endpoint)
  http.get(`${API_BASE_URL}/resources/:resourceId/annotations`, ({ params }) => {
    const { resourceId } = params;
    const filtered = mockAnnotations.filter(a => a.resource_id === resourceId);
    return HttpResponse.json(filtered);
  }),

  // Legacy: Create annotation (old endpoint)
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, async ({ request, params }) => {
    const { resourceId } = params;
    const body = await request.json() as AnnotationCreate;
    
    const newAnnotation: Annotation = {
      id: `ann-${Date.now()}`,
      resource_id: resourceId as string,
      user_id: mockUser.id,
      start_offset: body.start_offset,
      end_offset: body.end_offset,
      highlighted_text: body.highlighted_text,
      note: body.note,
      tags: body.tags,
      color: body.color || '#ffeb3b',
      is_shared: false,
      collection_ids: body.collection_ids,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(newAnnotation, { status: 201 });
  }),

  // Get single annotation
  http.get(`${API_BASE_URL}/annotations/:annotationId`, ({ params }) => {
    const { annotationId } = params;
    const annotation = mockAnnotations.find(a => a.id === annotationId);
    
    if (!annotation) {
      return HttpResponse.json(
        { detail: 'Annotation not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(annotation);
  }),

  // Update annotation
  http.put(`${API_BASE_URL}/annotations/:annotationId`, async ({ request, params }) => {
    const { annotationId } = params;
    const body = await request.json() as AnnotationUpdate;
    const annotation = mockAnnotations.find(a => a.id === annotationId);
    
    if (!annotation) {
      return HttpResponse.json(
        { detail: 'Annotation not found' },
        { status: 404 }
      );
    }
    
    const updated: Annotation = {
      ...annotation,
      ...body,
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(updated);
  }),

  // Delete annotation
  http.delete(`${API_BASE_URL}/annotations/:annotationId`, ({ params }) => {
    const { annotationId } = params;
    const annotation = mockAnnotations.find(a => a.id === annotationId);
    
    if (!annotation) {
      return HttpResponse.json(
        { detail: 'Annotation not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(null, { status: 204 });
  }),

  // Search annotations - fulltext
  http.get(`${API_BASE_URL}/annotations/search/fulltext`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('query') || '';
    
    const results = mockAnnotations.filter(a =>
      a.note?.toLowerCase().includes(query.toLowerCase()) ||
      a.highlighted_text.toLowerCase().includes(query.toLowerCase())
    );
    
    return HttpResponse.json(results);
  }),

  // Search annotations - semantic
  http.get(`${API_BASE_URL}/annotations/search/semantic`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('query') || '';
    
    // For testing, just return all annotations
    // In real implementation, this would use semantic search
    return HttpResponse.json(mockAnnotations);
  }),

  // ==========================================================================
  // Chunks
  // ==========================================================================

  // Get chunks
  http.get(`${API_BASE_URL}/resources/:resourceId/chunks`, ({ params }) => {
    const { resourceId } = params;
    const filtered = mockChunks.filter(c => c.resource_id === resourceId);
    return HttpResponse.json({
      items: filtered,
      total: filtered.length,
    });
  }),

  // Get single chunk
  http.get(`${API_BASE_URL}/chunks/:chunkId`, ({ params }) => {
    const { chunkId } = params;
    const chunk = mockChunks.find(c => c.id === chunkId);
    
    if (!chunk) {
      return HttpResponse.json(
        { detail: 'Chunk not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(chunk);
  }),

  // Trigger chunking
  http.post(`${API_BASE_URL}/resources/:resourceId/chunk`, async ({ request, params }) => {
    const { resourceId } = params;
    const body = await request.json() as ChunkingRequest;
    
    return HttpResponse.json({
      task_id: `task-${Date.now()}`,
      resource_id: resourceId,
      status: 'pending',
      message: 'Chunking task created',
    });
  }),

  // ==========================================================================
  // Quality
  // ==========================================================================

  // Get quality details
  http.get(`${API_BASE_URL}/resources/:resourceId/quality-details`, ({ params }) => {
    const { resourceId } = params;
    
    if (resourceId !== mockQualityDetails.resource_id) {
      return HttpResponse.json(
        { detail: 'Quality data not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(mockQualityDetails);
  }),

  // Recalculate quality
  http.post(`${API_BASE_URL}/quality/recalculate`, async ({ request }) => {
    const body = await request.json() as { resource_id?: string; resource_ids?: string[] };
    
    const count = body.resource_ids ? body.resource_ids.length : 1;
    
    return HttpResponse.json({
      status: 'accepted',
      message: `Quality computation queued for ${count} resource(s)`,
    });
  }),

  // ==========================================================================
  // Quality Analytics
  // ==========================================================================

  // Get quality outliers
  http.get(`${API_BASE_URL}/quality/outliers`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '20');
    
    return HttpResponse.json({
      total: 1,
      page,
      limit,
      outliers: [
        {
          resource_id: 'resource-1',
          title: 'example.ts',
          quality_overall: 0.45,
          outlier_score: 0.95,
          outlier_reasons: ['Low quality score', 'Below threshold'],
          needs_quality_review: true,
        },
      ],
    });
  }),

  // Get quality degradation
  http.get(`${API_BASE_URL}/quality/degradation`, ({ request }) => {
    const url = new URL(request.url);
    const days = parseInt(url.searchParams.get('days') || '30');
    
    return HttpResponse.json({
      time_window_days: days,
      degraded_count: 5,
      degraded_resources: [
        {
          resource_id: 'resource-1',
          title: 'example.ts',
          old_quality: 0.9,
          new_quality: 0.7,
          degradation_pct: -22.2,
        },
      ],
    });
  }),

  // Get quality distribution
  http.get(`${API_BASE_URL}/quality/distribution`, ({ request }) => {
    const url = new URL(request.url);
    const bins = parseInt(url.searchParams.get('bins') || '10');
    const dimension = url.searchParams.get('dimension') || 'overall';
    
    return HttpResponse.json({
      dimension,
      bins,
      distribution: Array.from({ length: bins }, (_, i) => ({
        range: `${(i * 0.1).toFixed(1)}-${((i + 1) * 0.1).toFixed(1)}`,
        count: Math.floor(Math.random() * 10),
      })),
      statistics: {
        mean: 0.75,
        median: 0.78,
        std_dev: 0.12,
      },
    });
  }),

  // Get quality trends
  http.get(`${API_BASE_URL}/quality/trends`, ({ request }) => {
    const url = new URL(request.url);
    const granularity = url.searchParams.get('granularity') || 'daily';
    const dimension = url.searchParams.get('dimension') || 'overall';
    
    return HttpResponse.json({
      dimension,
      granularity,
      data_points: [
        { period: '2024-01-01', avg_quality: 0.75, resource_count: 10 },
        { period: '2024-01-02', avg_quality: 0.78, resource_count: 12 },
        { period: '2024-01-03', avg_quality: 0.76, resource_count: 11 },
      ],
    });
  }),

  // Get quality dimensions
  http.get(`${API_BASE_URL}/quality/dimensions`, () => {
    return HttpResponse.json({
      dimensions: {
        accuracy: { avg: 0.85, min: 0.5, max: 1.0 },
        completeness: { avg: 0.82, min: 0.4, max: 1.0 },
        consistency: { avg: 0.88, min: 0.6, max: 1.0 },
        timeliness: { avg: 0.75, min: 0.3, max: 1.0 },
        relevance: { avg: 0.80, min: 0.5, max: 1.0 },
      },
      overall: { avg: 0.82, min: 0.45, max: 1.0 },
      total_resources: 100,
    });
  }),

  // Get quality review queue
  http.get(`${API_BASE_URL}/quality/review-queue`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const sortBy = url.searchParams.get('sort_by') || 'outlier_score';
    
    return HttpResponse.json({
      total: 1,
      page,
      limit,
      review_queue: [
        {
          resource_id: 'resource-1',
          title: 'example.ts',
          quality_overall: 0.45,
          is_quality_outlier: true,
          outlier_score: 0.95,
          outlier_reasons: ['Quality below threshold'],
          quality_last_computed: '2024-01-01T00:00:00Z',
        },
      ],
    });
  }),

  // ==========================================================================
  // Graph
  // ==========================================================================

  // Get hover info
  http.get(`${API_BASE_URL}/graph/hover`, ({ request }) => {
    const url = new URL(request.url);
    const resourceId = url.searchParams.get('resource_id');
    const filePath = url.searchParams.get('file_path');
    const line = url.searchParams.get('line');
    const column = url.searchParams.get('column');
    
    return HttpResponse.json({
      symbol_name: 'example',
      symbol_type: 'function',
      definition_location: {
        file_path: filePath || '/src/example.ts',
        line: parseInt(line || '1'),
        column: parseInt(column || '0'),
      },
      documentation: 'A function that returns the answer to everything',
      related_chunks: [
        {
          chunk_id: 'chunk-1',
          similarity_score: 0.95,
          preview: 'function example() { return 42; }',
        },
      ],
      context_lines: [
        'function example() {',
        '  return 42;',
        '}',
      ],
    });
  }),

  // Get Node2Vec summary (legacy)
  http.get(`${API_BASE_URL}/graph/node2vec/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json({
      ...mockNode2VecSummary,
      symbol: decodeURIComponent(symbol as string),
    });
  }),

  // Get connections (legacy)
  http.get(`${API_BASE_URL}/graph/connections/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json(mockGraphConnections);
  }),

  // Get hover info (legacy)
  http.get(`${API_BASE_URL}/graph/hover/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json({
      symbol: decodeURIComponent(symbol as string),
      summary: 'A function that does something',
      connections: mockGraphConnections,
      metadata: {
        type: 'function',
        file: 'example.ts',
      },
    });
  }),
];
