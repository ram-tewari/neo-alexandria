import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Settings, TrendingUp, Sparkles, Eye } from 'lucide-react';
import { useRecommendations, useRefreshRecommendations } from '@/hooks/useRecommendations';
import { RecommendationCard } from '../RecommendationCard';
import { SkeletonCard } from '@/components/common/Skeleton';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface RecommendationFeedProps {
  onResourceClick?: (resourceId: string) => void;
  onPreferencesClick?: () => void;
}

export const RecommendationFeed: React.FC<RecommendationFeedProps> = ({
  onResourceClick,
  onPreferencesClick,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'fresh' | 'similar' | 'hidden'>('all');
  const { data: recommendations = [], isLoading, error } = useRecommendations(
    selectedCategory === 'all' ? undefined : selectedCategory
  );
  const refreshRecommendations = useRefreshRecommendations();
  const prefersReducedMotion = useReducedMotion();

  const handleRefresh = () => {
    refreshRecommendations.mutate();
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'fresh':
        return <Sparkles className="w-4 h-4" />;
      case 'similar':
        return <TrendingUp className="w-4 h-4" />;
      case 'hidden':
        return <Eye className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const groupedRecommendations = recommendations.reduce((acc, rec) => {
    if (!acc[rec.category]) {
      acc[rec.category] = [];
    }
    acc[rec.category].push(rec);
    return acc;
  }, {} as Record<string, typeof recommendations>);

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
          <RefreshCw className="w-8 h-8 text-red-600 dark:text-red-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Failed to load recommendations
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          We couldn't fetch your personalized recommendations. Please try again.
        </p>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            For You
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Personalized recommendations based on your interests
          </p>
        </div>

        <div className="flex items-center gap-2">
          <motion.button
            whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
            whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
            onClick={handleRefresh}
            disabled={refreshRecommendations.isPending}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            aria-label="Refresh recommendations"
          >
            <RefreshCw className={`w-5 h-5 ${refreshRecommendations.isPending ? 'animate-spin' : ''}`} />
          </motion.button>

          {onPreferencesClick && (
            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
              onClick={onPreferencesClick}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              aria-label="Preferences"
            >
              <Settings className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {(['all', 'fresh', 'similar', 'hidden'] as const).map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
              selectedCategory === category
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {getCategoryIcon(category)}
            {category === 'all' ? 'All' : category === 'fresh' ? 'Fresh Finds' : category === 'similar' ? 'Similar' : 'Hidden Gems'}
          </button>
        ))}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      )}

      {/* Recommendations */}
      {!isLoading && (
        <AnimatePresence mode="wait">
          {selectedCategory === 'all' ? (
            // Show grouped recommendations
            <motion.div
              key="grouped"
              initial={prefersReducedMotion ? {} : { opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {Object.entries(groupedRecommendations).map(([category, recs]) => (
                <div key={category}>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(category)}
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {category === 'fresh' ? 'Fresh Finds' : category === 'similar' ? 'Similar to Recent' : 'Hidden Gems'}
                      </h3>
                    </div>
                    <div className="h-px flex-1 bg-gradient-to-r from-primary-500/20 to-transparent" />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {recs.slice(0, 6).map((recommendation, index) => (
                      <motion.div
                        key={recommendation.resource.id}
                        initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <RecommendationCard
                          recommendation={recommendation}
                          onResourceClick={onResourceClick}
                        />
                      </motion.div>
                    ))}
                  </div>
                </div>
              ))}
            </motion.div>
          ) : (
            // Show filtered recommendations
            <motion.div
              key={selectedCategory}
              initial={prefersReducedMotion ? {} : { opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {recommendations.map((recommendation, index) => (
                <motion.div
                  key={recommendation.resource.id}
                  initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <RecommendationCard
                    recommendation={recommendation}
                    onResourceClick={onResourceClick}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      )}

      {/* Empty State */}
      {!isLoading && recommendations.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No recommendations yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Start by adding some resources to your library and we'll find similar content for you.
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            Generate Recommendations
          </button>
        </div>
      )}
    </div>
  );
};
