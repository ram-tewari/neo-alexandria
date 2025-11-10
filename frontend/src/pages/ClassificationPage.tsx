// Neo Alexandria 2.0 Frontend - Classification Page
// Browse and navigate classification hierarchy

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useClassificationTree, useResources } from '@/hooks/useApi';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner, LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { ResourceListByClassification } from '@/components/classification/ResourceListByClassification';
import { BulkClassifyModal } from '@/components/classification/BulkClassifyModal';
import { useAppStore } from '@/store';
import { FolderTree, AlertCircle, Tag } from 'lucide-react';
import { cn } from '@/utils/cn';

const ClassificationPage: React.FC = () => {
  const [selectedClassification, setSelectedClassification] = useState<string | null>(null);
  const [resourceCounts, setResourceCounts] = useState<Record<string, number>>({});
  const [isBulkClassifyModalOpen, setIsBulkClassifyModalOpen] = useState(false);
  
  // Get selected resources from store
  const selectedResources = useAppStore(state => state.selectedResources);
  const clearSelection = useAppStore(state => state.clearSelection);
  
  // Fetch classification tree from API
  const { data, isLoading, error } = useClassificationTree();
  
  // Fetch all resources to calculate counts per classification
  const { data: resourcesData, refetch: refetchResources } = useResources({ limit: 1000 });
  
  // Calculate resource counts per classification code
  React.useEffect(() => {
    if (resourcesData?.items) {
      const counts: Record<string, number> = {};
      resourcesData.items.forEach((resource) => {
        if (resource.classification_code) {
          counts[resource.classification_code] = (counts[resource.classification_code] || 0) + 1;
        }
      });
      setResourceCounts(counts);
    }
  }, [resourcesData]);
  
  const handleBulkClassifySuccess = () => {
    // Refetch resources to update counts
    refetchResources();
  };

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-charcoal-grey-900">
        <div className="container mx-auto px-4 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card variant="glass">
              <CardContent className="text-center py-12">
                <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
                <h3 className="text-xl font-medium text-charcoal-grey-50 mb-2">
                  Error Loading Classification Tree
                </h3>
                <p className="text-charcoal-grey-400">
                  {error instanceof Error ? error.message : 'An unexpected error occurred'}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-charcoal-grey-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-3">
              <FolderTree className="w-8 h-8 text-accent-blue-500" />
              <h1 className="text-3xl font-bold text-charcoal-grey-50">
                Classification Browser
              </h1>
            </div>
            
            {/* Bulk Classify Button */}
            {selectedResources.length > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <Button
                  variant="primary"
                  onClick={() => setIsBulkClassifyModalOpen(true)}
                  icon={<Tag />}
                >
                  Classify {selectedResources.length} Resource{selectedResources.length !== 1 ? 's' : ''}
                </Button>
              </motion.div>
            )}
          </div>
          <p className="text-charcoal-grey-400">
            Browse and explore the classification hierarchy
          </p>
        </motion.div>

        {/* Main Content Area with Sidebar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex gap-6"
        >
          {/* Tree Sidebar */}
          <div className="w-80 flex-shrink-0">
            <Card variant="glass" className="sticky top-24">
              <CardHeader>
                <h2 className="text-lg font-semibold text-charcoal-grey-50">
                  Classification Tree
                </h2>
              </CardHeader>
              <CardContent className="max-h-[calc(100vh-12rem)] overflow-y-auto">
                {isLoading ? (
                  <div className="space-y-4">
                    <LoadingSkeleton lines={8} />
                  </div>
                ) : data?.tree && data.tree.length > 0 ? (
                  <div className="space-y-1">
                    {data.tree.map((node) => (
                      <ClassificationTreeNode
                        key={node.code}
                        node={node}
                        selectedCode={selectedClassification}
                        onSelect={setSelectedClassification}
                        level={0}
                        resourceCounts={resourceCounts}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-charcoal-grey-400">
                    <FolderTree className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No classifications available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Content Area */}
          <div className="flex-1 min-w-0">
            <Card variant="glass">
              <CardContent className="min-h-[60vh]">
                {isLoading ? (
                  <div className="flex items-center justify-center py-20">
                    <LoadingSpinner size="lg" text="Loading classification data..." />
                  </div>
                ) : selectedClassification ? (
                  <div className="py-6">
                    <h3 className="text-xl font-medium text-charcoal-grey-50 mb-6">
                      Classification: {selectedClassification}
                    </h3>
                    <ResourceListByClassification 
                      classificationCode={selectedClassification}
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-20 text-center">
                    <FolderTree className="w-16 h-16 text-charcoal-grey-600 mb-4" />
                    <h3 className="text-lg font-medium text-charcoal-grey-300 mb-2">
                      Select a Classification
                    </h3>
                    <p className="text-charcoal-grey-500 max-w-md">
                      Choose a classification from the tree on the left to view related resources
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>

      {/* Bulk Classify Modal */}
      <BulkClassifyModal
        isOpen={isBulkClassifyModalOpen}
        onClose={() => setIsBulkClassifyModalOpen(false)}
        resourceIds={selectedResources}
        onSuccess={handleBulkClassifySuccess}
      />
    </div>
  );
};

// Classification Tree Node Component
interface ClassificationTreeNodeProps {
  node: {
    code: string;
    name: string;
    description: string;
    children: any[];
  };
  selectedCode: string | null;
  onSelect: (code: string) => void;
  level: number;
  resourceCounts: Record<string, number>;
}

const ClassificationTreeNode: React.FC<ClassificationTreeNodeProps> = ({
  node,
  selectedCode,
  onSelect,
  level,
  resourceCounts,
}) => {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedCode === node.code;
  const resourceCount = resourceCounts[node.code] || 0;

  return (
    <div>
      <button
        onClick={() => {
          if (hasChildren) {
            setIsExpanded(!isExpanded);
          }
          onSelect(node.code);
        }}
        className={cn(
          'w-full text-left px-3 py-2 rounded-md transition-colors duration-150',
          'flex items-center justify-between group',
          isSelected
            ? 'bg-accent-blue-500/20 text-accent-blue-400'
            : 'text-charcoal-grey-300 hover:bg-charcoal-grey-700/50 hover:text-charcoal-grey-50'
        )}
        style={{ paddingLeft: `${level * 1 + 0.75}rem` }}
      >
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          {hasChildren && (
            <span className="text-charcoal-grey-500 group-hover:text-charcoal-grey-400 flex-shrink-0">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          <span className="text-sm font-medium truncate" title={`${node.code} - ${node.name}`}>
            {node.code} - {node.name}
          </span>
        </div>
        {resourceCount > 0 && (
          <span className={cn(
            'ml-2 px-2 py-0.5 text-xs rounded-full flex-shrink-0',
            isSelected 
              ? 'bg-accent-blue-500 text-white'
              : 'bg-charcoal-grey-700 text-charcoal-grey-300'
          )}>
            {resourceCount}
          </span>
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
            <ClassificationTreeNode
              key={child.code}
              node={child}
              selectedCode={selectedCode}
              onSelect={onSelect}
              level={level + 1}
              resourceCounts={resourceCounts}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
};

export { ClassificationPage };
