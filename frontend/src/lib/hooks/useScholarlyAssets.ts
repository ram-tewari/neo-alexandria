import { useQuery } from '@tanstack/react-query';
import { scholarlyApi } from '@/lib/api/scholarly';

/**
 * Custom hook for fetching scholarly assets (equations, tables, metadata)
 * Provides parallel loading with individual loading states
 */
export function useScholarlyAssets(resourceId: string) {
  // Fetch equations
  const equationsQuery = useQuery({
    queryKey: ['equations', resourceId],
    queryFn: () => scholarlyApi.getEquations(resourceId),
    staleTime: 30 * 60 * 1000, // 30 minutes
    enabled: !!resourceId,
  });

  // Fetch tables
  const tablesQuery = useQuery({
    queryKey: ['tables', resourceId],
    queryFn: () => scholarlyApi.getTables(resourceId),
    staleTime: 30 * 60 * 1000, // 30 minutes
    enabled: !!resourceId,
  });

  // Fetch metadata
  const metadataQuery = useQuery({
    queryKey: ['metadata', resourceId],
    queryFn: () => scholarlyApi.getMetadata(resourceId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!resourceId,
  });

  // Derived states
  const isLoading = equationsQuery.isLoading || tablesQuery.isLoading || metadataQuery.isLoading;
  const hasError = !!equationsQuery.error || !!tablesQuery.error || !!metadataQuery.error;
  const hasEquations = (equationsQuery.data?.length || 0) > 0;
  const hasTables = (tablesQuery.data?.length || 0) > 0;
  const hasMetadata = !!metadataQuery.data;

  // Refetch all assets
  const refetchAll = async () => {
    await Promise.all([
      equationsQuery.refetch(),
      tablesQuery.refetch(),
      metadataQuery.refetch(),
    ]);
  };

  return {
    // Data
    equations: equationsQuery.data || [],
    tables: tablesQuery.data || [],
    metadata: metadataQuery.data,

    // Loading states
    isLoading,
    isLoadingEquations: equationsQuery.isLoading,
    isLoadingTables: tablesQuery.isLoading,
    isLoadingMetadata: metadataQuery.isLoading,

    // Error states
    hasError,
    equationsError: equationsQuery.error,
    tablesError: tablesQuery.error,
    metadataError: metadataQuery.error,

    // Derived states
    hasEquations,
    hasTables,
    hasMetadata,
    hasAnyAssets: hasEquations || hasTables || hasMetadata,

    // Actions
    refetchAll,
    refetchEquations: equationsQuery.refetch,
    refetchTables: tablesQuery.refetch,
    refetchMetadata: metadataQuery.refetch,
  };
}
