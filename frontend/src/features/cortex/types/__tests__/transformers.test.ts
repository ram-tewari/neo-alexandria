/**
 * Unit tests for type transformation utilities
 * 
 * Tests data transformations between different graph representations
 */
import { describe, it, expect } from 'vitest';
import {
  entityToNode,
  relationshipToEdge,
  entitiesToGraphData,
  calculateDensity,
  calculateAverageDegree,
  calculateImpactLevel,
  nodeToBlastRadiusNode,
  calculateImpactScore,
  normalizeCentralityMetrics,
  applyCentralityToNodes,
  filterNodesByType,
  filterEdgesByType,
  filterEdgesByNodes,
  applyGraphFilters,
  centerGraph,
  scaleGraphToFit,
  searchNodesByLabel,
  getNodeDegree,
  getNodeNeighbors,
  buildAdjacencyList,
} from '../transformers';
import type { GraphEntity, GraphRelationship, GraphNode, GraphEdge, CentralityMetrics } from '../graph';

describe('API Response Transformations', () => {
  describe('entityToNode', () => {
    it('should transform entity to graph node', () => {
      const entity: GraphEntity = {
        id: 'entity-1',
        name: 'Test Entity',
        type: 'Concept',
        properties: {
          description: 'A test concept',
          confidence: 0.95,
        },
      };

      const node = entityToNode(entity);

      expect(node.id).toBe('entity-1');
      expect(node.label).toBe('Test Entity');
      expect(node.type).toBe('entity');
      expect(node.metadata.entityType).toBe('Concept');
      expect(node.metadata.description).toBe('A test concept');
      expect(node.metadata.confidence).toBe(0.95);
      expect(node.position).toEqual({ x: 0, y: 0 });
      expect(node.data.entity).toBe(entity);
    });
  });

  describe('relationshipToEdge', () => {
    it('should transform relationship to graph edge', () => {
      const relationship: GraphRelationship = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {
          weight: 0.85,
          confidence: 0.9,
        },
      };

      const edge = relationshipToEdge(relationship);

      expect(edge.id).toBe('rel-1');
      expect(edge.source).toBe('entity-1');
      expect(edge.target).toBe('entity-2');
      expect(edge.type).toBe('relationship');
      expect(edge.weight).toBe(0.85);
      expect(edge.metadata.relationType).toBe('EXTENDS');
      expect(edge.metadata.confidence).toBe(0.9);
    });

    it('should use default weight if not provided', () => {
      const relationship: GraphRelationship = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {},
      };

      const edge = relationshipToEdge(relationship);

      expect(edge.weight).toBe(0.5);
    });
  });

  describe('entitiesToGraphData', () => {
    it('should transform entities and relationships to graph data', () => {
      const entities: GraphEntity[] = [
        { id: 'e1', name: 'Entity 1', type: 'Concept', properties: {} },
        { id: 'e2', name: 'Entity 2', type: 'Concept', properties: {} },
      ];

      const relationships: GraphRelationship[] = [
        { id: 'r1', source: 'e1', target: 'e2', type: 'EXTENDS', properties: { weight: 0.8 } },
      ];

      const graphData = entitiesToGraphData(entities, relationships);

      expect(graphData.nodes).toHaveLength(2);
      expect(graphData.edges).toHaveLength(1);
      expect(graphData.metadata.totalNodes).toBe(2);
      expect(graphData.metadata.totalEdges).toBe(1);
      expect(graphData.metadata.density).toBeGreaterThan(0);
      expect(graphData.metadata.averageDegree).toBeGreaterThan(0);
    });
  });
});

describe('Graph Metric Calculations', () => {
  describe('calculateDensity', () => {
    it('should calculate density for complete graph', () => {
      // Complete graph with 4 nodes has 6 edges
      const density = calculateDensity(4, 6);
      expect(density).toBe(1.0);
    });

    it('should calculate density for sparse graph', () => {
      const density = calculateDensity(10, 5);
      expect(density).toBeLessThan(0.2);
    });

    it('should return 0 for graph with 0 or 1 nodes', () => {
      expect(calculateDensity(0, 0)).toBe(0);
      expect(calculateDensity(1, 0)).toBe(0);
    });
  });

  describe('calculateAverageDegree', () => {
    it('should calculate average degree correctly', () => {
      // 4 nodes, 4 edges -> average degree = 2
      const avgDegree = calculateAverageDegree(4, 4);
      expect(avgDegree).toBe(2);
    });

    it('should return 0 for empty graph', () => {
      expect(calculateAverageDegree(0, 0)).toBe(0);
    });
  });

  describe('calculateImpactLevel', () => {
    it('should return high for scores >= 0.7', () => {
      expect(calculateImpactLevel(0.7)).toBe('high');
      expect(calculateImpactLevel(0.9)).toBe('high');
      expect(calculateImpactLevel(1.0)).toBe('high');
    });

    it('should return medium for scores >= 0.4 and < 0.7', () => {
      expect(calculateImpactLevel(0.4)).toBe('medium');
      expect(calculateImpactLevel(0.5)).toBe('medium');
      expect(calculateImpactLevel(0.69)).toBe('medium');
    });

    it('should return low for scores < 0.4', () => {
      expect(calculateImpactLevel(0.0)).toBe('low');
      expect(calculateImpactLevel(0.2)).toBe('low');
      expect(calculateImpactLevel(0.39)).toBe('low');
    });
  });
});

describe('Blast Radius Transformations', () => {
  describe('nodeToBlastRadiusNode', () => {
    it('should transform node to blast radius node', () => {
      const node: GraphNode = {
        id: 'node-1',
        label: 'Test',
        type: 'default',
        metadata: {},
        position: { x: 0, y: 0 },
        data: {},
      };

      const blastNode = nodeToBlastRadiusNode(node, 0.85, 2);

      expect(blastNode.id).toBe('node-1');
      expect(blastNode.impactScore).toBe(0.85);
      expect(blastNode.impactLevel).toBe('high');
      expect(blastNode.hopDistance).toBe(2);
    });
  });

  describe('calculateImpactScore', () => {
    it('should return 1.0 for center node (distance 0)', () => {
      expect(calculateImpactScore(0)).toBe(1.0);
    });

    it('should return decreasing scores for increasing distances', () => {
      const score1 = calculateImpactScore(1);
      const score2 = calculateImpactScore(2);
      const score3 = calculateImpactScore(3);

      expect(score1).toBeGreaterThan(score2);
      expect(score2).toBeGreaterThan(score3);
      expect(score1).toBeLessThan(1.0);
    });

    it('should return 0 for distances beyond max hops', () => {
      expect(calculateImpactScore(6, 5)).toBe(0.0);
    });
  });
});

describe('Centrality Transformations', () => {
  describe('normalizeCentralityMetrics', () => {
    it('should normalize metrics to 0-1 range', () => {
      const metrics: CentralityMetrics[] = [
        { nodeId: 'n1', degree: 5, betweenness: 0.1, closeness: 0.3, eigenvector: 0.2 },
        { nodeId: 'n2', degree: 10, betweenness: 0.5, closeness: 0.7, eigenvector: 0.8 },
        { nodeId: 'n3', degree: 15, betweenness: 0.9, closeness: 1.0, eigenvector: 1.0 },
      ];

      const normalized = normalizeCentralityMetrics(metrics, 'degree');

      expect(normalized.get('n1')).toBe(0);
      expect(normalized.get('n2')).toBe(0.5);
      expect(normalized.get('n3')).toBe(1);
    });

    it('should handle all same values', () => {
      const metrics: CentralityMetrics[] = [
        { nodeId: 'n1', degree: 5, betweenness: 0.5, closeness: 0.5, eigenvector: 0.5 },
        { nodeId: 'n2', degree: 5, betweenness: 0.5, closeness: 0.5, eigenvector: 0.5 },
      ];

      const normalized = normalizeCentralityMetrics(metrics, 'degree');

      expect(normalized.get('n1')).toBe(0.5);
      expect(normalized.get('n2')).toBe(0.5);
    });
  });

  describe('applyCentralityToNodes', () => {
    it('should apply centrality scores to nodes', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'Node 1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n2', label: 'Node 2', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const scores = new Map([
        ['n1', 0.8],
        ['n2', 0.5],
      ]);

      const result = applyCentralityToNodes(nodes, scores);

      expect(result[0].metadata.centralityScore).toBe(0.8);
      expect(result[1].metadata.centralityScore).toBe(0.5);
    });

    it('should use 0 for nodes without scores', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'Node 1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const scores = new Map<string, number>();

      const result = applyCentralityToNodes(nodes, scores);

      expect(result[0].metadata.centralityScore).toBe(0);
    });
  });
});

describe('Graph Filtering Transformations', () => {
  describe('filterNodesByType', () => {
    it('should filter nodes by type', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'N1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n2', label: 'N2', type: 'cluster', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n3', label: 'N3', type: 'entity', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const filtered = filterNodesByType(nodes, ['default', 'entity']);

      expect(filtered).toHaveLength(2);
      expect(filtered.map(n => n.id)).toEqual(['n1', 'n3']);
    });

    it('should return all nodes if no types specified', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'N1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const filtered = filterNodesByType(nodes, []);

      expect(filtered).toHaveLength(1);
    });
  });

  describe('filterEdgesByType', () => {
    it('should filter edges by type', () => {
      const edges: GraphEdge[] = [
        { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e2', source: 'n2', target: 'n3', type: 'citation', weight: 0.8, metadata: {} },
      ];

      const filtered = filterEdgesByType(edges, ['citation']);

      expect(filtered).toHaveLength(1);
      expect(filtered[0].id).toBe('e2');
    });
  });

  describe('filterEdgesByNodes', () => {
    it('should filter edges to only include those connecting visible nodes', () => {
      const edges: GraphEdge[] = [
        { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e2', source: 'n2', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e3', source: 'n1', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
      ];

      const visibleNodes = new Set(['n1', 'n2']);

      const filtered = filterEdgesByNodes(edges, visibleNodes);

      expect(filtered).toHaveLength(1);
      expect(filtered[0].id).toBe('e1');
    });
  });

  describe('applyGraphFilters', () => {
    it('should apply node and edge type filters', () => {
      const graphData = {
        nodes: [
          { id: 'n1', label: 'N1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
          { id: 'n2', label: 'N2', type: 'cluster', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        ],
        edges: [
          { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        ],
        metadata: { totalNodes: 2, totalEdges: 1 },
      };

      const filtered = applyGraphFilters(graphData, ['default']);

      expect(filtered.nodes).toHaveLength(1);
      expect(filtered.edges).toHaveLength(0); // Edge removed because n2 is filtered out
    });
  });
});

describe('Position Transformations', () => {
  describe('centerGraph', () => {
    it('should center nodes around origin', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'N1', type: 'default', metadata: {}, position: { x: 100, y: 100 }, data: {} },
        { id: 'n2', label: 'N2', type: 'default', metadata: {}, position: { x: 200, y: 200 }, data: {} },
      ];

      const centered = centerGraph(nodes);

      // Centroid is at (150, 150), so nodes should be at (-50, -50) and (50, 50)
      expect(centered[0].position.x).toBe(-50);
      expect(centered[0].position.y).toBe(-50);
      expect(centered[1].position.x).toBe(50);
      expect(centered[1].position.y).toBe(50);
    });

    it('should handle empty array', () => {
      const centered = centerGraph([]);
      expect(centered).toEqual([]);
    });
  });

  describe('scaleGraphToFit', () => {
    it('should scale graph to fit within bounds', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'N1', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n2', label: 'N2', type: 'default', metadata: {}, position: { x: 1000, y: 1000 }, data: {} },
      ];

      const scaled = scaleGraphToFit(nodes, 500, 500, 50);

      // Check that nodes fit within bounds
      scaled.forEach(node => {
        expect(node.position.x).toBeGreaterThanOrEqual(50);
        expect(node.position.x).toBeLessThanOrEqual(450);
        expect(node.position.y).toBeGreaterThanOrEqual(50);
        expect(node.position.y).toBeLessThanOrEqual(450);
      });
    });

    it('should handle empty array', () => {
      const scaled = scaleGraphToFit([], 500, 500);
      expect(scaled).toEqual([]);
    });
  });
});

describe('Search Transformations', () => {
  describe('searchNodesByLabel', () => {
    it('should search nodes by label (case-insensitive)', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'Machine Learning', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n2', label: 'Deep Learning', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
        { id: 'n3', label: 'Neural Networks', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const results = searchNodesByLabel(nodes, 'learning');

      expect(results).toHaveLength(2);
      expect(results.map(n => n.id)).toEqual(['n1', 'n2']);
    });

    it('should return all nodes for empty query', () => {
      const nodes: GraphNode[] = [
        { id: 'n1', label: 'Test', type: 'default', metadata: {}, position: { x: 0, y: 0 }, data: {} },
      ];

      const results = searchNodesByLabel(nodes, '');

      expect(results).toHaveLength(1);
    });
  });

  describe('getNodeDegree', () => {
    it('should calculate node degree correctly', () => {
      const edges: GraphEdge[] = [
        { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e2', source: 'n1', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e3', source: 'n2', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
      ];

      expect(getNodeDegree('n1', edges)).toBe(2);
      expect(getNodeDegree('n2', edges)).toBe(2);
      expect(getNodeDegree('n3', edges)).toBe(2);
    });

    it('should return 0 for isolated node', () => {
      const edges: GraphEdge[] = [];
      expect(getNodeDegree('n1', edges)).toBe(0);
    });
  });

  describe('getNodeNeighbors', () => {
    it('should get all neighbors of a node', () => {
      const edges: GraphEdge[] = [
        { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e2', source: 'n1', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e3', source: 'n4', target: 'n1', type: 'default', weight: 0.5, metadata: {} },
      ];

      const neighbors = getNodeNeighbors('n1', edges);

      expect(neighbors.size).toBe(3);
      expect(neighbors.has('n2')).toBe(true);
      expect(neighbors.has('n3')).toBe(true);
      expect(neighbors.has('n4')).toBe(true);
    });
  });

  describe('buildAdjacencyList', () => {
    it('should build adjacency list from edges', () => {
      const edges: GraphEdge[] = [
        { id: 'e1', source: 'n1', target: 'n2', type: 'default', weight: 0.5, metadata: {} },
        { id: 'e2', source: 'n2', target: 'n3', type: 'default', weight: 0.5, metadata: {} },
      ];

      const adjList = buildAdjacencyList(edges);

      expect(adjList.get('n1')?.has('n2')).toBe(true);
      expect(adjList.get('n2')?.has('n1')).toBe(true);
      expect(adjList.get('n2')?.has('n3')).toBe(true);
      expect(adjList.get('n3')?.has('n2')).toBe(true);
    });
  });
});
