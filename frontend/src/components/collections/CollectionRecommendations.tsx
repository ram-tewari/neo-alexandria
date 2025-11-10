// Neo Alexandria 2.0 Frontend - Collection Recommendations Component
// Display resource and collection recommendations for a collection

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useCollectionRecommendations, useAddResourcesToCollection } from '@/hooks/useCollections';
import { useAppStore } from '@/store';
import { toast } from '@/store/toastStore';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { Sparkles, Plus, ExternalLink, FolderPlus, TrendingUp } from 'lucide-react';
import { cn } from '@/utils/cn';

interface CollectionRecommendationsProps {
  collectionId: string;
  className?: string;
}

const CollectionRecommendations: React.FC<CollectionRecommendationsProps> = ({
  collectionId,
  className,
}) => {
  const navigate = useNavigate();
  const userId = useAppStore((state) => state.userId) || 'demo-user';
  
  const [activeTab, setActiveTab] = useState<'resources' | 'collections'>('resources');

  // Fetch recommendations
  const { data, isLoading, error } = useCollectionRecommendations(collectionId, userId, 10);
  const resourceRecommendations = data?.resource_recommendations || [];
  const collectionRecommendations = data?.collection_recommendations || [];

  // Add resources mutation
  const addResourcesMutation = useAddResourcesToCollection();

  // Handle adding a recommended resource
  const handleAddResource = async (resourceId: string, resourceTitle: string) => {
    try {
      await addResourcesMutation.mutateAsync({
        collectionId,
        resourceIds: [resourceId],
        userId,
      });

      toast.success('Resource added', `"${resourceTitle}" has been added to this collection`);
    } catch (error: any) {
      toast.error('Failed to add resource', error?.response?.data?.detail || error.message);
    }
  };

  if (error) {
    return (
      <Card variant="glass" className={className}>
        <CardContent className="p-6 text-center">
          <Sparkles className="w-12 h-12 mx-auto mb-3 text-charcoal-grey-600" />
          <p className="text-sm text-charcoal-grey-400">
            Unable to load recommendations
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="glass" className={className}>
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-accent-blue-400" />
            <h3 className="text-lg font-semibold text-charcoal-grey-50">
              Recommendations
            </h3>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-4 bg-charcoal-grey-900 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('resources')}
            className={cn(
              'flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200',
              activeTab === 'resources'
                ? 'bg-accent-blue-500 text-white'
                : 'text-charcoal-grey-400 hover:text-charcoal-grey-200'
            )}
          >
            Resources ({resourceRecommendations.length})
          </button>
          <button
            onClick={() => setActiveTab('collections')}
            className={cn(
              'flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200',
              activeTab === 'collections'
                ? 'bg-accent-blue-500 text-white'
                : 'text-charcoal-grey-400 hover:text-charcoal-grey-200'
            )}
          >
            Collections ({collectionRecommendations.length})
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-3 bg-charcoal-grey-900 rounded-lg">
                <LoadingSkeleton lines={2} />
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Resource Recommendations */}
            {activeTab === 'resources' && (
              <div className="space-y-3">
                {resourceRecommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <Sparkles className="w-12 h-12 mx-auto mb-3 text-charcoal-grey-600" />
                    <p className="text-sm text-charcoal-grey-400">
                      No resource recommendations available
                    </p>
                  </div>
                ) : (
                  resourceRecommendations.map((rec: any, index: number) => (
                    <motion.div
                      key={rec.url || index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        'p-3 bg-charcoal-grey-900 rounded-lg border border-charcoal-grey-700',
                        'hover:border-accent-blue-500/50 transition-colors duration-200'
                      )}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-charcoal-grey-50 mb-1 line-clamp-1">
                            {rec.title}
                          </h4>
                          {rec.snippet && (
                            <p className="text-xs text-charcoal-grey-400 line-clamp-2 mb-2">
                              {rec.snippet}
                            </p>
                          )}
                          <div className="flex items-center space-x-3">
                            {rec.relevance_score !== undefined && (
                              <div className="flex items-center space-x-1">
                                <TrendingUp className="w-3 h-3 text-accent-blue-400" />
                                <span className="text-xs text-accent-blue-400">
                                  {(rec.relevance_score * 100).toFixed(0)}% match
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col space-y-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleAddResource(rec.id || rec.url, rec.title)}
                            disabled={addResourcesMutation.isPending}
                            icon={<Plus className="w-3 h-3" />}
                            title="Add to collection"
                          />
                          {rec.url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(rec.url, '_blank')}
                              icon={<ExternalLink className="w-3 h-3" />}
                              title="Open in new tab"
                            />
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            )}

            {/* Collection Recommendations */}
            {activeTab === 'collections' && (
              <div className="space-y-3">
                {collectionRecommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <FolderPlus className="w-12 h-12 mx-auto mb-3 text-charcoal-grey-600" />
                    <p className="text-sm text-charcoal-grey-400">
                      No collection recommendations available
                    </p>
                  </div>
                ) : (
                  collectionRecommendations.map((rec: any, index: number) => (
                    <motion.div
                      key={rec.id || index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        'p-3 bg-charcoal-grey-900 rounded-lg border border-charcoal-grey-700',
                        'hover:border-accent-blue-500/50 transition-colors duration-200 cursor-pointer'
                      )}
                      onClick={() => navigate(`/collections/${rec.id}`)}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-charcoal-grey-50 mb-1 line-clamp-1">
                            {rec.name}
                          </h4>
                          {rec.description && (
                            <p className="text-xs text-charcoal-grey-400 line-clamp-2 mb-2">
                              {rec.description}
                            </p>
                          )}
                          <div className="flex items-center space-x-3">
                            <span className="text-xs text-charcoal-grey-500">
                              {rec.resource_count || 0} resources
                            </span>
                            {rec.similarity_score !== undefined && (
                              <div className="flex items-center space-x-1">
                                <TrendingUp className="w-3 h-3 text-accent-blue-400" />
                                <span className="text-xs text-accent-blue-400">
                                  {(rec.similarity_score * 100).toFixed(0)}% similar
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex-shrink-0">
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<ExternalLink className="w-3 h-3" />}
                            title="View collection"
                          />
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export { CollectionRecommendations };
export type { CollectionRecommendationsProps };
