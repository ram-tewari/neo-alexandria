/**
 * Unit tests for resource type definitions
 */
import { describe, it, expect } from 'vitest';
import { ResourceStatus, ReadStatus } from './resource';
import type { Resource, ResourceListResponse, ResourceAccepted, ResourceStatusResponse, IngestResourcePayload } from './resource';

describe('Resource Type Definitions', () => {
  describe('ResourceStatus enum', () => {
    it('should have correct enum values', () => {
      expect(ResourceStatus.PENDING).toBe('pending');
      expect(ResourceStatus.PROCESSING).toBe('processing');
      expect(ResourceStatus.COMPLETED).toBe('completed');
      expect(ResourceStatus.FAILED).toBe('failed');
    });

    it('should have exactly 4 values', () => {
      const values = Object.values(ResourceStatus);
      expect(values).toHaveLength(4);
    });
  });

  describe('ReadStatus enum', () => {
    it('should have correct enum values', () => {
      expect(ReadStatus.UNREAD).toBe('unread');
      expect(ReadStatus.IN_PROGRESS).toBe('in_progress');
      expect(ReadStatus.COMPLETED).toBe('completed');
      expect(ReadStatus.ARCHIVED).toBe('archived');
    });

    it('should have exactly 4 values', () => {
      const values = Object.values(ReadStatus);
      expect(values).toHaveLength(4);
    });
  });

  describe('Resource interface', () => {
    it('should accept valid resource object', () => {
      const resource: Resource = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Test Resource',
        description: 'Test description',
        creator: 'Test Creator',
        publisher: null,
        contributor: null,
        date_created: null,
        date_modified: null,
        type: 'article',
        format: 'html',
        identifier: null,
        source: 'https://example.com',
        url: 'https://example.com',
        language: 'en',
        coverage: null,
        rights: null,
        subject: ['test', 'example'],
        relation: [],
        classification_code: 'A.1',
        read_status: ReadStatus.UNREAD,
        quality_score: 0.85,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: ResourceStatus.COMPLETED,
        ingestion_error: null,
        ingestion_started_at: '2024-01-01T00:00:00Z',
        ingestion_completed_at: '2024-01-01T00:00:05Z',
      };

      expect(resource.id).toBe('123e4567-e89b-12d3-a456-426614174000');
      expect(resource.title).toBe('Test Resource');
      expect(resource.ingestion_status).toBe(ResourceStatus.COMPLETED);
    });
  });

  describe('ResourceListResponse interface', () => {
    it('should accept valid list response', () => {
      const response: ResourceListResponse = {
        items: [],
        total: 0,
      };

      expect(response.items).toEqual([]);
      expect(response.total).toBe(0);
    });
  });

  describe('ResourceAccepted interface', () => {
    it('should accept valid accepted response', () => {
      const response: ResourceAccepted = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Resource ingestion started',
      };

      expect(response.id).toBe('123e4567-e89b-12d3-a456-426614174000');
      expect(response.message).toBe('Resource ingestion started');
    });
  });

  describe('ResourceStatusResponse interface', () => {
    it('should accept valid status response', () => {
      const response: ResourceStatusResponse = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        ingestion_status: ResourceStatus.PROCESSING,
        ingestion_error: null,
        ingestion_started_at: '2024-01-01T00:00:00Z',
        ingestion_completed_at: null,
      };

      expect(response.ingestion_status).toBe(ResourceStatus.PROCESSING);
      expect(response.ingestion_completed_at).toBeNull();
    });
  });

  describe('IngestResourcePayload interface', () => {
    it('should accept minimal payload', () => {
      const payload: IngestResourcePayload = {
        title: 'Test Resource',
      };

      expect(payload.title).toBe('Test Resource');
    });

    it('should accept full payload', () => {
      const payload: IngestResourcePayload = {
        title: 'Test Resource',
        source: 'https://example.com',
        url: 'https://example.com',
        description: 'Test description',
        type: 'article',
        format: 'html',
        language: 'en',
        subject: ['test'],
      };

      expect(payload.title).toBe('Test Resource');
      expect(payload.source).toBe('https://example.com');
      expect(payload.subject).toEqual(['test']);
    });
  });
});
