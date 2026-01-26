/**
 * API Client Interface Tests
 * 
 * Tests for API client interfaces, query key factories, and cache configuration.
 * 
 * Requirements:
 * - 7.1: Define TypeScript interfaces for all API request payloads
 * - 7.4: Export all types from a central types file
 */

import { describe, it, expect } from 'vitest';
import type { AxiosResponse } from 'axios';
import {
  type WorkbenchApi,
  type EditorApi,
  workbenchQueryKeys,
  editorQueryKeys,
  workbenchCacheConfig,
  editorCacheConfig,
} from '../types';

describe('API Client Interfaces', () => {
  describe('WorkbenchApi Interface', () => {
    it('should define all required authentication methods', () => {
      // Type-only test - ensures interface has correct shape
      const mockApi: WorkbenchApi = {
        getCurrentUser: async () => ({} as AxiosResponse),
        login: async () => ({} as AxiosResponse),
        refreshToken: async () => ({} as AxiosResponse),
        getRateLimit: async () => ({} as AxiosResponse),
        getResources: async () => ({} as AxiosResponse),
        createResource: async () => ({} as AxiosResponse),
        updateResource: async () => ({} as AxiosResponse),
        deleteResource: async () => ({} as AxiosResponse),
        getSystemHealth: async () => ({} as AxiosResponse),
        getAuthHealth: async () => ({} as AxiosResponse),
        getResourcesHealth: async () => ({} as AxiosResponse),
        getSystemMetrics: async () => ({} as AxiosResponse),
      };

      expect(mockApi).toBeDefined();
      expect(mockApi.getCurrentUser).toBeInstanceOf(Function);
      expect(mockApi.login).toBeInstanceOf(Function);
      expect(mockApi.refreshToken).toBeInstanceOf(Function);
      expect(mockApi.getRateLimit).toBeInstanceOf(Function);
    });

    it('should define all required resource methods', () => {
      const mockApi: WorkbenchApi = {
        getCurrentUser: async () => ({} as AxiosResponse),
        login: async () => ({} as AxiosResponse),
        refreshToken: async () => ({} as AxiosResponse),
        getRateLimit: async () => ({} as AxiosResponse),
        getResources: async () => ({} as AxiosResponse),
        createResource: async () => ({} as AxiosResponse),
        updateResource: async () => ({} as AxiosResponse),
        deleteResource: async () => ({} as AxiosResponse),
        getSystemHealth: async () => ({} as AxiosResponse),
        getAuthHealth: async () => ({} as AxiosResponse),
        getResourcesHealth: async () => ({} as AxiosResponse),
        getSystemMetrics: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getResources).toBeInstanceOf(Function);
      expect(mockApi.createResource).toBeInstanceOf(Function);
      expect(mockApi.updateResource).toBeInstanceOf(Function);
      expect(mockApi.deleteResource).toBeInstanceOf(Function);
    });

    it('should define all required health methods', () => {
      const mockApi: WorkbenchApi = {
        getCurrentUser: async () => ({} as AxiosResponse),
        login: async () => ({} as AxiosResponse),
        refreshToken: async () => ({} as AxiosResponse),
        getRateLimit: async () => ({} as AxiosResponse),
        getResources: async () => ({} as AxiosResponse),
        createResource: async () => ({} as AxiosResponse),
        updateResource: async () => ({} as AxiosResponse),
        deleteResource: async () => ({} as AxiosResponse),
        getSystemHealth: async () => ({} as AxiosResponse),
        getAuthHealth: async () => ({} as AxiosResponse),
        getResourcesHealth: async () => ({} as AxiosResponse),
        getSystemMetrics: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getSystemHealth).toBeInstanceOf(Function);
      expect(mockApi.getAuthHealth).toBeInstanceOf(Function);
      expect(mockApi.getResourcesHealth).toBeInstanceOf(Function);
      expect(mockApi.getSystemMetrics).toBeInstanceOf(Function);
    });
  });

  describe('EditorApi Interface', () => {
    it('should define all required resource content methods', () => {
      const mockApi: Partial<EditorApi> = {
        getResource: async () => ({} as AxiosResponse),
        getResourceStatus: async () => ({} as AxiosResponse),
        overrideClassification: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getResource).toBeInstanceOf(Function);
      expect(mockApi.getResourceStatus).toBeInstanceOf(Function);
      expect(mockApi.overrideClassification).toBeInstanceOf(Function);
    });

    it('should define all required chunk methods', () => {
      const mockApi: Partial<EditorApi> = {
        getChunks: async () => ({} as AxiosResponse),
        getChunk: async () => ({} as AxiosResponse),
        triggerChunking: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getChunks).toBeInstanceOf(Function);
      expect(mockApi.getChunk).toBeInstanceOf(Function);
      expect(mockApi.triggerChunking).toBeInstanceOf(Function);
    });

    it('should define all required annotation methods', () => {
      const mockApi: Partial<EditorApi> = {
        createAnnotation: async () => ({} as AxiosResponse),
        getAnnotations: async () => ({} as AxiosResponse),
        getAnnotation: async () => ({} as AxiosResponse),
        updateAnnotation: async () => ({} as AxiosResponse),
        deleteAnnotation: async () => ({} as AxiosResponse),
        searchAnnotationsFulltext: async () => ({} as AxiosResponse),
        searchAnnotationsSemantic: async () => ({} as AxiosResponse),
        searchAnnotationsByTags: async () => ({} as AxiosResponse),
        exportAnnotationsMarkdown: async () => ({} as AxiosResponse),
        exportAnnotationsJSON: async () => ({} as AxiosResponse),
      };

      expect(mockApi.createAnnotation).toBeInstanceOf(Function);
      expect(mockApi.getAnnotations).toBeInstanceOf(Function);
      expect(mockApi.getAnnotation).toBeInstanceOf(Function);
      expect(mockApi.updateAnnotation).toBeInstanceOf(Function);
      expect(mockApi.deleteAnnotation).toBeInstanceOf(Function);
      expect(mockApi.searchAnnotationsFulltext).toBeInstanceOf(Function);
      expect(mockApi.searchAnnotationsSemantic).toBeInstanceOf(Function);
      expect(mockApi.searchAnnotationsByTags).toBeInstanceOf(Function);
      expect(mockApi.exportAnnotationsMarkdown).toBeInstanceOf(Function);
      expect(mockApi.exportAnnotationsJSON).toBeInstanceOf(Function);
    });

    it('should define all required quality methods', () => {
      const mockApi: Partial<EditorApi> = {
        getQualityDetails: async () => ({} as AxiosResponse),
        recalculateQuality: async () => ({} as AxiosResponse),
        getQualityOutliers: async () => ({} as AxiosResponse),
        getQualityDegradation: async () => ({} as AxiosResponse),
        getQualityDistribution: async () => ({} as AxiosResponse),
        getQualityTrends: async () => ({} as AxiosResponse),
        getQualityDimensions: async () => ({} as AxiosResponse),
        getQualityReviewQueue: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getQualityDetails).toBeInstanceOf(Function);
      expect(mockApi.recalculateQuality).toBeInstanceOf(Function);
      expect(mockApi.getQualityOutliers).toBeInstanceOf(Function);
      expect(mockApi.getQualityDegradation).toBeInstanceOf(Function);
      expect(mockApi.getQualityDistribution).toBeInstanceOf(Function);
      expect(mockApi.getQualityTrends).toBeInstanceOf(Function);
      expect(mockApi.getQualityDimensions).toBeInstanceOf(Function);
      expect(mockApi.getQualityReviewQueue).toBeInstanceOf(Function);
    });

    it('should define hover method', () => {
      const mockApi: Partial<EditorApi> = {
        getHoverInfo: async () => ({} as AxiosResponse),
      };

      expect(mockApi.getHoverInfo).toBeInstanceOf(Function);
    });
  });
});

describe('Query Key Factories', () => {
  describe('workbenchQueryKeys', () => {
    it('should generate correct base keys', () => {
      expect(workbenchQueryKeys.all).toEqual(['workbench']);
      expect(workbenchQueryKeys.user()).toEqual(['workbench', 'user']);
      expect(workbenchQueryKeys.resources()).toEqual(['workbench', 'resources']);
      expect(workbenchQueryKeys.health()).toEqual(['workbench', 'health']);
    });

    it('should generate correct user keys', () => {
      expect(workbenchQueryKeys.currentUser()).toEqual(['workbench', 'user', 'current']);
      expect(workbenchQueryKeys.rateLimit()).toEqual(['workbench', 'user', 'rateLimit']);
    });

    it('should generate correct resource keys', () => {
      expect(workbenchQueryKeys.resourceList()).toEqual([
        'workbench',
        'resources',
        'list',
        undefined,
      ]);
      expect(workbenchQueryKeys.resourceList({ limit: 25 })).toEqual([
        'workbench',
        'resources',
        'list',
        { limit: 25 },
      ]);
      expect(workbenchQueryKeys.resource('resource-1')).toEqual([
        'workbench',
        'resources',
        'detail',
        'resource-1',
      ]);
    });

    it('should generate correct health keys', () => {
      expect(workbenchQueryKeys.systemHealth()).toEqual(['workbench', 'health', 'system']);
      expect(workbenchQueryKeys.authHealth()).toEqual(['workbench', 'health', 'auth']);
      expect(workbenchQueryKeys.resourcesHealth()).toEqual([
        'workbench',
        'health',
        'resources',
      ]);
      expect(workbenchQueryKeys.systemMetrics()).toEqual(['workbench', 'health', 'metrics']);
    });

    it('should support hierarchical invalidation', () => {
      // Invalidating 'workbench' should invalidate all workbench queries
      const allKey = workbenchQueryKeys.all;
      const userKey = workbenchQueryKeys.currentUser();
      const resourceKey = workbenchQueryKeys.resource('resource-1');

      expect(userKey[0]).toBe(allKey[0]);
      expect(resourceKey[0]).toBe(allKey[0]);
    });
  });

  describe('editorQueryKeys', () => {
    it('should generate correct base keys', () => {
      expect(editorQueryKeys.all).toEqual(['editor']);
      expect(editorQueryKeys.resources()).toEqual(['editor', 'resources']);
      expect(editorQueryKeys.chunks()).toEqual(['editor', 'chunks']);
      expect(editorQueryKeys.annotations()).toEqual(['editor', 'annotations']);
      expect(editorQueryKeys.quality()).toEqual(['editor', 'quality']);
      expect(editorQueryKeys.graph()).toEqual(['editor', 'graph']);
    });

    it('should generate correct resource keys', () => {
      expect(editorQueryKeys.resource('resource-1')).toEqual([
        'editor',
        'resources',
        'resource-1',
      ]);
      expect(editorQueryKeys.resourceStatus('resource-1')).toEqual([
        'editor',
        'resources',
        'resource-1',
        'status',
      ]);
    });

    it('should generate correct chunk keys', () => {
      expect(editorQueryKeys.chunkList('resource-1')).toEqual([
        'editor',
        'chunks',
        'list',
        'resource-1',
      ]);
      expect(editorQueryKeys.chunk('chunk-1')).toEqual(['editor', 'chunks', 'detail', 'chunk-1']);
    });

    it('should generate correct annotation keys', () => {
      expect(editorQueryKeys.annotationList('resource-1')).toEqual([
        'editor',
        'annotations',
        'list',
        'resource-1',
        undefined,
      ]);
      expect(editorQueryKeys.annotationList('resource-1', { page: 1, limit: 25 })).toEqual([
        'editor',
        'annotations',
        'list',
        'resource-1',
        { page: 1, limit: 25 },
      ]);
      expect(editorQueryKeys.annotation('annotation-1')).toEqual([
        'editor',
        'annotations',
        'detail',
        'annotation-1',
      ]);
    });

    it('should generate correct annotation search keys', () => {
      const searchParams = { query: 'test', limit: 10 };
      expect(editorQueryKeys.annotationSearch(searchParams)).toEqual([
        'editor',
        'annotations',
        'search',
        searchParams,
      ]);
      expect(editorQueryKeys.annotationSearchSemantic(searchParams)).toEqual([
        'editor',
        'annotations',
        'search',
        'semantic',
        searchParams,
      ]);
      expect(editorQueryKeys.annotationSearchTags({ tags: ['important'] })).toEqual([
        'editor',
        'annotations',
        'search',
        'tags',
        { tags: ['important'] },
      ]);
    });

    it('should generate correct quality keys', () => {
      expect(editorQueryKeys.qualityDetails('resource-1')).toEqual([
        'editor',
        'quality',
        'details',
        'resource-1',
      ]);
      expect(editorQueryKeys.qualityOutliers()).toEqual([
        'editor',
        'quality',
        'outliers',
        undefined,
      ]);
      expect(editorQueryKeys.qualityDegradation(7)).toEqual([
        'editor',
        'quality',
        'degradation',
        7,
      ]);
      expect(editorQueryKeys.qualityDistribution('accuracy', 10)).toEqual([
        'editor',
        'quality',
        'distribution',
        'accuracy',
        10,
      ]);
      expect(editorQueryKeys.qualityTrends('accuracy', 'daily')).toEqual([
        'editor',
        'quality',
        'trends',
        'accuracy',
        'daily',
      ]);
      expect(editorQueryKeys.qualityDimensions()).toEqual(['editor', 'quality', 'dimensions']);
      expect(editorQueryKeys.qualityReviewQueue()).toEqual([
        'editor',
        'quality',
        'reviewQueue',
        undefined,
      ]);
    });

    it('should generate correct hover keys', () => {
      const hoverParams = {
        resource_id: 'resource-1',
        symbol: 'myFunction',
        line: 10,
        column: 5,
      };
      expect(editorQueryKeys.hover(hoverParams)).toEqual(['editor', 'graph', 'hover', hoverParams]);
    });

    it('should support hierarchical invalidation', () => {
      // Invalidating 'editor' should invalidate all editor queries
      const allKey = editorQueryKeys.all;
      const resourceKey = editorQueryKeys.resource('resource-1');
      const annotationKey = editorQueryKeys.annotation('annotation-1');

      expect(resourceKey[0]).toBe(allKey[0]);
      expect(annotationKey[0]).toBe(allKey[0]);
    });
  });
});

describe('Cache Configuration', () => {
  describe('workbenchCacheConfig', () => {
    it('should define user cache configuration', () => {
      expect(workbenchCacheConfig.user).toBeDefined();
      expect(workbenchCacheConfig.user.staleTime).toBe(5 * 60 * 1000); // 5 minutes
      expect(workbenchCacheConfig.user.cacheTime).toBe(10 * 60 * 1000); // 10 minutes
    });

    it('should define resources cache configuration', () => {
      expect(workbenchCacheConfig.resources).toBeDefined();
      expect(workbenchCacheConfig.resources.staleTime).toBe(2 * 60 * 1000); // 2 minutes
      expect(workbenchCacheConfig.resources.cacheTime).toBe(10 * 60 * 1000); // 10 minutes
    });

    it('should define health cache configuration with polling', () => {
      expect(workbenchCacheConfig.health).toBeDefined();
      expect(workbenchCacheConfig.health.staleTime).toBe(30 * 1000); // 30 seconds
      expect(workbenchCacheConfig.health.cacheTime).toBe(2 * 60 * 1000); // 2 minutes
      expect(workbenchCacheConfig.health.refetchInterval).toBe(30 * 1000); // 30 seconds
    });

    it('should have reasonable cache times', () => {
      // Stale time should be less than cache time
      expect(workbenchCacheConfig.user.staleTime).toBeLessThan(
        workbenchCacheConfig.user.cacheTime
      );
      expect(workbenchCacheConfig.resources.staleTime).toBeLessThan(
        workbenchCacheConfig.resources.cacheTime
      );
      expect(workbenchCacheConfig.health.staleTime).toBeLessThan(
        workbenchCacheConfig.health.cacheTime
      );
    });
  });

  describe('editorCacheConfig', () => {
    it('should define resources cache configuration', () => {
      expect(editorCacheConfig.resources).toBeDefined();
      expect(editorCacheConfig.resources.staleTime).toBe(10 * 60 * 1000); // 10 minutes
      expect(editorCacheConfig.resources.cacheTime).toBe(30 * 60 * 1000); // 30 minutes
    });

    it('should define chunks cache configuration', () => {
      expect(editorCacheConfig.chunks).toBeDefined();
      expect(editorCacheConfig.chunks.staleTime).toBe(10 * 60 * 1000); // 10 minutes
      expect(editorCacheConfig.chunks.cacheTime).toBe(30 * 60 * 1000); // 30 minutes
    });

    it('should define annotations cache configuration', () => {
      expect(editorCacheConfig.annotations).toBeDefined();
      expect(editorCacheConfig.annotations.staleTime).toBe(5 * 60 * 1000); // 5 minutes
      expect(editorCacheConfig.annotations.cacheTime).toBe(10 * 60 * 1000); // 10 minutes
    });

    it('should define quality cache configuration', () => {
      expect(editorCacheConfig.quality).toBeDefined();
      expect(editorCacheConfig.quality.staleTime).toBe(15 * 60 * 1000); // 15 minutes
      expect(editorCacheConfig.quality.cacheTime).toBe(30 * 60 * 1000); // 30 minutes
    });

    it('should define graph cache configuration', () => {
      expect(editorCacheConfig.graph).toBeDefined();
      expect(editorCacheConfig.graph.staleTime).toBe(30 * 60 * 1000); // 30 minutes
      expect(editorCacheConfig.graph.cacheTime).toBe(60 * 60 * 1000); // 60 minutes
    });

    it('should define hover cache configuration with debounce', () => {
      expect(editorCacheConfig.hover).toBeDefined();
      expect(editorCacheConfig.hover.staleTime).toBe(30 * 60 * 1000); // 30 minutes
      expect(editorCacheConfig.hover.cacheTime).toBe(60 * 60 * 1000); // 60 minutes
      expect(editorCacheConfig.hover.debounceMs).toBe(300); // 300ms
    });

    it('should have reasonable cache times', () => {
      // Stale time should be less than cache time
      expect(editorCacheConfig.resources.staleTime).toBeLessThan(
        editorCacheConfig.resources.cacheTime
      );
      expect(editorCacheConfig.chunks.staleTime).toBeLessThan(
        editorCacheConfig.chunks.cacheTime
      );
      expect(editorCacheConfig.annotations.staleTime).toBeLessThan(
        editorCacheConfig.annotations.cacheTime
      );
      expect(editorCacheConfig.quality.staleTime).toBeLessThan(
        editorCacheConfig.quality.cacheTime
      );
      expect(editorCacheConfig.graph.staleTime).toBeLessThan(
        editorCacheConfig.graph.cacheTime
      );
      expect(editorCacheConfig.hover.staleTime).toBeLessThan(
        editorCacheConfig.hover.cacheTime
      );
    });

    it('should have longer cache times for less frequently changing data', () => {
      // Graph data changes less frequently than annotations
      expect(editorCacheConfig.graph.staleTime).toBeGreaterThan(
        editorCacheConfig.annotations.staleTime
      );
      // Quality data changes less frequently than annotations
      expect(editorCacheConfig.quality.staleTime).toBeGreaterThan(
        editorCacheConfig.annotations.staleTime
      );
    });
  });
});

describe('Type Exports', () => {
  it('should export WorkbenchApi interface', () => {
    // This is a compile-time test - if it compiles, the export works
    const _test: WorkbenchApi = {} as WorkbenchApi;
    expect(_test).toBeDefined();
  });

  it('should export EditorApi interface', () => {
    // This is a compile-time test - if it compiles, the export works
    const _test: EditorApi = {} as EditorApi;
    expect(_test).toBeDefined();
  });

  it('should export query key factories', () => {
    expect(workbenchQueryKeys).toBeDefined();
    expect(editorQueryKeys).toBeDefined();
  });

  it('should export cache configurations', () => {
    expect(workbenchCacheConfig).toBeDefined();
    expect(editorCacheConfig).toBeDefined();
  });
});
