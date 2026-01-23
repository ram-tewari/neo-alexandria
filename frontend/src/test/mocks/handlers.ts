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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Mock Data
// ============================================================================

export const mockAnnotations: Annotation[] = [
  {
    id: 'ann-1',
    resource_id: 'resource-1',
    user_id: 'user-1',
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
    user_id: 'user-1',
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

// ============================================================================
// Request Handlers
// ============================================================================

export const handlers = [
  // ==========================================================================
  // Annotations
  // ==========================================================================

  // Create annotation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, async ({ request, params }) => {
    const { resourceId } = params;
    const body = await request.json() as AnnotationCreate;
    
    const newAnnotation: Annotation = {
      id: `ann-${Date.now()}`,
      resource_id: resourceId as string,
      user_id: 'user-1',
      start_offset: body.start_offset,
      end_offset: body.end_offset,
      highlighted_text: body.highlighted_text,
      note: body.note,
      tags: body.tags,
      color: body.color || '#000000',
      is_shared: false,
      collection_ids: body.collection_ids,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(newAnnotation, { status: 201 });
  }),

  // Get annotations
  http.get(`${API_BASE_URL}/resources/:resourceId/annotations`, ({ params }) => {
    const { resourceId } = params;
    const filtered = mockAnnotations.filter(a => a.resource_id === resourceId);
    return HttpResponse.json(filtered);
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
    return HttpResponse.json(filtered);
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
  http.post(`${API_BASE_URL}/resources/:resourceId/chunks`, ({ params }) => {
    const { resourceId } = params;
    return HttpResponse.json({
      message: 'Chunking triggered',
      task_id: `task-${Date.now()}`,
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
    const body = await request.json() as { resource_id: string };
    
    if (body.resource_id !== mockQualityDetails.resource_id) {
      return HttpResponse.json(
        { detail: 'Resource not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(mockQualityDetails);
  }),

  // ==========================================================================
  // Graph (Placeholder)
  // ==========================================================================

  // Get Node2Vec summary
  http.get(`${API_BASE_URL}/graph/node2vec/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json({
      ...mockNode2VecSummary,
      symbol: decodeURIComponent(symbol as string),
    });
  }),

  // Get connections
  http.get(`${API_BASE_URL}/graph/connections/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json(mockGraphConnections);
  }),
];
