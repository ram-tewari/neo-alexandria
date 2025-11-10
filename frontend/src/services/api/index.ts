// Neo Alexandria 2.0 Frontend - API Services Index
// Central export for all API service modules

export { default as apiClient } from './client';
export { queryClient, clearQueryCache, invalidateQueries, prefetchQuery } from './queryClient';

export { resourcesApi } from './resources';
export { searchApi } from './search';
export { graphApi } from './graph';
export { collectionsApi } from './collections';
export { citationsApi } from './citations';

// Export main API service from parent directory
export { apiService, ApiService, pollResourceStatus } from '../api';

// Re-export types
export type {
  Collection,
  CreateCollectionRequest,
  CollectionListResponse,
  CollectionRecommendations,
  GetCollectionsParams,
} from './collections';

export type {
  Citation,
  CitationResponse,
  CitationGraphParams,
} from './citations';
