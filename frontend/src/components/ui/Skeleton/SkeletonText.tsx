/**
 * SkeletonText - Preset skeleton for text content placeholders
 */

import React from 'react';
import { Skeleton } from './Skeleton';

interface SkeletonTextProps {
  /** Number of lines to display */
  lines?: number;
  /** Width of the last line (percentage or pixels) */
  lastLineWidth?: string | number;
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  lastLineWidth = '60%',
}) => {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          height={16}
          width={index === lines - 1 ? lastLineWidth : '100%'}
        />
      ))}
    </div>
  );
};
