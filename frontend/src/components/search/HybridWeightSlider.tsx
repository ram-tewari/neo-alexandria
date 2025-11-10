// Neo Alexandria 2.0 Frontend - Hybrid Weight Slider Component
// Slider for adjusting keyword vs semantic search balance

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';

interface HybridWeightSliderProps {
  value: number;
  onChange: (value: number) => void;
  className?: string;
}

export const HybridWeightSlider: React.FC<HybridWeightSliderProps> = ({
  value,
  onChange,
  className,
}) => {
  const getLabel = (weight: number): string => {
    if (weight <= 0.2) return 'Keyword';
    if (weight >= 0.8) return 'Semantic';
    return 'Balanced';
  };

  const getDescription = (weight: number): string => {
    if (weight <= 0.2) return 'Exact keyword matching';
    if (weight >= 0.8) return 'Meaning-based search';
    return 'Mix of both approaches';
  };

  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-charcoal-grey-200">
          Search Mode
        </label>
        <motion.span
          key={getLabel(value)}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm font-semibold text-accent-blue-400"
        >
          {getLabel(value)}
        </motion.span>
      </div>

      <div className="relative">
        {/* Slider Track */}
        <div className="relative h-2 bg-charcoal-grey-700 rounded-full overflow-hidden">
          {/* Gradient Background */}
          <div className="absolute inset-0 bg-gradient-to-r from-neutral-blue-500 via-accent-blue-500 to-accent-blue-600 opacity-50" />
          
          {/* Progress Fill */}
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-neutral-blue-500 to-accent-blue-500"
            initial={false}
            animate={{ width: `${value * 100}%` }}
            transition={{ duration: 0.2 }}
          />
        </div>

        {/* Slider Input */}
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute inset-0 w-full h-2 opacity-0 cursor-pointer"
        />

        {/* Slider Thumb */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full shadow-lg border-2 border-accent-blue-500 pointer-events-none"
          initial={false}
          animate={{ left: `calc(${value * 100}% - 10px)` }}
          transition={{ duration: 0.2 }}
        />
      </div>

      {/* Labels */}
      <div className="flex items-center justify-between text-xs">
        <span className={cn(
          'transition-colors',
          value <= 0.2 ? 'text-neutral-blue-400 font-medium' : 'text-charcoal-grey-500'
        )}>
          Keyword (0.0)
        </span>
        <span className={cn(
          'transition-colors',
          value > 0.2 && value < 0.8 ? 'text-accent-blue-400 font-medium' : 'text-charcoal-grey-500'
        )}>
          Balanced (0.5)
        </span>
        <span className={cn(
          'transition-colors',
          value >= 0.8 ? 'text-accent-blue-600 font-medium' : 'text-charcoal-grey-500'
        )}>
          Semantic (1.0)
        </span>
      </div>

      {/* Description */}
      <motion.p
        key={getDescription(value)}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-xs text-charcoal-grey-400 text-center"
      >
        {getDescription(value)}
      </motion.p>
    </div>
  );
};
