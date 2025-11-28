import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Lightbulb, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { DiscoveryPath, Hypothesis } from '@/types/graph';
import { useFindPaths, useGenerateHypotheses, useValidateHypothesis } from '@/hooks/useGraph';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface DiscoveryPanelProps {
  sourceNode: string;
  targetNode: string;
  onPathSelect?: (path: DiscoveryPath) => void;
}

export const DiscoveryPanel: React.FC<DiscoveryPanelProps> = ({
  sourceNode,
  targetNode,
  onPathSelect,
}) => {
  const [selectedPath, setSelectedPath] = useState<DiscoveryPath | null>(null);
  const findPaths = useFindPaths();
  const generateHypotheses = useGenerateHypotheses();
  const validateHypothesis = useValidateHypothesis();
  const prefersReducedMotion = useReducedMotion();

  const handleFindPaths = () => {
    findPaths.mutate({
      sourceNodeId: sourceNode,
      targetNodeId: targetNode,
      maxDepth: 3,
      minScore: 0.5,
    });
  };

  const handleGenerateHypotheses = () => {
    generateHypotheses.mutate({
      sourceNodeId: sourceNode,
      targetNodeId: targetNode,
    });
  };

  const handlePathClick = (path: DiscoveryPath) => {
    setSelectedPath(path);
    onPathSelect?.(path);
  };

  const handleValidate = (hypothesisId: string, valid: boolean) => {
    validateHypothesis.mutate({ hypothesisId, valid });
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Open Discovery
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Find connections between concepts
        </p>
      </div>

      {/* Node Selection */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
        <div>
          <label className="text-xs font-medium text-gray-700 dark:text-gray-300 block mb-1">
            Source Node
          </label>
          <div className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded text-sm text-gray-900 dark:text-white">
            {sourceNode || 'Select a node'}
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-gray-700 dark:text-gray-300 block mb-1">
            Target Node
          </label>
          <div className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded text-sm text-gray-900 dark:text-white">
            {targetNode || 'Select a node'}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleFindPaths}
            disabled={!sourceNode || !targetNode || findPaths.isPending}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <Search className="w-4 h-4" />
            Find Paths
          </button>
          <button
            onClick={handleGenerateHypotheses}
            disabled={!sourceNode || !targetNode || generateHypotheses.isPending}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <Lightbulb className="w-4 h-4" />
            Hypotheses
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Paths */}
        {findPaths.data && findPaths.data.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-primary-600 dark:text-primary-400" />
              <h4 className="font-semibold text-gray-900 dark:text-white">
                Discovery Paths ({findPaths.data.length})
              </h4>
            </div>

            <div className="space-y-2">
              {findPaths.data.map((path, index) => (
                <motion.div
                  key={index}
                  initial={prefersReducedMotion ? {} : { opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => handlePathClick(path)}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedPath === path
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-primary-400 dark:hover:border-primary-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      Path {index + 1}
                    </span>
                    <span className="px-2 py-0.5 text-xs font-medium bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full">
                      {Math.round(path.score * 100)}% confidence
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                    {path.nodes.map((nodeId, i) => (
                      <React.Fragment key={nodeId}>
                        <span className="font-medium">{nodeId.slice(0, 8)}</span>
                        {i < path.nodes.length - 1 && (
                          <span className="text-gray-400">→</span>
                        )}
                      </React.Fragment>
                    ))}
                  </div>

                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    {path.edges.length} connections
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Hypotheses */}
        {generateHypotheses.data && generateHypotheses.data.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <h4 className="font-semibold text-gray-900 dark:text-white">
                Hypotheses ({generateHypotheses.data.length})
              </h4>
            </div>

            <div className="space-y-3">
              {generateHypotheses.data.map((hypothesis, index) => (
                <motion.div
                  key={hypothesis.id}
                  initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900 dark:text-white flex-1">
                      {hypothesis.description}
                    </p>
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                      hypothesis.status === 'validated'
                        ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                        : hypothesis.status === 'rejected'
                        ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}>
                      {hypothesis.status}
                    </span>
                  </div>

                  <div className="mb-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        Plausibility:
                      </span>
                      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-purple-600 dark:bg-purple-500 transition-all"
                          style={{ width: `${hypothesis.plausibility * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                        {Math.round(hypothesis.plausibility * 100)}%
                      </span>
                    </div>
                  </div>

                  {hypothesis.evidence.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                        Evidence:
                      </p>
                      <ul className="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                        {hypothesis.evidence.map((item, i) => (
                          <li key={i} className="pl-3 border-l-2 border-gray-300 dark:border-gray-600">
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {hypothesis.status === 'pending' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleValidate(hypothesis.id, true)}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                      >
                        <CheckCircle className="w-3 h-3" />
                        Validate
                      </button>
                      <button
                        onClick={() => handleValidate(hypothesis.id, false)}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                      >
                        <XCircle className="w-3 h-3" />
                        Reject
                      </button>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Loading States */}
        {(findPaths.isPending || generateHypotheses.isPending) && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        )}

        {/* Empty State */}
        {!findPaths.data && !generateHypotheses.data && !findPaths.isPending && !generateHypotheses.isPending && (
          <div className="text-center py-8">
            <Lightbulb className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Select source and target nodes to discover connections
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
