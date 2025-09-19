// Neo Alexandria 2.0 Frontend - Knowledge Graph Page
// Interactive visualization of resource relationships

import React, { useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useGraphOverview, useResourceNeighbors } from '@/hooks/useApi';
import { Network, Eye, Settings, Download, Maximize } from 'lucide-react';

interface KnowledgeGraphProps {
  focusResourceId?: string;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = () => {
  const { id: resourceId } = useParams<{ id: string }>();
  const [viewMode, setViewMode] = useState<'overview' | 'focused'>('overview');
  const [graphSettings, setGraphSettings] = useState({
    limit: 50,
    threshold: 0.85,
  });

  const { data: overviewData, isLoading: overviewLoading } = useGraphOverview(
    graphSettings.limit, 
    graphSettings.threshold
  );
  
  const { data: neighborsData, isLoading: neighborsLoading } = useResourceNeighbors(
    resourceId || '', 
    10
  );

  const isLoading = viewMode === 'overview' ? overviewLoading : neighborsLoading;
  const graphData = viewMode === 'overview' ? overviewData : neighborsData;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Knowledge Graph
          </h1>
          <p className="text-secondary-600">
            Explore connections and relationships between your resources
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'overview' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('overview')}
          >
            Overview
          </Button>
          <Button
            variant={viewMode === 'focused' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('focused')}
            disabled={!resourceId}
          >
            Focused View
          </Button>
        </div>
      </div>

      {/* Controls */}
      <Card variant="glass">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm text-secondary-600">Connections:</label>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={graphSettings.limit}
                  onChange={(e) => setGraphSettings(prev => ({
                    ...prev,
                    limit: parseInt(e.target.value)
                  }))}
                  className="w-20"
                />
                <span className="text-sm text-secondary-600">{graphSettings.limit}</span>
              </div>

              <div className="flex items-center space-x-2">
                <label className="text-sm text-secondary-600">Similarity:</label>
                <input
                  type="range"
                  min="0.5"
                  max="1"
                  step="0.05"
                  value={graphSettings.threshold}
                  onChange={(e) => setGraphSettings(prev => ({
                    ...prev,
                    threshold: parseFloat(e.target.value)
                  }))}
                  className="w-20"
                />
                <span className="text-sm text-secondary-600">{Math.round(graphSettings.threshold * 100)}%</span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button variant="glass" size="sm" icon={<Download className="w-4 h-4" />}>
                Export
              </Button>
              <Button variant="glass" size="sm" icon={<Maximize className="w-4 h-4" />}>
                Fullscreen
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Graph Visualization */}
      <Card variant="glass">
        <CardContent className="p-0">
          <div className="h-96 relative rounded-xl overflow-hidden">
            {isLoading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <LoadingSpinner text="Loading graph..." />
              </div>
            ) : graphData ? (
              <GraphVisualization data={graphData} />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Network className="w-16 h-16 mx-auto mb-4 text-secondary-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Connections Found
                  </h3>
                  <p className="text-gray-700">
                    Add more resources to see connections in your knowledge graph.
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Graph Statistics */}
      {graphData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card variant="glass">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {graphData.nodes.length}
              </div>
              <div className="text-sm text-gray-700">Resources</div>
            </CardContent>
          </Card>
          
          <Card variant="glass">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {graphData.edges.length}
              </div>
              <div className="text-sm text-gray-700">Connections</div>
            </CardContent>
          </Card>
          
          <Card variant="glass">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {graphData.edges.length > 0 ? 
                  Math.round(graphData.edges.reduce((sum, edge) => sum + edge.weight, 0) / graphData.edges.length * 100) : 
                  0
                }%
              </div>
              <div className="text-sm text-gray-700">Avg. Similarity</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Coming Soon Notice */}
      <Card variant="glass">
        <CardContent className="text-center py-8">
          <h3 className="text-lg font-medium mb-2 text-gray-900">Interactive Graph Visualization</h3>
          <p className="text-gray-700 mb-4">
            Full interactive graph visualization with D3.js is coming soon. 
            You'll be able to explore connections, filter by topics, and navigate through your knowledge network.
          </p>
          <div className="flex justify-center space-x-4">
            <div className="text-sm text-gray-600">
              • Drag and zoom
            </div>
            <div className="text-sm text-gray-600">
              • Filter by strength
            </div>
            <div className="text-sm text-gray-600">
              • Topic clustering
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Interactive Graph Visualization Component
interface GraphVisualizationProps {
  data: any;
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const graphData = useMemo(() => ({
    nodes: data.nodes.map((n: any) => ({ id: n.id, name: n.title || n.id, val: 1 + (n.degree || 1) })),
    links: data.edges.map((e: any) => ({ source: e.source, target: e.target, value: e.weight || 1 })),
  }), [data]);

  // Simple SVG-based visualization as fallback
  return (
    <div ref={containerRef} className="w-full h-96">
      <svg className="w-full h-full">
        {/* Render nodes */}
        {graphData.nodes.map((node: any, index: number) => {
          const x = 100 + (index % 10) * 50;
          const y = 100 + Math.floor(index / 10) * 50;
          
          return (
            <g key={node.id}>
              <circle
                cx={x}
                cy={y}
                r={8}
                fill="#3b82f6"
                stroke="#1e40af"
                strokeWidth="2"
              />
              <text
                x={x}
                y={y + 20}
                textAnchor="middle"
                fontSize="10"
                fill="#1f2937"
                className="font-medium"
              >
                {node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name}
              </text>
            </g>
          );
        })}
        
        {/* Render links */}
        {graphData.links.map((link: any, index: number) => {
          const sourceNode = graphData.nodes.find((n: any) => n.id === link.source);
          const targetNode = graphData.nodes.find((n: any) => n.id === link.target);
          
          if (!sourceNode || !targetNode) return null;
          
          const sourceIndex = graphData.nodes.indexOf(sourceNode);
          const targetIndex = graphData.nodes.indexOf(targetNode);
          
          const sourceX = 100 + (sourceIndex % 10) * 50;
          const sourceY = 100 + Math.floor(sourceIndex / 10) * 50;
          const targetX = 100 + (targetIndex % 10) * 50;
          const targetY = 100 + Math.floor(targetIndex / 10) * 50;
          
          return (
            <line
              key={index}
              x1={sourceX}
              y1={sourceY}
              x2={targetX}
              y2={targetY}
              stroke="#94a3b8"
              strokeWidth={1 + (link.value || 0) * 2}
              opacity="0.6"
            />
          );
        })}
      </svg>
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-gray-200">
        <div className="text-sm font-medium text-gray-900 mb-2">Graph Legend</div>
        <div className="space-y-1 text-xs text-gray-800">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span className="text-gray-900">Resources</span>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-0.5 bg-gray-500 mr-2"></div>
            <span className="text-gray-900">Connections</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export { KnowledgeGraph };
