// Neo Alexandria 2.0 Frontend - Input Component
// Flexible input component with validation states and icons

import React from 'react';
import { cn } from '@/utils/cn';
import { AlertCircle } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    containerClassName,
    label,
    error,
    hint,
    leftIcon,
    rightIcon,
    type = 'text',
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substring(2)}`;

    const baseClasses = [
      'w-full px-3 py-2 text-sm',
      'bg-white border border-secondary-300 rounded-lg text-secondary-900',
      'placeholder-secondary-500',
      'transition-colors duration-200',
      'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
      'disabled:bg-secondary-50 disabled:text-secondary-400 disabled:cursor-not-allowed',
    ];

    const errorClasses = error ? [
      'border-red-300 focus:border-red-500 focus:ring-red-500',
    ] : [];

    const paddingClasses = [
      leftIcon ? 'pl-10' : '',
      rightIcon || error ? 'pr-10' : '',
    ];

    const inputClasses = cn(
      baseClasses,
      errorClasses,
      paddingClasses,
      className
    );

    return (
      <div className={cn('relative', containerClassName)}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-secondary-700 mb-1"
          >
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {React.cloneElement(leftIcon as React.ReactElement, {
                className: cn('w-4 h-4 text-secondary-500'),
              })}
            </div>
          )}
          
          <input
            ref={ref}
            type={type}
            id={inputId}
            className={inputClasses}
            {...props}
          />
          
          {(rightIcon || error) && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {error ? (
                <AlertCircle className="w-4 h-4 text-red-500" />
              ) : (
                rightIcon && React.cloneElement(rightIcon as React.ReactElement, {
                  className: cn('w-4 h-4 text-secondary-500'),
                })
              )}
            </div>
          )}
        </div>
        
        {(error || hint) && (
          <div className="mt-1">
            {error && (
              <p className="text-sm text-red-600" role="alert">
                {error}
              </p>
            )}
            {hint && !error && (
              <p className="text-sm text-secondary-500">
                {hint}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export type { InputProps };
