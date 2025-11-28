import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ThumbsUp, ThumbsDown, Bookmark, ExternalLink, FileText, Info } from 'lucide-react';
import { Recommendation } from '@/types/recommendation';
import { useSubmitFeedback } from '@/hooks/useRecommendations';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onResourceClick?: (resourceId: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onResourceClick,
}) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<'like' | 'dislike' | null>(null);
  const submitFeedback = useSubmitFeedback();
  const prefersReducedMotion = useReducedMotion();

  const handleFeedback = (type: 'like' | 'dislike' | 'not_interested' | 'save') => {
    submitFeedback.mutate({
      recommendationId: `${recommendation.resource.id}-${recommendation.category}`,
      resourceId: recommendation.resource.id,
      type,
    });

    if (type === 'like' || type === 'dislike') {
      setFeedbackGiven(type);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'fresh':
        return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300';
      case 'similar':
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300';
      case 'hidden':
        return 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'fresh':
        return 'Fresh Find';
      case 'similar':
        return 'Similar to Recent';
      case 'hidden':
        return 'Hidden Gem';
      default:
        return category;
    }
  };

  return (
    <motion.div
      initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={prefersReducedMotion ? {} : { scale: 1.02, y: -4 }}
      transition={{ duration: 0.2 }}
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onResourceClick?.(recommendation.resource.id)}
    >
      {/* Category Badge */}
      <div className="p-4 pb-0">
        <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(recommendation.category)}`}>
          {getCategoryLabel(recommendation.category)}
        </span>
      </div>

      {/* Thumbnail */}
      <div className="relative h-40 bg-gray-100 dark:bg-gray-700 flex items-center justify-center mx-4 mt-3 rounded">
        {recommendation.resource.thumbnail ? (
          <img
            src={recommendation.resource.thumbnail}
            alt=""
            className="w-full h-full object-cover rounded"
          />
        ) : (
          <FileText className="w-16 h-16 text-gray-400" aria-hidden="true" />
        )}
        
        {recommendation.resource.type === 'url' && (
          <div className="absolute top-2 right-2 p-1.5 bg-white dark:bg-gray-800 rounded-full shadow">
            <ExternalLink className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {recommendation.resource.title}
        </h3>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          {recommendation.resource.authors.slice(0, 2).join(', ')}
          {recommendation.resource.authors.length > 2 && ` +${recommendation.resource.authors.length - 2}`}
        </p>

        <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 mb-3">
          {recommendation.resource.abstract}
        </p>

        {/* Classification Tags */}
        <div className="flex items-center gap-2 flex-wrap mb-3">
          {recommendation.resource.classification.slice(0, 2).map((cat) => (
            <span
              key={cat}
              className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
            >
              {cat}
            </span>
          ))}
        </div>

        {/* Explanation */}
        <div className="mb-4">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowExplanation(!showExplanation);
            }}
            className="flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
          >
            <Info className="w-4 h-4" />
            Why recommended?
          </button>
          
          {showExplanation && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded text-sm text-gray-700 dark:text-gray-300"
            >
              <p className="mb-2 font-medium">{recommendation.explanation}</p>
              <ul className="text-xs space-y-1">
                {recommendation.reasons.map((reason, index) => (
                  <li key={index}>• {reason}</li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.1 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
              onClick={(e) => {
                e.stopPropagation();
                handleFeedback('like');
              }}
              className={`p-2 rounded-full transition-colors ${
                feedbackGiven === 'like'
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                  : 'text-gray-400 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/10'
              }`}
              aria-label="Like recommendation"
            >
              <ThumbsUp className="w-4 h-4" />
            </motion.button>

            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.1 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
              onClick={(e) => {
                e.stopPropagation();
                handleFeedback('dislike');
              }}
              className={`p-2 rounded-full transition-colors ${
                feedbackGiven === 'dislike'
                  ? 'bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                  : 'text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10'
              }`}
              aria-label="Dislike recommendation"
            >
              <ThumbsDown className="w-4 h-4" />
            </motion.button>

            <motion.button
              whileHover={prefersReducedMotion ? {} : { scale: 1.1 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
              onClick={(e) => {
                e.stopPropagation();
                handleFeedback('save');
              }}
              className="p-2 rounded-full text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-colors"
              aria-label="Save recommendation"
            >
              <Bookmark className="w-4 h-4" />
            </motion.button>
          </div>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round(recommendation.score * 100)}% match
          </div>
        </div>
      </div>
    </motion.div>
  );
};
