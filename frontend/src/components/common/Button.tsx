/**
 * Interactive Button Component
 * Animated button with theme-aware styling
 * Requirements: 3.3, 1.7, 2.7
 */

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext';
import './Button.css';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref'> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

/**
 * Button Component
 * Features:
 * - Soft scaling animation on interaction
 * - Minimal spring motion effect
 * - Theme-specific colors for different states
 * - Proper hover and active states
 */
export function Button({
  variant = 'primary',
  size = 'md',
  children,
  className = '',
  disabled = false,
  ...props
}: ButtonProps) {
  const { theme } = useTheme();

  return (
    <motion.button
      className={`button button--${variant} button--${size} ${className}`}
      data-theme={theme}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 17,
      }}
      {...props}
    >
      {children}
    </motion.button>
  );
}
