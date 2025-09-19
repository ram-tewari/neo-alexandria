// Neo Alexandria 2.0 Frontend - Button Component
// Flexible button component with multiple variants and sizes

import React from 'react';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline' | 'glass';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
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
    ...props
  }, ref) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium transition-colors duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'rounded-lg',
    ];

    const variantClasses = {
      primary: [
        'bg-primary-600 text-white',
        'hover:bg-primary-700',
        'focus:ring-primary-500',
      ],
      secondary: [
        'bg-secondary-100 text-secondary-700',
        'hover:bg-secondary-200',
        'focus:ring-secondary-500',
      ],
      ghost: [
        'text-secondary-600 hover:text-secondary-700',
        'hover:bg-secondary-100',
        'focus:ring-secondary-500',
      ],
      danger: [
        'bg-red-600 text-white',
        'hover:bg-red-700',
        'focus:ring-red-500',
      ],
      outline: [
        'border border-secondary-300 text-secondary-700',
        'hover:bg-secondary-50',
        'focus:ring-secondary-500',
      ],
      glass: [
        'glass-holo text-white',
        'hover:bg-white/10',
        'focus:ring-primary-500',
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
      <button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
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
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
export type { ButtonProps };
