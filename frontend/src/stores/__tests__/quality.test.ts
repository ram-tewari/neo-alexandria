import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useQualityStore } from '../quality';
import type { QualityDetails } from '@/features/editor/types';

/**
 * Unit Tests for Quality Store
 * 
 * Feature: phase2-living-code-editor
 * Tests state updates, caching logic, and badge visibility
 * Validates: Requirements 3.1, 3.2
 */

describe('Quality Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to initial state
    useQualityStore.setState({
      qualityData: null,
      qualityCache: {},
      badgeVisibility: true,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Basic State Management', () => {
    it('should set quality data', () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setQualityData(mockQuality);

      expect(useQualityStore.getState().qualityData).toEqual(mockQuality);
    });

    it('should clear quality data', () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setQualityData(mockQuality);
      useQualityStore.getState().setQualityData(null);

      expect(useQualityStore.getState().qualityData).toBeNull();
    });
  });

  describe('Badge Visibility', () => {
    it('should toggle badge visibility', () => {
      expect(useQualityStore.getState().badgeVisibility).toBe(true);

      useQualityStore.getState().toggleBadgeVisibility();
      expect(useQualityStore.getState().badgeVisibility).toBe(false);

      useQualityStore.getState().toggleBadgeVisibility();
      expect(useQualityStore.getState().badgeVisibility).toBe(true);
    });

    it('should set badge visibility', () => {
      useQualityStore.getState().setBadgeVisibility(false);
      expect(useQualityStore.getState().badgeVisibility).toBe(false);

      useQualityStore.getState().setBadgeVisibility(true);
      expect(useQualityStore.getState().badgeVisibility).toBe(true);
    });

    it('should persist badge visibility to localStorage', async () => {
      useQualityStore.getState().setBadgeVisibility(false);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('quality-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.badgeVisibility).toBe(false);
      }
    });
  });

  describe('Quality Caching', () => {
    it('should cache quality data for a resource', () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setCachedQuality('resource-1', mockQuality);

      const cached = useQualityStore.getState().getCachedQuality('resource-1');
      expect(cached).toEqual(mockQuality);
    });

    it('should return null for uncached resource', () => {
      const cached = useQualityStore.getState().getCachedQuality('resource-999');
      expect(cached).toBeNull();
    });

    it('should clear all cached quality data', () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setCachedQuality('resource-1', mockQuality);
      useQualityStore.getState().setCachedQuality('resource-2', mockQuality);
      useQualityStore.getState().clearCache();

      expect(useQualityStore.getState().qualityCache).toEqual({});
    });

    it('should persist quality cache to localStorage', async () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setCachedQuality('resource-1', mockQuality);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('quality-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.qualityCache['resource-1']).toEqual(mockQuality);
      }
    });
  });

  describe('Fetch Quality Data', () => {
    it('should fetch quality data and update state', async () => {
      await useQualityStore.getState().fetchQualityData('resource-1');

      expect(useQualityStore.getState().isLoading).toBe(false);
      expect(useQualityStore.getState().qualityData).toBeNull();
    });

    it('should use cached quality data if available', async () => {
      const mockQuality: QualityDetails = {
        resource_id: 'resource-1',
        quality_dimensions: {
          accuracy: 0.9,
          completeness: 0.85,
          consistency: 0.95,
          timeliness: 0.8,
          relevance: 0.88,
        },
        quality_overall: 0.876,
        quality_weights: {
          accuracy: 0.3,
          completeness: 0.25,
          consistency: 0.2,
          timeliness: 0.15,
          relevance: 0.1,
        },
        quality_last_computed: '2024-01-01T00:00:00Z',
        is_quality_outlier: false,
        needs_quality_review: false,
      };

      useQualityStore.getState().setCachedQuality('resource-1', mockQuality);
      await useQualityStore.getState().fetchQualityData('resource-1');

      expect(useQualityStore.getState().qualityData).toEqual(mockQuality);
      expect(useQualityStore.getState().isLoading).toBe(false);
    });
  });
});
