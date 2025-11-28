import React from 'react';
import { Skeleton } from './Skeleton';

export const SkeletonList: React.FC<{ count?: number }> = ({ count = 5 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm flex gap-4">
          <Skeleton variant="rectangular" width={80} height={80} />
          <div className="flex-1">
            <Skeleton variant="text" width="70%" className="mb-2" />
            <Skeleton variant="text" width="50%" className="mb-2" />
            <Skeleton variant="text" width="90%" />
          </div>
        </div>
      ))}
    </div>
  );
};
