// Neo Alexandria 2.0 Frontend - AnimatedCard Component
// Card component with Framer Motion animations and hover effects

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/utils/cn';

interface AnimatedCardProps extends Omit<HTMLMotionProps<'div'>, 'variants'> {
  variant?: 'default' | 'glass' | 'elevated' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  enableHover?: boolean;
  children?: React.ReactNode;
}

const AnimatedCard = React.forwardRef<HTMLDivElement, AnimatedCardProps>(
  ({ 
    className, 
    variant = 'default', 
    padding = 'md', 
    enableHover = true,
    children, 
    ...props 
  }, ref) => {
    const baseClasses = 'rounded-lg transition-colors duration-200';

    const variantClasses = {
      default: 'bg-white border border-charcoal-grey-200 shadow-sm',
      glass: 'bg-charcoal-grey-800/50 backdrop-blur-md border border-charcoal-grey-700',
      elevated: 'bg-white shadow-lg border border-charcoal-grey-100',
      bordered: 'bg-white border-2 border-charcoal-grey-300',
    };

    const paddingClasses = {
      none: '',
      sm: 'p-3',
      md: 'p-4',
      lg: 'p-6',
    };

    // Hover animation variants
    const hoverVariants = {
      rest: { 
        scale: 1, 
        y: 0,
        boxShadow: variant === 'elevated' 
          ? '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
          : '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
      },
      hover: { 
        scale: 1.02, 
        y: -4,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        transition: {
          duration: 0.2,
          ease: 'easeOut' as const
        }
      }
    };

    return (
      <motion.div
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          paddingClasses[padding],
          className
        )}
        initial="rest"
        whileHover={enableHover ? "hover" : undefined}
        variants={enableHover ? hoverVariants : undefined}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

AnimatedCard.displayName = 'AnimatedCard';

export { AnimatedCard };
export type { AnimatedCardProps };
