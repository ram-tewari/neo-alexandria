/**
 * Input component with focus indicators and accessibility support
 */

import React, { forwardRef } from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Label for the input */
  label?: string;
  /** Error message to display */
  error?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Input component with 2px focus outline and accessibility features
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', disabled, ...props }, ref) => {
    const baseClasses = 'w-full px-3 py-2 rounded-lg border transition-colors duration-150';
    const stateClasses = error
      ? 'border-red-500 focus:border-red-600 focus:ring-2 focus:ring-red-200 dark:focus:ring-red-900'
      : 'border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-900';
    const disabledClasses = disabled
      ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed opacity-60'
      : 'bg-white dark:bg-gray-900';
    const textClasses = 'text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500';
    
    const combinedClasses = `${baseClasses} ${stateClasses} ${disabledClasses} ${textClasses} ${className}`;

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={combinedClasses}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${props.id}-error` : undefined}
          {...props}
        />
        {error && (
          <p
            id={`${props.id}-error`}
            className="mt-1 text-sm text-red-600 dark:text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
