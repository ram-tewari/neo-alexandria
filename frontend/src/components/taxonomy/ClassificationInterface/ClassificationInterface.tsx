import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Brain, TrendingUp } from 'lucide-react';
import { useActiveLearningQueue, useAcceptSuggestion, useRejectSuggestion, useTrainModel, useTrainingStatus, useClassificationMetrics } from '@/hooks/useTaxonomy';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export const ClassificationInterface: React.FC = () => {
  const { data: queue = [], isLoading } = useActiveLearningQueue();
  const { data: trainingStatus } = useTrainingStatus();
  const { data: metrics } = useClassificationMetrics();
  const acceptSuggestion = useAcceptSuggestion();
  const rejectSuggestion = useRejectSuggestion();
  const trainModel = useTrainModel();
  const prefersReducedMotion = useReducedMotion();

  const handleAccept = (suggestionId: string) => {
    acceptSuggestion.mutate(suggestionId);
  };

  const handleReject = (suggestionId: string) => {
    rejectSuggestion.mutate({ suggestionId });
  };

  const handleTrain = () => {
    trainModel.mutate();
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20';
    if (confidence >= 0.5) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20';
    return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Training */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            ML Classification
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {queue.length} items in active learning queue
          </p>
        </div>

        <button
          onClick={handleTrain}
          disabled={trainModel.isPending || trainingStatus?.status === 'training'}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          <Brain className={`w-4 h-4 ${trainingStatus?.status === 'training' ? 'animate-pulse' : ''}`} />
          {trainingStatus?.status === 'training' ? 'Training...' : 'Train Model'}
        </button>
      </div>

      {/* Training Status */}
      {trainingStatus && trainingStatus.status !== 'idle' && (
        <motion.div
          initial={prefersReducedMotion ? {} : { opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-purple-50 dark:bg-purple-900/10 rounded-lg border border-purple-200 dark:border-purple-800"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-900 dark:text-purple-100">
              {trainingStatus.stage}
            </span>
            <span className="text-sm text-purple-700 dark:text-purple-300">
              {Math.round(trainingStatus.progress * 100)}%
            </span>
          </div>
          <div className="w-full h-2 bg-purple-200 dark:bg-purple-900/20 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${trainingStatus.progress * 100}%` }}
              className="h-full bg-purple-600 dark:bg-purple-500"
            />
          </div>
          {trainingStatus.accuracy && (
            <p className="text-xs text-purple-700 dark:text-purple-300 mt-2">
              Accuracy: {Math.round(trainingStatus.accuracy * 100)}%
            </p>
          )}
        </motion.div>
      )}

      {/* Metrics */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Accuracy</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(metrics.accuracy * 100)}%
            </div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Precision</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(metrics.precision * 100)}%
            </div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Recall</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(metrics.recall * 100)}%
            </div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">F1 Score</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(metrics.f1Score * 100)}%
            </div>
          </div>
        </div>
      )}

      {/* Active Learning Queue */}
      <div className="space-y-3">
        {queue.map((item, index) => (
          <motion.div
            key={item.resourceId}
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                  {item.title}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                  {item.abstract}
                </p>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <TrendingUp className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                <span className="text-sm font-medium text-orange-600 dark:text-orange-400">
                  Priority: {item.priority}
                </span>
              </div>
            </div>

            {/* Suggestions */}
            <div className="space-y-2">
              {item.suggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {suggestion.category}
                      </span>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getConfidenceColor(suggestion.confidence)}`}>
                        {Math.round(suggestion.confidence * 100)}% confident
                      </span>
                    </div>
                    {suggestion.reasoning.length > 0 && (
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {suggestion.reasoning[0]}
                      </p>
                    )}
                  </div>

                  {suggestion.status === 'pending' && (
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleAccept(suggestion.id)}
                        className="p-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                        title="Accept"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleReject(suggestion.id)}
                        className="p-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                        title="Reject"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        ))}

        {queue.length === 0 && (
          <div className="text-center py-12">
            <Brain className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-gray-600 dark:text-gray-400">
              No items in active learning queue
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
