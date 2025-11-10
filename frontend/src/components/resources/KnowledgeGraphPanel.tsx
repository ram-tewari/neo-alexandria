// Neo Alexandria 2.0 Frontend - Knowledge Graph Panel Component
// Interactive force-directed graph visualization of related resources

import React, { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useKnowledgeGraph } from '@/hooks/useKnowledgeGraph';
import { Network, Maximize2, RefreshCw } from 'lucide-react';

interface KnowledgeGraphPanelProps {
  resourceId: string;
  maxNodes?: number;
}

// Classification code to color mapping
const CLASSIFICATION_COLORS: Record<string, string> = {
  '000': '#3B82F6', // Blue - Computer science
  '100': '#10B981', // Green - Philosophy
  '200': '#F59E0B', // Amber - Religion
  '300': '#EF4444', // Red - Social sciences
  '400': '#8B5CF6', // Purple - Language
  '500': '#EC4899', // Pink - Science
  '600': '#14B8A6', // Teal - Technology
  '700': '#F97316', // Orange - Arts
  '800': '#6366F1', // Indigo - Literature
  '900': '#84CC16', // Lime - History
};

// Get color for classification code
const getNodeColor = (classificationCode?: string): string => {
  if (!classificationCode) return '#718096'; // Default gray
  
  const prefix = classificationCode.substring(0, 3);
  return CLASSIFICATION_COLORS[prefix] || '#718096';
};

export const KnowledgeGraphPanel: React.FC<KnowledgeGraphPanelProps> = ({
  resourceId,
  maxNodes = 50,
}) => {
  const navigate = useNavigate();
  const { data: graphData, isLoading, error, refetch } = useKnowledgeGraph(resourceId, maxNodes);

  // Transform graph data for react-force-graph-2d
  const graphNodes = useMemo(() => {
    if (!graphData) return [];
    
    return graphData.nodes.map(node => ({
      id: node.id,
      name: node.title,
      type: node.type,
      classification_code: node.classification_code,
      color: getNodeColor(node.classification_code),
      // Size based on whether it's the current resource
      val: node.id === resourceId ? 15 : 8,
    }));
  }, [graphData, resourceId]);

  const graphLinks = useMemo(() => {
    if (!graphData) return [];
    
    return graphData.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      value: edge.weight,
      details: edge.details,
    }));
  }, [graphData]);

  // Handle node click
  const handleNodeClick = useCallback((node: any) => {
    if (node.id !== resourceId) {
      navigate(`/resources/${node.id}`);
    }
  }, [navigate, resourceId]);

  // Handle node hover
  const handleNodeHover = useCallback((node: any) => {
    if (node) {
      document.body.style.cursor = 'pointer';
    } else {
      document.body.style.cursor = 'default';
    }
  }, []);

  // Custom node canvas rendering
  const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.name;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    
    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color;
    ctx.fill();
    
    // Draw border for current resource
    if (node.id === resourceId) {
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
    }
    
    // Draw label
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(label, node.x, node.y + node.val + fontSize);
  }, [resourceId]);

  // Custom link canvas rendering
  const paintLink = useCallback((link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const start = link.source;
    const end = link.target;
    
    // Calculate link width based on weight
    const linkWidth = Math.max(1, link.value * 3) / globalScale;
    
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = linkWidth;
    ctx.stroke();
  }, []);

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-accent-blue-400" />
            <h2 className="text-xl font-semibold text-charcoal-grey-50">Knowledge Graph</h2>
          </div>
          
          <div className="flex items-center gap-2">
            {graphData && (
              <Badge variant="info" size="md">
                {graphData.nodes.length} nodes, {graphData.edges.length} connections
              </Badge>
            )}
            
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              Refresh
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              icon={<Maximize2 />}
              onClick={() => navigate(`/knowledge-graph?resource=${resourceId}`)}
            >
              Expand
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Loading State */}
        {isLoading && (
          <div className="h-96 flex items-center justify-center bg-charcoal-grey-900 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue-500 mx-auto mb-4" />
              <div className="text-charcoal-grey-400">Loading knowledge graph...</div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="h-96 flex items-center justify-center bg-charcoal-grey-900 rounded-lg">
            <div className="text-center">
              <Network className="w-12 h-12 text-charcoal-grey-400 mx-auto mb-4" />
              <div className="text-charcoal-grey-50 font-medium mb-2">Failed to load graph</div>
              <div className="text-charcoal-grey-400 text-sm mb-4">
                {error instanceof Error ? error.message : 'An error occurred'}
              </div>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                Try Again
              </Button>
            </div>
          </div>
        )}

        {/* Graph Visualization */}
        {!isLoading && !error && graphData && graphNodes.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="bg-charcoal-grey-900 rounded-lg overflow-hidden"
          >
            <ForceGraph2D
              graphData={{ nodes: graphNodes, links: graphLinks }}
              nodeLabel={(node: any) => `
                <div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px; color: white; font-size: 12px; max-width: 200px;">
                  <div style="font-weight: bold; margin-bottom: 4px;">${node.name}</div>
                  ${node.type ? `<div style="color: #9CA3AF;">Type: ${node.type}</div>` : ''}
                  ${node.classification_code ? `<div style="color: #9CA3AF;">Code: ${node.classification_code}</div>` : ''}
                </div>
              `}
              nodeCanvasObject={paintNode}
              linkCanvasObject={paintLink}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              width={800}
              height={400}
              backgroundColor="#171923"
              linkDirectionalParticles={2}
              linkDirectionalParticleWidth={2}
              linkDirectionalParticleSpeed={0.005}
              cooldownTicks={100}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
            />
          </motion.div>
        )}

        {/* Empty State */}
        {!isLoading && !error && graphData && graphNodes.length === 0 && (
          <div className="h-96 flex items-center justify-center bg-charcoal-grey-900 rounded-lg">
            <div className="text-center">
              <Network className="w-12 h-12 text-charcoal-grey-400 mx-auto mb-4" />
              <div className="text-charcoal-grey-50 font-medium mb-2">No Connections Found</div>
              <div className="text-charcoal-grey-400 text-sm">
                This resource doesn't have any related resources yet.
              </div>
            </div>
          </div>
        )}

        {/* Legend */}
        {!isLoading && !error && graphData && graphNodes.length > 0 && (
          <div className="mt-4 pt-4 border-t border-charcoal-grey-700">
            <div className="text-sm text-charcoal-grey-400 mb-2">Classification Legend</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(CLASSIFICATION_COLORS).map(([code, color]) => (
                <div key={code} className="flex items-center gap-1.5">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs text-charcoal-grey-300">{code}s</span>
                </div>
              ))}
            </div>
            <div className="text-xs text-charcoal-grey-400 mt-2">
              Node size indicates the current resource. Click any node to navigate.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
