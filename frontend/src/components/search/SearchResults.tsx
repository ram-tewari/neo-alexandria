// Neo Alexandria 2.0 Frontend - Search Results Component
// Display search results in grid or list view with relevance scores

import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { Search, ExternalLink, Star } from 'lucide-react';
import { cn } from '@/utils/cn';
import { 
  formatRelativeTime, 
  formatQualityScore, 
  getQualityBadgeClass,
  extractDomain,
  truncateText,
} from '@/utils/format';
import type { Resource } from '@/types/api';

interface SearchResultsProps {
  results: Resource[];
  total: number;
  isLoading?: boolean;
  viewMode?: 'grid' | 'list';
  snippets?: Record<string, string>;
  className?: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  total,
  isLoading = false,
  viewMode = 'list',
  snippets = {},
  className,
}) => {
  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        {[...Array(5)].map((_, i) => (
          <Card key={i} variant="glass">
            <CardContent className="p-4">
              <LoadingSkeleton lines={3} />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={className}
      >
        <Card variant="glass">
          <CardContent className="text-center py-16">
            <Search className="w-16 h-16 mx-auto mb-4 text-charcoal-grey-600" />
            <h3 className="text-xl font-medium text-charcoal-grey-300 mb-2">
              No results found
            </h3>
            <p className="text-charcoal-grey-500">
              Try adjusting your search terms or filters
            </p>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <div className={className}>
      {/* Results Count */}
      <div className="mb-4 text-sm text-charcoal-grey-400">
        Found <span className="font-semibold text-charcoal-grey-200">{total}</span> result{total !== 1 ? 's' : ''}
      </div>

      {/* Results List */}
      <div className={cn(
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
          : 'space-y-4'
      )}>
        {results.map((resource, index) => (
          <SearchResultCard
            key={resource.id}
            resource={resource}
            snippet={snippets[resource.id]}
            viewMode={viewMode}
            index={index}
          />
        ))}
      </div>
    </div>
  );
};

// Search Result Card Component
interface SearchResultCardProps {
  resource: Resource;
  snippet?: string;
  viewMode: 'grid' | 'list';
  index: number;
}

const SearchResultCard: React.FC<SearchResultCardProps> = ({
  resource,
  snippet,
  viewMode,
  index,
}) => {
  const domain = extractDomain(resource.url || resource.source);
  const isFavorited = resource.subject.includes('favorite');

  if (viewMode === 'grid') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 }}
      >
        <Card variant="glass" hover className="h-full">
          <CardContent className="p-4 h-full flex flex-col">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                {isFavorited && (
                  <Star className="w-4 h-4 text-yellow-500 fill-current flex-shrink-0" />
                )}
                <Badge 
                  className={getQualityBadgeClass(resource.quality_score)}
                  size="sm"
                >
                  {formatQualityScore(resource.quality_score)}
                </Badge>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1">
              <Link
                to={`/resources/${resource.id}`}
                className="block group"
              >
                <h3 className="text-lg font-medium text-charcoal-grey-50 group-hover:text-accent-blue-400 transition-colors line-clamp-2 mb-2">
                  {resource.title}
                </h3>
              </Link>

              {snippet ? (
                <p 
                  className="text-charcoal-grey-400 text-sm line-clamp-3 mb-3"
                  dangerouslySetInnerHTML={{ __html: snippet }}
                />
              ) : resource.description ? (
                <p className="text-charcoal-grey-400 text-sm line-clamp-3 mb-3">
                  {resource.description}
                </p>
              ) : null}

              {/* Tags */}
              {resource.subject.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {resource.subject.slice(0, 3).map((subject) => (
                    <Badge key={subject} variant="outline" size="sm">
                      {subject}
                    </Badge>
                  ))}
                  {resource.subject.length > 3 && (
                    <Badge variant="outline" size="sm">
                      +{resource.subject.length - 3}
                    </Badge>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-charcoal-grey-700 pt-3 mt-3">
              <div className="flex items-center justify-between text-xs text-charcoal-grey-500">
                <span>{domain}</span>
                <span>{formatRelativeTime(resource.updated_at)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  // List view
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
    >
      <Card variant="glass" hover>
        <CardContent className="p-4">
          <div className="flex items-start space-x-4">
            {/* Quality Badge */}
            <div className="flex-shrink-0 pt-1">
              <Badge 
                className={getQualityBadgeClass(resource.quality_score)}
                size="sm"
              >
                {formatQualityScore(resource.quality_score)}
              </Badge>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <Link
                      to={`/resources/${resource.id}`}
                      className="text-lg font-medium text-charcoal-grey-50 hover:text-accent-blue-400 transition-colors truncate"
                    >
                      {resource.title}
                    </Link>
                    
                    {isFavorited && (
                      <Star className="w-4 h-4 text-yellow-500 fill-current flex-shrink-0" />
                    )}
                  </div>

                  {snippet ? (
                    <p 
                      className="text-charcoal-grey-400 text-sm mb-2 line-clamp-2"
                      dangerouslySetInnerHTML={{ __html: snippet }}
                    />
                  ) : resource.description ? (
                    <p className="text-charcoal-grey-400 text-sm mb-2 line-clamp-2">
                      {truncateText(resource.description, 200)}
                    </p>
                  ) : null}

                  <div className="flex items-center space-x-4 text-sm text-charcoal-grey-500">
                    <span>{domain}</span>
                    <span>{formatRelativeTime(resource.updated_at)}</span>
                    {resource.classification_code && (
                      <Badge variant="outline" size="sm">
                        {resource.classification_code}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* External Link */}
                {resource.url && (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 ml-4 text-charcoal-grey-500 hover:text-accent-blue-400 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>

              {/* Tags */}
              {resource.subject.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {resource.subject.slice(0, 5).map((subject) => (
                    <Badge key={subject} variant="outline" size="sm">
                      {subject}
                    </Badge>
                  ))}
                  {resource.subject.length > 5 && (
                    <Badge variant="outline" size="sm">
                      +{resource.subject.length - 5}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
