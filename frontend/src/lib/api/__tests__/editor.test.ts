/**
 * Editor API Client Tests
 * 
 * Tests for editor API endpoints with MSW mocks
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { editorApi } from '../editor';
import type {
  AnnotationCreate,
  AnnotationUpdate,
  AnnotationSearchParams,
} from '../editor';
import {
  mockAnnotations,
  mockChunks,
  mockQualityDetails,
  mockNode2VecSummary,
  mockGraphConnections,
} from '@/test/mocks/handlers';

describe('Editor API Client', () => {
  // ==========================================================================
  // Annotations API Tests
  // ==========================================================================

  describe('Annotations API', () => {
    describe('createAnnotation', () => {
      it('should create a new annotation', async () => {
        const resourceId = 'resource-1';
        const data: AnnotationCreate = {
          start_offset: 0,
          end_offset: 50,
          highlighted_text: 'test code',
          note: 'Test note',
          tags: ['test'],
          color: '#ff0000',
        };

        const response = await editorApi.createAnnotation(resourceId, data);

        expect(response.status).toBe(201);
        expect(response.data).toMatchObject({
          resource_id: resourceId,
          start_offset: data.start_offset,
          end_offset: data.end_offset,
          highlighted_text: data.highlighted_text,
          note: data.note,
          tags: data.tags,
          color: data.color,
        });
        expect(response.data.id).toBeDefined();
        expect(response.data.created_at).toBeDefined();
      });

      it('should handle missing optional fields', async () => {
        const resourceId = 'resource-1';
        const data: AnnotationCreate = {
          start_offset: 0,
          end_offset: 50,
          highlighted_text: 'test code',
        };

        const response = await editorApi.createAnnotation(resourceId, data);

        expect(response.status).toBe(201);
        expect(response.data.highlighted_text).toBe(data.highlighted_text);
        expect(response.data.color).toBeDefined(); // Should have default color
      });
    });

    describe('getAnnotations', () => {
      it('should fetch all annotations for a resource', async () => {
        const resourceId = 'resource-1';

        const response = await editorApi.getAnnotations(resourceId);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
        expect(response.data.length).toBeGreaterThan(0);
        expect(response.data[0]).toHaveProperty('id');
        expect(response.data[0]).toHaveProperty('resource_id', resourceId);
      });

      it('should return empty array for resource with no annotations', async () => {
        const resourceId = 'resource-999';

        const response = await editorApi.getAnnotations(resourceId);

        expect(response.status).toBe(200);
        expect(response.data).toEqual([]);
      });
    });

    describe('getAnnotation', () => {
      it('should fetch a specific annotation', async () => {
        const annotationId = mockAnnotations[0].id;

        const response = await editorApi.getAnnotation(annotationId);

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(annotationId);
        expect(response.data).toHaveProperty('highlighted_text');
        expect(response.data).toHaveProperty('note');
      });

      it('should return 404 for non-existent annotation', async () => {
        const annotationId = 'non-existent';

        await expect(
          editorApi.getAnnotation(annotationId)
        ).rejects.toThrow();
      });
    });

    describe('updateAnnotation', () => {
      it('should update an annotation', async () => {
        const annotationId = mockAnnotations[0].id;
        const data: AnnotationUpdate = {
          note: 'Updated note',
          tags: ['updated', 'test'],
        };

        const response = await editorApi.updateAnnotation(annotationId, data);

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(annotationId);
        expect(response.data.note).toBe(data.note);
        expect(response.data.tags).toEqual(data.tags);
        expect(response.data.updated_at).toBeDefined();
      });

      it('should handle partial updates', async () => {
        const annotationId = mockAnnotations[0].id;
        const data: AnnotationUpdate = {
          note: 'Only note updated',
        };

        const response = await editorApi.updateAnnotation(annotationId, data);

        expect(response.status).toBe(200);
        expect(response.data.note).toBe(data.note);
      });

      it('should return 404 for non-existent annotation', async () => {
        const annotationId = 'non-existent';
        const data: AnnotationUpdate = { note: 'test' };

        await expect(
          editorApi.updateAnnotation(annotationId, data)
        ).rejects.toThrow();
      });
    });

    describe('deleteAnnotation', () => {
      it('should delete an annotation', async () => {
        const annotationId = mockAnnotations[0].id;

        const response = await editorApi.deleteAnnotation(annotationId);

        expect(response.status).toBe(204);
      });

      it('should return 404 for non-existent annotation', async () => {
        const annotationId = 'non-existent';

        await expect(
          editorApi.deleteAnnotation(annotationId)
        ).rejects.toThrow();
      });
    });

    describe('searchAnnotationsFulltext', () => {
      it('should search annotations by text', async () => {
        const params: AnnotationSearchParams = {
          query: 'test',
        };

        const response = await editorApi.searchAnnotationsFulltext(params);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
      });

      it('should filter results by query', async () => {
        const params: AnnotationSearchParams = {
          query: 'annotation',
        };

        const response = await editorApi.searchAnnotationsFulltext(params);

        expect(response.status).toBe(200);
        expect(response.data.length).toBeGreaterThan(0);
        // Results should contain the query term
        const hasMatch = response.data.some(
          (a) =>
            a.note?.toLowerCase().includes('annotation') ||
            a.highlighted_text.toLowerCase().includes('annotation')
        );
        expect(hasMatch).toBe(true);
      });

      it('should handle empty query', async () => {
        const params: AnnotationSearchParams = {
          query: '',
        };

        const response = await editorApi.searchAnnotationsFulltext(params);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
      });
    });

    describe('searchAnnotationsSemantic', () => {
      it('should search annotations semantically', async () => {
        const params: AnnotationSearchParams = {
          query: 'important code',
        };

        const response = await editorApi.searchAnnotationsSemantic(params);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
      });
    });
  });

  // ==========================================================================
  // Chunks API Tests
  // ==========================================================================

  describe('Chunks API', () => {
    describe('getChunks', () => {
      it('should fetch all chunks for a resource', async () => {
        const resourceId = 'resource-1';

        const response = await editorApi.getChunks(resourceId);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
        expect(response.data.length).toBeGreaterThan(0);
        expect(response.data[0]).toHaveProperty('id');
        expect(response.data[0]).toHaveProperty('chunk_metadata');
      });

      it('should return empty array for resource with no chunks', async () => {
        const resourceId = 'resource-999';

        const response = await editorApi.getChunks(resourceId);

        expect(response.status).toBe(200);
        expect(response.data).toEqual([]);
      });
    });

    describe('getChunk', () => {
      it('should fetch a specific chunk', async () => {
        const chunkId = mockChunks[0].id;

        const response = await editorApi.getChunk(chunkId);

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(chunkId);
        expect(response.data).toHaveProperty('content');
        expect(response.data).toHaveProperty('chunk_metadata');
      });

      it('should return 404 for non-existent chunk', async () => {
        const chunkId = 'non-existent';

        await expect(editorApi.getChunk(chunkId)).rejects.toThrow();
      });
    });

    describe('triggerChunking', () => {
      it('should trigger chunking for a resource', async () => {
        const resourceId = 'resource-1';

        const response = await editorApi.triggerChunking(resourceId);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('message');
        expect(response.data).toHaveProperty('task_id');
      });
    });
  });

  // ==========================================================================
  // Quality API Tests
  // ==========================================================================

  describe('Quality API', () => {
    describe('getQualityDetails', () => {
      it('should fetch quality details for a resource', async () => {
        const resourceId = mockQualityDetails.resource_id;

        const response = await editorApi.getQualityDetails(resourceId);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('quality_overall');
        expect(response.data).toHaveProperty('quality_dimensions');
        expect(response.data.quality_dimensions).toHaveProperty('accuracy');
        expect(response.data.quality_dimensions).toHaveProperty('completeness');
      });

      it('should return 404 for resource without quality data', async () => {
        const resourceId = 'resource-999';

        await expect(
          editorApi.getQualityDetails(resourceId)
        ).rejects.toThrow();
      });
    });

    describe('recalculateQuality', () => {
      it('should recalculate quality for a resource', async () => {
        const resourceId = mockQualityDetails.resource_id;

        const response = await editorApi.recalculateQuality(resourceId);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('quality_overall');
        expect(response.data).toHaveProperty('quality_dimensions');
      });

      it('should return 404 for non-existent resource', async () => {
        const resourceId = 'resource-999';

        await expect(
          editorApi.recalculateQuality(resourceId)
        ).rejects.toThrow();
      });
    });
  });

  // ==========================================================================
  // Graph API Tests (Placeholder)
  // ==========================================================================

  describe('Graph API', () => {
    describe('getNode2VecSummary', () => {
      it('should fetch Node2Vec summary for a symbol', async () => {
        const symbol = 'example';

        const response = await editorApi.getNode2VecSummary(symbol);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('symbol');
        expect(response.data).toHaveProperty('summary');
        expect(response.data.symbol).toBe(symbol);
      });

      it('should handle URL encoding for symbols', async () => {
        const symbol = 'MyClass::method';

        const response = await editorApi.getNode2VecSummary(symbol);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('symbol');
      });
    });

    describe('getConnections', () => {
      it('should fetch graph connections for a symbol', async () => {
        const symbol = 'example';

        const response = await editorApi.getConnections(symbol);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBe(true);
        expect(response.data.length).toBeGreaterThan(0);
        expect(response.data[0]).toHaveProperty('name');
        expect(response.data[0]).toHaveProperty('type');
        expect(response.data[0]).toHaveProperty('relationship');
      });
    });
  });

  // ==========================================================================
  // Error Handling Tests
  // ==========================================================================

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      // This test would require setting up a network error handler
      // For now, we'll just verify the error is thrown
      const annotationId = 'non-existent';

      await expect(
        editorApi.getAnnotation(annotationId)
      ).rejects.toThrow();
    });

    it('should handle 404 errors', async () => {
      const resourceId = 'resource-999';

      await expect(
        editorApi.getQualityDetails(resourceId)
      ).rejects.toThrow();
    });
  });

  // ==========================================================================
  // Request/Response Transformation Tests
  // ==========================================================================

  describe('Request/Response Transformations', () => {
    it('should send correct request body for annotation creation', async () => {
      const resourceId = 'resource-1';
      const data: AnnotationCreate = {
        start_offset: 100,
        end_offset: 200,
        highlighted_text: 'test',
        note: 'note',
        tags: ['tag1', 'tag2'],
        color: '#123456',
      };

      const response = await editorApi.createAnnotation(resourceId, data);

      expect(response.data.start_offset).toBe(data.start_offset);
      expect(response.data.end_offset).toBe(data.end_offset);
      expect(response.data.highlighted_text).toBe(data.highlighted_text);
      expect(response.data.note).toBe(data.note);
      expect(response.data.tags).toEqual(data.tags);
      expect(response.data.color).toBe(data.color);
    });

    it('should correctly parse annotation response', async () => {
      const resourceId = 'resource-1';

      const response = await editorApi.getAnnotations(resourceId);

      expect(response.data).toBeInstanceOf(Array);
      response.data.forEach((annotation) => {
        expect(annotation).toHaveProperty('id');
        expect(annotation).toHaveProperty('resource_id');
        expect(annotation).toHaveProperty('start_offset');
        expect(annotation).toHaveProperty('end_offset');
        expect(annotation).toHaveProperty('highlighted_text');
        expect(annotation).toHaveProperty('created_at');
        expect(annotation).toHaveProperty('updated_at');
      });
    });

    it('should correctly parse chunk response', async () => {
      const resourceId = 'resource-1';

      const response = await editorApi.getChunks(resourceId);

      expect(response.data).toBeInstanceOf(Array);
      response.data.forEach((chunk) => {
        expect(chunk).toHaveProperty('id');
        expect(chunk).toHaveProperty('resource_id');
        expect(chunk).toHaveProperty('content');
        expect(chunk).toHaveProperty('chunk_index');
        expect(chunk).toHaveProperty('chunk_metadata');
        expect(chunk.chunk_metadata).toHaveProperty('start_line');
        expect(chunk.chunk_metadata).toHaveProperty('end_line');
        expect(chunk.chunk_metadata).toHaveProperty('language');
      });
    });

    it('should correctly parse quality response', async () => {
      const resourceId = mockQualityDetails.resource_id;

      const response = await editorApi.getQualityDetails(resourceId);

      expect(response.data).toHaveProperty('resource_id');
      expect(response.data).toHaveProperty('quality_overall');
      expect(typeof response.data.quality_overall).toBe('number');
      expect(response.data).toHaveProperty('quality_dimensions');
      expect(response.data.quality_dimensions).toHaveProperty('accuracy');
      expect(response.data.quality_dimensions).toHaveProperty('completeness');
      expect(response.data.quality_dimensions).toHaveProperty('consistency');
      expect(response.data.quality_dimensions).toHaveProperty('timeliness');
      expect(response.data.quality_dimensions).toHaveProperty('relevance');
    });
  });
});
