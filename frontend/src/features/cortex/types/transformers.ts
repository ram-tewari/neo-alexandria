/**
 * Type Transformation Utilities for Graph Types
 * 
 * Functions to transform between different representations of graph data,
 * such as API responses to frontend models, or between different visualization formats.
 */

import type {
  GraphNode,
  GraphEdge,
  GraphData,
  GraphEntity,
  GraphRelationship,
  BlastRadiusNode,
  ImpactLevel,
  CentralityMetrics,
} from './graph';

// ============================================================================
// API Response Transformations
// ============================================================================

/**
 * Transform backend entity to graph node
 */
export function entityToNode(entity: GraphEntity): GraphNode {
  return {
    id: entity.id,
    label: entity.name,
    type: 'entity',
    metadata: {
      entityType: entity.type,
      ...entity.properties,
    },
    position: { x: 0, y: 0 }, // Position will be calculated by layout algorithm
    data: {
      entity,
    },
  };
}

/**
 * Transform backend relationship to graph edge
 */
export function relationshipToEdge(relationship: GraphRelationship): GraphEdge {
  return {
    id: relationship.id,
    source: relationship.source,
    target: relationship.target,
    type: 'relationship',
    weight: relationship.properties.weight ?? 0.5,
    metadata: {
      relationType: relationship.type,
      ...relationship.properties,
    },
  };
}

/**
 * Transform array of entities and relationships to graph data
 */
export function entitiesToGraphData(
  entities: GraphEntity[],
  relationships: GraphRelationship[]
): GraphData {
  const nodes = entities.map(entityToNode);
  const edges = relationships.map(relationshipToEdge);
  
  return {
    nodes,
    edges,
    metadata: {
      totalNodes: nodes.length,
      totalEdges: edges.length,
      density: calculateDensity(nodes.length, edges.length),
      averageDegree: calculateAverageDegree(nodes.length, edges.length),
    },
  };
}

// ============================================================================
// Graph Metric Calculations
// ============================================================================

/**
 * Calculate graph density (ratio of actual edges to possible edges)
 */
export function calculateDensity(nodeCount: number, edgeCount: number): number {
  if (nodeCount <= 1) return 0;
  const maxEdges = (nodeCount * (nodeCount - 1)) / 2;
  return edgeCount / maxEdges;
}

/**
 * Calculate average degree (average number of connections per node)
 */
export function calculateAverageDegree(nodeCount: number, edgeCount: number): number {
  if (nodeCount === 0) return 0;
  return (2 * edgeCount) / nodeCount;
}

/**
 * Calculate impact level based on impact score
 */
export function calculateImpactLevel(impactScore: number): ImpactLevel {
  if (impactScore >= 0.7) return 'high';
  if (impactScore >= 0.4) return 'medium';
  return 'low';
}

// ============================================================================
// Blast Radius Transformations
// ============================================================================

/**
 * Transform regular node to blast radius node with impact metrics
 */
export function nodeToBlastRadiusNode(
  node: GraphNode,
  impactScore: number,
  hopDistance: number
): BlastRadiusNode {
  return {
    ...node,
    impactScore,
    impactLevel: calculateImpactLevel(impactScore),
    hopDistance,
  };
}

/**
 * Calculate impact score based on hop distance (exponential decay)
 */
export function calculateImpactScore(hopDistance: number, maxHops: number = 5): number {
  if (hopDistance === 0) return 1.0;
  if (hopDistance > maxHops) return 0.0;
  
  // Exponential decay: score = e^(-distance/2)
  return Math.exp(-hopDistance / 2);
}

// ============================================================================
// Centrality Transformations
// ============================================================================

/**
 * Normalize centrality metrics to 0-1 range
 */
export function normalizeCentralityMetrics(
  metrics: CentralityMetrics[],
  metricType: keyof Omit<CentralityMetrics, 'nodeId'>
): Map<string, number> {
  const values = metrics.map((m) => m[metricType] as number);
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min;
  
  const normalized = new Map<string, number>();
  
  if (range === 0) {
    // All values are the same
    metrics.forEach((m) => normalized.set(m.nodeId, 0.5));
  } else {
    metrics.forEach((m) => {
      const value = m[metricType] as number;
      normalized.set(m.nodeId, (value - min) / range);
    });
  }
  
  return normalized;
}

/**
 * Apply centrality scores to nodes (for sizing/coloring)
 */
export function applyCentralityToNodes(
  nodes: GraphNode[],
  centralityScores: Map<string, number>
): GraphNode[] {
  return nodes.map((node) => ({
    ...node,
    metadata: {
      ...node.metadata,
      centralityScore: centralityScores.get(node.id) ?? 0,
    },
  }));
}

// ============================================================================
// Graph Filtering Transformations
// ============================================================================

/**
 * Filter nodes by type
 */
export function filterNodesByType(nodes: GraphNode[], types: string[]): GraphNode[] {
  if (types.length === 0) return nodes;
  return nodes.filter((node) => types.includes(node.type));
}

/**
 * Filter edges by type
 */
export function filterEdgesByType(edges: GraphEdge[], types: string[]): GraphEdge[] {
  if (types.length === 0) return edges;
  return edges.filter((edge) => types.includes(edge.type));
}

/**
 * Filter edges to only include those connecting visible nodes
 */
export function filterEdgesByNodes(edges: GraphEdge[], visibleNodeIds: Set<string>): GraphEdge[] {
  return edges.filter(
    (edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
  );
}

/**
 * Apply filters to graph data
 */
export function applyGraphFilters(
  graphData: GraphData,
  nodeTypes?: string[],
  edgeTypes?: string[]
): GraphData {
  let filteredNodes = graphData.nodes;
  let filteredEdges = graphData.edges;
  
  // Filter nodes by type
  if (nodeTypes && nodeTypes.length > 0) {
    filteredNodes = filterNodesByType(filteredNodes, nodeTypes);
  }
  
  // Filter edges by type
  if (edgeTypes && edgeTypes.length > 0) {
    filteredEdges = filterEdgesByType(filteredEdges, edgeTypes);
  }
  
  // Filter edges to only include those connecting visible nodes
  const visibleNodeIds = new Set(filteredNodes.map((n) => n.id));
  filteredEdges = filterEdgesByNodes(filteredEdges, visibleNodeIds);
  
  return {
    nodes: filteredNodes,
    edges: filteredEdges,
    metadata: {
      ...graphData.metadata,
      totalNodes: filteredNodes.length,
      totalEdges: filteredEdges.length,
    },
  };
}

// ============================================================================
// Position Transformations
// ============================================================================

/**
 * Center graph nodes around origin (0, 0)
 */
export function centerGraph(nodes: GraphNode[]): GraphNode[] {
  if (nodes.length === 0) return nodes;
  
  // Calculate centroid
  const sumX = nodes.reduce((sum, node) => sum + node.position.x, 0);
  const sumY = nodes.reduce((sum, node) => sum + node.position.y, 0);
  const centroidX = sumX / nodes.length;
  const centroidY = sumY / nodes.length;
  
  // Translate all nodes
  return nodes.map((node) => ({
    ...node,
    position: {
      x: node.position.x - centroidX,
      y: node.position.y - centroidY,
    },
  }));
}

/**
 * Scale graph to fit within bounds
 */
export function scaleGraphToFit(
  nodes: GraphNode[],
  width: number,
  height: number,
  padding: number = 50
): GraphNode[] {
  if (nodes.length === 0) return nodes;
  
  // Find bounding box
  const xs = nodes.map((n) => n.position.x);
  const ys = nodes.map((n) => n.position.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  
  const graphWidth = maxX - minX;
  const graphHeight = maxY - minY;
  
  if (graphWidth === 0 || graphHeight === 0) return nodes;
  
  // Calculate scale factor
  const targetWidth = width - 2 * padding;
  const targetHeight = height - 2 * padding;
  const scaleX = targetWidth / graphWidth;
  const scaleY = targetHeight / graphHeight;
  const scale = Math.min(scaleX, scaleY);
  
  // Scale and center
  return nodes.map((node) => ({
    ...node,
    position: {
      x: (node.position.x - minX) * scale + padding,
      y: (node.position.y - minY) * scale + padding,
    },
  }));
}

// ============================================================================
// Search Transformations
// ============================================================================

/**
 * Search nodes by label (case-insensitive)
 */
export function searchNodesByLabel(nodes: GraphNode[], query: string): GraphNode[] {
  if (!query.trim()) return nodes;
  
  const lowerQuery = query.toLowerCase();
  return nodes.filter((node) => node.label.toLowerCase().includes(lowerQuery));
}

/**
 * Get node degree (number of connections)
 */
export function getNodeDegree(nodeId: string, edges: GraphEdge[]): number {
  return edges.filter((edge) => edge.source === nodeId || edge.target === nodeId).length;
}

/**
 * Get node neighbors
 */
export function getNodeNeighbors(nodeId: string, edges: GraphEdge[]): Set<string> {
  const neighbors = new Set<string>();
  
  edges.forEach((edge) => {
    if (edge.source === nodeId) {
      neighbors.add(edge.target);
    } else if (edge.target === nodeId) {
      neighbors.add(edge.source);
    }
  });
  
  return neighbors;
}

/**
 * Build adjacency list from edges
 */
export function buildAdjacencyList(edges: GraphEdge[]): Map<string, Set<string>> {
  const adjacencyList = new Map<string, Set<string>>();
  
  edges.forEach((edge) => {
    // Add forward edge
    if (!adjacencyList.has(edge.source)) {
      adjacencyList.set(edge.source, new Set());
    }
    adjacencyList.get(edge.source)!.add(edge.target);
    
    // Add backward edge (undirected graph)
    if (!adjacencyList.has(edge.target)) {
      adjacencyList.set(edge.target, new Set());
    }
    adjacencyList.get(edge.target)!.add(edge.source);
  });
  
  return adjacencyList;
}
