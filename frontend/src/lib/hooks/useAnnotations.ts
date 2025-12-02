/**
 * React Query hooks for annotation operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getResourceAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    getAllAnnotations,
    searchAnnotations,
    semanticSearchAnnotations,
} from '../api/annotations';
import type {
    Annotation,
    AnnotationCreateRequest,
    AnnotationUpdateRequest,
    AnnotationSearchFilters,
} from '../../types/annotations';

// ============================================================================
// Query Keys
// ============================================================================

export const annotationKeys = {
    all: ['annotations'] as const,
    lists: () => [...annotationKeys.all, 'list'] as const,
    list: (filters?: AnnotationSearchFilters) =>
        [...annotationKeys.lists(), filters] as const,
    resource: (resourceId: string) =>
        [...annotationKeys.all, 'resource', resourceId] as const,
    search: (query: string, filters?: AnnotationSearchFilters) =>
        [...annotationKeys.all, 'search', query, filters] as const,
    semantic: (query: string, filters?: AnnotationSearchFilters) =>
        [...annotationKeys.all, 'semantic', query, filters] as const,
};

// ============================================================================
// Queries
// ============================================================================

/**
 * Get all annotations for a specific resource
 */
export function useResourceAnnotations(resourceId: string) {
    return useQuery({
        queryKey: annotationKeys.resource(resourceId),
        queryFn: () => getResourceAnnotations(resourceId),
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}

/**
 * Get all annotations with optional filters
 */
export function useAllAnnotations(
    filters?: AnnotationSearchFilters,
    limit?: number,
    offset?: number
) {
    return useQuery({
        queryKey: annotationKeys.list(filters),
        queryFn: () => getAllAnnotations(filters, limit, offset),
        staleTime: 1000 * 60 * 2, // 2 minutes
    });
}

/**
 * Full-text search annotations
 */
export function useSearchAnnotations(
    query: string,
    filters?: AnnotationSearchFilters,
    enabled = true
) {
    return useQuery({
        queryKey: annotationKeys.search(query, filters),
        queryFn: () => searchAnnotations(query, filters),
        enabled: enabled && query.length > 0,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}

/**
 * Semantic search annotations
 */
export function useSemanticSearch(
    query: string,
    filters?: AnnotationSearchFilters,
    enabled = true
) {
    return useQuery({
        queryKey: annotationKeys.semantic(query, filters),
        queryFn: () => semanticSearchAnnotations(query, filters),
        enabled: enabled && query.length > 0,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}

// ============================================================================
// Mutations
// ============================================================================

/**
 * Create a new annotation
 */
export function useCreateAnnotation(resourceId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: AnnotationCreateRequest) =>
            createAnnotation(resourceId, data),
        onSuccess: (newAnnotation) => {
            // Invalidate resource annotations
            queryClient.invalidateQueries({
                queryKey: annotationKeys.resource(resourceId),
            });
            // Invalidate all annotations list
            queryClient.invalidateQueries({
                queryKey: annotationKeys.lists(),
            });

            // Optimistically add to cache
            queryClient.setQueryData<Annotation[]>(
                annotationKeys.resource(resourceId),
                (old = []) => [...old, newAnnotation]
            );
        },
    });
}

/**
 * Update an existing annotation
 */
export function useUpdateAnnotation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            annotationId,
            data,
        }: {
            annotationId: string;
            data: AnnotationUpdateRequest;
        }) => updateAnnotation(annotationId, data),
        onSuccess: (updatedAnnotation) => {
            // Invalidate resource annotations
            queryClient.invalidateQueries({
                queryKey: annotationKeys.resource(updatedAnnotation.resourceId),
            });
            // Invalidate all annotations list
            queryClient.invalidateQueries({
                queryKey: annotationKeys.lists(),
            });

            // Update in cache
            queryClient.setQueryData<Annotation[]>(
                annotationKeys.resource(updatedAnnotation.resourceId),
                (old = []) =>
                    old.map((ann) =>
                        ann.id === updatedAnnotation.id ? updatedAnnotation : ann
                    )
            );
        },
    });
}

/**
 * Delete an annotation
 */
export function useDeleteAnnotation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            annotationId,
            resourceId,
        }: {
            annotationId: string;
            resourceId: string;
        }) => deleteAnnotation(annotationId),
        onSuccess: (_, { annotationId, resourceId }) => {
            // Invalidate resource annotations
            queryClient.invalidateQueries({
                queryKey: annotationKeys.resource(resourceId),
            });
            // Invalidate all annotations list
            queryClient.invalidateQueries({
                queryKey: annotationKeys.lists(),
            });

            // Remove from cache
            queryClient.setQueryData<Annotation[]>(
                annotationKeys.resource(resourceId),
                (old = []) => old.filter((ann) => ann.id !== annotationId)
            );
        },
    });
}
