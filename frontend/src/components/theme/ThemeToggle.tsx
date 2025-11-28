/**
 * ThemeToggle Component
 * Interactive control for switching between light and dark themes
 * Requirements: 5.3, 12.1, 13.1, 13.4
 */

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { motion } from 'framer-motion';
import './ThemeToggle.css';

export interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: 16,
  md: 20,
  lg: 24,
};

export function ThemeToggle({ 
  className = '', 
  showLabel = false,
  size = 'md' 
}: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const iconSize = sizeMap[size];

  return (
    <button
      onClick={toggleTheme}
      className={`theme-toggle theme-toggle--${size} ${className}`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      aria-pressed={theme === 'dark'}
      type="button"
    >
      <motion.div
        className="theme-toggle__icon-wrapper"
        initial={false}
        animate={{
          rotate: theme === 'dark' ? 180 : 0,
          scale: theme === 'dark' ? 1 : 1,
        }}
        transition={{
          duration: 0.3,
          ease: [0.4, 0, 0.2, 1],
        }}
      >
        {theme === 'light' ? (
          <Sun 
            size={iconSize} 
            className="theme-toggle__icon theme-toggle__icon--sun"
            aria-hidden="true"
          />
        ) : (
          <Moon 
            size={iconSize} 
            className="theme-toggle__icon theme-toggle__icon--moon"
            aria-hidden="true"
          />
        )}
      </motion.div>
      
      {showLabel && (
        <span className="theme-toggle__label">
          {theme === 'light' ? 'Light' : 'Dark'}
        </span>
      )}
    </button>
  );
}
