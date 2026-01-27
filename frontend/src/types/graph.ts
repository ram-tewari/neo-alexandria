/**
 * Graph Domain Types
 * 
 * Type definitions for graph visualization, nodes, edges, and related entities.
 * Used by the Cortex/Knowledge Base feature (Phase 4).
 * 
 * Phase: 4 Cortex/Knowledge Base
 * Epic: 1 Foundation
 * Task: 1.3
 */

// ============================================================================
// Core Graph Types
// ============================================================================

/**
 * Position in 2D space for graph layout
 */
export interface Position {
  x: number;
  y: number;
}

/**
 * Graph node representing a resource, entity, or cluster
 */
export interface GraphNode {
  /** Unique node identifier */
  id: string;
  
  /** Display label */
  label: string;
  
  /** Node type (resource, entity, cluster, hypothesis) */
  type: 'resource' | 'entity' | 'cluster' | 'hypothesis';
  
  /** Position in graph layout */
  position: Position;
  
  /** Additional metadata */
  metadata?: {
    /** Resource ID if node represents a resource */
    resourceId?: string;
    
    /** Entity type if node represents an entity */
    entityType?: string;
    
    /** Cluster size if node represents a cluster */
    clusterSize?: number;
    
    /** Hypothesis type if node represents a hypothesis */
    hypothesisType?: HypothesisType;
    
    /** Confidence score (0-1) */
    confidence?: number;
    
    /** Centrality scores */
    centrality?: {
      degree?: number;
      betweenness?: number;
      closeness?: number;
      eigenvector?: number;
    };
    
    /** Community ID for clustering */
    communityId?: string;
    
    /** Custom properties */
    [key: string]: unknown;
  };
}

/**
 * Graph edge representing a relationship between nodes
 */
export interface GraphEdge {
  /** Unique edge identifier */
  id: string;
  
  /** Source node ID */
  source: string;
  
  /** Target node ID */
  target: string;
  
  /** Edge type (citation, dependency, relationship, etc.) */
  type: 'citation' | 'dependency' | 'relationship' | 'similarity' | 'hidden_connection';
  
  /** Edge weight (0-1) */
  weight?: number;
  
  /** Additional metadata */
  metadata?: {
    /** Citation count for citation edges */
    citationCount?: number;
    
    /** Dependency type for dependency edges */
    dependencyType?: string;
    
    /** Relationship type for relationship edges */
    relationshipType?: string;
    
    /** Similarity score for similarity edges */
    similarityScore?: number;
    
    /** Custom properties */
    [key: string]: unknown;
  };
}

/**
 * Complete graph data structure
 */
export interface GraphData {
  /** All nodes in the graph */
  nodes: GraphNode[];
  
  /** All edges in the graph */
  edges: GraphEdge[];
  
  /** Graph metadata */
  metadata?: {
    /** Total node count */
    nodeCount?: number;
    
    /** Total edge count */
    edgeCount?: number;
    
    /** Graph density */
    density?: number;
    
    /** Average degree */
    averageDegree?: number;
    
    /** Number of communities */
    communityCount?: number;
    
    /** Custom properties */
    [key: string]: unknown;
  };
}

// ============================================================================
// Visualization Types
// ============================================================================

/**
 * Visualization mode for graph display
 */
export enum VisualizationMode {
  /** High-level clusters showing knowledge domains */
  CityMap = 'city_map',
  
  /** Refactoring impact analysis showing affected nodes */
  BlastRadius = 'blast_radius',
  
  /** Data flow DAG showing dependencies */
  DependencyWaterfall = 'dependency_waterfall',
  
  /** Hypothesis mode with LBD features */
  Hypothesis = 'hypothesis',
}

/**
 * Viewport state for graph canvas
 */
export interface ViewportState {
  /** Zoom level (0.1 - 2.0) */
  zoom: number;
  
  /** Center position */
  center: Position;
}

// ============================================================================
// Hypothesis Types (LBD - Literature-Based Discovery)
// ============================================================================

/**
 * Type of hypothesis discovered by LBD
 */
export enum HypothesisType {
  /** Contradicting papers or claims */
  Contradiction = 'contradiction',
  
  /** Hidden connections between papers */
  HiddenConnection = 'hidden_connection',
  
  /** Research gaps in the literature */
  ResearchGap = 'research_gap',
}

/**
 * Hypothesis discovered by LBD
 */
export interface Hypothesis {
  /** Unique hypothesis identifier */
  id: string;
  
  /** Hypothesis type */
  type: HypothesisType;
  
  /** Confidence score (0-1) */
  confidence: number;
  
  /** Evidence supporting the hypothesis */
  evidence: {
    /** Papers involved */
    papers: string[];
    
    /** Citations involved */
    citations: string[];
    
    /** Connections involved */
    connections: string[];
    
    /** Description of evidence */
    description: string;
  };
  
  /** Node IDs involved in the hypothesis */
  nodes: string[];
  
  /** Edge IDs involved in the hypothesis */
  edges?: string[];
  
  /** Additional metadata */
  metadata?: {
    /** Reasoning for the hypothesis */
    reasoning?: string;
    
    /** Suggested actions */
    suggestedActions?: string[];
    
    /** Custom properties */
    [key: string]: unknown;
  };
}

// ============================================================================
// Entity Types
// ============================================================================

/**
 * Graph entity extracted from content
 */
export interface GraphEntity {
  /** Unique entity identifier */
  id: string;
  
  /** Entity name */
  name: string;
  
  /** Entity type (person, organization, concept, etc.) */
  type: string;
  
  /** Entity properties */
  properties?: Record<string, unknown>;
}

/**
 * Relationship between entities
 */
export interface GraphRelationship {
  /** Unique relationship identifier */
  id: string;
  
  /** Source entity ID */
  source: string;
  
  /** Target entity ID */
  target: string;
  
  /** Relationship type */
  type: string;
  
  /** Relationship properties */
  properties?: Record<string, unknown>;
}

// ============================================================================
// Filter Types
// ============================================================================

/**
 * Filters for graph nodes
 */
export interface NodeFilter {
  /** Filter by node types */
  types?: Array<GraphNode['type']>;
  
  /** Filter by minimum centrality score */
  minCentrality?: number;
  
  /** Filter by maximum centrality score */
  maxCentrality?: number;
  
  /** Filter by community IDs */
  communityIds?: string[];
  
  /** Search query for node labels */
  search?: string;
}

/**
 * Filters for graph edges
 */
export interface EdgeFilter {
  /** Filter by edge types */
  types?: Array<GraphEdge['type']>;
  
  /** Filter by minimum weight */
  minWeight?: number;
  
  /** Filter by maximum weight */
  maxWeight?: number;
}

// ============================================================================
// Layout Types
// ============================================================================

/**
 * Layout algorithm for graph visualization
 */
export enum LayoutAlgorithm {
  /** Force-directed layout */
  ForceDirected = 'force_directed',
  
  /** Hierarchical layout */
  Hierarchical = 'hierarchical',
  
  /** Circular layout */
  Circular = 'circular',
  
  /** DAG layout using dagre */
  Dagre = 'dagre',
  
  /** Manual layout (user-positioned) */
  Manual = 'manual',
}

/**
 * Options for layout algorithms
 */
export interface LayoutOptions {
  /** Force-directed options */
  forceDirected?: {
    /** Charge strength (repulsion) */
    chargeStrength?: number;
    
    /** Link distance */
    linkDistance?: number;
    
    /** Collision radius */
    collisionRadius?: number;
  };
  
  /** Hierarchical options */
  hierarchical?: {
    /** Orientation (top-down or left-right) */
    orientation?: 'TB' | 'LR';
    
    /** Level spacing */
    levelSpacing?: number;
  };
  
  /** Circular options */
  circular?: {
    /** Radius */
    radius?: number;
    
    /** Sort by (centrality or alphabetical) */
    sortBy?: 'centrality' | 'alphabetical';
  };
  
  /** Dagre options */
  dagre?: {
    /** Rank direction */
    rankDir?: 'TB' | 'LR' | 'BT' | 'RL';
    
    /** Node separation */
    nodeSep?: number;
    
    /** Rank separation */
    rankSep?: number;
  };
}
