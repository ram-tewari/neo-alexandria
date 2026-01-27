/**
 * Graph Store Tests
 * 
 * Tests for the graph Zustand store including state management,
 * actions, and selectors.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 2 State Management
 * Task: 2.1
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { 
  useGraphStore,
  selectSelectedNodes,
  selectSelectedEdges,
  selectSelectedNodeCount,
  selectSelectedEdgeCount,
  selectHasSelection,
  selectNodeById,
  selectEdgeById,
  selectConnectedEdges,
  selectNeighbors,
  selectGraphStats,
  selectNodesByType,
  selectEdgesByType,
} from '../graph';
import type { GraphNode, GraphEdge, GraphData } from '@/types/graph';
import { VisualizationMode } from '@/types/graph';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock graph node for testing
 */
const createMockNode = (overrides?: Partial<GraphNode>): GraphNode => ({
  id: `node_${Math.random().toString(36).substr(2, 9)}`,
  label: 'Test Node',
  type: 'resource',
  position: { x: 0, y: 0 },
  ...overrides
});

/**
 * Create a mock graph edge for testing
 */
const createMockEdge = (overrides?: Partial<GraphEdge>): GraphEdge => ({
  id: `edge_${Math.random().toString(36).substr(2, 9)}`,
  source: 'node_1',
  target: 'node_2',
  type: 'citation',
  ...overrides
});

/**
 * Create mock graph data for testing
 */
const createMockGraphData = (): GraphData => ({
  nodes: [
    createMockNode({ id: 'node_1', label: 'Node 1' }),
    createMockNode({ id: 'node_2', label: 'Node 2' }),
  ],
  edges: [
    createMockEdge({ id: 'edge_1', source: 'node_1', target: 'node_2' }),
  ],
  metadata: {
    nodeCount: 2,
    edgeCount: 1,
  },
});

/**
 * Reset store to initial state before each test
 */
const resetStore = () => {
  useGraphStore.setState({
    nodes: [],
    edges: [],
    selectedNodes: new Set(),
    selectedEdges: new Set(),
    metadata: undefined,
    visualizationMode: VisualizationMode.CityMap,
    zoomLevel: 1.0,
    centerPosition: { x: 0, y: 0 },
    graphCache: new Map(),
    lastCacheUpdate: null,
    cacheTTL: 5 * 60 * 1000,
  });
};

// ============================================================================
// Tests
// ============================================================================

describe('Graph Store', () => {
  beforeEach(() => {
    resetStore();
  });

  // ==========================================================================
  // Initial State
  // ==========================================================================

  describe('Initial State', () => {
    it('should have empty nodes array', () => {
      const { nodes } = useGraphStore.getState();
      expect(nodes).toEqual([]);
    });

    it('should have empty edges array', () => {
      const { edges } = useGraphStore.getState();
      expect(edges).toEqual([]);
    });

    it('should have no selected nodes', () => {
      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.size).toBe(0);
    });

    it('should have no selected edges', () => {
      const { selectedEdges } = useGraphStore.getState();
      expect(selectedEdges.size).toBe(0);
    });

    it('should have default visualization mode (CityMap)', () => {
      const { visualizationMode } = useGraphStore.getState();
      expect(visualizationMode).toBe(VisualizationMode.CityMap);
    });

    it('should have default zoom level (1.0)', () => {
      const { zoomLevel } = useGraphStore.getState();
      expect(zoomLevel).toBe(1.0);
    });

    it('should have default center position (0, 0)', () => {
      const { centerPosition } = useGraphStore.getState();
      expect(centerPosition).toEqual({ x: 0, y: 0 });
    });

    it('should have empty cache', () => {
      const { graphCache } = useGraphStore.getState();
      expect(graphCache.size).toBe(0);
    });
  });

  // ==========================================================================
  // Graph Data Actions
  // ==========================================================================

  describe('setGraphData', () => {
    it('should set graph data', () => {
      const data = createMockGraphData();
      useGraphStore.getState().setGraphData(data);

      const state = useGraphStore.getState();
      expect(state.nodes).toEqual(data.nodes);
      expect(state.edges).toEqual(data.edges);
      expect(state.metadata).toEqual(data.metadata);
    });

    it('should clear selections when loading new graph', () => {
      const data = createMockGraphData();
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectEdge('edge_1');

      useGraphStore.getState().setGraphData(data);

      const state = useGraphStore.getState();
      expect(state.selectedNodes.size).toBe(0);
      expect(state.selectedEdges.size).toBe(0);
    });
  });

  describe('addNodes', () => {
    it('should add nodes to the graph', () => {
      const existing = [createMockNode({ id: 'node_1' })];
      const newNodes = [createMockNode({ id: 'node_2' })];

      useGraphStore.getState().setGraphData({ nodes: existing, edges: [] });
      useGraphStore.getState().addNodes(newNodes);

      const { nodes } = useGraphStore.getState();
      expect(nodes).toHaveLength(2);
      expect(nodes[1].id).toBe('node_2');
    });
  });

  describe('addEdges', () => {
    it('should add edges to the graph', () => {
      const existing = [createMockEdge({ id: 'edge_1' })];
      const newEdges = [createMockEdge({ id: 'edge_2' })];

      useGraphStore.getState().setGraphData({ nodes: [], edges: existing });
      useGraphStore.getState().addEdges(newEdges);

      const { edges } = useGraphStore.getState();
      expect(edges).toHaveLength(2);
      expect(edges[1].id).toBe('edge_2');
    });
  });

  describe('updateNode', () => {
    it('should update node by ID', () => {
      const node = createMockNode({ id: 'node_1', label: 'Original' });
      useGraphStore.getState().setGraphData({ nodes: [node], edges: [] });

      useGraphStore.getState().updateNode('node_1', { label: 'Updated' });

      const updated = useGraphStore.getState().nodes[0];
      expect(updated.label).toBe('Updated');
      expect(updated.id).toBe('node_1');
    });

    it('should not affect other nodes', () => {
      const nodes = [
        createMockNode({ id: 'node_1', label: 'First' }),
        createMockNode({ id: 'node_2', label: 'Second' }),
      ];
      useGraphStore.getState().setGraphData({ nodes, edges: [] });

      useGraphStore.getState().updateNode('node_1', { label: 'Updated' });

      const { nodes: updated } = useGraphStore.getState();
      expect(updated[0].label).toBe('Updated');
      expect(updated[1].label).toBe('Second');
    });
  });

  describe('updateEdge', () => {
    it('should update edge by ID', () => {
      const edge = createMockEdge({ id: 'edge_1', weight: 0.5 });
      useGraphStore.getState().setGraphData({ nodes: [], edges: [edge] });

      useGraphStore.getState().updateEdge('edge_1', { weight: 0.8 });

      const updated = useGraphStore.getState().edges[0];
      expect(updated.weight).toBe(0.8);
    });
  });

  describe('removeNodes', () => {
    it('should remove nodes by IDs', () => {
      const nodes = [
        createMockNode({ id: 'node_1' }),
        createMockNode({ id: 'node_2' }),
        createMockNode({ id: 'node_3' }),
      ];
      useGraphStore.getState().setGraphData({ nodes, edges: [] });

      useGraphStore.getState().removeNodes(['node_1', 'node_3']);

      const { nodes: remaining } = useGraphStore.getState();
      expect(remaining).toHaveLength(1);
      expect(remaining[0].id).toBe('node_2');
    });

    it('should remove connected edges', () => {
      const nodes = [
        createMockNode({ id: 'node_1' }),
        createMockNode({ id: 'node_2' }),
      ];
      const edges = [
        createMockEdge({ id: 'edge_1', source: 'node_1', target: 'node_2' }),
      ];
      useGraphStore.getState().setGraphData({ nodes, edges });

      useGraphStore.getState().removeNodes(['node_1']);

      const { edges: remaining } = useGraphStore.getState();
      expect(remaining).toHaveLength(0);
    });

    it('should clear selections for removed nodes', () => {
      const nodes = [createMockNode({ id: 'node_1' })];
      useGraphStore.getState().setGraphData({ nodes, edges: [] });
      useGraphStore.getState().selectNode('node_1');

      useGraphStore.getState().removeNodes(['node_1']);

      expect(useGraphStore.getState().selectedNodes.size).toBe(0);
    });
  });

  describe('removeEdges', () => {
    it('should remove edges by IDs', () => {
      const edges = [
        createMockEdge({ id: 'edge_1' }),
        createMockEdge({ id: 'edge_2' }),
      ];
      useGraphStore.getState().setGraphData({ nodes: [], edges });

      useGraphStore.getState().removeEdges(['edge_1']);

      const { edges: remaining } = useGraphStore.getState();
      expect(remaining).toHaveLength(1);
      expect(remaining[0].id).toBe('edge_2');
    });

    it('should clear selections for removed edges', () => {
      const edges = [createMockEdge({ id: 'edge_1' })];
      useGraphStore.getState().setGraphData({ nodes: [], edges });
      useGraphStore.getState().selectEdge('edge_1');

      useGraphStore.getState().removeEdges(['edge_1']);

      expect(useGraphStore.getState().selectedEdges.size).toBe(0);
    });
  });

  describe('clearGraph', () => {
    it('should clear all graph data', () => {
      const data = createMockGraphData();
      useGraphStore.getState().setGraphData(data);
      useGraphStore.getState().selectNode('node_1');

      useGraphStore.getState().clearGraph();

      const state = useGraphStore.getState();
      expect(state.nodes).toEqual([]);
      expect(state.edges).toEqual([]);
      expect(state.selectedNodes.size).toBe(0);
      expect(state.selectedEdges.size).toBe(0);
      expect(state.metadata).toBeUndefined();
    });
  });

  // ==========================================================================
  // Selection Actions
  // ==========================================================================

  describe('selectNode', () => {
    it('should select a node (replace mode)', () => {
      useGraphStore.getState().selectNode('node_1');

      expect(useGraphStore.getState().selectedNodes.has('node_1')).toBe(true);
    });

    it('should replace existing selection by default', () => {
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectNode('node_2');

      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.has('node_1')).toBe(false);
      expect(selectedNodes.has('node_2')).toBe(true);
    });

    it('should add to selection when replace=false', () => {
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectNode('node_2', false);

      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.has('node_1')).toBe(true);
      expect(selectedNodes.has('node_2')).toBe(true);
    });

    it('should clear edge selection when selecting node', () => {
      useGraphStore.getState().selectEdge('edge_1');
      useGraphStore.getState().selectNode('node_1');

      const state = useGraphStore.getState();
      expect(state.selectedEdges.size).toBe(0);
      expect(state.selectedNodes.has('node_1')).toBe(true);
    });
  });

  describe('selectNodes', () => {
    it('should select multiple nodes', () => {
      useGraphStore.getState().selectNodes(['node_1', 'node_2']);

      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.has('node_1')).toBe(true);
      expect(selectedNodes.has('node_2')).toBe(true);
    });

    it('should add to selection when replace=false', () => {
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectNodes(['node_2', 'node_3'], false);

      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.size).toBe(3);
    });
  });

  describe('deselectNode', () => {
    it('should deselect a node', () => {
      useGraphStore.getState().selectNodes(['node_1', 'node_2']);
      useGraphStore.getState().deselectNode('node_1');

      const { selectedNodes } = useGraphStore.getState();
      expect(selectedNodes.has('node_1')).toBe(false);
      expect(selectedNodes.has('node_2')).toBe(true);
    });
  });

  describe('selectEdge', () => {
    it('should select an edge', () => {
      useGraphStore.getState().selectEdge('edge_1');

      expect(useGraphStore.getState().selectedEdges.has('edge_1')).toBe(true);
    });

    it('should clear node selection when selecting edge', () => {
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectEdge('edge_1');

      const state = useGraphStore.getState();
      expect(state.selectedNodes.size).toBe(0);
      expect(state.selectedEdges.has('edge_1')).toBe(true);
    });
  });

  describe('clearSelection', () => {
    it('should clear all selections', () => {
      useGraphStore.getState().selectNode('node_1');
      useGraphStore.getState().selectEdge('edge_1', false);
      useGraphStore.getState().clearSelection();

      const state = useGraphStore.getState();
      expect(state.selectedNodes.size).toBe(0);
      expect(state.selectedEdges.size).toBe(0);
    });
  });

  describe('isNodeSelected', () => {
    it('should return true for selected node', () => {
      useGraphStore.getState().selectNode('node_1');
      expect(useGraphStore.getState().isNodeSelected('node_1')).toBe(true);
    });

    it('should return false for unselected node', () => {
      expect(useGraphStore.getState().isNodeSelected('node_1')).toBe(false);
    });
  });

  describe('isEdgeSelected', () => {
    it('should return true for selected edge', () => {
      useGraphStore.getState().selectEdge('edge_1');
      expect(useGraphStore.getState().isEdgeSelected('edge_1')).toBe(true);
    });

    it('should return false for unselected edge', () => {
      expect(useGraphStore.getState().isEdgeSelected('edge_1')).toBe(false);
    });
  });

  // ==========================================================================
  // Visualization Actions
  // ==========================================================================

  describe('setVisualizationMode', () => {
    it('should set visualization mode', () => {
      useGraphStore.getState().setVisualizationMode(VisualizationMode.BlastRadius);

      expect(useGraphStore.getState().visualizationMode).toBe(VisualizationMode.BlastRadius);
    });
  });

  describe('Zoom Actions', () => {
    it('should set zoom level', () => {
      useGraphStore.getState().setZoom(1.5);
      expect(useGraphStore.getState().zoomLevel).toBe(1.5);
    });

    it('should clamp zoom to minimum (0.1)', () => {
      useGraphStore.getState().setZoom(0.05);
      expect(useGraphStore.getState().zoomLevel).toBe(0.1);
    });

    it('should clamp zoom to maximum (2.0)', () => {
      useGraphStore.getState().setZoom(3.0);
      expect(useGraphStore.getState().zoomLevel).toBe(2.0);
    });

    it('should zoom in by factor', () => {
      useGraphStore.getState().setZoom(1.0);
      useGraphStore.getState().zoomIn(1.2);
      expect(useGraphStore.getState().zoomLevel).toBe(1.2);
    });

    it('should zoom out by factor', () => {
      useGraphStore.getState().setZoom(1.2);
      useGraphStore.getState().zoomOut(1.2);
      expect(useGraphStore.getState().zoomLevel).toBe(1.0);
    });

    it('should not zoom in beyond maximum', () => {
      useGraphStore.getState().setZoom(1.9);
      useGraphStore.getState().zoomIn(1.5);
      expect(useGraphStore.getState().zoomLevel).toBe(2.0);
    });

    it('should not zoom out below minimum', () => {
      useGraphStore.getState().setZoom(0.15);
      useGraphStore.getState().zoomOut(2.0);
      expect(useGraphStore.getState().zoomLevel).toBe(0.1);
    });

    it('should reset zoom to 1.0', () => {
      useGraphStore.getState().setZoom(1.5);
      useGraphStore.getState().resetZoom();
      expect(useGraphStore.getState().zoomLevel).toBe(1.0);
    });
  });

  describe('Pan Actions', () => {
    it('should set center position', () => {
      useGraphStore.getState().setCenter({ x: 100, y: 200 });

      const { centerPosition } = useGraphStore.getState();
      expect(centerPosition).toEqual({ x: 100, y: 200 });
    });

    it('should pan by delta', () => {
      useGraphStore.getState().setCenter({ x: 100, y: 100 });
      useGraphStore.getState().pan({ x: 50, y: -30 });

      const { centerPosition } = useGraphStore.getState();
      expect(centerPosition).toEqual({ x: 150, y: 70 });
    });
  });

  describe('Viewport Actions', () => {
    it('should get viewport state', () => {
      useGraphStore.getState().setZoom(1.5);
      useGraphStore.getState().setCenter({ x: 100, y: 200 });

      const viewport = useGraphStore.getState().getViewport();
      expect(viewport).toEqual({
        zoom: 1.5,
        center: { x: 100, y: 200 },
      });
    });

    it('should set viewport state', () => {
      useGraphStore.getState().setViewport({
        zoom: 1.5,
        center: { x: 100, y: 200 },
      });

      const state = useGraphStore.getState();
      expect(state.zoomLevel).toBe(1.5);
      expect(state.centerPosition).toEqual({ x: 100, y: 200 });
    });

    it('should clamp zoom when setting viewport', () => {
      useGraphStore.getState().setViewport({
        zoom: 3.0,
        center: { x: 0, y: 0 },
      });

      expect(useGraphStore.getState().zoomLevel).toBe(2.0);
    });

    it('should reset viewport', () => {
      useGraphStore.getState().setZoom(1.5);
      useGraphStore.getState().setCenter({ x: 100, y: 200 });
      useGraphStore.getState().resetViewport();

      const state = useGraphStore.getState();
      expect(state.zoomLevel).toBe(1.0);
      expect(state.centerPosition).toEqual({ x: 0, y: 0 });
    });
  });

  // ==========================================================================
  // Cache Actions
  // ==========================================================================

  describe('Cache Actions', () => {
    it('should cache graph data', () => {
      const data = createMockGraphData();
      useGraphStore.getState().cacheGraphData('test_key', data);

      const cached = useGraphStore.getState().getCachedGraphData('test_key');
      expect(cached).toEqual(data);
    });

    it('should return null for non-existent cache key', () => {
      const cached = useGraphStore.getState().getCachedGraphData('nonexistent');
      expect(cached).toBeNull();
    });

    it('should update lastCacheUpdate timestamp', () => {
      const before = Date.now();
      const data = createMockGraphData();
      useGraphStore.getState().cacheGraphData('test_key', data);
      const after = Date.now();

      const { lastCacheUpdate } = useGraphStore.getState();
      expect(lastCacheUpdate).toBeGreaterThanOrEqual(before);
      expect(lastCacheUpdate).toBeLessThanOrEqual(after);
    });

    it('should clear cache', () => {
      const data = createMockGraphData();
      useGraphStore.getState().cacheGraphData('test_key', data);
      useGraphStore.getState().clearCache();

      const cached = useGraphStore.getState().getCachedGraphData('test_key');
      expect(cached).toBeNull();
    });

    it('should return null for expired cache', () => {
      const data = createMockGraphData();
      useGraphStore.getState().cacheGraphData('test_key', data);
      
      // Manually set lastCacheUpdate to expired time
      useGraphStore.setState({
        lastCacheUpdate: Date.now() - (6 * 60 * 1000), // 6 minutes ago
      });

      const cached = useGraphStore.getState().getCachedGraphData('test_key');
      expect(cached).toBeNull();
    });

    it('should validate cache correctly', () => {
      expect(useGraphStore.getState().isCacheValid()).toBe(false);

      const data = createMockGraphData();
      useGraphStore.getState().cacheGraphData('test_key', data);
      expect(useGraphStore.getState().isCacheValid()).toBe(true);

      // Expire cache
      useGraphStore.setState({
        lastCacheUpdate: Date.now() - (6 * 60 * 1000),
      });
      expect(useGraphStore.getState().isCacheValid()).toBe(false);
    });
  });

  // ==========================================================================
  // Selectors
  // ==========================================================================

  describe('Selectors', () => {
    describe('selectSelectedNodes', () => {
      it('should return selected node objects', () => {
        const nodes = [
          createMockNode({ id: 'node_1', label: 'Node 1' }),
          createMockNode({ id: 'node_2', label: 'Node 2' }),
        ];
        useGraphStore.getState().setGraphData({ nodes, edges: [] });
        useGraphStore.getState().selectNode('node_1');

        const selected = selectSelectedNodes(useGraphStore.getState());
        expect(selected).toHaveLength(1);
        expect(selected[0].id).toBe('node_1');
      });
    });

    describe('selectSelectedEdges', () => {
      it('should return selected edge objects', () => {
        const edges = [
          createMockEdge({ id: 'edge_1' }),
          createMockEdge({ id: 'edge_2' }),
        ];
        useGraphStore.getState().setGraphData({ nodes: [], edges });
        useGraphStore.getState().selectEdge('edge_1');

        const selected = selectSelectedEdges(useGraphStore.getState());
        expect(selected).toHaveLength(1);
        expect(selected[0].id).toBe('edge_1');
      });
    });

    describe('selectSelectedNodeCount', () => {
      it('should return count of selected nodes', () => {
        useGraphStore.getState().selectNodes(['node_1', 'node_2']);
        const count = selectSelectedNodeCount(useGraphStore.getState());
        expect(count).toBe(2);
      });
    });

    describe('selectSelectedEdgeCount', () => {
      it('should return count of selected edges', () => {
        useGraphStore.getState().selectEdges(['edge_1', 'edge_2']);
        const count = selectSelectedEdgeCount(useGraphStore.getState());
        expect(count).toBe(2);
      });
    });

    describe('selectHasSelection', () => {
      it('should return true when nodes are selected', () => {
        useGraphStore.getState().selectNode('node_1');
        expect(selectHasSelection(useGraphStore.getState())).toBe(true);
      });

      it('should return true when edges are selected', () => {
        useGraphStore.getState().selectEdge('edge_1');
        expect(selectHasSelection(useGraphStore.getState())).toBe(true);
      });

      it('should return false when nothing is selected', () => {
        expect(selectHasSelection(useGraphStore.getState())).toBe(false);
      });
    });

    describe('selectNodeById', () => {
      it('should return node by ID', () => {
        const nodes = [
          createMockNode({ id: 'node_1', label: 'Node 1' }),
          createMockNode({ id: 'node_2', label: 'Node 2' }),
        ];
        useGraphStore.getState().setGraphData({ nodes, edges: [] });

        const getNode = selectNodeById(useGraphStore.getState());
        const node = getNode('node_1');
        expect(node?.label).toBe('Node 1');
      });

      it('should return undefined for non-existent ID', () => {
        const getNode = selectNodeById(useGraphStore.getState());
        const node = getNode('nonexistent');
        expect(node).toBeUndefined();
      });
    });

    describe('selectEdgeById', () => {
      it('should return edge by ID', () => {
        const edges = [createMockEdge({ id: 'edge_1', weight: 0.8 })];
        useGraphStore.getState().setGraphData({ nodes: [], edges });

        const getEdge = selectEdgeById(useGraphStore.getState());
        const edge = getEdge('edge_1');
        expect(edge?.weight).toBe(0.8);
      });
    });

    describe('selectConnectedEdges', () => {
      it('should return edges connected to a node', () => {
        const edges = [
          createMockEdge({ id: 'edge_1', source: 'node_1', target: 'node_2' }),
          createMockEdge({ id: 'edge_2', source: 'node_2', target: 'node_3' }),
          createMockEdge({ id: 'edge_3', source: 'node_3', target: 'node_4' }),
        ];
        useGraphStore.getState().setGraphData({ nodes: [], edges });

        const getConnected = selectConnectedEdges(useGraphStore.getState());
        const connected = getConnected('node_2');
        expect(connected).toHaveLength(2);
        expect(connected.map(e => e.id)).toContain('edge_1');
        expect(connected.map(e => e.id)).toContain('edge_2');
      });
    });

    describe('selectNeighbors', () => {
      it('should return neighbor nodes', () => {
        const nodes = [
          createMockNode({ id: 'node_1' }),
          createMockNode({ id: 'node_2' }),
          createMockNode({ id: 'node_3' }),
        ];
        const edges = [
          createMockEdge({ id: 'edge_1', source: 'node_1', target: 'node_2' }),
          createMockEdge({ id: 'edge_2', source: 'node_1', target: 'node_3' }),
        ];
        useGraphStore.getState().setGraphData({ nodes, edges });

        const getNeighbors = selectNeighbors(useGraphStore.getState());
        const neighbors = getNeighbors('node_1');
        expect(neighbors).toHaveLength(2);
        expect(neighbors.map(n => n.id)).toContain('node_2');
        expect(neighbors.map(n => n.id)).toContain('node_3');
      });
    });

    describe('selectGraphStats', () => {
      it('should return graph statistics', () => {
        const data = createMockGraphData();
        useGraphStore.getState().setGraphData(data);
        useGraphStore.getState().selectNode('node_1');

        const stats = selectGraphStats(useGraphStore.getState());
        expect(stats.nodeCount).toBe(2);
        expect(stats.edgeCount).toBe(1);
        expect(stats.selectedNodeCount).toBe(1);
        expect(stats.selectedEdgeCount).toBe(0);
      });
    });

    describe('selectNodesByType', () => {
      it('should return nodes filtered by type', () => {
        const nodes = [
          createMockNode({ id: 'node_1', type: 'resource' }),
          createMockNode({ id: 'node_2', type: 'entity' }),
          createMockNode({ id: 'node_3', type: 'resource' }),
        ];
        useGraphStore.getState().setGraphData({ nodes, edges: [] });

        const getByType = selectNodesByType(useGraphStore.getState());
        const resourceNodes = getByType('resource');
        expect(resourceNodes).toHaveLength(2);
      });
    });

    describe('selectEdgesByType', () => {
      it('should return edges filtered by type', () => {
        const edges = [
          createMockEdge({ id: 'edge_1', type: 'citation' }),
          createMockEdge({ id: 'edge_2', type: 'dependency' }),
          createMockEdge({ id: 'edge_3', type: 'citation' }),
        ];
        useGraphStore.getState().setGraphData({ nodes: [], edges });

        const getByType = selectEdgesByType(useGraphStore.getState());
        const citationEdges = getByType('citation');
        expect(citationEdges).toHaveLength(2);
      });
    });
  });
});
