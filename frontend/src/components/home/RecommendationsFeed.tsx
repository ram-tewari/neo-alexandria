// Neo Alexandria 2.0 Frontend - Recommendations Feed Component
// Displays personalized resource recommendations with relevance scores

import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, ExternalLink, TrendingUp } from 'lucide-react';
import { apiService } from '@/services/api';
import { AnimatedCard } from '@/components/ui/AnimatedCard';
import { SkeletonLoader } from '@/components/ui/SkeletonLoader';
import { Badge } from '@/components/ui/Badge';

const RecommendationsFeed: React.FC = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => apiService.getRecommendations(10),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (error) {
    return (
      <div className="bg-charcoal-grey-800 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Sparkles className="w-6 h-6 text-accent-blue-500 mr-2" />
          <h2 className="text-2xl font-bold text-charcoal-grey-50">
            Recommended for You
          </h2>
        </div>
        <div className="text-center py-8">
          <p className="text-charcoal-grey-400">
            Unable to load recommendations. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-charcoal-grey-800 rounded-lg p-6">
      <div className="flex items-center mb-6">
        <Sparkles className="w-6 h-6 text-accent-blue-500 mr-2" />
        <h2 className="text-2xl font-bold text-charcoal-grey-50">
          Recommended for You
        </h2>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <SkeletonLoader key={i} variant="card" />
          ))}
        </div>
      ) : data?.items && data.items.length > 0 ? (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1,
              },
            },
          }}
          initial="hidden"
          animate="show"
        >
          {data.items.map((recommendation, index) => (
            <motion.div
              key={index}
              variants={{
                hidden: { opacity: 0, y: 20 },
                show: { opacity: 1, y: 0 },
              }}
            >
              <AnimatedCard
                className="h-full flex flex-col bg-charcoal-grey-700 hover:bg-charcoal-grey-600 transition-colors"
              >
                <div className="flex-1 p-4">
                  {/* Relevance Score Badge */}
                  <div className="flex items-center justify-between mb-3">
                    <Badge
                      variant={
                        recommendation.relevance_score >= 0.8
                          ? 'success'
                          : recommendation.relevance_score >= 0.6
                          ? 'warning'
                          : 'default'
                      }
                    >
                      <TrendingUp className="w-3 h-3 mr-1" />
                      {Math.round(recommendation.relevance_score * 100)}% Match
                    </Badge>
                  </div>

                  {/* Title */}
                  <h3 className="text-lg font-semibold text-charcoal-grey-50 mb-2 line-clamp-2">
                    {recommendation.title}
                  </h3>

                  {/* Snippet */}
                  <p className="text-sm text-charcoal-grey-300 mb-3 line-clamp-3">
                    {recommendation.snippet}
                  </p>

                  {/* Reasoning */}
                  {recommendation.reasoning && recommendation.reasoning.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-charcoal-grey-600">
                      <p className="text-xs text-charcoal-grey-400 mb-2 font-medium">
                        Why this recommendation:
                      </p>
                      <ul className="space-y-1">
                        {recommendation.reasoning.slice(0, 2).map((reason, idx) => (
                          <li
                            key={idx}
                            className="text-xs text-charcoal-grey-300 flex items-start"
                          >
                            <span className="text-accent-blue-400 mr-1">•</span>
                            <span className="line-clamp-2">{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Action Button */}
                <div className="p-4 pt-0">
                  <a
                    href={recommendation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center w-full px-4 py-2 bg-accent-blue-500 hover:bg-accent-blue-600 text-white rounded-md transition-colors text-sm font-medium"
                  >
                    View Resource
                    <ExternalLink className="w-4 h-4 ml-2" />
                  </a>
                </div>
              </AnimatedCard>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <div className="text-center py-12">
          <Sparkles className="w-16 h-16 text-charcoal-grey-600 mx-auto mb-4" />
          <p className="text-charcoal-grey-400 text-lg">
            No recommendations available yet.
          </p>
          <p className="text-charcoal-grey-500 text-sm mt-2">
            Add more resources to your library to get personalized recommendations.
          </p>
        </div>
      )}
    </div>
  );
};

export { RecommendationsFeed };
