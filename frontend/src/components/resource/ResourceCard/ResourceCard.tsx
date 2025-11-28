import React from 'react';
import { motion } from 'framer-motion';
import { FileText, ExternalLink, Star, Calendar, Users } from 'lucide-react';
import { Resource, ViewMode } from '@/types/resource';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface ResourceCardProps {
  resource: Resource;
  view?: ViewMode;
  isSelected?: boolean;
  onSelect?: (id: string) => void;
  onClick?: (id: string) => void;
}

export const ResourceCard: React.FC<ResourceCardProps> = ({
  resource,
  view = 'card',
  isSelected = false,
  onSelect,
  onClick,
}) => {
  const prefersReducedMotion = useReducedMotion();

  const handleClick = () => {
    onClick?.(resource.id);
  };

  const handleSelectClick = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSelect?.(resource.id);
  };

  if (view === 'list') {
    return (
      <motion.div
        initial={prefersReducedMotion ? {} : { opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        onClick={handleClick}
        className={`
          flex gap-4 p-4 bg-white dark:bg-gray-800 rounded-lg border
          cursor-pointer transition-all duration-200
          ${
            isSelected
              ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800'
              : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600'
          }
        `}
        role="article"
        aria-label={resource.title}
      >
        {onSelect && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={handleSelectClick}
            className="mt-1 w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
            aria-label={`Select ${resource.title}`}
          />
        )}

        <div className="flex-shrink-0 w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
          {resource.thumbnail ? (
            <img
              src={resource.thumbnail}
              alt=""
              className="w-full h-full object-cover rounded"
            />
          ) : (
            <FileText className="w-8 h-8 text-gray-400" aria-hidden="true" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 truncate">
            {resource.title}
          </h3>
          
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
            <Users className="w-4 h-4" aria-hidden="true" />
            <span className="truncate">{resource.authors.join(', ')}</span>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
            {resource.abstract}
          </p>

          <div className="flex items-center gap-3 mt-2">
            <QualityBadge score={resource.qualityScore} />
            {resource.classification.slice(0, 2).map((cat) => (
              <span
                key={cat}
                className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
              >
                {cat}
              </span>
            ))}
          </div>
        </div>

        <div className="flex-shrink-0 text-sm text-gray-500 dark:text-gray-400">
          <Calendar className="w-4 h-4 inline mr-1" aria-hidden="true" />
          {new Date(resource.createdAt).toLocaleDateString()}
        </div>
      </motion.div>
    );
  }

  if (view === 'compact') {
    return (
      <motion.div
        initial={prefersReducedMotion ? {} : { opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        onClick={handleClick}
        className={`
          flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border
          cursor-pointer transition-all duration-200
          ${
            isSelected
              ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800'
              : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600'
          }
        `}
        role="article"
        aria-label={resource.title}
      >
        {onSelect && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={handleSelectClick}
            className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
            aria-label={`Select ${resource.title}`}
          />
        )}

        <FileText className="w-5 h-5 text-gray-400 flex-shrink-0" aria-hidden="true" />

        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {resource.title}
          </h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
            {resource.authors[0]}
            {resource.authors.length > 1 && ` +${resource.authors.length - 1}`}
          </p>
        </div>

        <QualityBadge score={resource.qualityScore} size="sm" />
      </motion.div>
    );
  }

  // Card view (default)
  return (
    <motion.div
      initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={prefersReducedMotion ? {} : { scale: 1.02 }}
      transition={{ duration: 0.2 }}
      onClick={handleClick}
      className={`
        relative bg-white dark:bg-gray-800 rounded-lg border overflow-hidden
        cursor-pointer transition-all duration-200
        ${
          isSelected
            ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800'
            : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:shadow-lg'
        }
      `}
      role="article"
      aria-label={resource.title}
    >
      {onSelect && (
        <div className="absolute top-3 left-3 z-10">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={handleSelectClick}
            onClick={handleSelectClick}
            className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500 bg-white"
            aria-label={`Select ${resource.title}`}
          />
        </div>
      )}

      {/* Thumbnail */}
      <div className="relative h-40 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
        {resource.thumbnail ? (
          <img
            src={resource.thumbnail}
            alt=""
            className="w-full h-full object-cover"
          />
        ) : (
          <FileText className="w-16 h-16 text-gray-400" aria-hidden="true" />
        )}
        
        {resource.type === 'url' && (
          <div className="absolute top-2 right-2 p-1.5 bg-white dark:bg-gray-800 rounded-full shadow">
            <ExternalLink className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {resource.title}
        </h3>

        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
          <Users className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
          <span className="truncate">
            {resource.authors[0]}
            {resource.authors.length > 1 && ` +${resource.authors.length - 1}`}
          </span>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 mb-3">
          {resource.abstract}
        </p>

        <div className="flex items-center gap-2 flex-wrap">
          <QualityBadge score={resource.qualityScore} />
          {resource.classification.slice(0, 2).map((cat) => (
            <span
              key={cat}
              className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
            >
              {cat}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

interface QualityBadgeProps {
  score: number;
  size?: 'sm' | 'md';
}

const QualityBadge: React.FC<QualityBadgeProps> = ({ score, size = 'md' }) => {
  const getColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300';
    if (score >= 60) return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300';
    return 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300';
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1 font-semibold rounded ${getColor(score)} ${sizeClasses}`}
      aria-label={`Quality score: ${score}`}
    >
      <Star className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} aria-hidden="true" />
      {score}
    </span>
  );
};
