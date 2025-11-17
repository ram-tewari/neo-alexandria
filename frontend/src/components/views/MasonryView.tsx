/**
 * Masonry View Component
 * 
 * Variable height cards in a waterfall layout (2-4 columns)
 */

import { motion } from 'framer-motion';
import { ResourceCard } from '../cards/ResourceCard';
import type { Resource } from '@/types/resource';
import './MasonryView.css';

interface MasonryViewProps {
  resources: Resource[];
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const MasonryView = ({
  resources,
  onRead,
  onArchive,
  onAnnotate,
  onShare,
}: MasonryViewProps) => {
  return (
    <div className="masonry-view">
      {resources.map((resource, index) => (
        <motion.div
          key={resource.id}
          className="masonry-item"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
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
