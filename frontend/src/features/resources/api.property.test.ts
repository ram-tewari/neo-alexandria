/**
 * Property-based tests for resource API client
 * 
 * Feature: phase1-ingestion-management
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import { apiClient } from '@/core/api/client';
import { fetchResources } from './api';

// Mock apiClient
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('Resource API Client - Property Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful response
    vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } });
  });

  it('Property 1: API Client Parameter Correctness - offset calculation', async () => {
    // Feature: phase1-ingestion-management, Property 1: API Client Parameter Correctness
    // Validates: Requirements 1.7, 3.6
    
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 100 }), // page
        fc.integer({ min: 1, max: 100 }), // limit
        async (page, limit) => {
          vi.clearAllMocks();
          vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } });

          await fetchResources({ page, limit });

          // Verify offset = (page - 1) * limit
          const expectedOffset = (page - 1) * limit;
          const callUrl = vi.mocked(apiClient.get).mock.calls[0][0] as string;
          
          expect(callUrl).toContain(`offset=${expectedOffset}`);
          expect(callUrl).toContain(`limit=${limit}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 1: API Client Parameter Correctness - sort parameter parsing', async () => {
    // Feature: phase1-ingestion-management, Property 1: API Client Parameter Correctness
    // Validates: Requirements 1.7, 3.6
    
    const sortFields = ['created_at', 'updated_at', 'title', 'quality_score'];
    const sortDirections = ['asc', 'desc'];

    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom(...sortFields),
        fc.constantFrom(...sortDirections),
        async (field, direction) => {
          vi.clearAllMocks();
          vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } });

          const sortParam = `${field}:${direction}`;
          await fetchResources({ sort: sortParam });

          const callUrl = vi.mocked(apiClient.get).mock.calls[0][0] as string;
          
          // Verify sort_by and sort_dir extracted correctly
          expect(callUrl).toContain(`sort_by=${field}`);
          expect(callUrl).toContain(`sort_dir=${direction}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 1: API Client Parameter Correctness - combined parameters', async () => {
    // Feature: phase1-ingestion-management, Property 1: API Client Parameter Correctness
    // Validates: Requirements 1.7, 3.6
    
    const sortFields = ['created_at', 'updated_at', 'title', 'quality_score'];
    const sortDirections = ['asc', 'desc'];

    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 50 }), // page
        fc.integer({ min: 10, max: 100 }), // limit
        fc.constantFrom(...sortFields),
        fc.constantFrom(...sortDirections),
        async (page, limit, field, direction) => {
          vi.clearAllMocks();
          vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } });

          const sortParam = `${field}:${direction}`;
          await fetchResources({ page, limit, sort: sortParam });

          const callUrl = vi.mocked(apiClient.get).mock.calls[0][0] as string;
          
          // Verify all parameters are correct
          const expectedOffset = (page - 1) * limit;
          expect(callUrl).toContain(`offset=${expectedOffset}`);
          expect(callUrl).toContain(`limit=${limit}`);
          expect(callUrl).toContain(`sort_by=${field}`);
          expect(callUrl).toContain(`sort_dir=${direction}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 1: API Client Parameter Correctness - edge cases', async () => {
    // Feature: phase1-ingestion-management, Property 1: API Client Parameter Correctness
    // Validates: Requirements 1.7, 3.6
    
    // Test edge cases: page 1, large pages, various limits
    const testCases = [
      { page: 1, limit: 1, expectedOffset: 0 },
      { page: 1, limit: 100, expectedOffset: 0 },
      { page: 100, limit: 1, expectedOffset: 99 },
      { page: 10, limit: 50, expectedOffset: 450 },
    ];

    for (const { page, limit, expectedOffset } of testCases) {
      vi.clearAllMocks();
      vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } });

      await fetchResources({ page, limit });

      const callUrl = vi.mocked(apiClient.get).mock.calls[0][0] as string;
      expect(callUrl).toContain(`offset=${expectedOffset}`);
      expect(callUrl).toContain(`limit=${limit}`);
    }
  });
});
