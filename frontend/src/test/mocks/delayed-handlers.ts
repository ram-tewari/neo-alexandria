/**
 * MSW Delayed Response Handlers
 * 
 * Mock handlers with configurable delays for testing loading states
 */

import { http, HttpResponse, delay } from 'msw';
import {
  mockUser,
  mockResources,
  mockResource,
  mockAnnotations,
  mockChunks,
  mockQualityDetails,
  mockProcessingStatus,
  mockRateLimitStatus,
  mockHealthStatus,
} from './handlers';
import type {
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
} from '@/lib/api/editor';

const API_BASE_URL = 'https://pharos.onrender.com';

// ============================================================================
// Configurable Delay Settings
// ============================================================================

/**
 * Default delay times for different operations (in milliseconds)
 */
export const DEFAULT_DELAYS = {
  fast: 100,      // Fast operations (cached data)
  normal: 500,    // Normal operations (typical API calls)
  slow: 2000,     // Slow operations (complex queries)
  verySlow: 5000, // Very slow operations (heavy processing)
};

/**
 * Current delay configuration
 */
let currentDelay = DEFAULT_DELAYS.normal;

/**
 * Set the delay for all delayed handlers
 */
export function setMockDelay(delayMs: number) {
  currentDelay = delayMs;
}

/**
 * Reset delay to default
 */
export function resetMockDelay() {
  currentDelay = DEFAULT_DELAYS.normal;
}

/**
 * Get current delay
 */
export function getCurrentDelay() {
  return currentDelay;
}

// ============================================================================
// Delayed Auth Handlers
// ============================================================================

export const delayedAuthHandlers = [
  // Get current user with delay
  http.get(`${API_BASE_URL}/api/auth/me`, async () => {
    await delay(currentDelay);
    return HttpResponse.json(mockUser);
  }),

  // Get rate limit with delay
  http.get(`${API_BASE_URL}/api/auth/rate-limit`, async () => {
    await delay(currentDelay);
    return HttpResponse.json(mockRateLimitStatus);
  }),
];

// ============================================================================
// Delayed Health Handlers
// ============================================================================

export const delayedHealthHandlers = [
  // Get system health with delay
  http.get(`${API_BASE_URL}/health`, async () => {
    await delay(currentDelay);
    return HttpResponse.json(mockHealthStatus);
  }),

  // Get module health with delay
  http.get(`${API_BASE_URL}/health/:module`, async ({ params }) => {
    await delay(currentDelay);
    const { module } = params;
    const moduleHealth = mockHealthStatus.modules[module as string] || 'healthy';
    return HttpResponse.json({ status: moduleHealth });
  }),
];

// ============================================================================
// Delayed Resource Handlers
// ============================================================================

export const delayedResourceHandlers = [
  // List resources with delay
  http.get(`${API_BASE_URL}/resources`, async ({ request }) => {
    await delay(currentDelay);
    
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    const q = url.searchParams.get('q');
    
    let filtered = [...mockResources];
    
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

  // Get resource with delay
  http.get(`${API_BASE_URL}/resources/:resourceId`, async ({ params }) => {
    await delay(currentDelay);
    
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

  // Get resource status with delay
  http.get(`${API_BASE_URL}/resources/:resourceId/status`, async ({ params }) => {
    await delay(currentDelay);
    
    const { resourceId } = params;
    
    if (resourceId === 'resource-1') {
      return HttpResponse.json(mockProcessingStatus);
    }
    
    return HttpResponse.json(
      { detail: 'Status not found' },
      { status: 404 }
    );
  }),
];

// ============================================================================
// Delayed Annotation Handlers
// ============================================================================

export const delayedAnnotationHandlers = [
  // Create annotation with delay
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, async ({ request, params }) => {
    await delay(currentDelay);
    
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

  // Get annotations with delay
  http.get(`${API_BASE_URL}/resources/:resourceId/annotations`, async ({ params }) => {
    await delay(currentDelay);
    
    const { resourceId } = params;
    const filtered = mockAnnotations.filter(a => a.resource_id === resourceId);
    return HttpResponse.json(filtered);
  }),

  // Get single annotation with delay
  http.get(`${API_BASE_URL}/annotations/:annotationId`, async ({ params }) => {
    await delay(currentDelay);
    
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

  // Update annotation with delay
  http.put(`${API_BASE_URL}/annotations/:annotationId`, async ({ request, params }) => {
    await delay(currentDelay);
    
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

  // Delete annotation with delay
  http.delete(`${API_BASE_URL}/annotations/:annotationId`, async ({ params }) => {
    await delay(currentDelay);
    
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

  // Search annotations with delay
  http.get(`${API_BASE_URL}/annotations/search/fulltext`, async ({ request }) => {
    await delay(currentDelay);
    
    const url = new URL(request.url);
    const query = url.searchParams.get('query') || '';
    
    const results = mockAnnotations.filter(a =>
      a.note?.toLowerCase().includes(query.toLowerCase()) ||
      a.highlighted_text.toLowerCase().includes(query.toLowerCase())
    );
    
    return HttpResponse.json(results);
  }),
];

// ============================================================================
// Delayed Chunk Handlers
// ============================================================================

export const delayedChunkHandlers = [
  // Get chunks with delay
  http.get(`${API_BASE_URL}/resources/:resourceId/chunks`, async ({ params }) => {
    await delay(currentDelay);
    
    const { resourceId } = params;
    const filtered = mockChunks.filter(c => c.resource_id === resourceId);
    return HttpResponse.json({
      items: filtered,
      total: filtered.length,
    });
  }),

  // Get single chunk with delay
  http.get(`${API_BASE_URL}/chunks/:chunkId`, async ({ params }) => {
    await delay(currentDelay);
    
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

  // Trigger chunking with delay
  http.post(`${API_BASE_URL}/resources/:resourceId/chunk`, async ({ params }) => {
    await delay(currentDelay);
    
    const { resourceId } = params;
    
    return HttpResponse.json({
      task_id: `task-${Date.now()}`,
      resource_id: resourceId,
      status: 'pending',
      message: 'Chunking task created',
    });
  }),
];

// ============================================================================
// Delayed Quality Handlers
// ============================================================================

export const delayedQualityHandlers = [
  // Get quality details with delay
  http.get(`${API_BASE_URL}/resources/:resourceId/quality-details`, async ({ params }) => {
    await delay(currentDelay);
    
    const { resourceId } = params;
    
    if (resourceId !== mockQualityDetails.resource_id) {
      return HttpResponse.json(
        { detail: 'Quality data not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(mockQualityDetails);
  }),

  // Recalculate quality with delay
  http.post(`${API_BASE_URL}/quality/recalculate`, async ({ request }) => {
    await delay(currentDelay);
    
    const body = await request.json() as { resource_id?: string; resource_ids?: string[] };
    const count = body.resource_ids ? body.resource_ids.length : 1;
    
    return HttpResponse.json({
      status: 'accepted',
      message: `Quality computation queued for ${count} resource(s)`,
    });
  }),

  // Get quality outliers with delay
  http.get(`${API_BASE_URL}/quality/outliers`, async ({ request }) => {
    await delay(currentDelay);
    
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
];

// ============================================================================
// Delayed Graph Handlers
// ============================================================================

export const delayedGraphHandlers = [
  // Get hover info with delay
  http.get(`${API_BASE_URL}/graph/hover`, async ({ request }) => {
    await delay(currentDelay);
    
    const url = new URL(request.url);
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
];

// ============================================================================
// Combined Delayed Handlers
// ============================================================================

/**
 * All delayed handlers combined
 */
export const allDelayedHandlers = [
  ...delayedAuthHandlers,
  ...delayedHealthHandlers,
  ...delayedResourceHandlers,
  ...delayedAnnotationHandlers,
  ...delayedChunkHandlers,
  ...delayedQualityHandlers,
  ...delayedGraphHandlers,
];

/**
 * Helper to create a delayed handler for any endpoint
 */
export function createDelayedHandler<T>(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
  responseData: T,
  statusCode: number = 200,
  delayMs?: number
) {
  const httpMethod = http[method];
  
  return httpMethod(`${API_BASE_URL}${path}`, async () => {
    await delay(delayMs ?? currentDelay);
    return HttpResponse.json(responseData, { status: statusCode });
  });
}
