/**
 * Graph Store
 * 
 * Zustand store for managing graph visualization state including nodes, edges,
 * selected elements, visualization mode, and viewport state.
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 2 State Management
 * Task: 2.1
 */

import { create } from 'zustand';
import {
  VisualizationMode,
  type GraphNode,
  type GraphEdge,
  type GraphData,
  type ViewportState,
  type Position,
} from '@/types/graph';

// ============================================================================
// State Interface
// ============================================================================

/**
 * Graph store state and actions
 */
interface GraphState {
  // ========================================================================
  // Graph Data State
  // ========================================================================
  
  /** All nodes in the graph */
  nodes: GraphNode[];
  
  /** All edges in the graph */
  edges: GraphEdge[];
  
  /** Currently selected node IDs */
  selectedNodes: Set<string>;
  
  /** Currently selected edge IDs */
  selectedEdges: Set<string>;
  
  /** Graph metadata */
  metadata: GraphData['metadata'];
  
  // ========================================================================
  // Visualization State
  // ========================================================================
  
  /** Current visualization mode */
  visualizationMode: VisualizationMode;
  
  /** Zoom level (0.1 - 2.0) */
  zoomLevel: number;
  
  /** Center position of the viewport */
  centerPosition: Position;
  
  // ========================================================================
  // Cache State
  // ========================================================================
  
  /** Cached graph data by resource ID or query */
  graphCache: Map<string, GraphData>;
  
  /** Timestamp of last cache update */
  lastCacheUpdate: number | null;
  
  /** Cache TTL in milliseconds (default: 5 minutes) */
  cacheTTL: number;
  
  // ========================================================================
  // Graph Data Actions
  // ========================================================================
  
  /**
   * Set complete graph data (replaces existing)
   * Used when fetching fresh data from API
   */
  setGraphData: (data: GraphData) => void;
  
  /**
   * Add nodes to the graph
   * Used for incremental updates
   */
  addNodes: (nodes: GraphNode[]) => void;
  
  /**
   * Add edges to the graph
   * Used for incremental updates
   */
  addEdges: (edges: GraphEdge[]) => void;
  
  /**
   * Update a node by ID
   * Used for optimistic updates
   */
  updateNode: (id: string, updates: Partial<GraphNode>) => void;
  
  /**
   * Update an edge by ID
   * Used for optimistic updates
   */
  updateEdge: (id: string, updates: Partial<GraphEdge>) => void;
  
  /**
   * Remove nodes by IDs
   * Also removes connected edges
   */
  removeNodes: (ids: string[]) => void;
  
  /**
   * Remove edges by IDs
   */
  removeEdges: (ids: string[]) => void;
  
  /**
   * Clear all graph data
   */
  clearGraph: () => void;
  
  // ========================================================================
  // Selection Actions
  // ========================================================================
  
  /**
   * Select a node
   * Pass replace=true to replace current selection
   * Pass replace=false to add to selection (multi-select)
   */
  selectNode: (id: string, replace?: boolean) => void;
  
  /**
   * Select multiple nodes
   * Pass replace=true to replace current selection
   */
  selectNodes: (ids: string[], replace?: boolean) => void;
  
  /**
   * Deselect a node
   */
  deselectNode: (id: string) => void;
  
  /**
   * Select an edge
   * Pass replace=true to replace current selection
   */
  selectEdge: (id: string, replace?: boolean) => void;
  
  /**
   * Select multiple edges
   * Pass replace=true to replace current selection
   */
  selectEdges: (ids: string[], replace?: boolean) => void;
  
  /**
   * Deselect an edge
   */
  deselectEdge: (id: string) => void;
  
  /**
   * Clear all selections (nodes and edges)
   */
  clearSelection: () => void;
  
  /**
   * Check if a node is selected
   */
  isNodeSelected: (id: string) => boolean;
  
  /**
   * Check if an edge is selected
   */
  isEdgeSelected: (id: string) => boolean;
  
  // ========================================================================
  // Visualization Actions
  // ========================================================================
  
  /**
   * Set visualization mode
   * Changes how the graph is displayed
   */
  setVisualizationMode: (mode: VisualizationMode) => void;
  
  /**
   * Set zoom level
   * Clamped between 0.1 and 2.0
   */
  setZoom: (zoom: number) => void;
  
  /**
   * Zoom in by a factor
   * Default factor: 1.2
   */
  zoomIn: (factor?: number) => void;
  
  /**
   * Zoom out by a factor
   * Default factor: 1.2
   */
  zoomOut: (factor?: number) => void;
  
  /**
   * Reset zoom to 1.0
   */
  resetZoom: () => void;
  
  /**
   * Set center position
   */
  setCenter: (position: Position) => void;
  
  /**
   * Pan the viewport by a delta
   */
  pan: (delta: Position) => void;
  
  /**
   * Get current viewport state
   */
  getViewport: () => ViewportState;
  
  /**
   * Set viewport state (zoom and center)
   */
  setViewport: (viewport: ViewportState) => void;
  
  /**
   * Reset viewport to default (zoom=1, center={0,0})
   */
  resetViewport: () => void;
  
  // ========================================================================
  // Cache Actions
  // ========================================================================
  
  /**
   * Cache graph data with a key
   * Used to avoid re-fetching the same data
   */
  cacheGraphData: (key: string, data: GraphData) => void;
  
  /**
   * Get cached graph data by key
   * Returns null if not found or expired
   */
  getCachedGraphData: (key: string) => GraphData | null;
  
  /**
   * Clear graph cache
   */
  clearCache: () => void;
  
  /**
   * Check if cache is valid (not expired)
   */
  isCacheValid: () => boolean;
}

// ============================================================================
// Store Implementation
// ============================================================================

/**
 * Graph store instance
 * 
 * @example
 * ```typescript
 * // In a component
 * const { nodes, edges, selectNode, setVisualizationMode } = useGraphStore();
 * 
 * // Select a node
 * selectNode('node_123');
 * 
 * // Change visualization mode
 * setVisualizationMode(VisualizationMode.CityMap);
 * 
 * // Zoom in
 * zoomIn();
 * ```
 */
export const useGraphStore = create<GraphState>((set, get) => ({
  // ========================================================================
  // Initial State
  // ========================================================================
  
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
  cacheTTL: 5 * 60 * 1000, // 5 minutes
  
  // ========================================================================
  // Graph Data Actions
  // ========================================================================
  
  setGraphData: (data) => set({
    nodes: data.nodes,
    edges: data.edges,
    metadata: data.metadata,
    // Clear selections when loading new graph
    selectedNodes: new Set(),
    selectedEdges: new Set(),
  }),
  
  addNodes: (nodes) => set((state) => ({
    nodes: [...state.nodes, ...nodes],
  })),
  
  addEdges: (edges) => set((state) => ({
    edges: [...state.edges, ...edges],
  })),
  
  updateNode: (id, updates) => set((state) => ({
    nodes: state.nodes.map((node) =>
      node.id === id ? { ...node, ...updates } : node
    ),
  })),
  
  updateEdge: (id, updates) => set((state) => ({
    edges: state.edges.map((edge) =>
      edge.id === id ? { ...edge, ...updates } : edge
    ),
  })),
  
  removeNodes: (ids) => set((state) => {
    const idsSet = new Set(ids);
    return {
      // Remove nodes
      nodes: state.nodes.filter((node) => !idsSet.has(node.id)),
      // Remove edges connected to removed nodes
      edges: state.edges.filter(
        (edge) => !idsSet.has(edge.source) && !idsSet.has(edge.target)
      ),
      // Clear selections for removed nodes
      selectedNodes: new Set(
        Array.from(state.selectedNodes).filter((id) => !idsSet.has(id))
      ),
    };
  }),
  
  removeEdges: (ids) => set((state) => {
    const idsSet = new Set(ids);
    return {
      edges: state.edges.filter((edge) => !idsSet.has(edge.id)),
      // Clear selections for removed edges
      selectedEdges: new Set(
        Array.from(state.selectedEdges).filter((id) => !idsSet.has(id))
      ),
    };
  }),
  
  clearGraph: () => set({
    nodes: [],
    edges: [],
    selectedNodes: new Set(),
    selectedEdges: new Set(),
    metadata: undefined,
  }),
  
  // ========================================================================
  // Selection Actions
  // ========================================================================
  
  selectNode: (id, replace = true) => set((state) => {
    if (replace) {
      return {
        selectedNodes: new Set([id]),
        selectedEdges: new Set(), // Clear edge selection
      };
    } else {
      const newSelection = new Set(state.selectedNodes);
      newSelection.add(id);
      return { selectedNodes: newSelection };
    }
  }),
  
  selectNodes: (ids, replace = true) => set((state) => {
    if (replace) {
      return {
        selectedNodes: new Set(ids),
        selectedEdges: new Set(), // Clear edge selection
      };
    } else {
      const newSelection = new Set(state.selectedNodes);
      ids.forEach((id) => newSelection.add(id));
      return { selectedNodes: newSelection };
    }
  }),
  
  deselectNode: (id) => set((state) => {
    const newSelection = new Set(state.selectedNodes);
    newSelection.delete(id);
    return { selectedNodes: newSelection };
  }),
  
  selectEdge: (id, replace = true) => set((state) => {
    if (replace) {
      return {
        selectedEdges: new Set([id]),
        selectedNodes: new Set(), // Clear node selection
      };
    } else {
      const newSelection = new Set(state.selectedEdges);
      newSelection.add(id);
      return { selectedEdges: newSelection };
    }
  }),
  
  selectEdges: (ids, replace = true) => set((state) => {
    if (replace) {
      return {
        selectedEdges: new Set(ids),
        selectedNodes: new Set(), // Clear node selection
      };
    } else {
      const newSelection = new Set(state.selectedEdges);
      ids.forEach((id) => newSelection.add(id));
      return { selectedEdges: newSelection };
    }
  }),
  
  deselectEdge: (id) => set((state) => {
    const newSelection = new Set(state.selectedEdges);
    newSelection.delete(id);
    return { selectedEdges: newSelection };
  }),
  
  clearSelection: () => set({
    selectedNodes: new Set(),
    selectedEdges: new Set(),
  }),
  
  isNodeSelected: (id) => {
    return get().selectedNodes.has(id);
  },
  
  isEdgeSelected: (id) => {
    return get().selectedEdges.has(id);
  },
  
  // ========================================================================
  // Visualization Actions
  // ========================================================================
  
  setVisualizationMode: (mode) => set({ visualizationMode: mode }),
  
  setZoom: (zoom) => set({
    // Clamp zoom between 0.1 and 2.0
    zoomLevel: Math.max(0.1, Math.min(2.0, zoom)),
  }),
  
  zoomIn: (factor = 1.2) => set((state) => ({
    zoomLevel: Math.min(2.0, state.zoomLevel * factor),
  })),
  
  zoomOut: (factor = 1.2) => set((state) => ({
    zoomLevel: Math.max(0.1, state.zoomLevel / factor),
  })),
  
  resetZoom: () => set({ zoomLevel: 1.0 }),
  
  setCenter: (position) => set({ centerPosition: position }),
  
  pan: (delta) => set((state) => ({
    centerPosition: {
      x: state.centerPosition.x + delta.x,
      y: state.centerPosition.y + delta.y,
    },
  })),
  
  getViewport: () => {
    const state = get();
    return {
      zoom: state.zoomLevel,
      center: state.centerPosition,
    };
  },
  
  setViewport: (viewport) => set({
    zoomLevel: Math.max(0.1, Math.min(2.0, viewport.zoom)),
    centerPosition: viewport.center,
  }),
  
  resetViewport: () => set({
    zoomLevel: 1.0,
    centerPosition: { x: 0, y: 0 },
  }),
  
  // ========================================================================
  // Cache Actions
  // ========================================================================
  
  cacheGraphData: (key, data) => set((state) => {
    const newCache = new Map(state.graphCache);
    newCache.set(key, data);
    return {
      graphCache: newCache,
      lastCacheUpdate: Date.now(),
    };
  }),
  
  getCachedGraphData: (key) => {
    const state = get();
    if (!state.isCacheValid()) {
      return null;
    }
    return state.graphCache.get(key) || null;
  },
  
  clearCache: () => set({
    graphCache: new Map(),
    lastCacheUpdate: null,
  }),
  
  isCacheValid: () => {
    const state = get();
    if (!state.lastCacheUpdate) {
      return false;
    }
    return Date.now() - state.lastCacheUpdate < state.cacheTTL;
  },
}));

// ============================================================================
// Selectors
// ============================================================================

/**
 * Selector: Get selected node objects
 * 
 * @example
 * ```typescript
 * const selectedNodes = useGraphStore(selectSelectedNodes);
 * console.log(`${selectedNodes.length} nodes selected`);
 * ```
 */
export const selectSelectedNodes = (state: GraphState): GraphNode[] => {
  return state.nodes.filter((node) => state.selectedNodes.has(node.id));
};

/**
 * Selector: Get selected edge objects
 * 
 * @example
 * ```typescript
 * const selectedEdges = useGraphStore(selectSelectedEdges);
 * console.log(`${selectedEdges.length} edges selected`);
 * ```
 */
export const selectSelectedEdges = (state: GraphState): GraphEdge[] => {
  return state.edges.filter((edge) => state.selectedEdges.has(edge.id));
};

/**
 * Selector: Get number of selected nodes
 * 
 * @example
 * ```typescript
 * const count = useGraphStore(selectSelectedNodeCount);
 * ```
 */
export const selectSelectedNodeCount = (state: GraphState): number => {
  return state.selectedNodes.size;
};

/**
 * Selector: Get number of selected edges
 * 
 * @example
 * ```typescript
 * const count = useGraphStore(selectSelectedEdgeCount);
 * ```
 */
export const selectSelectedEdgeCount = (state: GraphState): number => {
  return state.selectedEdges.size;
};

/**
 * Selector: Check if any elements are selected
 * 
 * @example
 * ```typescript
 * const hasSelection = useGraphStore(selectHasSelection);
 * if (hasSelection) {
 *   // Show selection toolbar
 * }
 * ```
 */
export const selectHasSelection = (state: GraphState): boolean => {
  return state.selectedNodes.size > 0 || state.selectedEdges.size > 0;
};

/**
 * Selector: Get node by ID
 * 
 * @example
 * ```typescript
 * const getNode = useGraphStore(selectNodeById);
 * const node = getNode('node_123');
 * ```
 */
export const selectNodeById = (state: GraphState) => {
  return (id: string): GraphNode | undefined => {
    return state.nodes.find((node) => node.id === id);
  };
};

/**
 * Selector: Get edge by ID
 * 
 * @example
 * ```typescript
 * const getEdge = useGraphStore(selectEdgeById);
 * const edge = getEdge('edge_123');
 * ```
 */
export const selectEdgeById = (state: GraphState) => {
  return (id: string): GraphEdge | undefined => {
    return state.edges.find((edge) => edge.id === id);
  };
};

/**
 * Selector: Get edges connected to a node
 * 
 * @example
 * ```typescript
 * const getConnectedEdges = useGraphStore(selectConnectedEdges);
 * const edges = getConnectedEdges('node_123');
 * ```
 */
export const selectConnectedEdges = (state: GraphState) => {
  return (nodeId: string): GraphEdge[] => {
    return state.edges.filter(
      (edge) => edge.source === nodeId || edge.target === nodeId
    );
  };
};

/**
 * Selector: Get neighbors of a node
 * 
 * @example
 * ```typescript
 * const getNeighbors = useGraphStore(selectNeighbors);
 * const neighbors = getNeighbors('node_123');
 * ```
 */
export const selectNeighbors = (state: GraphState) => {
  return (nodeId: string): GraphNode[] => {
    const connectedEdges = state.edges.filter(
      (edge) => edge.source === nodeId || edge.target === nodeId
    );
    
    const neighborIds = new Set<string>();
    connectedEdges.forEach((edge) => {
      if (edge.source === nodeId) {
        neighborIds.add(edge.target);
      } else {
        neighborIds.add(edge.source);
      }
    });
    
    return state.nodes.filter((node) => neighborIds.has(node.id));
  };
};

/**
 * Selector: Get graph statistics
 * 
 * @example
 * ```typescript
 * const stats = useGraphStore(selectGraphStats);
 * console.log(`Nodes: ${stats.nodeCount}, Edges: ${stats.edgeCount}`);
 * ```
 */
export const selectGraphStats = (state: GraphState) => {
  return {
    nodeCount: state.nodes.length,
    edgeCount: state.edges.length,
    selectedNodeCount: state.selectedNodes.size,
    selectedEdgeCount: state.selectedEdges.size,
    density: state.metadata?.density,
    averageDegree: state.metadata?.averageDegree,
    communityCount: state.metadata?.communityCount,
  };
};

/**
 * Selector: Get nodes by type
 * 
 * @example
 * ```typescript
 * const getNodesByType = useGraphStore(selectNodesByType);
 * const resourceNodes = getNodesByType('resource');
 * ```
 */
export const selectNodesByType = (state: GraphState) => {
  return (type: GraphNode['type']): GraphNode[] => {
    return state.nodes.filter((node) => node.type === type);
  };
};

/**
 * Selector: Get edges by type
 * 
 * @example
 * ```typescript
 * const getEdgesByType = useGraphStore(selectEdgesByType);
 * const citationEdges = getEdgesByType('citation');
 * ```
 */
export const selectEdgesByType = (state: GraphState) => {
  return (type: GraphEdge['type']): GraphEdge[] => {
    return state.edges.filter((edge) => edge.type === type);
  };
};
