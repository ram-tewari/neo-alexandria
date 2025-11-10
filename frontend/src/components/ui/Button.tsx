// Neo Alexandria 2.0 Frontend - Button Component
// Flexible button component with multiple variants and sizes

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'type'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline' | 'glass';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    iconPosition = 'left',
    fullWidth = false,
    children,
    disabled,
    type = 'button',
    ...props
  }, ref) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium transition-colors duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus-visible:ring-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'rounded-lg',
    ];

    const variantClasses = {
      primary: [
        'bg-accent-blue-500 text-white',
        'hover:bg-accent-blue-600',
        'focus:ring-accent-blue-500',
      ],
      secondary: [
        'bg-neutral-blue-600 text-white',
        'hover:bg-neutral-blue-700',
        'focus:ring-neutral-blue-500',
      ],
      ghost: [
        'text-charcoal-grey-300 hover:text-charcoal-grey-50',
        'hover:bg-charcoal-grey-700',
        'focus:ring-charcoal-grey-500',
      ],
      danger: [
        'bg-error text-white',
        'hover:bg-red-700',
        'focus:ring-error',
      ],
      outline: [
        'border border-charcoal-grey-600 text-charcoal-grey-300',
        'hover:bg-charcoal-grey-800 hover:border-charcoal-grey-500',
        'focus:ring-charcoal-grey-500',
      ],
      glass: [
        'bg-charcoal-grey-800/50 backdrop-blur-md text-white border border-charcoal-grey-700',
        'hover:bg-charcoal-grey-700/50',
        'focus:ring-accent-blue-500',
      ],
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    };

    const iconSizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-4 h-4',
      lg: 'w-5 h-5',
    };

    const iconSpacingClasses = {
      left: children ? 'mr-2' : '',
      right: children ? 'ml-2' : '',
    };

    const classes = cn(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      fullWidth && 'w-full',
      className
    );

    const iconElement = loading ? (
      <Loader2 className={cn(iconSizeClasses[size], 'animate-spin')} />
    ) : icon ? (
      React.cloneElement(icon as React.ReactElement, {
        className: cn(iconSizeClasses[size]),
      })
    ) : null;

    return (
      <motion.button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
        type={type}
        whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
        transition={{ duration: 0.15 }}
        {...props}
      >
        {iconElement && iconPosition === 'left' && (
          <span className={iconSpacingClasses[iconPosition]}>
            {iconElement}
          </span>
        )}
        {children}
        {iconElement && iconPosition === 'right' && (
          <span className={iconSpacingClasses[iconPosition]}>
            {iconElement}
          </span>
        )}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
export type { ButtonProps };
