import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Filter, Layers } from 'lucide-react';
import { GraphCanvas } from '@/components/graph/GraphCanvas';
import { DiscoveryPanel } from '@/components/graph/DiscoveryPanel';
import { useGraph, useExportGraph, useClusters } from '@/hooks/useGraph';
import { GraphLayout, GraphFilters, DiscoveryPath } from '@/types/graph';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export const Graph: React.FC = () => {
  const [layout, setLayout] = useState<GraphLayout['type']>('force');
  const [filters, setFilters] = useState<GraphFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [showDiscovery, setShowDiscovery] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();
  const [sourceNode, setSourceNode] = useState('');
  const [targetNode, setTargetNode] = useState('');
  const [highlightedPaths, setHighlightedPaths] = useState<string[][]>([]);

  const { data: graphData, isLoading } = useGraph(filters);
  const { data: clusters = [] } = useClusters();
  const exportGraph = useExportGraph();
  const prefersReducedMotion = useReducedMotion();

  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    
    // Set as source or target for discovery
    if (!sourceNode) {
      setSourceNode(nodeId);
    } else if (!targetNode && nodeId !== sourceNode) {
      setTargetNode(nodeId);
      setShowDiscovery(true);
    } else {
      // Reset and start over
      setSourceNode(nodeId);
      setTargetNode('');
    }
  };

  const handleNodeExpand = (nodeId: string) => {
    // Could load subgraph here
    console.log('Expand node:', nodeId);
  };

  const handlePathSelect = (path: DiscoveryPath) => {
    setHighlightedPaths([path.nodes]);
  };

  const handleExport = (format: 'json' | 'graphml' | 'png') => {
    exportGraph.mutate(format);
  };

  const toggleNodeTypeFilter = (type: 'resource' | 'concept' | 'author') => {
    setFilters(prev => {
      const nodeTypes = prev.nodeTypes || [];
      const newTypes = nodeTypes.includes(type)
        ? nodeTypes.filter(t => t !== type)
        : [...nodeTypes, type];
      return { ...prev, nodeTypes: newTypes.length > 0 ? newTypes : undefined };
    });
  };

  const toggleEdgeTypeFilter = (type: 'citation' | 'similarity' | 'co-authorship') => {
    setFilters(prev => {
      const edgeTypes = prev.edgeTypes || [];
      const newTypes = edgeTypes.includes(type)
        ? edgeTypes.filter(t => t !== type)
        : [...edgeTypes, type];
      return { ...prev, edgeTypes: newTypes.length > 0 ? newTypes : undefined };
    });
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading knowledge graph...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Knowledge Graph
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {graphData?.nodes.length || 0} nodes, {graphData?.edges.length || 0} edges
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showFilters
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>

          <button
            onClick={() => setShowDiscovery(!showDiscovery)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showDiscovery
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <Layers className="w-4 h-4" />
            Discovery
          </button>

          <div className="relative">
            <button
              onClick={() => {}}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <motion.div
          initial={prefersReducedMotion ? {} : { opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="p-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Node Types */}
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Node Types
              </label>
              <div className="space-y-2">
                {(['resource', 'concept', 'author'] as const).map((type) => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!filters.nodeTypes || filters.nodeTypes.includes(type)}
                      onChange={() => toggleNodeTypeFilter(type)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                      {type}s
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Edge Types */}
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Edge Types
              </label>
              <div className="space-y-2">
                {(['citation', 'similarity', 'co-authorship'] as const).map((type) => (
                  <label key={type} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!filters.edgeTypes || filters.edgeTypes.includes(type)}
                      onChange={() => toggleEdgeTypeFilter(type)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                      {type}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Clusters */}
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Clusters ({clusters.length})
              </label>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {clusters.length} semantic clusters detected
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph Canvas */}
        <div className="flex-1">
          {graphData && (
            <GraphCanvas
              nodes={graphData.nodes}
              edges={graphData.edges}
              layout={layout}
              onNodeClick={handleNodeClick}
              onNodeExpand={handleNodeExpand}
              selectedNodeId={selectedNodeId}
              highlightedPaths={highlightedPaths}
            />
          )}
        </div>

        {/* Discovery Panel */}
        {showDiscovery && (
          <div className="w-96">
            <DiscoveryPanel
              sourceNode={sourceNode}
              targetNode={targetNode}
              onPathSelect={handlePathSelect}
            />
          </div>
        )}
      </div>
    </div>
  );
};
