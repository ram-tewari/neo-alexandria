/**
 * DensityToggle component
 * Allows users to switch between compact, comfortable, and spacious view densities
 */

import React from 'react';

export type Density = 'compact' | 'comfortable' | 'spacious';

export interface DensityToggleProps {
  /** Current density value */
  value: Density;
  /** Callback when density changes */
  onChange: (density: Density) => void;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Toggle control for view density selection
 */
export const DensityToggle: React.FC<DensityToggleProps> = ({
  value,
  onChange,
  className = '',
}) => {
  const densities: Density[] = ['compact', 'comfortable', 'spacious'];

  return (
    <div
      className={`flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 ${className}`}
      role="group"
      aria-label="View density"
    >
      {densities.map((density) => (
        <button
          key={density}
          onClick={() => onChange(density)}
          className={`
            px-3 py-1 rounded text-sm font-medium transition-all duration-200
            ${
              value === density
                ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-gray-100'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
            }
          `}
          aria-pressed={value === density}
          aria-label={`${density} density`}
        >
          {density.charAt(0).toUpperCase() + density.slice(1)}
        </button>
      ))}
    </div>
  );
};
