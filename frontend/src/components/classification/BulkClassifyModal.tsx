// Neo Alexandria 2.0 Frontend - Bulk Classify Modal Component
// Modal for bulk classification assignment with tree selector

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { useClassificationTree, useBatchUpdate } from '@/hooks/useApi';
import { useAppStore } from '@/store';
import { FolderTree, Check } from 'lucide-react';
import { cn } from '@/utils/cn';

interface BulkClassifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  resourceIds: string[];
  onSuccess?: () => void;
}

const BulkClassifyModal: React.FC<BulkClassifyModalProps> = ({
  isOpen,
  onClose,
  resourceIds,
  onSuccess,
}) => {
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const { data, isLoading } = useClassificationTree();
  const batchUpdate = useBatchUpdate();
  const clearSelection = useAppStore(state => state.clearSelection);

  const handleSubmit = async () => {
    if (!selectedCode) return;

    try {
      await batchUpdate.mutateAsync({
        resource_ids: resourceIds,
        updates: {
          classification_code: selectedCode,
        },
      });

      // Clear selection and close modal
      clearSelection();
      onClose();
      
      // Notify parent of success
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to bulk classify resources:', error);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Bulk Classify Resources"
      description={`Select a classification for ${resourceIds.length} resource${resourceIds.length !== 1 ? 's' : ''}`}
      size="lg"
    >
      <div className="space-y-4">
        {/* Classification Tree Selector */}
        <div className="border border-charcoal-grey-700 rounded-lg p-4 max-h-96 overflow-y-auto bg-charcoal-grey-900">
          {isLoading ? (
            <LoadingSkeleton lines={8} />
          ) : data?.tree && data.tree.length > 0 ? (
            <div className="space-y-1">
              {data.tree.map((node) => (
                <ClassificationTreeSelector
                  key={node.code}
                  node={node}
                  selectedCode={selectedCode}
                  onSelect={setSelectedCode}
                  level={0}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-charcoal-grey-400">
              <FolderTree className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No classifications available</p>
            </div>
          )}
        </div>

        {/* Selected Classification Display */}
        {selectedCode && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 p-3 bg-accent-blue-500/10 border border-accent-blue-500/30 rounded-lg"
          >
            <Check className="w-5 h-5 text-accent-blue-500" />
            <div>
              <p className="text-sm font-medium text-charcoal-grey-50">
                Selected Classification
              </p>
              <p className="text-sm text-charcoal-grey-300">
                {selectedCode}
              </p>
            </div>
          </motion.div>
        )}
      </div>

      <ModalFooter>
        <Button
          variant="ghost"
          onClick={onClose}
          disabled={batchUpdate.isPending}
        >
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={!selectedCode || batchUpdate.isPending}
          loading={batchUpdate.isPending}
        >
          Apply Classification
        </Button>
      </ModalFooter>
    </Modal>
  );
};

// Classification Tree Selector Component (simplified for selection only)
interface ClassificationTreeSelectorProps {
  node: {
    code: string;
    name: string;
    description: string;
    children: any[];
  };
  selectedCode: string | null;
  onSelect: (code: string) => void;
  level: number;
}

const ClassificationTreeSelector: React.FC<ClassificationTreeSelectorProps> = ({
  node,
  selectedCode,
  onSelect,
  level,
}) => {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedCode === node.code;

  return (
    <div>
      <button
        onClick={() => {
          onSelect(node.code);
          if (hasChildren) {
            setIsExpanded(!isExpanded);
          }
        }}
        className={cn(
          'w-full text-left px-3 py-2 rounded-md transition-colors duration-150',
          'flex items-center space-x-2 group',
          isSelected
            ? 'bg-accent-blue-500/20 text-accent-blue-400 ring-2 ring-accent-blue-500/50'
            : 'text-charcoal-grey-300 hover:bg-charcoal-grey-800 hover:text-charcoal-grey-50'
        )}
        style={{ paddingLeft: `${level * 1 + 0.75}rem` }}
      >
        {hasChildren && (
          <span className="text-charcoal-grey-500 group-hover:text-charcoal-grey-400 flex-shrink-0">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        <span className="flex-1 text-sm font-medium truncate" title={`${node.code} - ${node.name}`}>
          {node.code} - {node.name}
        </span>
        {isSelected && (
          <Check className="w-4 h-4 text-accent-blue-500 flex-shrink-0" />
        )}
      </button>

      {hasChildren && isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
        >
          {node.children.map((child) => (
            <ClassificationTreeSelector
              key={child.code}
              node={child}
              selectedCode={selectedCode}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
};

export { BulkClassifyModal };
