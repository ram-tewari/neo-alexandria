import { describe, it, expect } from 'vitest';
import { mapResourceToRepository } from '../repository';
import type { Resource } from '@/types/api';

/**
 * Unit Tests for Repository Store
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 3.3 Update workbench store to use real data
 * Validates: Requirements 2.2, 2.5, 2.6
 */

describe('Repository Store - mapResourceToRepository', () => {
  it('should map GitHub resource to repository', () => {
    const resource: Resource = {
      id: '1',
      title: 'neo-alexandria-2.0',
      description: 'Knowledge management system',
      url: 'https://github.com/example/neo-alexandria-2.0',
      language: 'TypeScript',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
      ingestion_status: 'completed',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository).toEqual({
      id: '1',
      name: 'neo-alexandria-2.0',
      source: 'github',
      url: 'https://github.com/example/neo-alexandria-2.0',
      description: 'Knowledge management system',
      language: 'TypeScript',
      lastUpdated: new Date('2024-01-15T00:00:00Z'),
      status: 'ready',
    });
  });

  it('should map GitLab resource to repository', () => {
    const resource: Resource = {
      id: '2',
      title: 'gitlab-project',
      url: 'https://gitlab.com/example/project',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
      ingestion_status: 'completed',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository.source).toBe('gitlab');
    expect(repository.status).toBe('ready');
  });

  it('should map local resource to repository', () => {
    const resource: Resource = {
      id: '3',
      title: 'local-project',
      file_path: '/path/to/local/project',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
      ingestion_status: 'completed',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository.source).toBe('local');
    expect(repository.status).toBe('ready');
  });

  it('should map ingestion status to repository status', () => {
    const statusMap: Array<[Resource['ingestion_status'], 'ready' | 'indexing' | 'error']> = [
      ['completed', 'ready'],
      ['processing', 'indexing'],
      ['pending', 'indexing'],
      ['failed', 'error'],
    ];

    statusMap.forEach(([ingestionStatus, expectedStatus]) => {
      const resource: Resource = {
        id: '1',
        title: 'Test Resource',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        ingestion_status: ingestionStatus,
      };

      const repository = mapResourceToRepository(resource);

      expect(repository.status).toBe(expectedStatus);
    });
  });

  it('should handle resource without optional fields', () => {
    const resource: Resource = {
      id: '1',
      title: 'Minimal Resource',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
      ingestion_status: 'completed',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository.id).toBe('1');
    expect(repository.name).toBe('Minimal Resource');
    expect(repository.source).toBe('local');
    expect(repository.url).toBeUndefined();
    expect(repository.description).toBeUndefined();
    expect(repository.language).toBeUndefined();
  });

  it('should convert ISO date string to Date object', () => {
    const resource: Resource = {
      id: '1',
      title: 'Test Resource',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T12:30:45Z',
      ingestion_status: 'completed',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository.lastUpdated).toBeInstanceOf(Date);
    expect(repository.lastUpdated.toISOString()).toBe('2024-01-15T12:30:45.000Z');
  });

  it('should handle all resource fields', () => {
    const resource: Resource = {
      id: '1',
      title: 'Complete Resource',
      description: 'A complete resource with all fields',
      creator: 'John Doe',
      publisher: 'Example Publisher',
      contributor: 'Jane Smith',
      source: 'example.com',
      language: 'Python',
      type: 'code',
      format: 'text/plain',
      identifier: 'resource-123',
      subject: ['AI', 'Machine Learning'],
      relation: ['related-1', 'related-2'],
      coverage: 'Global',
      rights: 'MIT License',
      classification_code: 'CS.AI',
      read_status: 'completed',
      quality_score: 0.95,
      quality_dimensions: {
        accuracy: 0.9,
        completeness: 0.95,
        consistency: 0.92,
        timeliness: 0.98,
        relevance: 0.96,
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T00:00:00Z',
      ingestion_status: 'completed',
      url: 'https://github.com/example/repo',
      content_type: 'code',
      file_path: '/path/to/file.py',
    };

    const repository = mapResourceToRepository(resource);

    expect(repository.id).toBe('1');
    expect(repository.name).toBe('Complete Resource');
    expect(repository.description).toBe('A complete resource with all fields');
    expect(repository.language).toBe('Python');
    expect(repository.url).toBe('https://github.com/example/repo');
    expect(repository.source).toBe('github');
    expect(repository.status).toBe('ready');
  });
});
