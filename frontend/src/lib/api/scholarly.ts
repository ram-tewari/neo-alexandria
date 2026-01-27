/**
 * Scholarly API Client
 * 
 * Provides API endpoints for Phase 3 Living Library scholarly features:
 * - Equation extraction and rendering
 * - Table extraction and formatting
 * - Metadata extraction and completeness tracking
 * 
 * Phase: 3 Living Library
 * Requirements: US-3.5, US-3.6
 */

import { apiClient } from '@/core/api/client';
import type {
  Equation,
  Table,
  Metadata,
  CompletenessStats,
  EquationListResponse,
  TableListResponse,
} from '@/types/library';

// ============================================================================
// Scholarly API Client Interface
// ============================================================================

/**
 * Scholarly API client with all Phase 3 scholarly-related endpoints
 */
export const scholarlyApi = {
  // ==========================================================================
  // Equation Endpoints
  // ==========================================================================

  /**
   * Get equations extracted from a resource
   * 
   * Fetches all mathematical equations extracted from a document,
   * including LaTeX source, rendered HTML, and position information.
   * 
   * @param resourceId - Resource ID
   * @returns Array of equations
   * @endpoint GET /scholarly/resources/{resource_id}/equations
   * 
   * @example
   * ```typescript
   * const equations = await scholarlyApi.getEquations('res_123');
   * equations.forEach(eq => {
   *   console.log(`Equation ${eq.equation_number}: ${eq.latex_source}`);
   * });
   * ```
   */
  getEquations: async (resourceId: string): Promise<Equation[]> => {
    const response = await apiClient.get<EquationListResponse>(
      `/scholarly/resources/${resourceId}/equations`
    );
    
    // Handle both array and object response formats
    if (Array.isArray(response.data)) {
      return response.data;
    }
    
    return response.data.equations || [];
  },

  // ==========================================================================
  // Table Endpoints
  // ==========================================================================

  /**
   * Get tables extracted from a resource
   * 
   * Fetches all tables extracted from a document, including headers,
   * rows, captions, and position information.
   * 
   * @param resourceId - Resource ID
   * @returns Array of tables
   * @endpoint GET /scholarly/resources/{resource_id}/tables
   * 
   * @example
   * ```typescript
   * const tables = await scholarlyApi.getTables('res_123');
   * tables.forEach(table => {
   *   console.log(`Table ${table.table_number}: ${table.caption}`);
   *   console.log(`Headers: ${table.headers.join(', ')}`);
   *   console.log(`Rows: ${table.rows.length}`);
   * });
   * ```
   */
  getTables: async (resourceId: string): Promise<Table[]> => {
    const response = await apiClient.get<TableListResponse>(
      `/scholarly/resources/${resourceId}/tables`
    );
    
    // Handle both array and object response formats
    if (Array.isArray(response.data)) {
      return response.data;
    }
    
    return response.data.tables || [];
  },

  // ==========================================================================
  // Metadata Endpoints
  // ==========================================================================

  /**
   * Get metadata for a resource
   * 
   * Fetches extracted metadata including title, authors, publication date,
   * DOI, ISBN, abstract, keywords, citations, and completeness tracking.
   * 
   * @param resourceId - Resource ID
   * @returns Metadata object with completeness score
   * @endpoint GET /scholarly/metadata/{resource_id}
   * 
   * @example
   * ```typescript
   * const metadata = await scholarlyApi.getMetadata('res_123');
   * console.log(`Title: ${metadata.title}`);
   * console.log(`Authors: ${metadata.authors?.join(', ')}`);
   * console.log(`Completeness: ${metadata.completeness_score}%`);
   * console.log(`Missing fields: ${metadata.missing_fields.join(', ')}`);
   * ```
   */
  getMetadata: async (resourceId: string): Promise<Metadata> => {
    const response = await apiClient.get<Metadata>(
      `/scholarly/metadata/${resourceId}`
    );
    
    return response.data;
  },

  /**
   * Get metadata completeness statistics
   * 
   * Fetches aggregated statistics about metadata completeness across
   * all resources, including distribution and most commonly missing fields.
   * 
   * @returns Completeness statistics
   * @endpoint GET /scholarly/metadata/completeness-stats
   * 
   * @example
   * ```typescript
   * const stats = await scholarlyApi.getCompletenessStats();
   * console.log(`Total resources: ${stats.total_resources}`);
   * console.log(`Average completeness: ${stats.avg_completeness}%`);
   * 
   * stats.most_missing_fields.forEach(field => {
   *   console.log(`${field.field}: missing in ${field.missing_count} resources`);
   * });
   * ```
   */
  getCompletenessStats: async (): Promise<CompletenessStats> => {
    const response = await apiClient.get<CompletenessStats>(
      '/scholarly/metadata/completeness-stats'
    );
    
    return response.data;
  },

  // ==========================================================================
  // Health Check Endpoint
  // ==========================================================================

  /**
   * Health check for scholarly module
   * 
   * Checks if the scholarly module is operational and can process requests.
   * Used for connection testing and monitoring.
   * 
   * @returns Health status
   * @endpoint GET /scholarly/health
   * 
   * @example
   * ```typescript
   * try {
   *   const health = await scholarlyApi.health();
   *   console.log('Scholarly module is healthy:', health);
   * } catch (error) {
   *   console.error('Scholarly module is down:', error);
   * }
   * ```
   */
  health: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/scholarly/health');
    return response.data;
  },
};

// ============================================================================
// TanStack Query Key Factories
// ============================================================================

/**
 * Query key factories for TanStack Query caching
 * 
 * These factories generate consistent cache keys for React Query.
 * Use these keys in useQuery and useMutation hooks to ensure proper
 * cache invalidation and data consistency.
 * 
 * @example
 * ```typescript
 * const { data } = useQuery({
 *   queryKey: scholarlyQueryKeys.equations.detail('res_123'),
 *   queryFn: () => scholarlyApi.getEquations('res_123'),
 * });
 * ```
 */
export const scholarlyQueryKeys = {
  /**
   * Equation-related query keys
   */
  equations: {
    /** All equations query keys */
    all: () => ['scholarly', 'equations'] as const,
    /** Equations for a specific resource */
    detail: (resourceId: string) =>
      ['scholarly', 'equations', resourceId] as const,
  },

  /**
   * Table-related query keys
   */
  tables: {
    /** All tables query keys */
    all: () => ['scholarly', 'tables'] as const,
    /** Tables for a specific resource */
    detail: (resourceId: string) =>
      ['scholarly', 'tables', resourceId] as const,
  },

  /**
   * Metadata-related query keys
   */
  metadata: {
    /** All metadata query keys */
    all: () => ['scholarly', 'metadata'] as const,
    /** Metadata for a specific resource */
    detail: (resourceId: string) =>
      ['scholarly', 'metadata', resourceId] as const,
    /** Completeness statistics */
    stats: () => ['scholarly', 'metadata', 'completeness-stats'] as const,
  },

  /**
   * Health check query key
   */
  health: () => ['scholarly', 'health'] as const,
};

// ============================================================================
// Cache Configuration
// ============================================================================

/**
 * Default cache times for TanStack Query (in milliseconds)
 * 
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 */
export const scholarlyCacheConfig = {
  equations: {
    staleTime: 30 * 60 * 1000, // 30 minutes (equations don't change often)
    cacheTime: 60 * 60 * 1000, // 1 hour
  },
  tables: {
    staleTime: 30 * 60 * 1000, // 30 minutes (tables don't change often)
    cacheTime: 60 * 60 * 1000, // 1 hour
  },
  metadata: {
    staleTime: 10 * 60 * 1000, // 10 minutes (metadata may be updated)
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  completenessStats: {
    staleTime: 60 * 60 * 1000, // 1 hour (stats change slowly)
    cacheTime: 2 * 60 * 60 * 1000, // 2 hours
  },
  health: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
};
