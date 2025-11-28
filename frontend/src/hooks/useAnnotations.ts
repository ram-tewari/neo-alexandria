import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { annotationsApi } from '@/services/api/annotations';
import { Annotation, AnnotationFilters } from '@/types/annotation';
import { useToastStore } from '@/store/toastStore';

export const useAnnotations = (resourceId: string) => {
  return useQuery({
    queryKey: ['annotations', resourceId],
    queryFn: () => annotationsApi.getAnnotations(resourceId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useAllAnnotations = (filters?: AnnotationFilters) => {
  return useQuery({
    queryKey: ['annotations', 'all', filters],
    queryFn: () => annotationsApi.getAllAnnotations(filters),
    staleTime: 2 * 60 * 1000,
  });
};

export const useCreateAnnotation = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (annotation: Omit<Annotation, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) =>
      annotationsApi.createAnnotation(annotation),
    onMutate: async (newAnnotation) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['annotations', newAnnotation.resourceId] });
      
      const previousAnnotations = queryClient.getQueryData<Annotation[]>([
        'annotations',
        newAnnotation.resourceId,
      ]);

      const optimisticAnnotation: Annotation = {
        ...newAnnotation,
        id: `temp-${Date.now()}`,
        userId: 'current-user',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      queryClient.setQueryData<Annotation[]>(
        ['annotations', newAnnotation.resourceId],
        (old = []) => [...old, optimisticAnnotation]
      );

      return { previousAnnotations };
    },
    onError: (error: any, newAnnotation, context) => {
      // Rollback on error
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          ['annotations', newAnnotation.resourceId],
          context.previousAnnotations
        );
      }
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to create annotation',
      });
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['annotations', variables.resourceId] });
      queryClient.invalidateQueries({ queryKey: ['annotations', 'all'] });
      addToast({
        type: 'success',
        message: 'Annotation created',
      });
    },
  });
};

export const useUpdateAnnotation = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Annotation> }) =>
      annotationsApi.updateAnnotation(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['annotations', data.resourceId] });
      queryClient.invalidateQueries({ queryKey: ['annotations', 'all'] });
      addToast({
        type: 'success',
        message: 'Annotation updated',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update annotation',
      });
    },
  });
};

export const useDeleteAnnotation = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ id, resourceId }: { id: string; resourceId: string }) =>
      annotationsApi.deleteAnnotation(id),
    onMutate: async ({ id, resourceId }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['annotations', resourceId] });
      
      const previousAnnotations = queryClient.getQueryData<Annotation[]>([
        'annotations',
        resourceId,
      ]);

      queryClient.setQueryData<Annotation[]>(
        ['annotations', resourceId],
        (old = []) => old.filter(a => a.id !== id)
      );

      return { previousAnnotations, resourceId };
    },
    onError: (error: any, variables, context) => {
      // Rollback on error
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          ['annotations', context.resourceId],
          context.previousAnnotations
        );
      }
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to delete annotation',
      });
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['annotations', variables.resourceId] });
      queryClient.invalidateQueries({ queryKey: ['annotations', 'all'] });
      addToast({
        type: 'success',
        message: 'Annotation deleted',
      });
    },
  });
};

export const useSemanticSearch = (query: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['annotations', 'semantic-search', query],
    queryFn: () => annotationsApi.semanticSearch(query),
    enabled: enabled && query.length > 0,
    staleTime: 5 * 60 * 1000,
  });
};

export const useConceptClusters = () => {
  return useQuery({
    queryKey: ['annotations', 'concept-clusters'],
    queryFn: annotationsApi.getConceptClusters,
    staleTime: 10 * 60 * 1000,
  });
};

export const useTagSuggestions = (query: string) => {
  return useQuery({
    queryKey: ['annotations', 'tag-suggestions', query],
    queryFn: () => annotationsApi.getTagSuggestions(query),
    enabled: query.length > 0,
    staleTime: 5 * 60 * 1000,
  });
};

export const useExportAnnotations = () => {
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({
      format,
      filters,
    }: {
      format: 'markdown' | 'json';
      filters?: AnnotationFilters;
    }) => annotationsApi.exportAnnotations(format, filters),
    onSuccess: (blob, variables) => {
      // Download the file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `annotations.${variables.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      addToast({
        type: 'success',
        message: 'Annotations exported successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to export annotations',
      });
    },
  });
};
