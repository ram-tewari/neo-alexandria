/**
 * BatchOperations Component
 * 
 * Provides bulk actions for selected documents in the library.
 * Displays a floating action bar when documents are selected.
 * 
 * Features:
 * - Add selected documents to collections
 * - Remove selected documents from collections
 * - Delete selected documents
 * - Undo last operation (except delete)
 * - Selection count badge
 * - Loading states during operations
 * - Confirmation dialogs for destructive actions
 * 
 * @example
 * ```tsx
 * <BatchOperations 
 *   onDelete={(ids) => console.log('Delete', ids)}
 * />
 * ```
 */

import { useState } from 'react';
import { FolderPlus, FolderMinus, Trash2, X, Undo2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCollectionsStore, selectSelectedCount, selectSelectedResourceIdsArray } from '@/stores/collections';
import { useCollections } from '@/lib/hooks/useCollections';
import { CollectionPicker } from './CollectionPicker';
import { useToast } from '@/hooks/use-toast';

/**
 * Props for the BatchOperations component
 */
interface BatchOperationsProps {
  /** Callback when documents are deleted */
  onDelete?: (resourceIds: string[]) => void;
  /** Optional CSS class name for styling */
  className?: string;
}
export function BatchOperations({
  onDelete,
  className = '',
}: BatchOperationsProps) {
  const selectedCount = useCollectionsStore(selectSelectedCount);
  const selectedIds = useCollectionsStore(selectSelectedResourceIdsArray);
  const { clearSelection, disableBatchMode } = useCollectionsStore();
  const { batchAddResources, batchRemoveResources, isBatchAdding, isBatchRemoving } = useCollections();
  const { toast } = useToast();

  const [showAddPicker, setShowAddPicker] = useState(false);
  const [showRemovePicker, setShowRemovePicker] = useState(false);
  const [lastOperation, setLastOperation] = useState<{
    type: 'add' | 'remove' | 'delete';
    collectionId?: string;
    resourceIds: string[];
  } | null>(null);

  const handleAddToCollections = (collectionIds: string[]) => {
    if (selectedIds.length === 0) return;

    // Add to each selected collection
    collectionIds.forEach((collectionId) => {
      batchAddResources(
        { collectionId, resourceIds: selectedIds },
        {
          onSuccess: () => {
            toast({
              title: 'Success',
              description: `Added ${selectedIds.length} documents to collection`,
            });
            setLastOperation({
              type: 'add',
              collectionId,
              resourceIds: [...selectedIds],
            });
            clearSelection();
          },
          onError: () => {
            toast({
              title: 'Error',
              description: 'Failed to add documents to collection',
              variant: 'destructive',
            });
          },
        }
      );
    });
  };

  const handleRemoveFromCollections = (collectionIds: string[]) => {
    if (selectedIds.length === 0) return;

    // Remove from each selected collection
    collectionIds.forEach((collectionId) => {
      batchRemoveResources(
        { collectionId, resourceIds: selectedIds },
        {
          onSuccess: () => {
            toast({
              title: 'Success',
              description: `Removed ${selectedIds.length} documents from collection`,
            });
            setLastOperation({
              type: 'remove',
              collectionId,
              resourceIds: [...selectedIds],
            });
            clearSelection();
          },
          onError: () => {
            toast({
              title: 'Error',
              description: 'Failed to remove documents from collection',
              variant: 'destructive',
            });
          },
        }
      );
    });
  };

  const handleDelete = () => {
    if (selectedIds.length === 0) return;

    if (confirm(`Are you sure you want to delete ${selectedIds.length} documents? This cannot be undone.`)) {
      setLastOperation({
        type: 'delete',
        resourceIds: [...selectedIds],
      });
      onDelete?.(selectedIds);
      clearSelection();
    }
  };

  const handleUndo = () => {
    if (!lastOperation) return;

    switch (lastOperation.type) {
      case 'add':
        if (lastOperation.collectionId) {
          batchRemoveResources({
            collectionId: lastOperation.collectionId,
            resourceIds: lastOperation.resourceIds,
          });
        }
        break;
      case 'remove':
        if (lastOperation.collectionId) {
          batchAddResources({
            collectionId: lastOperation.collectionId,
            resourceIds: lastOperation.resourceIds,
          });
        }
        break;
      // Delete cannot be undone
    }

    setLastOperation(null);
    toast({
      title: 'Undone',
      description: 'Operation has been reversed',
    });
  };

  const handleCancel = () => {
    clearSelection();
    disableBatchMode();
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <>
      <div className={`batch-operations fixed bottom-4 left-1/2 -translate-x-1/2 z-50 ${className}`}>
        <div className="bg-background border rounded-lg shadow-lg p-4 min-w-[400px]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{selectedCount} selected</Badge>
              {lastOperation && lastOperation.type !== 'delete' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleUndo}
                  className="h-7"
                >
                  <Undo2 className="h-3 w-3 mr-1" />
                  Undo
                </Button>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="h-7"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAddPicker(true)}
              disabled={isBatchAdding}
            >
              <FolderPlus className="h-4 w-4 mr-1" />
              Add to Collection
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRemovePicker(true)}
              disabled={isBatchRemoving}
            >
              <FolderMinus className="h-4 w-4 mr-1" />
              Remove from Collection
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </Button>
          </div>

          {(isBatchAdding || isBatchRemoving) && (
            <Alert className="mt-3">
              <AlertDescription>
                {isBatchAdding ? 'Adding documents...' : 'Removing documents...'}
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Collection Pickers */}
      <CollectionPicker
        open={showAddPicker}
        onOpenChange={setShowAddPicker}
        onSelect={handleAddToCollections}
        title="Add to Collections"
      />
      <CollectionPicker
        open={showRemovePicker}
        onOpenChange={setShowRemovePicker}
        onSelect={handleRemoveFromCollections}
        title="Remove from Collections"
      />
    </>
  );
}
