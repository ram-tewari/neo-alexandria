// Neo Alexandria 2.0 Frontend - SkeletonLoader Component
// Skeleton loader with shimmer animation for loading states

import React from 'react';
import { cn } from '@/utils/cn';

interface SkeletonLoaderProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card' | 'list';
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'text',
  width,
  height,
  count = 1,
  className,
}) => {
  const baseClasses = [
    'bg-gradient-to-r from-charcoal-grey-800 via-charcoal-grey-700 to-charcoal-grey-800',
    'bg-[length:200%_100%]',
    'animate-shimmer',
  ];

  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'h-48 rounded-lg',
    list: 'h-16 rounded-lg',
  };

  const getStyle = () => {
    const style: React.CSSProperties = {};
    if (width) style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) style.height = typeof height === 'number' ? `${height}px` : height;
    return style;
  };

  const renderSkeleton = (index: number) => (
    <div
      key={index}
      className={cn(baseClasses, variantClasses[variant], className)}
      style={getStyle()}
      aria-hidden="true"
    />
  );

  if (count === 1) {
    return renderSkeleton(0);
  }

  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => renderSkeleton(index))}
    </div>
  );
};

// Specialized skeleton components for common use cases
const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({ 
  lines = 3, 
  className 
}) => {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <SkeletonLoader
          key={index}
          variant="text"
          width={index === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
};

const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('p-4 border border-charcoal-grey-700 rounded-lg', className)}>
      <div className="flex items-start space-x-4">
        <SkeletonLoader variant="circular" width={48} height={48} />
        <div className="flex-1 space-y-3">
          <SkeletonLoader variant="text" width="60%" />
          <SkeletonLoader variant="text" width="100%" />
          <SkeletonLoader variant="text" width="80%" />
        </div>
      </div>
    </div>
  );
};

const SkeletonList: React.FC<{ count?: number; className?: string }> = ({ 
  count = 5, 
  className 
}) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center space-x-4 p-3 border border-charcoal-grey-700 rounded-lg">
          <SkeletonLoader variant="circular" width={40} height={40} />
          <div className="flex-1 space-y-2">
            <SkeletonLoader variant="text" width="40%" />
            <SkeletonLoader variant="text" width="70%" />
          </div>
        </div>
      ))}
    </div>
  );
};

const SkeletonGrid: React.FC<{ 
  count?: number; 
  columns?: number;
  className?: string;
}> = ({ 
  count = 6, 
  columns = 3,
  className 
}) => {
  return (
    <div 
      className={cn('grid gap-4', className)}
      style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
    >
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  );
};

export { 
  SkeletonLoader, 
  SkeletonText, 
  SkeletonCard, 
  SkeletonList,
  SkeletonGrid 
};
export type { SkeletonLoaderProps };
