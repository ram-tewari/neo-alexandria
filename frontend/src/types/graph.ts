export interface GraphNode {
  id: string;
  label: string;
  type: 'resource' | 'concept' | 'author';
  cluster?: string;
  metadata: Record<string, any>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  type: 'citation' | 'similarity' | 'co-authorship';
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface DiscoveryPath {
  nodes: string[];
  edges: GraphEdge[];
  score: number;
}

export interface Hypothesis {
  id: string;
  description: string;
  plausibility: number;
  evidence: string[];
  status: 'pending' | 'validated' | 'rejected';
  createdAt: Date;
}

export interface DiscoveryQuery {
  sourceNodeId: string;
  targetNodeId: string;
  maxDepth?: number;
  minScore?: number;
}

export interface GraphLayout {
  type: 'force' | 'hierarchical' | 'circular';
  options?: Record<string, any>;
}

export interface GraphFilters {
  nodeTypes?: ('resource' | 'concept' | 'author')[];
  edgeTypes?: ('citation' | 'similarity' | 'co-authorship')[];
  clusters?: string[];
  minWeight?: number;
}

export interface CitationMetrics {
  nodeId: string;
  citationCount: number;
  influenceScore: number;
  hIndex: number;
  temporalEvolution: {
    date: Date;
    count: number;
  }[];
}

export const NODE_COLORS = {
  resource: '#3b82f6', // blue
  concept: '#8b5cf6', // purple
  author: '#10b981', // green
} as const;

export const EDGE_COLORS = {
  citation: '#ef4444', // red
  similarity: '#3b82f6', // blue
  'co-authorship': '#10b981', // green
} as const;
