/**
 * API client for annotation operations
 */

import { apiRequest } from './apiUtils';
import type {
    Annotation,
    AnnotationCreateRequest,
    AnnotationUpdateRequest,
    AnnotationListResponse,
    AnnotationSearchFilters,
    AnnotationSearchResponse,
    SemanticSearchResponse,
    ExportFormat,
    ExportResponse,
} from '../../types/annotations';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================================================
// Resource Annotations
// ============================================================================

/**
 * Get all annotations for a specific resource
 */
export async function getResourceAnnotations(
    resourceId: string
): Promise<Annotation[]> {
    const response = await apiRequest<AnnotationListResponse>(
        `${BASE_URL}/resources/${resourceId}/annotations`
    );
    return response.items;
}

/**
 * Create a new annotation for a resource
 */
export async function createAnnotation(
    resourceId: string,
    data: AnnotationCreateRequest
): Promise<Annotation> {
    return apiRequest<Annotation>(
        `${BASE_URL}/resources/${resourceId}/annotations`,
        {
            method: 'POST',
            body: JSON.stringify(data),
        }
    );
}

// ============================================================================
// Annotation CRUD
// ============================================================================

/**
 * Get a single annotation by ID
 */
export async function getAnnotation(annotationId: string): Promise<Annotation> {
    return apiRequest<Annotation>(`${BASE_URL}/annotations/${annotationId}`);
}

/**
 * Update an existing annotation
 */
export async function updateAnnotation(
    annotationId: string,
    data: AnnotationUpdateRequest
): Promise<Annotation> {
    return apiRequest<Annotation>(`${BASE_URL}/annotations/${annotationId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

/**
 * Delete an annotation
 */
export async function deleteAnnotation(annotationId: string): Promise<void> {
    return apiRequest<void>(`${BASE_URL}/annotations/${annotationId}`, {
        method: 'DELETE',
    });
}

// ============================================================================
// Global Annotation Queries
// ============================================================================

/**
 * Get all annotations with optional filters
 */
export async function getAllAnnotations(
    filters?: AnnotationSearchFilters,
    limit = 50,
    offset = 0
): Promise<AnnotationListResponse> {
    const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
    });

    if (filters) {
        if (filters.resourceId) params.append('resource_id', filters.resourceId);
        if (filters.tags?.length) {
            filters.tags.forEach(tag => params.append('tags', tag));
        }
        if (filters.color) params.append('color', filters.color);
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);
        if (filters.query) params.append('q', filters.query);
    }

    return apiRequest<AnnotationListResponse>(
        `${BASE_URL}/annotations?${params.toString()}`
    );
}

// ============================================================================
// Search
// ============================================================================

/**
 * Full-text search across annotation notes and highlights
 */
export async function searchAnnotations(
    query: string,
    filters?: AnnotationSearchFilters
): Promise<AnnotationSearchResponse> {
    const params = new URLSearchParams({ q: query });

    if (filters) {
        if (filters.resourceId) params.append('resource_id', filters.resourceId);
        if (filters.tags?.length) {
            filters.tags.forEach(tag => params.append('tags', tag));
        }
        if (filters.color) params.append('color', filters.color);
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);
    }

    return apiRequest<AnnotationSearchResponse>(
        `${BASE_URL}/annotations/search/fulltext?${params.toString()}`
    );
}

/**
 * Semantic search for conceptually similar annotations
 */
export async function semanticSearchAnnotations(
    query: string,
    filters?: AnnotationSearchFilters,
    limit = 20
): Promise<SemanticSearchResponse> {
    const params = new URLSearchParams({
        q: query,
        limit: limit.toString(),
    });

    if (filters) {
        if (filters.resourceId) params.append('resource_id', filters.resourceId);
        if (filters.tags?.length) {
            filters.tags.forEach(tag => params.append('tags', tag));
        }
    }

    return apiRequest<SemanticSearchResponse>(
        `${BASE_URL}/annotations/search/semantic?${params.toString()}`
    );
}

// ============================================================================
// Export
// ============================================================================

/**
 * Export annotations in specified format
 */
export async function exportAnnotations(
    format: ExportFormat,
    filters?: AnnotationSearchFilters
): Promise<ExportResponse> {
    const params = new URLSearchParams();

    if (filters) {
        if (filters.resourceId) params.append('resource_id', filters.resourceId);
        if (filters.tags?.length) {
            filters.tags.forEach(tag => params.append('tags', tag));
        }
        if (filters.color) params.append('color', filters.color);
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);
    }

    const endpoint =
        format === 'markdown'
            ? '/annotations/export/markdown'
            : '/annotations/export/json';

    const queryString = params.toString();
    const url = queryString
        ? `${BASE_URL}${endpoint}?${queryString}`
        : `${BASE_URL}${endpoint}`;

    const response = await apiRequest<{ content: string }>(url);

    return {
        content: response.content,
        filename: `annotations-${new Date().toISOString().split('T')[0]}.${format === 'markdown' ? 'md' : 'json'}`,
        mimeType: format === 'markdown' ? 'text/markdown' : 'application/json',
    };
}

// ============================================================================
// Mock Data (for development when backend is not available)
// ============================================================================

const MOCK_ENABLED = import.meta.env.VITE_USE_MOCK_DATA === 'true';

if (MOCK_ENABLED) {
    console.warn('🎭 Annotations API: Using mock data');
}
