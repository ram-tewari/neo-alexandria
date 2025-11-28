import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { searchApi } from '@/services/api/search';
import { SearchQuery } from '@/types/search';
import { useToastStore } from '@/store/toastStore';

export const useSearch = (query: SearchQuery) => {
  return useInfiniteQuery({
    queryKey: ['search', query],
    queryFn: ({ pageParam = 1 }) => searchApi.search(query, pageParam, 20),
    getNextPageParam: (lastPage) => {
      return lastPage.hasMore ? lastPage.page + 1 : undefined;
    },
    initialPageParam: 1,
    enabled: !!query.text,
  });
};

export const useSearchSuggestions = (query: string) => {
  return useQuery({
    queryKey: ['search-suggestions', query],
    queryFn: () => searchApi.getSuggestions(query),
    enabled: query.length > 2,
    staleTime: 30000, // 30 seconds
  });
};

export const useSearchHistory = () => {
  return useQuery({
    queryKey: ['search-history'],
    queryFn: searchApi.getHistory,
  });
};

export const useAddToHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: searchApi.addToHistory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-history'] });
    },
  });
};

export const useClearHistory = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: searchApi.clearHistory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-history'] });
      addToast({
        type: 'success',
        message: 'Search history cleared',
      });
    },
  });
};

export const useSaveSearch = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ name, query }: { name: string; query: SearchQuery }) =>
      searchApi.saveSearch(name, query),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-searches'] });
      addToast({
        type: 'success',
        message: 'Search saved successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to save search',
      });
    },
  });
};

export const useSavedSearches = () => {
  return useQuery({
    queryKey: ['saved-searches'],
    queryFn: searchApi.getSavedSearches,
  });
};

export const useDeleteSavedSearch = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: searchApi.deleteSavedSearch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-searches'] });
      addToast({
        type: 'success',
        message: 'Search deleted',
      });
    },
  });
};
