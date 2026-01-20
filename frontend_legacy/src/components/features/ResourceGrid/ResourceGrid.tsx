/**
 * ResourceGrid component
 * Displays resources in a responsive grid layout
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ResourceCard } from './ResourceCard';
import { getDensityConfig } from '../../../lib/utils/density-config';
import type { Resource, ResourceRead } from '../../../lib/api/types';
import type { Density } from '../../ui/DensityToggle';

interface ResourceGridProps {
  resources: (Resource | ResourceRead)[];
  onResourceClick?: (resource: Resource | ResourceRead) => void;
  /** Whether batch mode is active */
  batchMode?: boolean;
  /** Set of selected resource IDs */
  selectedIds?: Set<string>;
  /** Callback when selection changes */
  onToggleSelection?: (id: string, index?: number) => void;
  /** View density setting */
  density?: Density;
}

/**
 * Grid layout for displaying resources
 */
export const ResourceGrid: React.FC<ResourceGridProps> = ({
  resources,
  onResourceClick,
  batchMode = false,
  selectedIds = new Set(),
  onToggleSelection,
  density = 'comfortable',
}) => {
  const config = getDensityConfig(density);

  if (resources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          No resources found
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Start by adding your first resource
        </p>
      </div>
    );
  }

  return (
    <motion.div
      layout
      className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 ${config.gap}`}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      {resources.map((resource, index) => (
        <motion.div key={resource.id} layout transition={{ duration: 0.3, ease: 'easeOut' }}>
          <ResourceCard
            resource={resource}
            onClick={onResourceClick}
            batchMode={batchMode}
            isSelected={selectedIds.has(resource.id)}
            onToggleSelection={(id) => onToggleSelection?.(id, index)}
            padding={config.cardPadding}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};
