/**
 * Scholarly API Client Tests
 * 
 * Tests for the scholarly API client functions including:
 * - Equation fetching
 * - Table fetching
 * - Metadata fetching
 * - Completeness statistics
 * - Health check
 * - Error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { scholarlyApi, scholarlyQueryKeys, scholarlyCacheConfig } from '../scholarly';
import { apiClient } from '@/core/api/client';
import type { Equation, Table, Metadata, CompletenessStats } from '@/types/library';

// Mock the API client
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('scholarlyApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Equation Tests
  // ==========================================================================

  describe('getEquations', () => {
    it('should fetch equations for a resource', async () => {
      const mockEquations: Equation[] = [
        {
          id: 'eq_1',
          resource_id: 'res_123',
          equation_number: 1,
          latex_source: 'E = mc^2',
          rendered_html: '<span>E = mc²</span>',
          page_number: 5,
          is_inline: false,
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 'eq_2',
          resource_id: 'res_123',
          equation_number: 2,
          latex_source: 'F = ma',
          rendered_html: '<span>F = ma</span>',
          page_number: 7,
          is_inline: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockEquations,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getEquations('res_123');

      expect(apiClient.get).toHaveBeenCalledWith('/scholarly/resources/res_123/equations');
      expect(result).toEqual(mockEquations);
      expect(result).toHaveLength(2);
      expect(result[0].latex_source).toBe('E = mc^2');
    });

    it('should handle object response format with equations array', async () => {
      const mockEquations: Equation[] = [
        {
          id: 'eq_1',
          resource_id: 'res_123',
          equation_number: 1,
          latex_source: 'E = mc^2',
          is_inline: false,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({
        data: { equations: mockEquations, total: 1 },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getEquations('res_123');

      expect(result).toEqual(mockEquations);
      expect(result).toHaveLength(1);
    });

    it('should return empty array when no equations found', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({
        data: [],
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getEquations('res_123');

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      await expect(scholarlyApi.getEquations('res_123')).rejects.toThrow('Network error');
    });
  });

  // ==========================================================================
  // Table Tests
  // ==========================================================================

  describe('getTables', () => {
    it('should fetch tables for a resource', async () => {
      const mockTables: Table[] = [
        {
          id: 'tbl_1',
          resource_id: 'res_123',
          table_number: 1,
          caption: 'Experimental Results',
          headers: ['Trial', 'Result', 'Error'],
          rows: [
            ['1', '42.5', '±0.2'],
            ['2', '43.1', '±0.3'],
          ],
          page_number: 10,
          format: 'csv',
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockTables,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getTables('res_123');

      expect(apiClient.get).toHaveBeenCalledWith('/scholarly/resources/res_123/tables');
      expect(result).toEqual(mockTables);
      expect(result).toHaveLength(1);
      expect(result[0].caption).toBe('Experimental Results');
      expect(result[0].headers).toHaveLength(3);
      expect(result[0].rows).toHaveLength(2);
    });

    it('should handle object response format with tables array', async () => {
      const mockTables: Table[] = [
        {
          id: 'tbl_1',
          resource_id: 'res_123',
          table_number: 1,
          headers: ['A', 'B'],
          rows: [['1', '2']],
          format: 'json',
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({
        data: { tables: mockTables, total: 1 },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getTables('res_123');

      expect(result).toEqual(mockTables);
      expect(result).toHaveLength(1);
    });

    it('should return empty array when no tables found', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({
        data: [],
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getTables('res_123');

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      await expect(scholarlyApi.getTables('res_123')).rejects.toThrow('Network error');
    });
  });

  // ==========================================================================
  // Metadata Tests
  // ==========================================================================

  describe('getMetadata', () => {
    it('should fetch metadata for a resource', async () => {
      const mockMetadata: Metadata = {
        resource_id: 'res_123',
        title: 'Introduction to Quantum Mechanics',
        authors: ['John Doe', 'Jane Smith'],
        publication_date: '2023-01-15',
        publisher: 'Academic Press',
        doi: '10.1234/example.doi',
        isbn: '978-0-123456-78-9',
        abstract: 'This paper introduces fundamental concepts...',
        keywords: ['quantum', 'mechanics', 'physics'],
        citations: ['ref1', 'ref2', 'ref3'],
        references: ['bib1', 'bib2'],
        completeness_score: 85,
        missing_fields: ['contributor', 'coverage'],
        last_updated: '2024-01-01T00:00:00Z',
      };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockMetadata,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getMetadata('res_123');

      expect(apiClient.get).toHaveBeenCalledWith('/scholarly/metadata/res_123');
      expect(result).toEqual(mockMetadata);
      expect(result.title).toBe('Introduction to Quantum Mechanics');
      expect(result.authors).toHaveLength(2);
      expect(result.completeness_score).toBe(85);
      expect(result.missing_fields).toContain('contributor');
    });

    it('should handle partial metadata', async () => {
      const mockMetadata: Metadata = {
        resource_id: 'res_123',
        title: 'Untitled Document',
        completeness_score: 20,
        missing_fields: ['authors', 'publication_date', 'doi', 'abstract'],
        last_updated: '2024-01-01T00:00:00Z',
      };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockMetadata,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getMetadata('res_123');

      expect(result.completeness_score).toBe(20);
      expect(result.missing_fields).toHaveLength(4);
    });

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Resource not found'));

      await expect(scholarlyApi.getMetadata('res_123')).rejects.toThrow('Resource not found');
    });
  });

  // ==========================================================================
  // Completeness Stats Tests
  // ==========================================================================

  describe('getCompletenessStats', () => {
    it('should fetch completeness statistics', async () => {
      const mockStats: CompletenessStats = {
        total_resources: 150,
        avg_completeness: 72.5,
        completeness_distribution: [
          { range: '0-20', count: 10 },
          { range: '20-40', count: 15 },
          { range: '40-60', count: 30 },
          { range: '60-80', count: 50 },
          { range: '80-100', count: 45 },
        ],
        most_missing_fields: [
          { field: 'doi', missing_count: 80 },
          { field: 'abstract', missing_count: 60 },
          { field: 'keywords', missing_count: 45 },
        ],
      };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockStats,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getCompletenessStats();

      expect(apiClient.get).toHaveBeenCalledWith('/scholarly/metadata/completeness-stats');
      expect(result).toEqual(mockStats);
      expect(result.total_resources).toBe(150);
      expect(result.avg_completeness).toBe(72.5);
      expect(result.completeness_distribution).toHaveLength(5);
      expect(result.most_missing_fields).toHaveLength(3);
      expect(result.most_missing_fields[0].field).toBe('doi');
    });

    it('should handle empty statistics', async () => {
      const mockStats: CompletenessStats = {
        total_resources: 0,
        avg_completeness: 0,
        completeness_distribution: [],
        most_missing_fields: [],
      };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockStats,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.getCompletenessStats();

      expect(result.total_resources).toBe(0);
      expect(result.completeness_distribution).toHaveLength(0);
    });

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Service unavailable'));

      await expect(scholarlyApi.getCompletenessStats()).rejects.toThrow('Service unavailable');
    });
  });

  // ==========================================================================
  // Health Check Tests
  // ==========================================================================

  describe('health', () => {
    it('should check scholarly module health', async () => {
      const mockHealth = { status: 'healthy' };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockHealth,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.health();

      expect(apiClient.get).toHaveBeenCalledWith('/scholarly/health');
      expect(result).toEqual(mockHealth);
      expect(result.status).toBe('healthy');
    });

    it('should handle unhealthy status', async () => {
      const mockHealth = { status: 'degraded' };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: mockHealth,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      });

      const result = await scholarlyApi.health();

      expect(result.status).toBe('degraded');
    });

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Connection refused'));

      await expect(scholarlyApi.health()).rejects.toThrow('Connection refused');
    });
  });
});

// ==========================================================================
// Query Key Tests
// ==========================================================================

describe('scholarlyQueryKeys', () => {
  it('should generate correct equation query keys', () => {
    expect(scholarlyQueryKeys.equations.all()).toEqual(['scholarly', 'equations']);
    expect(scholarlyQueryKeys.equations.detail('res_123')).toEqual([
      'scholarly',
      'equations',
      'res_123',
    ]);
  });

  it('should generate correct table query keys', () => {
    expect(scholarlyQueryKeys.tables.all()).toEqual(['scholarly', 'tables']);
    expect(scholarlyQueryKeys.tables.detail('res_123')).toEqual([
      'scholarly',
      'tables',
      'res_123',
    ]);
  });

  it('should generate correct metadata query keys', () => {
    expect(scholarlyQueryKeys.metadata.all()).toEqual(['scholarly', 'metadata']);
    expect(scholarlyQueryKeys.metadata.detail('res_123')).toEqual([
      'scholarly',
      'metadata',
      'res_123',
    ]);
    expect(scholarlyQueryKeys.metadata.stats()).toEqual([
      'scholarly',
      'metadata',
      'completeness-stats',
    ]);
  });

  it('should generate correct health query key', () => {
    expect(scholarlyQueryKeys.health()).toEqual(['scholarly', 'health']);
  });
});

// ==========================================================================
// Cache Configuration Tests
// ==========================================================================

describe('scholarlyCacheConfig', () => {
  it('should have correct cache times for equations', () => {
    expect(scholarlyCacheConfig.equations.staleTime).toBe(30 * 60 * 1000); // 30 minutes
    expect(scholarlyCacheConfig.equations.cacheTime).toBe(60 * 60 * 1000); // 1 hour
  });

  it('should have correct cache times for tables', () => {
    expect(scholarlyCacheConfig.tables.staleTime).toBe(30 * 60 * 1000); // 30 minutes
    expect(scholarlyCacheConfig.tables.cacheTime).toBe(60 * 60 * 1000); // 1 hour
  });

  it('should have correct cache times for metadata', () => {
    expect(scholarlyCacheConfig.metadata.staleTime).toBe(10 * 60 * 1000); // 10 minutes
    expect(scholarlyCacheConfig.metadata.cacheTime).toBe(30 * 60 * 1000); // 30 minutes
  });

  it('should have correct cache times for completeness stats', () => {
    expect(scholarlyCacheConfig.completenessStats.staleTime).toBe(60 * 60 * 1000); // 1 hour
    expect(scholarlyCacheConfig.completenessStats.cacheTime).toBe(2 * 60 * 60 * 1000); // 2 hours
  });

  it('should have correct cache times for health', () => {
    expect(scholarlyCacheConfig.health.staleTime).toBe(5 * 60 * 1000); // 5 minutes
    expect(scholarlyCacheConfig.health.cacheTime).toBe(10 * 60 * 1000); // 10 minutes
  });
});
