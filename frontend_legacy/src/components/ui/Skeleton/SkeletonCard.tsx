/**
 * SkeletonCard - Preset skeleton matching ResourceCard dimensions
 */

import React from 'react';
import { Skeleton } from './Skeleton';

export const SkeletonCard: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Image/Icon placeholder */}
      <Skeleton variant="rectangular" height={48} width={48} className="mb-3" />
      
      {/* Title */}
      <Skeleton variant="text" height={24} className="mb-2" />
      
      {/* Description - 2 lines */}
      <Skeleton variant="text" height={16} className="mb-1" />
      <Skeleton variant="text" height={16} width="80%" className="mb-3" />
      
      {/* Tags */}
      <div className="flex gap-2">
        <Skeleton variant="rectangular" height={24} width={60} />
        <Skeleton variant="rectangular" height={24} width={80} />
        <Skeleton variant="rectangular" height={24} width={70} />
      </div>
    </div>
  );
};
