// Neo Alexandria 2.0 Frontend - Collection Card Component
// Display collection information with hover animations

import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FolderOpen, Lock, Users, Globe, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { Collection } from '@/services/api/collections';

interface CollectionCardProps {
  collection: Collection;
  depth?: number;
  className?: string;
}

const CollectionCard: React.FC<CollectionCardProps> = ({ 
  collection, 
  depth = 0,
  className 
}) => {
  const navigate = useNavigate();

  // Visibility icon mapping
  const visibilityIcons = {
    private: <Lock className="w-4 h-4" />,
    shared: <Users className="w-4 h-4" />,
    public: <Globe className="w-4 h-4" />,
  };

  // Visibility badge colors
  const visibilityColors = {
    private: 'bg-charcoal-grey-700 text-charcoal-grey-300',
    shared: 'bg-neutral-blue-900/50 text-neutral-blue-300',
    public: 'bg-accent-blue-900/50 text-accent-blue-300',
  };

  const handleClick = () => {
    navigate(`/collections/${collection.id}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'group cursor-pointer',
        className
      )}
      style={{ marginLeft: `${depth * 24}px` }}
      onClick={handleClick}
    >
      <div
        className={cn(
          'bg-charcoal-grey-800 rounded-lg border border-charcoal-grey-700',
          'hover:border-accent-blue-500/50 hover:shadow-lg hover:shadow-accent-blue-500/10',
          'transition-all duration-200 p-4'
        )}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            {/* Icon */}
            <div className="flex-shrink-0 mt-1">
              <div className="w-10 h-10 rounded-lg bg-accent-blue-500/10 flex items-center justify-center">
                <FolderOpen className="w-5 h-5 text-accent-blue-400" />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="text-base font-semibold text-charcoal-grey-50 truncate">
                  {collection.name}
                </h3>
                
                {/* Visibility Badge */}
                <span
                  className={cn(
                    'inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium',
                    visibilityColors[collection.visibility]
                  )}
                >
                  {visibilityIcons[collection.visibility]}
                  <span className="capitalize">{collection.visibility}</span>
                </span>
              </div>

              {/* Description */}
              {collection.description && (
                <p className="text-sm text-charcoal-grey-400 line-clamp-2 mb-2">
                  {collection.description}
                </p>
              )}

              {/* Resource Count */}
              <div className="flex items-center space-x-4 text-xs text-charcoal-grey-500">
                <span>
                  {collection.resource_count} {collection.resource_count === 1 ? 'resource' : 'resources'}
                </span>
                {collection.subcollections && collection.subcollections.length > 0 && (
                  <span>
                    {collection.subcollections.length} {collection.subcollections.length === 1 ? 'subcollection' : 'subcollections'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Arrow Icon */}
          <div className="flex-shrink-0 ml-2">
            <ChevronRight className="w-5 h-5 text-charcoal-grey-600 group-hover:text-accent-blue-400 transition-colors" />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export { CollectionCard };
export type { CollectionCardProps };
