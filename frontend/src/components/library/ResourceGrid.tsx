// Neo Alexandria 2.0 Frontend - Resource Grid Component
// Grid layout for displaying resources with responsive columns

import React from 'react';
import { motion } from 'framer-motion';
import { ResourceCard } from '@/components/resources/ResourceCard';
import type { Resource } from '@/types/api';

interface ResourceGridProps {
  resources: Resource[];
  selectedResources: string[];
  isLoading?: boolean;
}

export const ResourceGrid: React.FC<ResourceGridProps> = ({
  resources,
  selectedResources,
  isLoading = false,
}) => {
  // Animation variants for stagger effect
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {resources.map((resource) => (
        <motion.div
          key={resource.id}
          variants={itemVariants}
          layout
          className="h-full"
        >
          <ResourceCard
            resource={resource}
            viewMode="grid"
            selected={selectedResources.includes(resource.id)}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};
