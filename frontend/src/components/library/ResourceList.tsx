// Neo Alexandria 2.0 Frontend - Resource List Component
// Compact list layout for displaying resources

import React from 'react';
import { motion } from 'framer-motion';
import { ResourceCard } from '@/components/resources/ResourceCard';
import type { Resource } from '@/types/api';

interface ResourceListProps {
  resources: Resource[];
  selectedResources: string[];
  isLoading?: boolean;
}

export const ResourceList: React.FC<ResourceListProps> = ({
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
        staggerChildren: 0.03,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-3"
    >
      {resources.map((resource) => (
        <motion.div
          key={resource.id}
          variants={itemVariants}
          layout
        >
          <ResourceCard
            resource={resource}
            viewMode="list"
            selected={selectedResources.includes(resource.id)}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};
