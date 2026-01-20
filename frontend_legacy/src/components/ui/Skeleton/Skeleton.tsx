/**
 * Skeleton component for loading states
 * Provides visual feedback during data loading to prevent layout shift
 */

import React from 'react';
import './Skeleton.css';

export interface SkeletonProps {
  /** Variant of the skeleton */
  variant?: 'text' | 'circular' | 'rectangular';
  /** Width of the skeleton */
  width?: string | number;
  /** Height of the skeleton */
  height?: string | number;
  /** Animation type */
  animation?: 'pulse' | 'wave' | 'none';
  /** Additional CSS classes */
  className?: string;
}

/**
 * Skeleton component for loading placeholders
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
  className = '',
}) => {
  const variantClasses = {
    text: 'skeleton-text',
    circular: 'skeleton-circular',
    rectangular: 'skeleton-rectangular',
  };

  const animationClass = animation !== 'none' ? `skeleton-${animation}` : '';

  const style: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div
      className={`skeleton ${variantClasses[variant]} ${animationClass} ${className}`}
      style={style}
      aria-busy="true"
      aria-live="polite"
    />
  );
};
