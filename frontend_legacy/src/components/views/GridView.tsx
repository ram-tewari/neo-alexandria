/**
 * Grid View Component
 * 
 * Displays resources in a responsive grid layout (2-6 columns)
 */

import { motion } from 'framer-motion';
import { ResourceCard } from '../cards/ResourceCard';
import type { Resource } from '@/types/resource';
import './GridView.css';

interface GridViewProps {
  resources: Resource[];
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const GridView = ({
  resources,
  onRead,
  onArchive,
  onAnnotate,
  onShare,
}: GridViewProps) => {
  return (
    <div className="grid-view">
      {resources.map((resource, index) => (
        <motion.div
          key={resource.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05, duration: 0.3 }}
        >
          <ResourceCard
            resource={resource}
            viewMode="grid"
            delay={index * 0.05}
            onRead={onRead}
            onArchive={onArchive}
            onAnnotate={onAnnotate}
            onShare={onShare}
          />
        </motion.div>
      ))}
    </div>
  );
};
