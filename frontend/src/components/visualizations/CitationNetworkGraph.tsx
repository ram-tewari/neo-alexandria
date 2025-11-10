// Neo Alexandria 2.0 Frontend - Citation Network Graph Component
// Interactive force-directed graph visualization for citation networks

import React, { useCallback, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import type { GraphResponse } from '@/types/api';
import type { Citation } from '@/services/api/citations';

interface CitationNetworkGraphProps {
  /**
   * Graph data with nodes and edges
   */
  data: GraphResponse;
  /**
   * Width of the graph container
   * @default 800
   */
  width?: number;
  /**
   * Height of the graph container
   * @default 600
   */
  height?: number;
  /**
   * Callback when a node is clicked
   */
  onNodeClick?: (nodeId: string) => void;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get color based on citation type
 */
const getCitationTypeColor = (citationType?: string): string => {
  switch (citationType) {
    case 'reference':
      return '#3B82F6'; // Accent blue - academic references
    case 'dataset':
      return '#10B981'; // Green - data sources
    case 'code':
      return '#8B5CF6'; // Purple - code repositories
    case 'general':
    default:
      return '#6B7280'; // Grey - general citations
  }
};

/**
 * Get node size based on importance score (PageRank)
 * Higher importance = larger node
 */
const getNodeSize = (importanceScore?: number): number => {
  if (!importanceScore) return 5;
  // Scale importance score (0-1) to node size (5-15)
  return 5 + (importanceScore * 10);
};

/**
 * CitationNetworkGraph - Interactive force-directed graph for citation networks
 * 
 * Features:
 * - Renders citation graph using react-force-graph-2d
 * - Sizes nodes by importance score (PageRank)
 * - Colors nodes by citation type
 * - Hover tooltips with resource information
 * - Click navigation to resource details
 * - Force-directed layout for optimal visualization
 * 
 * @example
 * ```tsx
 * <CitationNetworkGraph 
 *   data={graphData} 
 *   onNodeClick={(id) => navigate(`/resources/${id}`)}
 * />
 * ```
 */
export const CitationNetworkGraph: React.FC<CitationNetworkGraphProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  className = '',
}) => {
  // Transform graph data for react-force-graph-2d
  const graphData = useMemo(() => {
    // Create a map to store importance scores from edges
    const importanceMap = new Map<string, number>();
    
    // Calculate importance scores from edge weights
    data.edges.forEach(edge => {
      const currentImportance = importanceMap.get(edge.target) || 0;
      importanceMap.set(edge.target, currentImportance + edge.weight);
    });

    // Normalize importance scores to 0-1 range
    const maxImportance = Math.max(...Array.from(importanceMap.values()), 1);
    
    return {
      nodes: data.nodes.map(node => ({
        id: node.id,
        name: node.title,
        type: node.type,
        classification_code: node.classification_code,
        importance: (importanceMap.get(node.id) || 0) / maxImportance,
      })),
      links: data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        value: edge.weight,
        citationType: edge.details.connection_type,
      })),
    };
  }, [data]);

  // Handle node click
  const handleNodeClick = useCallback(
    (node: any) => {
      if (onNodeClick) {
        onNodeClick(node.id);
      }
    },
    [onNodeClick]
  );

  // Custom node rendering with size based on importance
  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.name;
    const fontSize = 11 / globalScale;
    const nodeSize = getNodeSize(node.importance);
    
    // Draw node circle with subtle fill
    ctx.beginPath();
    ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI);
    ctx.fillStyle = '#18181B'; // Very dark grey
    ctx.fill();
    
    // Draw node border with type color
    ctx.strokeStyle = getCitationTypeColor(node.type);
    ctx.lineWidth = 2 / globalScale;
    ctx.stroke();
    
    // Draw label with better contrast
    ctx.font = `${fontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#A1A1AA'; // Subtle grey text
    ctx.fillText(label, node.x, node.y + nodeSize + fontSize + 2);
  }, []);

  // Custom link rendering with color based on citation type
  const linkColor = useCallback((link: any) => {
    return getCitationTypeColor(link.citationType);
  }, []);

  // Link width based on weight
  const linkWidth = useCallback((link: any) => {
    return Math.max(1, link.value * 3);
  }, []);

  // Node tooltip
  const nodeLabel = useCallback((node: any) => {
    return `
      <div style="background: #09090B; padding: 10px 14px; border-radius: 8px; border: 1px solid #27272A; color: #FAFAFA; font-size: 12px; max-width: 220px; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
        <div style="font-weight: 500; margin-bottom: 6px; color: #FAFAFA;">${node.name}</div>
        <div style="color: #71717A; font-size: 11px; line-height: 1.5;">Type: ${node.type || 'Unknown'}</div>
        ${node.classification_code ? `<div style="color: #71717A; font-size: 11px; line-height: 1.5;">Classification: ${node.classification_code}</div>` : ''}
        <div style="color: #71717A; font-size: 11px; line-height: 1.5;">Importance: ${(node.importance * 100).toFixed(1)}%</div>
      </div>
    `;
  }, []);

  return (
    <div className={`citation-network-graph ${className}`}>
      <ForceGraph2D
        graphData={graphData}
        width={width}
        height={height}
        nodeLabel={nodeLabel}
        nodeCanvasObject={nodeCanvasObject}
        nodeCanvasObjectMode={() => 'replace'}
        onNodeClick={handleNodeClick}
        linkColor={linkColor}
        linkWidth={linkWidth}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        backgroundColor="#000000"
        cooldownTicks={100}
        onEngineStop={() => {
          // Optional: callback when force simulation stabilizes
        }}
      />
    </div>
  );
};

export default CitationNetworkGraph;
