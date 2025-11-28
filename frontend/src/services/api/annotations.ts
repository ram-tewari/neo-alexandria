import { apiClient } from './client';
import {
  Annotation,
  AnnotationFilters,
  SemanticSearchResult,
  ConceptCluster,
} from '@/types/annotation';

export const annotationsApi = {
  // Get annotations for a resource
  getAnnotations: async (resourceId: string): Promise<Annotation[]> => {
    const response = await apiClient.get<Annotation[]>(
      `/resources/${resourceId}/annotations`
    );
    return response.data;
  },

  // Get all annotations with filters
  getAllAnnotations: async (filters?: AnnotationFilters): Promise<Annotation[]> => {
    const params = new URLSearchParams();
    
    if (filters?.resourceIds) {
      filters.resourceIds.forEach(id => params.append('resourceId', id));
    }
    if (filters?.tags) {
      filters.tags.forEach(tag => params.append('tag', tag));
    }
    if (filters?.colors) {
      filters.colors.forEach(color => params.append('color', color));
    }
    if (filters?.dateRange) {
      params.append('startDate', filters.dateRange[0].toISOString());
      params.append('endDate', filters.dateRange[1].toISOString());
    }
    if (filters?.searchQuery) {
      params.append('q', filters.searchQuery);
    }

    const response = await apiClient.get<Annotation[]>(
      `/annotations?${params.toString()}`
    );
    return response.data;
  },

  // Create annotation
  createAnnotation: async (
    annotation: Omit<Annotation, 'id' | 'userId' | 'createdAt' | 'updatedAt'>
  ): Promise<Annotation> => {
    const response = await apiClient.post<Annotation>('/annotations', annotation);
    return response.data;
  },

  // Update annotation
  updateAnnotation: async (
    id: string,
    updates: Partial<Annotation>
  ): Promise<Annotation> => {
    const response = await apiClient.patch<Annotation>(`/annotations/${id}`, updates);
    return response.data;
  },

  // Delete annotation
  deleteAnnotation: async (id: string): Promise<void> => {
    await apiClient.delete(`/annotations/${id}`);
  },

  // Semantic search
  semanticSearch: async (query: string): Promise<SemanticSearchResult[]> => {
    const response = await apiClient.post<SemanticSearchResult[]>(
      '/annotations/semantic-search',
      { query }
    );
    return response.data;
  },

  // Get concept clusters
  getConceptClusters: async (): Promise<ConceptCluster[]> => {
    const response = await apiClient.get<ConceptCluster[]>(
      '/annotations/concept-clusters'
    );
    return response.data;
  },

  // Export annotations
  exportAnnotations: async (
    format: 'markdown' | 'json',
    filters?: AnnotationFilters
  ): Promise<Blob> => {
    const params = new URLSearchParams({ format });
    
    if (filters?.resourceIds) {
      filters.resourceIds.forEach(id => params.append('resourceId', id));
    }
    if (filters?.tags) {
      filters.tags.forEach(tag => params.append('tag', tag));
    }

    const response = await apiClient.get(
      `/annotations/export?${params.toString()}`,
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Get tag suggestions
  getTagSuggestions: async (query: string): Promise<string[]> => {
    const response = await apiClient.get<string[]>(
      `/annotations/tags/suggestions?q=${encodeURIComponent(query)}`
    );
    return response.data;
  },
};
