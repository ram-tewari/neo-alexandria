/**
 * SkeletonTable - Preset skeleton matching table row structure
 */

import React from 'react';
import { Skeleton } from './Skeleton';

interface SkeletonTableProps {
  /** Number of rows to display */
  rows?: number;
}

export const SkeletonTable: React.FC<SkeletonTableProps> = ({ rows = 5 }) => {
  return (
    <div className="w-full">
      {/* Table header */}
      <div className="flex gap-4 p-4 border-b border-gray-200 dark:border-gray-700">
        <Skeleton variant="text" width={200} height={16} />
        <Skeleton variant="text" width={100} height={16} />
        <Skeleton variant="text" width={150} height={16} />
        <Skeleton variant="text" width={100} height={16} />
      </div>
      
      {/* Table rows */}
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className="flex gap-4 p-4 border-b border-gray-200 dark:border-gray-700"
        >
          <Skeleton variant="text" width={200} height={16} />
          <Skeleton variant="text" width={100} height={16} />
          <Skeleton variant="text" width={150} height={16} />
          <Skeleton variant="text" width={100} height={16} />
        </div>
      ))}
    </div>
  );
};
