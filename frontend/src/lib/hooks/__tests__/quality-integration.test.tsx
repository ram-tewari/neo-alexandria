/**
 * Quality Data Flow Integration Tests
 * 
 * Tests complete quality data flows with real API interactions:
 * - Quality badge display from resource metadata
 * - Quality recalculation workflow
 * - Quality analytics endpoints (outliers, degradation, distribution, trends, dimensions, review queue)
 * - Error handling and loading states
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 8.4 - Write integration tests for quality data flow
 * Requirements: 10.3 (quality badge display, recalculation, analytics)
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse, delay } from 'msw';
import { server } from '@/test/mocks/server';
import {
  useQualityDetails,
  useRecalculateQuality,
  useQualityOutliers,
  useQualityDegradation,
  useQualityDistribution,
  useQualityTrends,
  useQualityDimensions,
  useQualityReviewQueue,
} from '../useEditorData';
import type {
  Resource,
  QualityDetails,
  QualityRecalculateRequest,
  QualityOutlier,
  QualityDegradation,
  QualityDistribution,
  QualityTrend,
  QualityDimensionStats,
  QualityReviewItem,
} from '@/types/api';
import React from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Create a fresh QueryClient for each test to avoid cache pollution
 */
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * Wrapper component that provides QueryClient context
 */
function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

// ============================================================================
// Mock Data
// ============================================================================

const mockResource: Resource = {
  id: 'resource-1',
  title: 'Test Resource',
  content_type: 'code' as const,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ingestion_status: 'completed' as const,
  quality_overall: 0.85,
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.85,
    consistency: 0.88,
    timeliness: 0.82,
    relevance: 0.8,
  },
};

const mockQualityDetails: QualityDetails = {
  resource_id: 'resource-1',
  quality_overall: 0.85,
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.85,
    consistency: 0.88,
    timeliness: 0.82,
    relevance: 0.8,
  },
  quality_weights: {
    accuracy: 0.25,
    completeness: 0.25,
    consistency: 0.2,
    timeliness: 0.15,
    relevance: 0.15,
  },
  computed_at: '2024-01-01T00:00:00Z',
};

const mockOutliers: QualityOutlier[] = [
  {
    resource_id: 'resource-2',
    resource_title: 'Low Quality Resource',
    quality_overall: 0.3,
    outlier_score: 0.95,
    reason: 'Significantly below average quality',
    dimensions_below_threshold: ['accuracy', 'completeness'],
  },
  {
    resource_id: 'resource-3',
    resource_title: 'Another Low Quality Resource',
    quality_overall: 0.4,
    outlier_score: 0.85,
    reason: 'Multiple dimensions below threshold',
    dimensions_below_threshold: ['timeliness'],
  },
];

const mockDegradation: QualityDegradation = {
  days: 30,
  degraded_count: 5,
  average_change: -0.15,
  degraded_resources: [
    {
      resource_id: 'resource-4',
      resource_title: 'Degraded Resource',
      quality_before: 0.9,
      quality_after: 0.7,
      quality_change: -0.2,
      degraded_at: '2024-01-15T00:00:00Z',
    },
  ],
};

const mockDistribution: QualityDistribution = {
  bins: [
    { range: '0.0-0.1', count: 2 },
    { range: '0.1-0.2', count: 5 },
    { range: '0.2-0.3', count: 8 },
    { range: '0.3-0.4', count: 12 },
    { range: '0.4-0.5', count: 15 },
    { range: '0.5-0.6', count: 20 },
    { range: '0.6-0.7', count: 25 },
    { range: '0.7-0.8', count: 30 },
    { range: '0.8-0.9', count: 35 },
    { range: '0.9-1.0', count: 28 },
  ],
  mean: 0.72,
  median: 0.75,
  std_dev: 0.18,
  total_resources: 180,
};

const mockTrends: QualityTrend[] = [
  {
    date: '2024-01-01',
    average_quality: 0.75,
    resource_count: 100,
  },
  {
    date: '2024-01-08',
    average_quality: 0.78,
    resource_count: 105,
  },
  {
    date: '2024-01-15',
    average_quality: 0.76,
    resource_count: 110,
  },
];

const mockDimensionStats: QualityDimensionStats = {
  accuracy: { mean: 0.85, median: 0.87, std_dev: 0.12 },
  completeness: { mean: 0.82, median: 0.84, std_dev: 0.15 },
  consistency: { mean: 0.88, median: 0.9, std_dev: 0.1 },
  timeliness: { mean: 0.75, median: 0.78, std_dev: 0.18 },
  relevance: { mean: 0.8, median: 0.82, std_dev: 0.14 },
};

const mockReviewQueue: QualityReviewItem[] = [
  {
    resource_id: 'resource-5',
    resource_title: 'Needs Review',
    quality_overall: 0.45,
    priority: 'high' as const,
    review_reason: 'Low quality score',
    flagged_at: '2024-01-20T00:00:00Z',
  },
];

// ============================================================================
// Test Suite: Quality Badge Display
// ============================================================================

describe('Quality Badge Display Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('should fetch and display quality data from resource metadata', async () => {
    /**
     * Requirement: 10.3 - Quality badge display
     * 
     * Verifies that quality data is fetched from resource metadata
     * and can be displayed in quality badges.
     */

    const resourceId = 'resource-1';

    // Setup: Mock resource endpoint with quality data
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId}`, () => {
        return HttpResponse.json(mockResource);
      })
    );

    // Execute: Fetch quality details
    const { result } = renderHook(
      () => useQualityDetails(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Loading state
    expect(result.current.isLoading).toBe(true);

    // Assert: Quality data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.quality_overall).toBe(0.85);
    expect(result.current.data?.quality_dimensions).toEqual({
      accuracy: 0.9,
      completeness: 0.85,
      consistency: 0.88,
      timeliness: 0.82,
      relevance: 0.8,
    });
  });

  it('should handle resource without quality data', async () => {
    /**
     * Requirement: 10.3 - Handle missing quality data gracefully
     */

    const resourceId = 'resource-no-quality';
    const resourceWithoutQuality: Resource = {
      ...mockResource,
      id: resourceId,
      quality_overall: undefined,
      quality_dimensions: undefined,
    };

    // Setup: Mock resource without quality data
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId}`, () => {
        return HttpResponse.json(resourceWithoutQuality);
      })
    );

    // Execute: Fetch quality details
    const { result } = renderHook(
      () => useQualityDetails(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Data loaded but no quality scores
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.quality_overall).toBeUndefined();
    expect(result.current.data?.quality_dimensions).toBeUndefined();
  });

  it('should show loading state while fetching quality data', async () => {
    /**
     * Requirement: 10.3 - Loading states
     */

    const resourceId = 'resource-1';

    // Setup: Mock delayed response
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId}`, async () => {
        await delay(500);
        return HttpResponse.json(mockResource);
      })
    );

    // Execute: Fetch quality details
    const { result } = renderHook(
      () => useQualityDetails(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Loading state is true
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Assert: Eventually loads
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    }, { timeout: 2000 });

    expect(result.current.data?.quality_overall).toBe(0.85);
  });

  it('should handle quality data fetch error', async () => {
    /**
     * Requirement: 10.3 - Error handling
     */

    const resourceId = 'resource-error';

    // Setup: Mock error response
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId}`, () => {
        return HttpResponse.json(
          { detail: 'Resource not found' },
          { status: 404 }
        );
      })
    );

    // Execute: Fetch quality details
    const { result } = renderHook(
      () => useQualityDetails(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });
});

// ============================================================================
// Test Suite: Quality Recalculation
// ============================================================================

describe('Quality Recalculation Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('should recalculate quality for a single resource', async () => {
    /**
     * Requirement: 10.3 - Quality recalculation
     * 
     * Verifies that quality can be recalculated and the cache
     * is invalidated to show updated scores.
     */

    const resourceId = 'resource-1';
    const recalculateRequest: QualityRecalculateRequest = {
      resource_id: resourceId,
      weights: {
        accuracy: 0.3,
        completeness: 0.3,
        consistency: 0.2,
        timeliness: 0.1,
        relevance: 0.1,
      },
    };

    const updatedQuality: QualityDetails = {
      ...mockQualityDetails,
      quality_overall: 0.92,
      computed_at: new Date().toISOString(),
    };

    // Setup: Mock recalculation endpoint
    server.use(
      http.post(`${API_BASE_URL}/quality/recalculate`, async ({ request }) => {
        const body = await request.json() as QualityRecalculateRequest;
        expect(body.resource_id).toBe(resourceId);
        return HttpResponse.json(updatedQuality);
      }),
      http.get(`${API_BASE_URL}/resources/${resourceId}`, () => {
        return HttpResponse.json({
          ...mockResource,
          quality_overall: updatedQuality.quality_overall,
        });
      })
    );

    // Execute: Recalculate quality
    const { result } = renderHook(
      () => useRecalculateQuality(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      result.current.mutate(recalculateRequest);
    });

    // Assert: Mutation in progress
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Assert: Mutation succeeded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.quality_overall).toBe(0.92);

    // Verify cache invalidation - resource query should be invalidated
    const resourceQueryState = queryClient.getQueryState(['resource', resourceId]);
    expect(resourceQueryState?.isInvalidated).toBe(true);
  });

  it('should recalculate quality for multiple resources', async () => {
    /**
     * Requirement: 10.3 - Batch quality recalculation
     */

    const resourceIds = ['resource-1', 'resource-2', 'resource-3'];
    const recalculateRequest: QualityRecalculateRequest = {
      resource_ids: resourceIds,
      weights: {
        accuracy: 0.25,
        completeness: 0.25,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
    };

    // Setup: Mock batch recalculation
    server.use(
      http.post(`${API_BASE_URL}/quality/recalculate`, async ({ request }) => {
        const body = await request.json() as QualityRecalculateRequest;
        expect(body.resource_ids).toEqual(resourceIds);
        return HttpResponse.json({
          ...mockQualityDetails,
          computed_at: new Date().toISOString(),
        });
      })
    );

    // Execute: Recalculate quality for multiple resources
    const { result } = renderHook(
      () => useRecalculateQuality(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      result.current.mutate(recalculateRequest);
    });

    // Assert: Mutation succeeded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Verify all resource caches are invalidated
    resourceIds.forEach((resourceId) => {
      const queryState = queryClient.getQueryState(['resource', resourceId]);
      expect(queryState?.isInvalidated).toBe(true);
    });
  });

  it('should handle recalculation error', async () => {
    /**
     * Requirement: 10.3 - Error handling for recalculation
     */

    const recalculateRequest: QualityRecalculateRequest = {
      resource_id: 'resource-error',
      weights: {
        accuracy: 0.25,
        completeness: 0.25,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
    };

    // Setup: Mock error response
    server.use(
      http.post(`${API_BASE_URL}/quality/recalculate`, () => {
        return HttpResponse.json(
          { detail: 'Failed to recalculate quality' },
          { status: 500 }
        );
      })
    );

    // Execute: Attempt recalculation
    const { result } = renderHook(
      () => useRecalculateQuality(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      result.current.mutate(recalculateRequest);
    });

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

// ============================================================================
// Test Suite: Quality Analytics Endpoints
// ============================================================================

describe('Quality Analytics Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('should fetch quality outliers', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (outliers)
     */

    const params = {
      page: 1,
      limit: 20,
      min_outlier_score: 0.8,
    };

    // Setup: Mock outliers endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/outliers`, ({ request }) => {
        const url = new URL(request.url);
        expect(url.searchParams.get('page')).toBe('1');
        expect(url.searchParams.get('limit')).toBe('20');
        expect(url.searchParams.get('min_outlier_score')).toBe('0.8');
        return HttpResponse.json(mockOutliers);
      })
    );

    // Execute: Fetch outliers
    const { result } = renderHook(
      () => useQualityOutliers(params),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Outliers loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].outlier_score).toBe(0.95);
    expect(result.current.data?.[0].reason).toBe('Significantly below average quality');
  });

  it('should fetch quality degradation', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (degradation)
     */

    const days = 30;

    // Setup: Mock degradation endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/degradation`, ({ request }) => {
        const url = new URL(request.url);
        expect(url.searchParams.get('days')).toBe('30');
        return HttpResponse.json(mockDegradation);
      })
    );

    // Execute: Fetch degradation
    const { result } = renderHook(
      () => useQualityDegradation(days),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Degradation data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.degraded_count).toBe(5);
    expect(result.current.data?.average_change).toBe(-0.15);
    expect(result.current.data?.degraded_resources).toHaveLength(1);
  });

  it('should fetch quality distribution', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (distribution)
     */

    const bins = 10;

    // Setup: Mock distribution endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/distribution`, ({ request }) => {
        const url = new URL(request.url);
        expect(url.searchParams.get('bins')).toBe('10');
        return HttpResponse.json(mockDistribution);
      })
    );

    // Execute: Fetch distribution
    const { result } = renderHook(
      () => useQualityDistribution(bins),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Distribution data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.bins).toHaveLength(10);
    expect(result.current.data?.mean).toBe(0.72);
    expect(result.current.data?.median).toBe(0.75);
    expect(result.current.data?.total_resources).toBe(180);
  });

  it('should fetch quality trends', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (trends)
     */

    const days = 30;

    // Setup: Mock trends endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/trends`, ({ request }) => {
        const url = new URL(request.url);
        expect(url.searchParams.get('days')).toBe('30');
        return HttpResponse.json(mockTrends);
      })
    );

    // Execute: Fetch trends
    const { result } = renderHook(
      () => useQualityTrends(days),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Trends data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(3);
    expect(result.current.data?.[0].average_quality).toBe(0.75);
    expect(result.current.data?.[1].average_quality).toBe(0.78);
  });

  it('should fetch quality dimension statistics', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (dimensions)
     */

    // Setup: Mock dimensions endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/dimensions`, () => {
        return HttpResponse.json(mockDimensionStats);
      })
    );

    // Execute: Fetch dimension stats
    const { result } = renderHook(
      () => useQualityDimensions(),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Dimension stats loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.accuracy.mean).toBe(0.85);
    expect(result.current.data?.completeness.mean).toBe(0.82);
    expect(result.current.data?.consistency.mean).toBe(0.88);
    expect(result.current.data?.timeliness.mean).toBe(0.75);
    expect(result.current.data?.relevance.mean).toBe(0.8);
  });

  it('should fetch quality review queue', async () => {
    /**
     * Requirement: 10.3 - Quality analytics (review queue)
     */

    const params = {
      priority: 'high' as const,
      limit: 50,
    };

    // Setup: Mock review queue endpoint
    server.use(
      http.get(`${API_BASE_URL}/quality/review-queue`, ({ request }) => {
        const url = new URL(request.url);
        expect(url.searchParams.get('priority')).toBe('high');
        expect(url.searchParams.get('limit')).toBe('50');
        return HttpResponse.json(mockReviewQueue);
      })
    );

    // Execute: Fetch review queue
    const { result } = renderHook(
      () => useQualityReviewQueue(params),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Review queue loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].priority).toBe('high');
    expect(result.current.data?.[0].review_reason).toBe('Low quality score');
  });

  it('should handle analytics endpoint errors gracefully', async () => {
    /**
     * Requirement: 10.3 - Error handling for analytics
     */

    // Setup: Mock error responses for all analytics endpoints
    server.use(
      http.get(`${API_BASE_URL}/quality/outliers`, () => {
        return HttpResponse.json(
          { detail: 'Service unavailable' },
          { status: 503 }
        );
      })
    );

    // Execute: Attempt to fetch outliers
    const { result } = renderHook(
      () => useQualityOutliers({ page: 1, limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('should handle empty analytics results', async () => {
    /**
     * Requirement: 10.3 - Handle empty analytics data
     */

    // Setup: Mock empty outliers response
    server.use(
      http.get(`${API_BASE_URL}/quality/outliers`, () => {
        return HttpResponse.json([]);
      })
    );

    // Execute: Fetch outliers
    const { result } = renderHook(
      () => useQualityOutliers({ page: 1, limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: Empty array returned
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });
});

// ============================================================================
// Test Suite: Complete Quality Workflow
// ============================================================================

describe('Complete Quality Workflow Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('should complete full quality workflow: display → recalculate → verify', async () => {
    /**
     * Requirement: 10.3 - Complete quality workflow
     * 
     * This test verifies the complete quality workflow:
     * 1. Fetch and display quality badge
     * 2. Recalculate quality with custom weights
     * 3. Verify updated quality is displayed
     */

    const resourceId = 'resource-1';

    // Setup: Mock initial resource with quality
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId}`, () => {
        return HttpResponse.json(mockResource);
      }),
      http.post(`${API_BASE_URL}/quality/recalculate`, () => {
        return HttpResponse.json({
          ...mockQualityDetails,
          quality_overall: 0.95,
          computed_at: new Date().toISOString(),
        });
      })
    );

    // Step 1: Fetch initial quality
    const { result: qualityResult } = renderHook(
      () => useQualityDetails(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(qualityResult.current.isSuccess).toBe(true);
    });

    expect(qualityResult.current.data?.quality_overall).toBe(0.85);

    // Step 2: Recalculate quality
    const { result: recalculateResult } = renderHook(
      () => useRecalculateQuality(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      recalculateResult.current.mutate({
        resource_id: resourceId,
        weights: {
          accuracy: 0.3,
          completeness: 0.3,
          consistency: 0.2,
          timeliness: 0.1,
          relevance: 0.1,
        },
      });
    });

    await waitFor(() => {
      expect(recalculateResult.current.isSuccess).toBe(true);
    });

    expect(recalculateResult.current.data?.quality_overall).toBe(0.95);

    // Step 3: Verify cache invalidation triggered refetch
    const resourceQueryState = queryClient.getQueryState(['resource', resourceId]);
    expect(resourceQueryState?.isInvalidated).toBe(true);
  });

  it('should handle concurrent quality operations', async () => {
    /**
     * Requirement: 10.3 - Handle concurrent operations
     */

    const resourceId1 = 'resource-1';
    const resourceId2 = 'resource-2';

    // Setup: Mock multiple resources
    server.use(
      http.get(`${API_BASE_URL}/resources/${resourceId1}`, () => {
        return HttpResponse.json({ ...mockResource, id: resourceId1 });
      }),
      http.get(`${API_BASE_URL}/resources/${resourceId2}`, () => {
        return HttpResponse.json({ ...mockResource, id: resourceId2 });
      }),
      http.get(`${API_BASE_URL}/quality/outliers`, () => {
        return HttpResponse.json(mockOutliers);
      })
    );

    // Execute: Fetch multiple quality data simultaneously
    const { result: quality1 } = renderHook(
      () => useQualityDetails(resourceId1),
      { wrapper: createWrapper(queryClient) }
    );

    const { result: quality2 } = renderHook(
      () => useQualityDetails(resourceId2),
      { wrapper: createWrapper(queryClient) }
    );

    const { result: outliers } = renderHook(
      () => useQualityOutliers({ page: 1, limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Assert: All queries succeed
    await waitFor(() => {
      expect(quality1.current.isSuccess).toBe(true);
      expect(quality2.current.isSuccess).toBe(true);
      expect(outliers.current.isSuccess).toBe(true);
    });

    expect(quality1.current.data?.id).toBe(resourceId1);
    expect(quality2.current.data?.id).toBe(resourceId2);
    expect(outliers.current.data).toHaveLength(2);
  });
});
