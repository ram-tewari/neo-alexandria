/**
 * Unit tests for resource API client
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '@/core/api/client';
import { fetchResources, ingestResource, getResourceStatus, getResource } from './api';
import { ResourceStatus, ReadStatus } from '@/core/types/resource';
import type { Resource, ResourceAccepted, ResourceStatusResponse } from '@/core/types/resource';

// Mock apiClient
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('Resource API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchResources', () => {
    it('should calculate offset correctly for page 1', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ page: 1, limit: 25 });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('offset=0')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('limit=25')
      );
    });

    it('should calculate offset correctly for page 2', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ page: 2, limit: 25 });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('offset=25')
      );
    });

    it('should calculate offset correctly for page 3 with limit 10', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ page: 3, limit: 10 });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('offset=20')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('limit=10')
      );
    });

    it('should parse sort parameter correctly', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ sort: 'created_at:desc' });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=created_at')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_dir=desc')
      );
    });

    it('should parse sort parameter with asc direction', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ sort: 'title:asc' });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=title')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_dir=asc')
      );
    });

    it('should default to desc when sort direction not specified', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({ sort: 'quality_score' });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=quality_score')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('sort_dir=desc')
      );
    });

    it('should include filter parameters', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources({
        q: 'test query',
        classification_code: 'A.1',
        min_quality: 0.7,
      });

      const callUrl = vi.mocked(apiClient.get).mock.calls[0][0];
      expect(callUrl).toContain('q=test+query');
      expect(callUrl).toContain('classification_code=A.1');
      expect(callUrl).toContain('min_quality=0.7');
    });

    it('should use default values when no params provided', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await fetchResources();

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('offset=0')
      );
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('limit=25')
      );
    });

    it('should return response data', async () => {
      const mockData = {
        items: [
          {
            id: '123',
            title: 'Test',
            ingestion_status: ResourceStatus.COMPLETED,
          } as Resource,
        ],
        total: 1,
      };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockData });

      const result = await fetchResources();

      expect(result).toEqual(mockData);
    });
  });

  describe('ingestResource', () => {
    it('should call POST /resources with payload', async () => {
      const mockResponse: ResourceAccepted = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Resource ingestion started',
      };
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const payload = {
        title: 'Test Resource',
        url: 'https://example.com',
      };

      const result = await ingestResource(payload);

      expect(apiClient.post).toHaveBeenCalledWith('/resources', payload);
      expect(result).toEqual(mockResponse);
    });

    it('should handle minimal payload', async () => {
      const mockResponse: ResourceAccepted = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Resource ingestion started',
      };
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const payload = {
        title: 'Test Resource',
      };

      await ingestResource(payload);

      expect(apiClient.post).toHaveBeenCalledWith('/resources', payload);
    });
  });

  describe('getResourceStatus', () => {
    it('should call GET /resources/:id/status', async () => {
      const mockResponse: ResourceStatusResponse = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        ingestion_status: ResourceStatus.PROCESSING,
        ingestion_error: null,
        ingestion_started_at: '2024-01-01T00:00:00Z',
        ingestion_completed_at: null,
      };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await getResourceStatus('123e4567-e89b-12d3-a456-426614174000');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/resources/123e4567-e89b-12d3-a456-426614174000/status'
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getResource', () => {
    it('should call GET /resources/:id', async () => {
      const mockResponse: Resource = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Test Resource',
        description: null,
        creator: null,
        publisher: null,
        contributor: null,
        date_created: null,
        date_modified: null,
        type: null,
        format: null,
        identifier: null,
        source: null,
        url: 'https://example.com',
        language: null,
        coverage: null,
        rights: null,
        subject: [],
        relation: [],
        classification_code: null,
        read_status: ReadStatus.UNREAD,
        quality_score: 0.0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: ResourceStatus.COMPLETED,
        ingestion_error: null,
        ingestion_started_at: '2024-01-01T00:00:00Z',
        ingestion_completed_at: '2024-01-01T00:00:05Z',
      };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await getResource('123e4567-e89b-12d3-a456-426614174000');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/resources/123e4567-e89b-12d3-a456-426614174000'
      );
      expect(result).toEqual(mockResponse);
    });
  });
});
