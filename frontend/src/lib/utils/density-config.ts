/**
 * View density configuration
 * Defines spacing and sizing for different density modes
 */

import type { Density } from '../../components/ui/DensityToggle';

export interface DensityConfig {
  /** Grid gap class */
  gap: string;
  /** Card padding size */
  cardPadding: 'sm' | 'md' | 'lg';
}

/**
 * Density configuration mapping
 */
export const densityConfig: Record<Density, DensityConfig> = {
  compact: {
    gap: 'gap-2',
    cardPadding: 'sm',
  },
  comfortable: {
    gap: 'gap-4',
    cardPadding: 'md',
  },
  spacious: {
    gap: 'gap-6',
    cardPadding: 'lg',
  },
};

/**
 * Get density configuration for a given density value
 */
export function getDensityConfig(density: Density): DensityConfig {
  return densityConfig[density];
}
