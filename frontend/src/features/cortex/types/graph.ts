/**
 * Graph Domain Types for Cortex/Knowledge Base
 * 
 * TypeScript type definitions for graph visualization, knowledge graph entities,
 * and Literature-Based Discovery (LBD) features.
 * 
 * Compatible with React Flow node and edge types while adding domain-specific properties.
 * 
 * Backend API: backend/docs/api/graph.md
 * Module: app.modules.graph
 */

import type { Node as ReactFlowNode, Edge as ReactFlowEdge } from 'reactflow';

// ============================================================================
// Core Graph Types
// ============================================================================

/**
 * Graph node representing a resource in the knowledge graph
 * Extends React Flow Node with domain-specific metadata
 */
export interface GraphNode extends ReactFlowNode {
  id: string;
  label: string;
  type: 'default' | 'cluster' | 'entity' | 'hypothesis';
  metadata: {
    title?: string;
    resourceType?: string;
    qualityScore?: number;
    centralityScore?: number;
    communityId?: string;
    entityType?: string;
    hypothesisType?: HypothesisType;
    confidence?: number;
    [key: string]: unknown;
  };
  position: {
    x: number;
    y: number;
  };
}

/**
 * Graph edge representing a relationship between nodes
 * Extends React Flow Edge with domain-specific metadata
 */
export interface GraphEdge extends ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  type: 'default' | 'citation' | 'dependency' | 'relationship' | 'similarity';
  weight: number;
  metadata: {
    relationshipType?: string;
    vectorSimilarity?: number;
    sharedSubjects?: number;
    classificationMatch?: boolean;
    citationCount?: number;
    dependencyType?: string;
    relationType?: string;
    [key: string]: unknown;
  };
}

/**
 * Complete graph data structure
 */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    totalNodes: number;
    totalEdges: number;
    density?: number;
    averageDegree?: number;
    communities?: number;
    lastUpdated?: string;
    [key: string]: unknown;
  };
}

// ============================================================================
// Hypothesis Types (Literature-Based Discovery)
// ============================================================================

/**
 * Types of hypotheses discovered through LBD
 */
export enum HypothesisType {
  CONTRADICTION = 'contradiction',
  HIDDEN_CONNECTION = 'hidden_connection',
  RESEARCH_GAP = 'research_gap',
}

/**
 * Hypothesis discovered through ABC pattern or other LBD methods
 */
export interface Hypothesis {
  id: string;
  type: HypothesisType;
  confidence: number; // 0.0 - 1.0
  evidence: {
    aResourceId?: string;
    cResourceId?: string;
    bResourceIds?: string[];
    supportStrength?: number;
    noveltyScore?: number;
    evidenceCount?: number;
    pathStrength?: number;
    pathLength?: number;
    commonNeighbors?: number;
  };
  nodes: string[]; // Node IDs involved in the hypothesis
  description?: string;
  discoveredAt?: string; // ISO 8601
  isValidated?: boolean | null;
  validationNotes?: string | null;
}

/**
 * ABC Pattern hypothesis (bridging concept discovery)
 */
export interface ABCHypothesis extends Hypothesis {
  type: HypothesisType.HIDDEN_CONNECTION;
  conceptA: string;
  conceptC: string;
  bridgingConcept: string;
  aToB: string[]; // Resource IDs connecting A to B
  bToC: string[]; // Resource IDs connecting B to C
}

/**
 * Hypothesis discovery request parameters
 */
export interface HypothesisDiscoveryParams {
  conceptA: string;
  conceptC: string;
  limit?: number;
  startDate?: string; // ISO 8601
  endDate?: string; // ISO 8601
}

/**
 * Hypothesis discovery response
 */
export interface HypothesisDiscoveryResponse {
  conceptA: string;
  conceptC: string;
  hypotheses: Array<{
    bridgingConcept: string;
    supportStrength: number;
    noveltyScore: number;
    evidenceCount: number;
    aToB: string[];
    bToC: string[];
  }>;
  count: number;
  executionTime: number;
  timeSlice?: {
    startDate: string;
    endDate: string;
  };
}

// ============================================================================
// Visualization Mode Types
// ============================================================================

/**
 * Available visualization modes for the graph
 */
export enum VisualizationMode {
  CITY_MAP = 'city_map',
  BLAST_RADIUS = 'blast_radius',
  DEPENDENCY_WATERFALL = 'dependency_waterfall',
  HYPOTHESIS = 'hypothesis',
  DEFAULT = 'default',
}

/**
 * Layout algorithm options
 */
export type LayoutAlgorithm = 'force-directed' | 'hierarchical' | 'circular' | 'dagre' | 'manual';

/**
 * Layout configuration options
 */
export interface LayoutOptions {
  algorithm: LayoutAlgorithm;
  animated?: boolean;
  animationDuration?: number;
  // Force-directed options
  chargeStrength?: number;
  linkDistance?: number;
  centerStrength?: number;
  // Hierarchical options
  orientation?: 'TB' | 'BT' | 'LR' | 'RL'; // Top-Bottom, Bottom-Top, Left-Right, Right-Left
  levelSpacing?: number;
  nodeSpacing?: number;
  // Circular options
  radius?: number;
  sortBy?: 'centrality' | 'alphabetical' | 'none';
}

// ============================================================================
// Entity and Relationship Types (Phase 17.5)
// ============================================================================

/**
 * Entity types in the knowledge graph
 */
export type EntityType = 'Concept' | 'Person' | 'Organization' | 'Method' | 'File' | 'Function' | 'Class' | 'Variable';

/**
 * Graph entity extracted from content
 */
export interface GraphEntity {
  id: string;
  name: string;
  type: EntityType;
  properties: {
    description?: string;
    aliases?: string[];
    confidence?: number;
    sourceChunkId?: string;
    [key: string]: unknown;
  };
  createdAt?: string; // ISO 8601
}

/**
 * Relationship types in the knowledge graph
 */
export type RelationType = 
  | 'CONTRADICTS'
  | 'SUPPORTS'
  | 'EXTENDS'
  | 'CITES'
  | 'CALLS'
  | 'IMPORTS'
  | 'DEFINES'
  | 'SEMANTIC_SIMILARITY';

/**
 * Graph relationship between entities
 */
export interface GraphRelationship {
  id: string;
  source: string; // Entity ID
  target: string; // Entity ID
  type: RelationType;
  properties: {
    weight?: number;
    confidence?: number;
    provenanceChunkId?: string;
    metadata?: Record<string, unknown>;
    [key: string]: unknown;
  };
  createdAt?: string; // ISO 8601
}

/**
 * Entity extraction response
 */
export interface EntityExtractionResponse {
  status: 'success';
  chunkId: string;
  extractionMethod: 'hybrid' | 'llm' | 'rule-based';
  entities: Array<{
    id: string;
    name: string;
    type: EntityType;
  }>;
  relationships: Array<{
    id: string;
    sourceEntity: string;
    targetEntity: string;
    relationType: RelationType;
    weight: number;
  }>;
  counts: {
    entities: number;
    relationships: number;
  };
}

/**
 * Entity list query parameters
 */
export interface EntityListParams {
  entityType?: EntityType;
  nameContains?: string;
  limit?: number;
  skip?: number;
}

/**
 * Entity list response
 */
export interface EntityListResponse {
  entities: GraphEntity[];
  totalCount: number;
  skip: number;
  limit: number;
}

/**
 * Entity relationships query parameters
 */
export interface EntityRelationshipsParams {
  relationType?: RelationType;
  direction?: 'outgoing' | 'incoming' | 'both';
}

/**
 * Entity relationships response
 */
export interface EntityRelationshipsResponse {
  entity: GraphEntity;
  outgoingRelationships: Array<{
    id: string;
    targetEntity: GraphEntity;
    relationType: RelationType;
    weight: number;
    provenanceChunkId?: string;
    createdAt: string;
  }>;
  incomingRelationships: Array<{
    id: string;
    sourceEntity: GraphEntity;
    relationType: RelationType;
    weight: number;
    provenanceChunkId?: string;
    createdAt: string;
  }>;
  counts: {
    outgoing: number;
    incoming: number;
    total: number;
  };
}

// ============================================================================
// Graph Traversal Types
// ============================================================================

/**
 * Graph traversal query parameters
 */
export interface GraphTraversalParams {
  startEntityId: string;
  relationTypes?: RelationType[];
  maxHops?: number;
}

/**
 * Graph traversal response
 */
export interface GraphTraversalResponse {
  startEntity: GraphEntity;
  entities: GraphEntity[];
  relationships: Array<{
    id: string;
    sourceEntityId: string;
    targetEntityId: string;
    relationType: RelationType;
    weight: number;
  }>;
  traversalInfo: {
    maxHops: number;
    entitiesByHop: Record<string, string[]>;
    totalEntities: number;
    totalRelationships: number;
  };
}

// ============================================================================
// Graph Embeddings Types
// ============================================================================

/**
 * Graph embedding algorithm
 */
export type EmbeddingAlgorithm = 'node2vec' | 'deepwalk';

/**
 * Graph embedding generation parameters
 */
export interface EmbeddingGenerationParams {
  algorithm?: EmbeddingAlgorithm;
  dimensions?: number;
  walkLength?: number;
  numWalks?: number;
  p?: number; // Node2Vec return parameter
  q?: number; // Node2Vec in-out parameter
}

/**
 * Graph embedding generation response
 */
export interface EmbeddingGenerationResponse {
  status: 'success';
  embeddingsComputed: number;
  dimensions: number;
  executionTime: number;
}

/**
 * Node embedding
 */
export interface NodeEmbedding {
  nodeId: string;
  embedding: number[];
  dimensions: number;
}

/**
 * Similar nodes query parameters
 */
export interface SimilarNodesParams {
  limit?: number;
  minSimilarity?: number;
}

/**
 * Similar nodes response
 */
export interface SimilarNodesResponse {
  nodeId: string;
  similarNodes: Array<{
    nodeId: string;
    similarity: number;
    title: string;
    type: string;
  }>;
  count: number;
}

// ============================================================================
// Citation Types
// ============================================================================

/**
 * Citation marker in text
 */
export interface Citation {
  marker: string;
  position: number;
  context: string;
  text: string;
}

/**
 * Citation extraction response
 */
export interface CitationExtractionResponse {
  status: 'success';
  resourceId: string;
  citations: Citation[];
  count: number;
}

// ============================================================================
// Graph Visualization Types
// ============================================================================

/**
 * Community detection response
 */
export interface CommunityDetectionResponse {
  communities: Array<{
    id: string;
    nodes: string[];
    size: number;
    density: number;
    label?: string;
  }>;
  modularity: number;
  algorithm: string;
}

/**
 * Centrality metrics
 */
export interface CentralityMetrics {
  nodeId: string;
  degree: number;
  betweenness: number;
  closeness: number;
  eigenvector: number;
  pagerank?: number;
}

/**
 * Centrality response
 */
export interface CentralityResponse {
  metrics: CentralityMetrics[];
  topNodes: {
    byDegree: string[];
    byBetweenness: string[];
    byCloseness: string[];
    byEigenvector: string[];
  };
}

/**
 * Graph export format
 */
export type GraphExportFormat = 'json' | 'graphml' | 'csv' | 'png' | 'svg';

/**
 * Graph export options
 */
export interface GraphExportOptions {
  format: GraphExportFormat;
  includeMetadata?: boolean;
  includeFilters?: boolean;
  includeLayout?: boolean;
}

// ============================================================================
// Graph Neighbors Types
// ============================================================================

/**
 * Neighbor query parameters
 */
export interface NeighborParams {
  limit?: number;
}

/**
 * Neighbor response (mind-map view)
 */
export interface NeighborResponse {
  nodes: Array<{
    id: string;
    title: string;
    type: string;
    qualityScore: number;
  }>;
  edges: Array<{
    source: string;
    target: string;
    weight: number;
    relationshipType: string;
    metadata: {
      vectorSimilarity?: number;
      sharedSubjects?: number;
      classificationMatch?: boolean;
    };
  }>;
}

/**
 * Graph overview query parameters
 */
export interface GraphOverviewParams {
  limit?: number;
  vectorThreshold?: number;
}

// ============================================================================
// Filter and Search Types
// ============================================================================

/**
 * Graph filter state
 */
export interface GraphFilters {
  nodeTypes?: string[];
  edgeTypes?: string[];
  minQuality?: number;
  maxQuality?: number;
  minCentrality?: number;
  maxCentrality?: number;
  communities?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  searchQuery?: string;
}

/**
 * Graph search result
 */
export interface GraphSearchResult {
  nodeId: string;
  label: string;
  type: string;
  score: number;
  metadata: Record<string, unknown>;
}

// ============================================================================
// Blast Radius Types
// ============================================================================

/**
 * Impact level for blast radius visualization
 */
export type ImpactLevel = 'high' | 'medium' | 'low';

/**
 * Blast radius node with impact score
 */
export interface BlastRadiusNode extends GraphNode {
  impactScore: number;
  impactLevel: ImpactLevel;
  hopDistance: number;
}

/**
 * Blast radius calculation result
 */
export interface BlastRadiusResult {
  centerNodeId: string;
  affectedNodes: BlastRadiusNode[];
  criticalPaths: string[][]; // Array of node ID paths
  totalImpact: number;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Graph statistics
 */
export interface GraphStatistics {
  nodeCount: number;
  edgeCount: number;
  selectedNodeCount: number;
  selectedEdgeCount: number;
  density: number;
  averageDegree: number;
  communities?: number;
  isolatedNodes?: number;
}

/**
 * Graph preferences (persisted to local storage)
 */
export interface GraphPreferences {
  showLabels: boolean;
  showMinimap: boolean;
  showControls: boolean;
  animationSpeed: number;
  nodeSize: number;
  edgeWidth: number;
  colorScheme: 'light' | 'dark' | 'auto';
  defaultLayout: LayoutAlgorithm;
  defaultVisualizationMode: VisualizationMode;
}

/**
 * Graph interaction state
 */
export interface GraphInteractionState {
  selectedNodes: string[];
  selectedEdges: string[];
  hoveredNode: string | null;
  hoveredEdge: string | null;
  zoomLevel: number;
  centerPosition: { x: number; y: number };
  isLayouting: boolean;
  isPanning: boolean;
}
