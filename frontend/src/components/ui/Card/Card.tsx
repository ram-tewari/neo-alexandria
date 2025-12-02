/**
 * Card component for content containers
 * Supports light/dark theme and optional hover animation
 */

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { hover } from '../../../lib/utils/animations';

export interface CardProps extends Omit<HTMLMotionProps<'div'>, 'ref'> {
  /** Whether to show hover animation */
  hoverable?: boolean;
  /** Card padding size */
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Card content */
  children: React.ReactNode;
}

/**
 * Card component for content containers
 */
export const Card: React.FC<CardProps> = ({
  hoverable = false,
  padding = 'md',
  className = '',
  children,
  ...props
}) => {
  const baseClasses = 'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700';
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  const combinedClasses = `${baseClasses} ${paddingClasses[padding]} ${className}`;

  return (
    <motion.div
      className={combinedClasses}
      {...(hoverable ? hover : {})}
      {...props}
    >
      {children}
    </motion.div>
  );
};
