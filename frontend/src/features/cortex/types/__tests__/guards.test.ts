/**
 * Unit tests for type guards and validators
 * 
 * Tests runtime type checking and validation for graph domain models
 */
import { describe, it, expect } from 'vitest';
import {
  isHypothesisType,
  isVisualizationMode,
  isEntityType,
  isRelationType,
  isLayoutAlgorithm,
  isImpactLevel,
  isGraphNode,
  isGraphEdge,
  isGraphData,
  isHypothesis,
  isABCHypothesis,
  isGraphEntity,
  isGraphRelationship,
  validateConfidence,
  validateWeight,
  validateGraphNode,
  validateGraphEdge,
  validateHypothesis,
  validateGraphEntity,
  validateGraphRelationship,
} from '../guards';
import { HypothesisType, VisualizationMode } from '../graph';

describe('Type Guards', () => {
  describe('isHypothesisType', () => {
    it('should return true for valid hypothesis types', () => {
      expect(isHypothesisType('contradiction')).toBe(true);
      expect(isHypothesisType('hidden_connection')).toBe(true);
      expect(isHypothesisType('research_gap')).toBe(true);
    });

    it('should return false for invalid hypothesis types', () => {
      expect(isHypothesisType('invalid')).toBe(false);
      expect(isHypothesisType('')).toBe(false);
      expect(isHypothesisType(123)).toBe(false);
      expect(isHypothesisType(null)).toBe(false);
      expect(isHypothesisType(undefined)).toBe(false);
      expect(isHypothesisType({})).toBe(false);
    });
  });

  describe('isVisualizationMode', () => {
    it('should return true for valid visualization modes', () => {
      expect(isVisualizationMode('city_map')).toBe(true);
      expect(isVisualizationMode('blast_radius')).toBe(true);
      expect(isVisualizationMode('dependency_waterfall')).toBe(true);
      expect(isVisualizationMode('hypothesis')).toBe(true);
      expect(isVisualizationMode('default')).toBe(true);
    });

    it('should return false for invalid visualization modes', () => {
      expect(isVisualizationMode('invalid')).toBe(false);
      expect(isVisualizationMode('')).toBe(false);
      expect(isVisualizationMode(123)).toBe(false);
      expect(isVisualizationMode(null)).toBe(false);
    });
  });

  describe('isEntityType', () => {
    it('should return true for valid entity types', () => {
      expect(isEntityType('Concept')).toBe(true);
      expect(isEntityType('Person')).toBe(true);
      expect(isEntityType('Organization')).toBe(true);
      expect(isEntityType('Method')).toBe(true);
      expect(isEntityType('File')).toBe(true);
      expect(isEntityType('Function')).toBe(true);
      expect(isEntityType('Class')).toBe(true);
      expect(isEntityType('Variable')).toBe(true);
    });

    it('should return false for invalid entity types', () => {
      expect(isEntityType('InvalidType')).toBe(false);
      expect(isEntityType('concept')).toBe(false); // Case-sensitive
      expect(isEntityType('')).toBe(false);
      expect(isEntityType(123)).toBe(false);
    });
  });

  describe('isRelationType', () => {
    it('should return true for valid relation types', () => {
      expect(isRelationType('CONTRADICTS')).toBe(true);
      expect(isRelationType('SUPPORTS')).toBe(true);
      expect(isRelationType('EXTENDS')).toBe(true);
      expect(isRelationType('CITES')).toBe(true);
      expect(isRelationType('CALLS')).toBe(true);
      expect(isRelationType('IMPORTS')).toBe(true);
      expect(isRelationType('DEFINES')).toBe(true);
      expect(isRelationType('SEMANTIC_SIMILARITY')).toBe(true);
    });

    it('should return false for invalid relation types', () => {
      expect(isRelationType('INVALID')).toBe(false);
      expect(isRelationType('contradicts')).toBe(false); // Case-sensitive
      expect(isRelationType('')).toBe(false);
      expect(isRelationType(123)).toBe(false);
    });
  });

  describe('isLayoutAlgorithm', () => {
    it('should return true for valid layout algorithms', () => {
      expect(isLayoutAlgorithm('force-directed')).toBe(true);
      expect(isLayoutAlgorithm('hierarchical')).toBe(true);
      expect(isLayoutAlgorithm('circular')).toBe(true);
      expect(isLayoutAlgorithm('dagre')).toBe(true);
      expect(isLayoutAlgorithm('manual')).toBe(true);
    });

    it('should return false for invalid layout algorithms', () => {
      expect(isLayoutAlgorithm('invalid')).toBe(false);
      expect(isLayoutAlgorithm('force_directed')).toBe(false);
      expect(isLayoutAlgorithm('')).toBe(false);
      expect(isLayoutAlgorithm(123)).toBe(false);
    });
  });

  describe('isImpactLevel', () => {
    it('should return true for valid impact levels', () => {
      expect(isImpactLevel('high')).toBe(true);
      expect(isImpactLevel('medium')).toBe(true);
      expect(isImpactLevel('low')).toBe(true);
    });

    it('should return false for invalid impact levels', () => {
      expect(isImpactLevel('critical')).toBe(false);
      expect(isImpactLevel('HIGH')).toBe(false); // Case-sensitive
      expect(isImpactLevel('')).toBe(false);
      expect(isImpactLevel(123)).toBe(false);
    });
  });

  describe('isGraphNode', () => {
    it('should return true for valid graph nodes', () => {
      const validNode = {
        id: 'node-1',
        label: 'Test Node',
        type: 'default',
        metadata: {},
        position: { x: 100, y: 200 },
        data: {},
      };
      expect(isGraphNode(validNode)).toBe(true);
    });

    it('should return false for invalid graph nodes', () => {
      expect(isGraphNode(null)).toBe(false);
      expect(isGraphNode(undefined)).toBe(false);
      expect(isGraphNode({})).toBe(false);
      expect(isGraphNode({ id: 'node-1' })).toBe(false);
      
      // Missing required fields
      expect(isGraphNode({
        id: 'node-1',
        label: 'Test',
        type: 'default',
        metadata: {},
        // Missing position
      })).toBe(false);
      
      // Invalid position
      expect(isGraphNode({
        id: 'node-1',
        label: 'Test',
        type: 'default',
        metadata: {},
        position: { x: 'invalid', y: 200 },
      })).toBe(false);
    });
  });

  describe('isGraphEdge', () => {
    it('should return true for valid graph edges', () => {
      const validEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 0.5,
        metadata: {},
      };
      expect(isGraphEdge(validEdge)).toBe(true);
    });

    it('should return false for invalid graph edges', () => {
      expect(isGraphEdge(null)).toBe(false);
      expect(isGraphEdge({})).toBe(false);
      
      // Missing required fields
      expect(isGraphEdge({
        id: 'edge-1',
        source: 'node-1',
        // Missing target
        type: 'default',
        weight: 0.5,
        metadata: {},
      })).toBe(false);
      
      // Invalid weight type
      expect(isGraphEdge({
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 'invalid',
        metadata: {},
      })).toBe(false);
    });
  });

  describe('isGraphData', () => {
    it('should return true for valid graph data', () => {
      const validData = {
        nodes: [],
        edges: [],
        metadata: { totalNodes: 0, totalEdges: 0 },
      };
      expect(isGraphData(validData)).toBe(true);
    });

    it('should return false for invalid graph data', () => {
      expect(isGraphData(null)).toBe(false);
      expect(isGraphData({})).toBe(false);
      expect(isGraphData({ nodes: [] })).toBe(false);
      expect(isGraphData({ nodes: 'invalid', edges: [], metadata: {} })).toBe(false);
    });
  });

  describe('isHypothesis', () => {
    it('should return true for valid hypotheses', () => {
      const validHypothesis = {
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.85,
        evidence: {},
        nodes: ['node-1', 'node-2'],
      };
      expect(isHypothesis(validHypothesis)).toBe(true);
    });

    it('should return false for invalid hypotheses', () => {
      expect(isHypothesis(null)).toBe(false);
      expect(isHypothesis({})).toBe(false);
      
      // Invalid type
      expect(isHypothesis({
        id: 'hyp-1',
        type: 'invalid',
        confidence: 0.85,
        evidence: {},
        nodes: [],
      })).toBe(false);
      
      // Invalid confidence type
      expect(isHypothesis({
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 'invalid',
        evidence: {},
        nodes: [],
      })).toBe(false);
    });
  });

  describe('isABCHypothesis', () => {
    it('should return true for valid ABC hypotheses', () => {
      const validABC = {
        id: 'abc-1',
        type: HypothesisType.HIDDEN_CONNECTION,
        confidence: 0.85,
        evidence: {},
        nodes: ['a', 'b', 'c'],
        conceptA: 'ML',
        conceptC: 'Drug Discovery',
        bridgingConcept: 'Molecular Modeling',
        aToB: ['res-1'],
        bToC: ['res-2'],
      };
      expect(isABCHypothesis(validABC)).toBe(true);
    });

    it('should return false for non-ABC hypotheses', () => {
      // Wrong type
      expect(isABCHypothesis({
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.85,
        evidence: {},
        nodes: [],
      })).toBe(false);
      
      // Missing ABC fields
      expect(isABCHypothesis({
        id: 'abc-1',
        type: HypothesisType.HIDDEN_CONNECTION,
        confidence: 0.85,
        evidence: {},
        nodes: [],
        // Missing conceptA, conceptC, etc.
      })).toBe(false);
    });
  });

  describe('isGraphEntity', () => {
    it('should return true for valid graph entities', () => {
      const validEntity = {
        id: 'entity-1',
        name: 'Test Entity',
        type: 'Concept',
        properties: {},
      };
      expect(isGraphEntity(validEntity)).toBe(true);
    });

    it('should return false for invalid graph entities', () => {
      expect(isGraphEntity(null)).toBe(false);
      expect(isGraphEntity({})).toBe(false);
      
      // Invalid type
      expect(isGraphEntity({
        id: 'entity-1',
        name: 'Test',
        type: 'InvalidType',
        properties: {},
      })).toBe(false);
    });
  });

  describe('isGraphRelationship', () => {
    it('should return true for valid graph relationships', () => {
      const validRel = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {},
      };
      expect(isGraphRelationship(validRel)).toBe(true);
    });

    it('should return false for invalid graph relationships', () => {
      expect(isGraphRelationship(null)).toBe(false);
      expect(isGraphRelationship({})).toBe(false);
      
      // Invalid type
      expect(isGraphRelationship({
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'INVALID',
        properties: {},
      })).toBe(false);
    });
  });
});

describe('Validators', () => {
  describe('validateConfidence', () => {
    it('should validate correct confidence values', () => {
      expect(validateConfidence(0.0).valid).toBe(true);
      expect(validateConfidence(0.5).valid).toBe(true);
      expect(validateConfidence(1.0).valid).toBe(true);
    });

    it('should reject out-of-range confidence values', () => {
      const result1 = validateConfidence(-0.1);
      expect(result1.valid).toBe(false);
      expect(result1.errors).toContain('Confidence must be between 0.0 and 1.0');
      
      const result2 = validateConfidence(1.5);
      expect(result2.valid).toBe(false);
      expect(result2.errors).toContain('Confidence must be between 0.0 and 1.0');
    });

    it('should reject NaN confidence values', () => {
      const result = validateConfidence(NaN);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Confidence cannot be NaN');
    });

    it('should reject non-number confidence values', () => {
      const result = validateConfidence('0.5' as any);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Confidence must be a number');
    });
  });

  describe('validateWeight', () => {
    it('should validate correct weight values', () => {
      expect(validateWeight(0.0).valid).toBe(true);
      expect(validateWeight(0.5).valid).toBe(true);
      expect(validateWeight(1.0).valid).toBe(true);
    });

    it('should reject out-of-range weight values', () => {
      const result1 = validateWeight(-0.1);
      expect(result1.valid).toBe(false);
      expect(result1.errors).toContain('Weight must be between 0.0 and 1.0');
      
      const result2 = validateWeight(1.5);
      expect(result2.valid).toBe(false);
    });

    it('should reject NaN weight values', () => {
      const result = validateWeight(NaN);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Weight cannot be NaN');
    });
  });

  describe('validateGraphNode', () => {
    it('should validate correct graph nodes', () => {
      const validNode = {
        id: 'node-1',
        label: 'Test Node',
        type: 'default',
        metadata: {},
        position: { x: 100, y: 200 },
        data: {},
      };
      const result = validateGraphNode(validNode);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject nodes with empty IDs', () => {
      const invalidNode = {
        id: '  ',
        label: 'Test',
        type: 'default',
        metadata: {},
        position: { x: 0, y: 0 },
        data: {},
      };
      const result = validateGraphNode(invalidNode);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Node ID cannot be empty');
    });

    it('should reject nodes with empty labels', () => {
      const invalidNode = {
        id: 'node-1',
        label: '  ',
        type: 'default',
        metadata: {},
        position: { x: 0, y: 0 },
        data: {},
      };
      const result = validateGraphNode(invalidNode);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Node label cannot be empty');
    });

    it('should reject nodes with invalid types', () => {
      const invalidNode = {
        id: 'node-1',
        label: 'Test',
        type: 'invalid-type',
        metadata: {},
        position: { x: 0, y: 0 },
        data: {},
      };
      const result = validateGraphNode(invalidNode);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.includes('Invalid node type'))).toBe(true);
    });

    it('should reject nodes with NaN positions', () => {
      const invalidNode = {
        id: 'node-1',
        label: 'Test',
        type: 'default',
        metadata: {},
        position: { x: NaN, y: 200 },
        data: {},
      };
      const result = validateGraphNode(invalidNode);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Node position coordinates must be valid numbers');
    });
  });

  describe('validateGraphEdge', () => {
    it('should validate correct graph edges', () => {
      const validEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 0.5,
        metadata: {},
      };
      const result = validateGraphEdge(validEdge);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject edges with empty IDs', () => {
      const invalidEdge = {
        id: '  ',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 0.5,
        metadata: {},
      };
      const result = validateGraphEdge(invalidEdge);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Edge ID cannot be empty');
    });

    it('should reject self-loops', () => {
      const selfLoop = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-1',
        type: 'default',
        weight: 0.5,
        metadata: {},
      };
      const result = validateGraphEdge(selfLoop);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Edge source and target cannot be the same (self-loops not allowed)');
    });

    it('should reject edges with invalid types', () => {
      const invalidEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'invalid-type',
        weight: 0.5,
        metadata: {},
      };
      const result = validateGraphEdge(invalidEdge);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.includes('Invalid edge type'))).toBe(true);
    });

    it('should reject edges with invalid weights', () => {
      const invalidEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 1.5,
        metadata: {},
      };
      const result = validateGraphEdge(invalidEdge);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.includes('Weight must be between'))).toBe(true);
    });
  });

  describe('validateHypothesis', () => {
    it('should validate correct hypotheses', () => {
      const validHypothesis = {
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.85,
        evidence: {},
        nodes: ['node-1', 'node-2'],
      };
      const result = validateHypothesis(validHypothesis);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject hypotheses with empty IDs', () => {
      const invalidHypothesis = {
        id: '  ',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.85,
        evidence: {},
        nodes: ['node-1'],
      };
      const result = validateHypothesis(invalidHypothesis);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Hypothesis ID cannot be empty');
    });

    it('should reject hypotheses with invalid confidence', () => {
      const invalidHypothesis = {
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 1.5,
        evidence: {},
        nodes: ['node-1'],
      };
      const result = validateHypothesis(invalidHypothesis);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.includes('Confidence'))).toBe(true);
    });

    it('should reject hypotheses with no nodes', () => {
      const invalidHypothesis = {
        id: 'hyp-1',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.85,
        evidence: {},
        nodes: [],
      };
      const result = validateHypothesis(invalidHypothesis);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Hypothesis must involve at least one node');
    });
  });

  describe('validateGraphEntity', () => {
    it('should validate correct graph entities', () => {
      const validEntity = {
        id: 'entity-1',
        name: 'Test Entity',
        type: 'Concept',
        properties: {},
      };
      const result = validateGraphEntity(validEntity);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject entities with empty IDs', () => {
      const invalidEntity = {
        id: '  ',
        name: 'Test',
        type: 'Concept',
        properties: {},
      };
      const result = validateGraphEntity(invalidEntity);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Entity ID cannot be empty');
    });

    it('should reject entities with empty names', () => {
      const invalidEntity = {
        id: 'entity-1',
        name: '  ',
        type: 'Concept',
        properties: {},
      };
      const result = validateGraphEntity(invalidEntity);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Entity name cannot be empty');
    });
  });

  describe('validateGraphRelationship', () => {
    it('should validate correct graph relationships', () => {
      const validRel = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {},
      };
      const result = validateGraphRelationship(validRel);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject relationships with empty IDs', () => {
      const invalidRel = {
        id: '  ',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {},
      };
      const result = validateGraphRelationship(invalidRel);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Relationship ID cannot be empty');
    });

    it('should reject self-relationships', () => {
      const selfRel = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-1',
        type: 'EXTENDS',
        properties: {},
      };
      const result = validateGraphRelationship(selfRel);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Relationship source and target cannot be the same');
    });
  });
});
