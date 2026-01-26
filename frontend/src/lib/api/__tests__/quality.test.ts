/**
 * Quality API Client Tests
 * 
 * Tests for quality-related API endpoints in the editor API client.
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 8.1 Create quality API client methods
 * Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { editorApi } from '../editor';
import type {
  QualityRecalculateRequest,
  QualityOutliersParams,
  ReviewQueueParams,
} from '@/types/api';

// ============================================================================
// Mock Server Setup
// ============================================================================

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// ============================================================================
// Test Data
// ============================================================================

const mockQualityDetails = {
  resource_id: 'resource-1',
  quality_dimensions: {
    accuracy: 0.85,
    completeness: 0.90,
    consistency: 0.88,
    timeliness: 0.75,
    relevance: 0.92,
  },
  quality_overall: 0.86,
  quality_weights: {
    accuracy: 0.30,
    completeness: 0.25,
    consistency: 0.20,
    timeliness: 0.15,
    relevance: 0.10,
  },
  quality_last_computed: '2024-01-01T10:00:00Z',
  is_quality_outlier: false,
  needs_quality_review: false,
};

const mockQualityOutliers = {
  total: 15,
  page: 1,
  limit: 50,
  outliers: [
    {
      resource_id: 'resource-1',
      title: 'Low Quality Resource',
      quality_overall: 0.35,
      outlier_score: -2.5,
      outlier_reasons: ['low_completeness', 'inconsistent_metadata'],
      needs_quality_review: true,
    },
  ],
};

const mockQualityDegradation = {
  time_window_days: 30,
  degraded_count: 5,
  degraded_resources: [
    {
      resource_id: 'resource-1',
      title: 'Degraded Resource',
      old_quality: 0.85,
      new_quality: 0.65,
      degradation_pct: 23.5,
    },
  ],
};

const mockQualityDistribution = {
  dimension: 'overall',
  bins: 10,
  distribution: [
    { range: '0.0-0.1', count: 5 },
    { range: '0.1-0.2', count: 8 },
    { range: '0.8-0.9', count: 45 },
    { range: '0.9-1.0', count: 32 },
  ],
  statistics: {
    mean: 0.78,
    median: 0.82,
    std_dev: 0.15,
  },
};

const mockQualityTrends = {
  dimension: 'overall',
  granularity: 'weekly' as const,
  data_points: [
    {
      period: '2024-W01',
      avg_quality: 0.82,
      resource_count: 45,
    },
    {
      period: '2024-W02',
      avg_quality: 0.85,
      resource_count: 52,
    },
  ],
};

const mockQualityDimensions = {
  dimensions: {
    accuracy: { avg: 0.85, min: 0.45, max: 1.0 },
    completeness: { avg: 0.88, min: 0.50, max: 1.0 },
    consistency: { avg: 0.82, min: 0.40, max: 1.0 },
    timeliness: { avg: 0.75, min: 0.30, max: 1.0 },
    relevance: { avg: 0.90, min: 0.55, max: 1.0 },
  },
  overall: { avg: 0.84, min: 0.42, max: 1.0 },
  total_resources: 1250,
};

const mockReviewQueue = {
  total: 25,
  page: 1,
  limit: 50,
  review_queue: [
    {
      resource_id: 'resource-1',
      title: 'Needs Review',
      quality_overall: 0.35,
      is_quality_outlier: true,
      outlier_score: -2.5,
      outlier_reasons: ['low_completeness', 'inconsistent_metadata'],
      quality_last_computed: '2024-01-01T10:00:00Z',
    },
  ],
};

// ============================================================================
// Tests
// ============================================================================

describe('Quality API Client', () => {
  describe('recalculateQuality', () => {
    it('should trigger quality recalculation for a single resource', async () => {
      // Requirement 5.2: Recalculate quality endpoint
      server.use(
        http.post('*/quality/recalculate', () => {
          return HttpResponse.json({
            status: 'accepted',
            message: 'Quality computation queued for 1 resource(s)',
          });
        })
      );

      const request: QualityRecalculateRequest = {
        resource_id: 'resource-1',
      };

      const result = await editorApi.recalculateQuality(request);

      expect(result).toBeDefined();
      expect(result.resource_id).toBe('resource-1');
    });

    it('should trigger quality recalculation for multiple resources', async () => {
      // Requirement 5.2: Recalculate quality endpoint
      server.use(
        http.post('*/quality/recalculate', () => {
          return HttpResponse.json({
            status: 'accepted',
            message: 'Quality computation queued for 2 resource(s)',
          });
        })
      );

      const request: QualityRecalculateRequest = {
        resource_ids: ['resource-1', 'resource-2'],
      };

      const result = await editorApi.recalculateQuality(request);

      expect(result).toBeDefined();
    });

    it('should include custom weights in recalculation request', async () => {
      // Requirement 5.2: Recalculate quality endpoint
      let capturedRequest: any;

      server.use(
        http.post('*/quality/recalculate', async ({ request }) => {
          capturedRequest = await request.json();
          return HttpResponse.json({
            status: 'accepted',
            message: 'Quality computation queued',
          });
        })
      );

      const request: QualityRecalculateRequest = {
        resource_id: 'resource-1',
        weights: {
          accuracy: 0.4,
          completeness: 0.3,
          consistency: 0.15,
          timeliness: 0.1,
          relevance: 0.05,
        },
      };

      await editorApi.recalculateQuality(request);

      expect(capturedRequest.weights).toEqual(request.weights);
    });
  });

  describe('getQualityOutliers', () => {
    it('should fetch quality outliers with default parameters', async () => {
      // Requirement 5.3: Get quality outliers endpoint
      server.use(
        http.get('*/quality/outliers', () => {
          return HttpResponse.json(mockQualityOutliers);
        })
      );

      const result = await editorApi.getQualityOutliers();

      expect(result).toHaveLength(1);
      expect(result[0].resource_id).toBe('resource-1');
      expect(result[0].outlier_score).toBe(-2.5);
      expect(result[0].needs_quality_review).toBe(true);
    });

    it('should fetch quality outliers with pagination', async () => {
      // Requirement 5.3: Get quality outliers endpoint
      server.use(
        http.get('*/quality/outliers', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('page')).toBe('2');
          expect(url.searchParams.get('limit')).toBe('20');
          return HttpResponse.json(mockQualityOutliers);
        })
      );

      const params: QualityOutliersParams = {
        page: 2,
        limit: 20,
      };

      await editorApi.getQualityOutliers(params);
    });

    it('should filter outliers by minimum score', async () => {
      // Requirement 5.3: Get quality outliers endpoint
      server.use(
        http.get('*/quality/outliers', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('min_outlier_score')).toBe('-2.0');
          return HttpResponse.json(mockQualityOutliers);
        })
      );

      const params: QualityOutliersParams = {
        min_outlier_score: -2.0,
      };

      await editorApi.getQualityOutliers(params);
    });
  });

  describe('getQualityDegradation', () => {
    it('should fetch quality degradation for specified time window', async () => {
      // Requirement 5.4: Get quality degradation endpoint
      server.use(
        http.get('*/quality/degradation', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('days')).toBe('30');
          return HttpResponse.json(mockQualityDegradation);
        })
      );

      const result = await editorApi.getQualityDegradation(30);

      expect(result.time_window_days).toBe(30);
      expect(result.degraded_count).toBe(5);
      expect(result.degraded_resources).toHaveLength(1);
      expect(result.degraded_resources[0].degradation_pct).toBe(23.5);
    });
  });

  describe('getQualityDistribution', () => {
    it('should fetch quality distribution histogram', async () => {
      // Requirement 5.5: Get quality distribution endpoint
      server.use(
        http.get('*/quality/distribution', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('bins')).toBe('10');
          return HttpResponse.json(mockQualityDistribution);
        })
      );

      const result = await editorApi.getQualityDistribution(10);

      expect(result.dimension).toBe('overall');
      expect(result.bins).toBe(10);
      expect(result.distribution).toHaveLength(4);
      expect(result.statistics.mean).toBe(0.78);
    });
  });

  describe('getQualityTrends', () => {
    it('should fetch quality trends with daily granularity', async () => {
      // Requirement 5.6: Get quality trends endpoint
      server.use(
        http.get('*/quality/trends', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('granularity')).toBe('daily');
          return HttpResponse.json({
            ...mockQualityTrends,
            granularity: 'daily',
          });
        })
      );

      const result = await editorApi.getQualityTrends('daily');

      expect(result.granularity).toBe('daily');
      expect(result.data_points).toBeDefined();
    });

    it('should fetch quality trends with weekly granularity', async () => {
      // Requirement 5.6: Get quality trends endpoint
      server.use(
        http.get('*/quality/trends', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('granularity')).toBe('weekly');
          return HttpResponse.json(mockQualityTrends);
        })
      );

      const result = await editorApi.getQualityTrends('weekly');

      expect(result.granularity).toBe('weekly');
      expect(result.data_points).toHaveLength(2);
    });

    it('should fetch quality trends with monthly granularity', async () => {
      // Requirement 5.6: Get quality trends endpoint
      server.use(
        http.get('*/quality/trends', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('granularity')).toBe('monthly');
          return HttpResponse.json({
            ...mockQualityTrends,
            granularity: 'monthly',
          });
        })
      );

      const result = await editorApi.getQualityTrends('monthly');

      expect(result.granularity).toBe('monthly');
    });
  });

  describe('getQualityDimensions', () => {
    it('should fetch quality dimension scores', async () => {
      // Requirement 5.7: Get quality dimensions endpoint
      server.use(
        http.get('*/quality/dimensions', () => {
          return HttpResponse.json(mockQualityDimensions);
        })
      );

      const result = await editorApi.getQualityDimensions();

      expect(result.dimensions).toBeDefined();
      expect(result.dimensions.accuracy.avg).toBe(0.85);
      expect(result.dimensions.completeness.avg).toBe(0.88);
      expect(result.overall.avg).toBe(0.84);
      expect(result.total_resources).toBe(1250);
    });
  });

  describe('getQualityReviewQueue', () => {
    it('should fetch quality review queue with default parameters', async () => {
      // Requirement 5.8: Get quality review queue endpoint
      server.use(
        http.get('*/quality/review-queue', () => {
          return HttpResponse.json(mockReviewQueue);
        })
      );

      const result = await editorApi.getQualityReviewQueue();

      expect(result).toHaveLength(1);
      expect(result[0].resource_id).toBe('resource-1');
      expect(result[0].needs_quality_review).toBe(true);
    });

    it('should fetch quality review queue with pagination', async () => {
      // Requirement 5.8: Get quality review queue endpoint
      server.use(
        http.get('*/quality/review-queue', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('page')).toBe('2');
          expect(url.searchParams.get('limit')).toBe('25');
          return HttpResponse.json(mockReviewQueue);
        })
      );

      const params: ReviewQueueParams = {
        page: 2,
        limit: 25,
      };

      await editorApi.getQualityReviewQueue(params);
    });

    it('should sort review queue by specified field', async () => {
      // Requirement 5.8: Get quality review queue endpoint
      server.use(
        http.get('*/quality/review-queue', ({ request }) => {
          const url = new URL(request.url);
          expect(url.searchParams.get('sort_by')).toBe('quality_overall');
          return HttpResponse.json(mockReviewQueue);
        })
      );

      const params: ReviewQueueParams = {
        sort_by: 'quality_overall',
      };

      await editorApi.getQualityReviewQueue(params);
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors gracefully', async () => {
      server.use(
        http.get('*/quality/outliers', () => {
          return HttpResponse.json(
            { detail: 'Not found' },
            { status: 404 }
          );
        })
      );

      await expect(editorApi.getQualityOutliers()).rejects.toThrow();
    });

    it('should handle 500 errors gracefully', async () => {
      server.use(
        http.get('*/quality/dimensions', () => {
          return HttpResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
          );
        })
      );

      await expect(editorApi.getQualityDimensions()).rejects.toThrow();
    });

    it('should handle network errors gracefully', async () => {
      server.use(
        http.get('*/quality/trends', () => {
          return HttpResponse.error();
        })
      );

      await expect(editorApi.getQualityTrends('weekly')).rejects.toThrow();
    });
  });
});
