// Neo Alexandria 2.0 Frontend - Recommendations Page
// Personalized content discovery and recommendations

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useRecommendations } from '@/hooks/useApi';
import { Lightbulb, ExternalLink, Plus, RefreshCw, Sparkles } from 'lucide-react';
import { formatNumber } from '@/utils/format';

const Recommendations: React.FC = () => {
  const { data: recommendations, isLoading, error, refetch } = useRecommendations(10);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="p-8">
            <LoadingSpinner centered text="Finding personalized recommendations..." />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          Discover New Knowledge
        </h1>
        <p className="text-secondary-600">
          AI-powered recommendations based on your reading interests and library
        </p>
      </div>

      {/* Recommendations */}
      {error ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-secondary-400 mb-4">
              <Lightbulb className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">
                Unable to Load Recommendations
              </h3>
              <p className="text-secondary-600">{error.message}</p>
            </div>
            <Button onClick={() => refetch()} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      ) : recommendations?.items.length ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              Recommended for You
            </h2>
            <Button
              variant="outline"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              Refresh
            </Button>
          </div>

          <div className="space-y-4">
            {recommendations.items.map((recommendation, index) => (
              <Card key={index} hover>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-secondary-900 mb-2">
                        {recommendation.title}
                      </h3>
                      
                      <p className="text-secondary-600 mb-3 line-clamp-2">
                        {recommendation.snippet}
                      </p>

                      <div className="flex items-center space-x-4 mb-3">
                        <div className="flex items-center space-x-1">
                          <Sparkles className="w-4 h-4 text-primary-600" />
                          <span className="text-sm text-secondary-600">
                            {Math.round(recommendation.relevance_score * 100)}% match
                          </span>
                        </div>
                        
                        <div className="text-sm text-secondary-500">
                          {new URL(recommendation.url).hostname}
                        </div>
                      </div>

                      {recommendation.reasoning.length > 0 && (
                        <div className="mb-4">
                          <p className="text-sm text-secondary-600 mb-2">Why this was recommended:</p>
                          <div className="flex flex-wrap gap-1">
                            {recommendation.reasoning.map((reason, idx) => (
                              <Badge key={idx} variant="outline" size="sm">
                                {reason}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col space-y-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(recommendation.url, '_blank')}
                        icon={<ExternalLink className="w-4 h-4" />}
                      >
                        View
                      </Button>
                      
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => {
                          // Add to library
                          window.location.href = `/add?url=${encodeURIComponent(recommendation.url)}&title=${encodeURIComponent(recommendation.title)}`;
                        }}
                        icon={<Plus className="w-4 h-4" />}
                      >
                        Add
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-secondary-400 mb-6">
              <Lightbulb className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">
                No Recommendations Yet
              </h3>
              <p className="text-secondary-600 max-w-sm mx-auto">
                Add more resources to your library to receive personalized recommendations.
              </p>
            </div>
            
            <Button 
              variant="primary"
              onClick={() => window.location.href = '/add'}
              icon={<Plus className="w-4 h-4" />}
            >
              Add Resources
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export { Recommendations };
