/**
 * List View Component
 * 
 * Displays resources in a single-column list with full metadata
 */

import { motion } from 'framer-motion';
import { ResourceCard } from '../cards/ResourceCard';
import type { Resource } from '@/types/resource';
import './ListView.css';

interface ListViewProps {
  resources: Resource[];
  onRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onAnnotate?: (id: string) => void;
  onShare?: (id: string) => void;
}

export const ListView = ({
  resources,
  onRead,
  onArchive,
  onAnnotate,
  onShare,
}: ListViewProps) => {
  return (
    <div className="list-view">
      {resources.map((resource, index) => (
        <motion.div
          key={resource.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.03, duration: 0.3 }}
        >
          <ResourceCard
            resource={resource}
            viewMode="list"
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
