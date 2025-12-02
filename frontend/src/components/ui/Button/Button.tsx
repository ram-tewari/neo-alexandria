/**
 * Button component with micro-interactions
 * Implements scale-press animation and hover states
 */

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { scalePress } from '../../../lib/utils/animations';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref'> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Button content */
  children: React.ReactNode;
  /** Accessible label for icon-only buttons */
  'aria-label'?: string;
  /** Whether button is pressed (for toggle buttons) */
  'aria-pressed'?: boolean;
}

/**
 * Button component with consistent styling and animations
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  children,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:outline-blue-600 disabled:bg-blue-300',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:outline-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 disabled:bg-gray-100 dark:disabled:bg-gray-800',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus-visible:outline-gray-500 dark:text-gray-300 dark:hover:bg-gray-800 disabled:text-gray-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus-visible:outline-red-600 disabled:bg-red-300',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const disabledClasses = disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer';
  
  const combinedClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${className}`;

  return (
    <motion.button
      className={combinedClasses}
      disabled={disabled}
      {...(disabled ? {} : scalePress)}
      {...props}
    >
      {children}
    </motion.button>
  );
};
