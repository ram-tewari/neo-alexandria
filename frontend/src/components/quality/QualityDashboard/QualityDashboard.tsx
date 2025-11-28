import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { RefreshCw, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import { useQualityMetrics, useQualityDistribution, useQualityOutliers, useRecalculateScores } from '@/hooks/useQuality';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export const QualityDashboard: React.FC = () => {
  const [selectedDimension, setSelectedDimension] = useState<string | null>(null);
  const { data: metrics, isLoading: metricsLoading } = useQualityMetrics();
  const { data: distribution, isLoading: distributionLoading } = useQualityDistribution();
  const { data: outliers = [], isLoading: outliersLoading } = useQualityOutliers();
  const recalculateScores = useRecalculateScores();
  const prefersReducedMotion = useReducedMotion();

  const handleRecalculate = () => {
    recalculateScores.mutate(undefined);
  };

  if (metricsLoading || distributionLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading quality metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-white dark:bg-gray-900">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Quality Dashboard
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Library-wide quality metrics and insights
            </p>
          </div>

          <button
            onClick={handleRecalculate}
            disabled={recalculateScores.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${recalculateScores.isPending ? 'animate-spin' : ''}`} />
            Recalculate
          </button>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800"
          >
            <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
              Total Resources
            </div>
            <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">
              {metrics?.totalResources || 0}
            </div>
          </motion.div>

          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-800"
          >
            <div className="text-sm font-medium text-green-600 dark:text-green-400 mb-1">
              Average Quality
            </div>
            <div className="text-3xl font-bold text-green-900 dark:text-green-100">
              {Math.round((metrics?.averageQuality || 0) * 100)}%
            </div>
          </motion.div>

          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-800"
          >
            <div className="text-sm font-medium text-purple-600 dark:text-purple-400 mb-1">
              Median Score
            </div>
            <div className="text-3xl font-bold text-purple-900 dark:text-purple-100">
              {Math.round((distribution?.median || 0) * 100)}%
            </div>
          </motion.div>

          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg border border-orange-200 dark:border-orange-800"
          >
            <div className="text-sm font-medium text-orange-600 dark:text-orange-400 mb-1">
              Outliers
            </div>
            <div className="text-3xl font-bold text-orange-900 dark:text-orange-100">
              {metrics?.outlierCount || 0}
            </div>
          </motion.div>
        </div>

        {/* Distribution Histogram */}
        <motion.div
          initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quality Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distribution?.bins.map(bin => ({
              range: `${Math.round(bin.min * 100)}-${Math.round(bin.max * 100)}%`,
              count: bin.count,
            }))}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
              <XAxis dataKey="range" className="text-gray-600 dark:text-gray-400" />
              <YAxis className="text-gray-600 dark:text-gray-400" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Dimension Radar Chart */}
        {metrics?.topDimensions && (
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quality Dimensions
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={metrics.topDimensions.map(d => ({
                dimension: d.name,
                score: Math.round(d.score * 100),
              }))}>
                <PolarGrid className="stroke-gray-300 dark:stroke-gray-600" />
                <PolarAngleAxis dataKey="dimension" className="text-gray-600 dark:text-gray-400" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Score"
                  dataKey="score"
                  stroke="#8b5cf6"
                  fill="#8b5cf6"
                  fillOpacity={0.6}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>
        )}

        {/* Top and Bottom Dimensions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Dimensions */}
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Top Dimensions
              </h3>
            </div>
            <div className="space-y-3">
              {metrics?.topDimensions.slice(0, 3).map((dimension, index) => (
                <div key={dimension.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {dimension.name}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${dimension.score * 100}%` }}
                        transition={{ delay: 0.7 + index * 0.1, duration: 0.5 }}
                        className="h-full bg-green-600 dark:bg-green-500"
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                      {Math.round(dimension.score * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Bottom Dimensions */}
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Needs Improvement
              </h3>
            </div>
            <div className="space-y-3">
              {metrics?.bottomDimensions.slice(0, 3).map((dimension, index) => (
                <div key={dimension.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {dimension.name}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${dimension.score * 100}%` }}
                        transition={{ delay: 0.7 + index * 0.1, duration: 0.5 }}
                        className="h-full bg-orange-600 dark:bg-orange-500"
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                      {Math.round(dimension.score * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Outliers */}
        {outliers.length > 0 && (
          <motion.div
            initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Quality Outliers
              </h3>
            </div>
            <div className="space-y-3">
              {outliers.slice(0, 5).map((outlier) => (
                <div
                  key={outlier.resourceId}
                  className="p-4 bg-orange-50 dark:bg-orange-900/10 rounded-lg border border-orange-200 dark:border-orange-800"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {outlier.title}
                    </h4>
                    <span className="px-2 py-1 text-xs font-medium bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 rounded">
                      {Math.round(outlier.score * 100)}%
                    </span>
                  </div>
                  <div className="space-y-1">
                    {outlier.suggestions.slice(0, 2).map((suggestion, index) => (
                      <p key={index} className="text-sm text-gray-600 dark:text-gray-400">
                        • {suggestion}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};
