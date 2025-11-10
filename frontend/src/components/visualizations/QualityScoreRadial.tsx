// Neo Alexandria 2.0 Frontend - Quality Score Radial Component
// Reusable radial progress indicator for quality scores with color coding and animations

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface QualityScoreRadialProps {
  /**
   * Quality score value (0-100)
   */
  value: number;
  /**
   * Size of the radial indicator in pixels
   * @default 120
   */
  size?: number;
  /**
   * Width of the progress stroke
   * @default 8
   */
  strokeWidth?: number;
  /**
   * Whether to show the label below the percentage
   * @default true
   */
  showLabel?: boolean;
  /**
   * Custom label text
   * @default "Quality Score"
   */
  label?: string;
  /**
   * Animation duration in seconds
   * @default 1
   */
  animationDuration?: number;
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get color based on quality score value
 * - Red (0-59): Low quality, needs review
 * - Yellow (60-79): Medium quality, acceptable
 * - Green (80-100): High quality, excellent
 */
const getQualityColor = (value: number): string => {
  if (value >= 80) return '#10B981'; // Green - High quality
  if (value >= 60) return '#F59E0B'; // Yellow/Amber - Medium quality
  return '#EF4444'; // Red - Low quality
};

/**
 * QualityScoreRadial - A radial progress indicator for displaying quality scores
 * 
 * Features:
 * - SVG-based radial progress with smooth animations
 * - Color-coded by quality level (red, yellow, green)
 * - Animated fill on mount with configurable duration
 * - Displays percentage in center with optional label
 * - Fully customizable size and styling
 * 
 * @example
 * ```tsx
 * <QualityScoreRadial value={85} size={120} />
 * ```
 */
export const QualityScoreRadial: React.FC<QualityScoreRadialProps> = ({
  value,
  size = 120,
  strokeWidth = 8,
  showLabel = true,
  label = 'Quality Score',
  animationDuration = 1,
  className = '',
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  
  // Ensure value is within 0-100 range
  const clampedValue = Math.max(0, Math.min(100, value));
  
  // Calculate SVG circle properties
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (animatedValue / 100) * circumference;
  
  // Get color based on current animated value
  const color = getQualityColor(animatedValue);

  // Animate the value on mount or when value changes
  useEffect(() => {
    // Small delay before starting animation for better visual effect
    const timer = setTimeout(() => {
      setAnimatedValue(clampedValue);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [clampedValue]);

  return (
    <div className={`inline-flex flex-col items-center justify-center ${className}`}>
      {/* SVG Radial Progress */}
      <div className="relative inline-flex items-center justify-center">
        <svg 
          width={size} 
          height={size} 
          className="transform -rotate-90"
          role="img"
          aria-label={`Quality score: ${Math.round(clampedValue)}%`}
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#27272A"
            strokeWidth={strokeWidth}
            fill="none"
            opacity={0.5}
          />
          
          {/* Animated progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ 
              duration: animationDuration, 
              ease: 'easeOut',
              delay: 0.1 
            }}
          />
        </svg>
        
        {/* Center content - percentage display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ 
              delay: animationDuration * 0.5, 
              duration: 0.3,
              ease: 'easeOut'
            }}
            className="text-3xl font-semibold text-zinc-100"
            style={{ color }}
          >
            {Math.round(animatedValue)}
          </motion.div>
          
          {showLabel && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ 
                delay: animationDuration * 0.7, 
                duration: 0.3 
              }}
              className="text-xs text-zinc-500 mt-1"
            >
              {label}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityScoreRadial;
