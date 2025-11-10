// Neo Alexandria 2.0 Frontend - LoadingSpinner Component
// Loading spinner with rotation animation and variants

import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'dots' | 'pulse';
  className?: string;
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'default',
  className,
  text,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  if (variant === 'dots') {
    return (
      <div className={cn('flex items-center justify-center gap-2', className)}>
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className={cn(
              'rounded-full bg-accent-blue-500',
              size === 'sm' && 'w-2 h-2',
              size === 'md' && 'w-3 h-3',
              size === 'lg' && 'w-4 h-4',
              size === 'xl' && 'w-5 h-5'
            )}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: index * 0.2,
            }}
          />
        ))}
        {text && (
          <span className={cn('ml-2 text-charcoal-grey-300', textSizeClasses[size])}>
            {text}
          </span>
        )}
      </div>
    );
  }

  if (variant === 'pulse') {
    return (
      <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
        <motion.div
          className={cn(
            'rounded-full bg-accent-blue-500',
            sizeClasses[size]
          )}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        {text && (
          <span className={cn('text-charcoal-grey-300', textSizeClasses[size])}>
            {text}
          </span>
        )}
      </div>
    );
  }

  // Default spinner variant
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 
        className={cn(
          'animate-spin text-accent-blue-500',
          sizeClasses[size]
        )}
      />
      {text && (
        <span className={cn('text-charcoal-grey-300', textSizeClasses[size])}>
          {text}
        </span>
      )}
    </div>
  );
};

// Full page loading overlay
interface LoadingOverlayProps {
  isLoading: boolean;
  text?: string;
  variant?: 'default' | 'dots' | 'pulse';
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  text = 'Loading...',
  variant = 'default',
}) => {
  if (!isLoading) return null;

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal-grey-900/80 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex flex-col items-center gap-4 p-8 bg-charcoal-grey-800 rounded-lg border border-charcoal-grey-700 shadow-2xl">
        <LoadingSpinner size="xl" variant={variant} />
        <p className="text-lg text-charcoal-grey-200">{text}</p>
      </div>
    </motion.div>
  );
};

// Inline loading state for buttons or small areas
interface InlineLoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const InlineLoading: React.FC<InlineLoadingProps> = ({ 
  size = 'sm', 
  className 
}) => {
  return (
    <LoadingSpinner 
      size={size} 
      variant="default" 
      className={cn('inline-flex', className)} 
    />
  );
};

// Skeleton loader for content placeholders
interface LoadingSkeletonProps {
  lines?: number;
  className?: string;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  lines = 3, 
  className 
}) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-charcoal-grey-700 rounded animate-pulse"
          style={{ width: `${100 - (i * 10)}%` }}
        />
      ))}
    </div>
  );
};

export { LoadingSpinner, LoadingOverlay, InlineLoading, LoadingSkeleton };
export type { LoadingSpinnerProps, LoadingOverlayProps, InlineLoadingProps, LoadingSkeletonProps };
