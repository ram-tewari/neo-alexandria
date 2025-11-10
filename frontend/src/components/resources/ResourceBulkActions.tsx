// Neo Alexandria 2.0 Frontend - ResourceBulkActions Component
// Bulk actions for selected resources

import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Trash2, FolderPlus, Tag, Download } from 'lucide-react';

interface ResourceBulkActionsProps {
  selectedCount: number;
  onClearSelection?: () => void;
}

const ResourceBulkActions: React.FC<ResourceBulkActionsProps> = ({
  selectedCount,
  onClearSelection,
}) => {
  return (
    <Card variant="glass">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-charcoal-grey-300">
              {selectedCount} resource{selectedCount === 1 ? '' : 's'} selected
            </span>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <FolderPlus className="w-4 h-4 mr-2" />
                Add to Collection
              </Button>
              <Button variant="outline" size="sm">
                <Tag className="w-4 h-4 mr-2" />
                Add Tags
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
          {onClearSelection && (
            <Button variant="ghost" size="sm" onClick={onClearSelection}>
              Clear Selection
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export { ResourceBulkActions };
