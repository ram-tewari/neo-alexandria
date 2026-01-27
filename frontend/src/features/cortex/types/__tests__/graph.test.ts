/**
 * Unit tests for graph type definitions
 * 
 * Tests type guards, validators, and enum values for the Cortex graph domain models
 */
import { describe, it, expect } from 'vitest';
import {
  HypothesisType,
  VisualizationMode,
  type GraphNode,
  type GraphEdge,
  type GraphData,
  type Hypothesis,
  type ABCHypothesis,
  type GraphEntity,
  type GraphRelationship,
  type EntityType,
  type RelationType,
  type LayoutAlgorithm,
  type GraphStatistics,
  type GraphPreferences,
  type BlastRadiusNode,
  type ImpactLevel,
} from '../graph';

describe('Graph Type Definitions', () => {
  describe('HypothesisType enum', () => {
    it('should have correct enum values', () => {
      expect(HypothesisType.CONTRADICTION).toBe('contradiction');
      expect(HypothesisType.HIDDEN_CONNECTION).toBe('hidden_connection');
      expect(HypothesisType.RESEARCH_GAP).toBe('research_gap');
    });

    it('should have exactly 3 values', () => {
      const values = Object.values(HypothesisType);
      expect(values).toHaveLength(3);
    });
  });

  describe('VisualizationMode enum', () => {
    it('should have correct enum values', () => {
      expect(VisualizationMode.CITY_MAP).toBe('city_map');
      expect(VisualizationMode.BLAST_RADIUS).toBe('blast_radius');
      expect(VisualizationMode.DEPENDENCY_WATERFALL).toBe('dependency_waterfall');
      expect(VisualizationMode.HYPOTHESIS).toBe('hypothesis');
      expect(VisualizationMode.DEFAULT).toBe('default');
    });

    it('should have exactly 5 values', () => {
      const values = Object.values(VisualizationMode);
      expect(values).toHaveLength(5);
    });
  });

  describe('GraphNode interface', () => {
    it('should accept valid default node', () => {
      const node: GraphNode = {
        id: 'node-1',
        label: 'Test Node',
        type: 'default',
        metadata: {
          title: 'Test Resource',
          resourceType: 'article',
          qualityScore: 0.85,
        },
        position: { x: 100, y: 200 },
        data: {},
      };

      expect(node.id).toBe('node-1');
      expect(node.label).toBe('Test Node');
      expect(node.type).toBe('default');
      expect(node.metadata.qualityScore).toBe(0.85);
      expect(node.position).toEqual({ x: 100, y: 200 });
    });

    it('should accept cluster node', () => {
      const node: GraphNode = {
        id: 'cluster-1',
        label: 'Machine Learning',
        type: 'cluster',
        metadata: {
          communityId: 'comm-1',
          centralityScore: 0.92,
        },
        position: { x: 0, y: 0 },
        data: {},
      };

      expect(node.type).toBe('cluster');
      expect(node.metadata.communityId).toBe('comm-1');
    });

    it('should accept entity node', () => {
      const node: GraphNode = {
        id: 'entity-1',
        label: 'Gradient Descent',
        type: 'entity',
        metadata: {
          entityType: 'Concept',
        },
        position: { x: 50, y: 50 },
        data: {},
      };

      expect(node.type).toBe('entity');
      expect(node.metadata.entityType).toBe('Concept');
    });

    it('should accept hypothesis node', () => {
      const node: GraphNode = {
        id: 'hyp-1',
        label: 'Contradiction',
        type: 'hypothesis',
        metadata: {
          hypothesisType: HypothesisType.CONTRADICTION,
          confidence: 0.87,
        },
        position: { x: 150, y: 150 },
        data: {},
      };

      expect(node.type).toBe('hypothesis');
      expect(node.metadata.hypothesisType).toBe(HypothesisType.CONTRADICTION);
      expect(node.metadata.confidence).toBe(0.87);
    });
  });

  describe('GraphEdge interface', () => {
    it('should accept valid default edge', () => {
      const edge: GraphEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 0.75,
        metadata: {
          relationshipType: 'semantic_similarity',
        },
      };

      expect(edge.id).toBe('edge-1');
      expect(edge.source).toBe('node-1');
      expect(edge.target).toBe('node-2');
      expect(edge.weight).toBe(0.75);
    });

    it('should accept citation edge', () => {
      const edge: GraphEdge = {
        id: 'cite-1',
        source: 'paper-1',
        target: 'paper-2',
        type: 'citation',
        weight: 1.0,
        metadata: {
          citationCount: 5,
        },
      };

      expect(edge.type).toBe('citation');
      expect(edge.metadata.citationCount).toBe(5);
    });

    it('should accept dependency edge', () => {
      const edge: GraphEdge = {
        id: 'dep-1',
        source: 'file-1',
        target: 'file-2',
        type: 'dependency',
        weight: 0.9,
        metadata: {
          dependencyType: 'import',
        },
      };

      expect(edge.type).toBe('dependency');
      expect(edge.metadata.dependencyType).toBe('import');
    });

    it('should accept relationship edge with full metadata', () => {
      const edge: GraphEdge = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'relationship',
        weight: 0.85,
        metadata: {
          relationType: 'EXTENDS',
          vectorSimilarity: 0.82,
          sharedSubjects: 3,
          classificationMatch: true,
        },
      };

      expect(edge.type).toBe('relationship');
      expect(edge.metadata.vectorSimilarity).toBe(0.82);
      expect(edge.metadata.sharedSubjects).toBe(3);
      expect(edge.metadata.classificationMatch).toBe(true);
    });
  });

  describe('GraphData interface', () => {
    it('should accept valid graph data', () => {
      const graphData: GraphData = {
        nodes: [
          {
            id: 'node-1',
            label: 'Node 1',
            type: 'default',
            metadata: {},
            position: { x: 0, y: 0 },
            data: {},
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
            type: 'default',
            weight: 0.5,
            metadata: {},
          },
        ],
        metadata: {
          totalNodes: 2,
          totalEdges: 1,
          density: 0.5,
          averageDegree: 1.0,
        },
      };

      expect(graphData.nodes).toHaveLength(1);
      expect(graphData.edges).toHaveLength(1);
      expect(graphData.metadata.totalNodes).toBe(2);
      expect(graphData.metadata.density).toBe(0.5);
    });

    it('should accept empty graph', () => {
      const graphData: GraphData = {
        nodes: [],
        edges: [],
        metadata: {
          totalNodes: 0,
          totalEdges: 0,
        },
      };

      expect(graphData.nodes).toHaveLength(0);
      expect(graphData.edges).toHaveLength(0);
    });
  });

  describe('Hypothesis interface', () => {
    it('should accept valid hypothesis', () => {
      const hypothesis: Hypothesis = {
        id: 'hyp-1',
        type: HypothesisType.HIDDEN_CONNECTION,
        confidence: 0.87,
        evidence: {
          aResourceId: 'res-1',
          cResourceId: 'res-2',
          bResourceIds: ['res-3', 'res-4'],
          supportStrength: 0.85,
          noveltyScore: 0.72,
          evidenceCount: 15,
        },
        nodes: ['node-1', 'node-2', 'node-3'],
        description: 'Hidden connection between ML and drug discovery',
        discoveredAt: '2024-01-01T10:00:00Z',
        isValidated: null,
      };

      expect(hypothesis.id).toBe('hyp-1');
      expect(hypothesis.type).toBe(HypothesisType.HIDDEN_CONNECTION);
      expect(hypothesis.confidence).toBe(0.87);
      expect(hypothesis.evidence.evidenceCount).toBe(15);
      expect(hypothesis.nodes).toHaveLength(3);
    });

    it('should accept contradiction hypothesis', () => {
      const hypothesis: Hypothesis = {
        id: 'hyp-2',
        type: HypothesisType.CONTRADICTION,
        confidence: 0.92,
        evidence: {
          pathStrength: 0.88,
          pathLength: 2,
        },
        nodes: ['node-1', 'node-2'],
      };

      expect(hypothesis.type).toBe(HypothesisType.CONTRADICTION);
      expect(hypothesis.evidence.pathLength).toBe(2);
    });

    it('should accept research gap hypothesis', () => {
      const hypothesis: Hypothesis = {
        id: 'hyp-3',
        type: HypothesisType.RESEARCH_GAP,
        confidence: 0.65,
        evidence: {
          commonNeighbors: 8,
        },
        nodes: ['node-1', 'node-2', 'node-3', 'node-4'],
        description: 'Missing research on X',
      };

      expect(hypothesis.type).toBe(HypothesisType.RESEARCH_GAP);
      expect(hypothesis.evidence.commonNeighbors).toBe(8);
    });
  });

  describe('ABCHypothesis interface', () => {
    it('should accept valid ABC hypothesis', () => {
      const hypothesis: ABCHypothesis = {
        id: 'abc-1',
        type: HypothesisType.HIDDEN_CONNECTION,
        confidence: 0.85,
        evidence: {
          supportStrength: 0.85,
          noveltyScore: 0.72,
          evidenceCount: 15,
        },
        nodes: ['node-a', 'node-b', 'node-c'],
        conceptA: 'machine learning',
        conceptC: 'drug discovery',
        bridgingConcept: 'molecular modeling',
        aToB: ['res-1', 'res-2'],
        bToC: ['res-3', 'res-4'],
      };

      expect(hypothesis.conceptA).toBe('machine learning');
      expect(hypothesis.conceptC).toBe('drug discovery');
      expect(hypothesis.bridgingConcept).toBe('molecular modeling');
      expect(hypothesis.aToB).toHaveLength(2);
      expect(hypothesis.bToC).toHaveLength(2);
    });
  });

  describe('GraphEntity interface', () => {
    it('should accept valid entity', () => {
      const entity: GraphEntity = {
        id: 'entity-1',
        name: 'Gradient Descent',
        type: 'Concept',
        properties: {
          description: 'An optimization algorithm',
          confidence: 0.95,
          sourceChunkId: 'chunk-1',
        },
        createdAt: '2024-01-01T10:00:00Z',
      };

      expect(entity.id).toBe('entity-1');
      expect(entity.name).toBe('Gradient Descent');
      expect(entity.type).toBe('Concept');
      expect(entity.properties.confidence).toBe(0.95);
    });

    it('should accept all entity types', () => {
      const types: EntityType[] = [
        'Concept',
        'Person',
        'Organization',
        'Method',
        'File',
        'Function',
        'Class',
        'Variable',
      ];

      types.forEach((type) => {
        const entity: GraphEntity = {
          id: `entity-${type}`,
          name: `Test ${type}`,
          type,
          properties: {},
        };

        expect(entity.type).toBe(type);
      });
    });
  });

  describe('GraphRelationship interface', () => {
    it('should accept valid relationship', () => {
      const relationship: GraphRelationship = {
        id: 'rel-1',
        source: 'entity-1',
        target: 'entity-2',
        type: 'EXTENDS',
        properties: {
          weight: 0.9,
          confidence: 0.85,
          provenanceChunkId: 'chunk-1',
        },
        createdAt: '2024-01-01T10:00:00Z',
      };

      expect(relationship.id).toBe('rel-1');
      expect(relationship.source).toBe('entity-1');
      expect(relationship.target).toBe('entity-2');
      expect(relationship.type).toBe('EXTENDS');
      expect(relationship.properties.weight).toBe(0.9);
    });

    it('should accept all relationship types', () => {
      const types: RelationType[] = [
        'CONTRADICTS',
        'SUPPORTS',
        'EXTENDS',
        'CITES',
        'CALLS',
        'IMPORTS',
        'DEFINES',
        'SEMANTIC_SIMILARITY',
      ];

      types.forEach((type) => {
        const relationship: GraphRelationship = {
          id: `rel-${type}`,
          source: 'entity-1',
          target: 'entity-2',
          type,
          properties: {},
        };

        expect(relationship.type).toBe(type);
      });
    });
  });

  describe('LayoutAlgorithm type', () => {
    it('should accept all layout algorithms', () => {
      const algorithms: LayoutAlgorithm[] = [
        'force-directed',
        'hierarchical',
        'circular',
        'dagre',
        'manual',
      ];

      algorithms.forEach((algorithm) => {
        const layout: LayoutAlgorithm = algorithm;
        expect(layout).toBe(algorithm);
      });
    });
  });

  describe('GraphStatistics interface', () => {
    it('should accept valid statistics', () => {
      const stats: GraphStatistics = {
        nodeCount: 100,
        edgeCount: 250,
        selectedNodeCount: 5,
        selectedEdgeCount: 8,
        density: 0.05,
        averageDegree: 5.0,
        communities: 12,
        isolatedNodes: 3,
      };

      expect(stats.nodeCount).toBe(100);
      expect(stats.edgeCount).toBe(250);
      expect(stats.density).toBe(0.05);
      expect(stats.communities).toBe(12);
    });

    it('should accept minimal statistics', () => {
      const stats: GraphStatistics = {
        nodeCount: 0,
        edgeCount: 0,
        selectedNodeCount: 0,
        selectedEdgeCount: 0,
        density: 0,
        averageDegree: 0,
      };

      expect(stats.nodeCount).toBe(0);
      expect(stats.edgeCount).toBe(0);
    });
  });

  describe('GraphPreferences interface', () => {
    it('should accept valid preferences', () => {
      const prefs: GraphPreferences = {
        showLabels: true,
        showMinimap: true,
        showControls: true,
        animationSpeed: 1.0,
        nodeSize: 50,
        edgeWidth: 2,
        colorScheme: 'dark',
        defaultLayout: 'force-directed',
        defaultVisualizationMode: VisualizationMode.CITY_MAP,
      };

      expect(prefs.showLabels).toBe(true);
      expect(prefs.colorScheme).toBe('dark');
      expect(prefs.defaultLayout).toBe('force-directed');
      expect(prefs.defaultVisualizationMode).toBe(VisualizationMode.CITY_MAP);
    });

    it('should accept all color schemes', () => {
      const schemes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];

      schemes.forEach((scheme) => {
        const prefs: GraphPreferences = {
          showLabels: true,
          showMinimap: true,
          showControls: true,
          animationSpeed: 1.0,
          nodeSize: 50,
          edgeWidth: 2,
          colorScheme: scheme,
          defaultLayout: 'force-directed',
          defaultVisualizationMode: VisualizationMode.DEFAULT,
        };

        expect(prefs.colorScheme).toBe(scheme);
      });
    });
  });

  describe('BlastRadiusNode interface', () => {
    it('should accept valid blast radius node', () => {
      const node: BlastRadiusNode = {
        id: 'node-1',
        label: 'Affected Node',
        type: 'default',
        metadata: {},
        position: { x: 100, y: 100 },
        data: {},
        impactScore: 0.85,
        impactLevel: 'high',
        hopDistance: 1,
      };

      expect(node.impactScore).toBe(0.85);
      expect(node.impactLevel).toBe('high');
      expect(node.hopDistance).toBe(1);
    });

    it('should accept all impact levels', () => {
      const levels: ImpactLevel[] = ['high', 'medium', 'low'];

      levels.forEach((level) => {
        const node: BlastRadiusNode = {
          id: `node-${level}`,
          label: `${level} impact`,
          type: 'default',
          metadata: {},
          position: { x: 0, y: 0 },
          data: {},
          impactScore: level === 'high' ? 0.9 : level === 'medium' ? 0.5 : 0.2,
          impactLevel: level,
          hopDistance: 1,
        };

        expect(node.impactLevel).toBe(level);
      });
    });
  });

  describe('Type compatibility', () => {
    it('should allow GraphNode to be used as React Flow node', () => {
      const node: GraphNode = {
        id: 'node-1',
        label: 'Test',
        type: 'default',
        metadata: {},
        position: { x: 0, y: 0 },
        data: {},
      };

      // This test verifies that GraphNode extends ReactFlowNode
      // If it compiles, the type is compatible
      expect(node.id).toBeDefined();
      expect(node.position).toBeDefined();
      expect(node.data).toBeDefined();
    });

    it('should allow GraphEdge to be used as React Flow edge', () => {
      const edge: GraphEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        weight: 0.5,
        metadata: {},
      };

      // This test verifies that GraphEdge extends ReactFlowEdge
      // If it compiles, the type is compatible
      expect(edge.id).toBeDefined();
      expect(edge.source).toBeDefined();
      expect(edge.target).toBeDefined();
    });
  });
});
