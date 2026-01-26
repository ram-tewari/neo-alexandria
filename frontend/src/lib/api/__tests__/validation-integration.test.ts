/**
 * Integration Tests for API Client with Runtime Validation
 * 
 * Tests that API client methods properly validate responses using zod schemas.
 * These tests verify that validation catches type mismatches between frontend
 * and backend in development mode.
 */

import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { workbenchApi } from '../workbench';
import { editorApi } from '../editor';

// Setup MSW server for mocking API responses
const server = setupServer();

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
  // Mock console to avoid noise in tests
  vi.spyOn(console, 'error').mockImplementation(() => {});
  vi.spyOn(console, 'log').mockImplementation(() => {});
});

afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
});

afterAll(() => {
  server.close();
  vi.restoreAllMocks();
});

describe('Workbench API Validation Integration', () => {
  describe('getCurrentUser', () => {
    it('should validate correct user response', async () => {
      server.use(
        http.get('*/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-123',
            username: 'testuser',
            email: 'test@example.com',
            tier: 'free',
            is_active: true,
          });
        })
      );

      const user = await workbenchApi.getCurrentUser();

      expect(user).toEqual({
        id: 'user-123',
        username: 'testuser',
        email: 'test@example.com',
        tier: 'free',
        is_active: true,
      });
    });

    it('should throw validation error for invalid user response', async () => {
      server.use(
        http.get('*/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-123',
            username: 'testuser',
            email: 'invalid-email', // Invalid email format
            tier: 'invalid-tier', // Invalid tier value
            is_active: 'yes', // Should be boolean
          });
        })
      );

      await expect(workbenchApi.getCurrentUser()).rejects.toThrow(
        /API response validation failed/
      );
    });

    it('should throw validation error for missing required fields', async () => {
      server.use(
        http.get('*/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-123',
            username: 'testuser',
            // Missing email, tier, is_active
          });
        })
      );

      await expect(workbenchApi.getCurrentUser()).rejects.toThrow();
    });
  });

  describe('getRateLimit', () => {
    it('should validate correct rate limit response', async () => {
      server.use(
        http.get('*/api/auth/rate-limit', () => {
          return HttpResponse.json({
            tier: 'premium',
            limit: 1000,
            remaining: 950,
            reset: 1704067200,
          });
        })
      );

      const rateLimit = await workbenchApi.getRateLimit();

      expect(rateLimit.tier).toBe('premium');
      expect(rateLimit.limit).toBe(1000);
      expect(rateLimit.remaining).toBe(950);
    });

    it('should throw validation error for invalid rate limit response', async () => {
      server.use(
        http.get('*/api/auth/rate-limit', () => {
          return HttpResponse.json({
            tier: 'premium',
            limit: '1000', // Should be number
            remaining: 950,
            reset: 1704067200,
          });
        })
      );

      await expect(workbenchApi.getRateLimit()).rejects.toThrow();
    });
  });

  describe('getResources', () => {
    it('should validate correct resources list response', async () => {
      server.use(
        http.get('*/resources', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'resource-1',
                title: 'Test Resource',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
                ingestion_status: 'completed',
              },
            ],
            total: 1,
          });
        })
      );

      const resources = await workbenchApi.getResources();

      expect(resources).toHaveLength(1);
      expect(resources[0].id).toBe('resource-1');
    });

    it('should throw validation error for invalid resource in list', async () => {
      server.use(
        http.get('*/resources', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'resource-1',
                title: 'Test Resource',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
                ingestion_status: 'invalid-status', // Invalid enum value
              },
            ],
            total: 1,
          });
        })
      );

      await expect(workbenchApi.getResources()).rejects.toThrow();
    });
  });

  describe('getSystemHealth', () => {
    it('should validate correct health status response', async () => {
      server.use(
        http.get('*/api/monitoring/health', () => {
          return HttpResponse.json({
            status: 'healthy',
            message: 'All systems operational',
            timestamp: '2024-01-01T00:00:00Z',
            components: {
              database: { status: 'healthy' },
              cache: { status: 'healthy' },
              event_bus: { status: 'healthy' },
            },
            modules: {
              resources: 'healthy',
              search: 'healthy',
            },
          });
        })
      );

      const health = await workbenchApi.getSystemHealth();

      expect(health.status).toBe('healthy');
      expect(health.components.database.status).toBe('healthy');
    });

    it('should throw validation error for invalid health status', async () => {
      server.use(
        http.get('*/api/monitoring/health', () => {
          return HttpResponse.json({
            status: 'invalid-status', // Invalid enum value
            message: 'All systems operational',
            timestamp: '2024-01-01T00:00:00Z',
            components: {
              database: { status: 'healthy' },
              cache: { status: 'healthy' },
              event_bus: { status: 'healthy' },
            },
            modules: {},
          });
        })
      );

      await expect(workbenchApi.getSystemHealth()).rejects.toThrow();
    });
  });
});

describe('Editor API Validation Integration', () => {
  describe('getResource', () => {
    it('should validate correct resource response', async () => {
      server.use(
        http.get('*/resources/:id', () => {
          return HttpResponse.json({
            id: 'resource-1',
            title: 'Test Resource',
            content: 'function test() { return true; }',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            ingestion_status: 'completed',
          });
        })
      );

      const resource = await editorApi.getResource('resource-1');

      expect(resource.id).toBe('resource-1');
      expect(resource.content).toBeDefined();
    });

    it('should throw validation error for invalid resource response', async () => {
      server.use(
        http.get('*/resources/:id', () => {
          return HttpResponse.json({
            id: 'resource-1',
            title: 123, // Should be string
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            ingestion_status: 'completed',
          });
        })
      );

      await expect(editorApi.getResource('resource-1')).rejects.toThrow();
    });
  });

  describe('getChunks', () => {
    it('should validate correct chunks response', async () => {
      server.use(
        http.get('*/resources/:id/chunks', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'chunk-1',
                resource_id: 'resource-1',
                content: 'function test() {}',
                chunk_index: 0,
                chunk_metadata: {
                  start_line: 1,
                  end_line: 3,
                  language: 'typescript',
                },
                created_at: '2024-01-01T00:00:00Z',
              },
            ],
            total: 1,
          });
        })
      );

      const chunks = await editorApi.getChunks('resource-1');

      expect(chunks).toHaveLength(1);
      expect(chunks[0].chunk_metadata.language).toBe('typescript');
    });

    it('should throw validation error for invalid chunk metadata', async () => {
      server.use(
        http.get('*/resources/:id/chunks', () => {
          return HttpResponse.json({
            items: [
              {
                id: 'chunk-1',
                resource_id: 'resource-1',
                content: 'function test() {}',
                chunk_index: 0,
                chunk_metadata: {
                  start_line: '1', // Should be number
                  end_line: 3,
                  language: 'typescript',
                },
                created_at: '2024-01-01T00:00:00Z',
              },
            ],
            total: 1,
          });
        })
      );

      await expect(editorApi.getChunks('resource-1')).rejects.toThrow();
    });
  });

  describe('createAnnotation', () => {
    it('should validate correct annotation response', async () => {
      server.use(
        http.post('*/resources/:id/annotations', () => {
          return HttpResponse.json({
            id: 'annotation-1',
            resource_id: 'resource-1',
            user_id: 'user-1',
            start_offset: 0,
            end_offset: 10,
            highlighted_text: 'test code',
            color: '#ffff00',
            is_shared: false,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          });
        })
      );

      const annotation = await editorApi.createAnnotation('resource-1', {
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'test code',
      });

      expect(annotation.id).toBe('annotation-1');
      expect(annotation.highlighted_text).toBe('test code');
    });

    it('should throw validation error for invalid annotation response', async () => {
      server.use(
        http.post('*/resources/:id/annotations', () => {
          return HttpResponse.json({
            id: 'annotation-1',
            resource_id: 'resource-1',
            user_id: 'user-1',
            start_offset: '0', // Should be number
            end_offset: 10,
            highlighted_text: 'test code',
            color: '#ffff00',
            is_shared: false,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          });
        })
      );

      await expect(
        editorApi.createAnnotation('resource-1', {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'test code',
        })
      ).rejects.toThrow();
    });
  });

  describe('getHoverInfo', () => {
    it('should validate correct hover info response', async () => {
      server.use(
        http.post('*/api/graph/hover', () => {
          return HttpResponse.json({
            symbol: 'testFunction',
            definition: 'function testFunction(): void',
            documentation: 'A test function',
            type: 'function',
          });
        })
      );

      const hoverInfo = await editorApi.getHoverInfo({
        resource_id: 'resource-1',
        symbol: 'testFunction',
        line: 10,
        column: 5,
      });

      expect(hoverInfo.symbol).toBe('testFunction');
      expect(hoverInfo.type).toBe('function');
    });

    it('should throw validation error for invalid hover info response', async () => {
      server.use(
        http.post('*/api/graph/hover', () => {
          return HttpResponse.json({
            symbol: 123, // Should be string
            definition: 'function testFunction(): void',
          });
        })
      );

      await expect(
        editorApi.getHoverInfo({
          resource_id: 'resource-1',
          symbol: 'testFunction',
        })
      ).rejects.toThrow();
    });
  });
});
