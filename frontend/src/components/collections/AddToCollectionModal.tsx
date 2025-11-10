// Neo Alexandria 2.0 Frontend - Add to Collection Modal
// Modal for adding resources to one or more collections

import React, { useState, useMemo } from 'react';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useCollections, useAddResourcesToCollection } from '@/hooks/useCollections';
import { useAppStore } from '@/store';
import { toast } from '@/store/toastStore';
import { FolderPlus, Search, Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { Collection } from '@/services/api/collections';

interface AddToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  resourceIds: string[];
}

const AddToCollectionModal: React.FC<AddToCollectionModalProps> = ({
  isOpen,
  onClose,
  resourceIds,
}) => {
  const userId = useAppStore((state) => state.userId) || 'demo-user';
  
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCollectionIds, setSelectedCollectionIds] = useState<Set<string>>(new Set());

  // Fetch collections
  const { data: collectionsData, isLoading } = useCollections({ user_id: userId });
  const collections = collectionsData?.items || [];

  // Add resources mutation
  const addResourcesMutation = useAddResourcesToCollection();

  // Filter collections by search query
  const filteredCollections = useMemo(() => {
    if (!searchQuery.trim()) {
      return collections;
    }

    const query = searchQuery.toLowerCase();
    return collections.filter(
      (collection) =>
        collection.name.toLowerCase().includes(query) ||
        collection.description?.toLowerCase().includes(query)
    );
  }, [collections, searchQuery]);

  // Toggle collection selection
  const toggleCollection = (collectionId: string) => {
    setSelectedCollectionIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(collectionId)) {
        newSet.delete(collectionId);
      } else {
        newSet.add(collectionId);
      }
      return newSet;
    });
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (selectedCollectionIds.size === 0) {
      toast.warning('No collections selected', 'Please select at least one collection');
      return;
    }

    try {
      // Add resources to each selected collection
      const promises = Array.from(selectedCollectionIds).map((collectionId) =>
        addResourcesMutation.mutateAsync({
          collectionId,
          resourceIds,
          userId,
        })
      );

      await Promise.all(promises);

      const resourceCount = resourceIds.length;
      const collectionCount = selectedCollectionIds.size;
      
      toast.success(
        'Resources added',
        `${resourceCount} resource${resourceCount === 1 ? '' : 's'} added to ${collectionCount} collection${collectionCount === 1 ? '' : 's'}`
      );

      handleClose();
    } catch (error: any) {
      toast.error('Failed to add resources', error?.response?.data?.detail || error.message);
    }
  };

  // Handle modal close
  const handleClose = () => {
    setSearchQuery('');
    setSelectedCollectionIds(new Set());
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Add to Collection"
      description={`Add ${resourceIds.length} resource${resourceIds.length === 1 ? '' : 's'} to collections`}
      size="md"
    >
      <div className="space-y-4">
        {/* Search */}
        <Input
          placeholder="Search collections..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
        />

        {/* Collections List */}
        <div className="max-h-96 overflow-y-auto space-y-2">
          {isLoading ? (
            <div className="text-center py-8 text-charcoal-grey-400">
              Loading collections...
            </div>
          ) : filteredCollections.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-charcoal-grey-400">
                {searchQuery ? 'No collections found' : 'No collections available'}
              </p>
              {!searchQuery && (
                <p className="text-sm text-charcoal-grey-500 mt-2">
                  Create a collection first to organize your resources
                </p>
              )}
            </div>
          ) : (
            filteredCollections.map((collection) => {
              const isSelected = selectedCollectionIds.has(collection.id);
              
              return (
                <button
                  key={collection.id}
                  type="button"
                  onClick={() => toggleCollection(collection.id)}
                  className={cn(
                    'w-full flex items-start p-3 rounded-lg border-2 transition-all duration-200',
                    'hover:border-accent-blue-500/50',
                    isSelected
                      ? 'border-accent-blue-500 bg-accent-blue-500/10'
                      : 'border-charcoal-grey-700 bg-charcoal-grey-900'
                  )}
                >
                  <div className="flex-1 text-left min-w-0">
                    <div className="text-sm font-medium text-charcoal-grey-50 truncate">
                      {collection.name}
                    </div>
                    {collection.description && (
                      <div className="text-xs text-charcoal-grey-400 mt-0.5 line-clamp-1">
                        {collection.description}
                      </div>
                    )}
                    <div className="text-xs text-charcoal-grey-500 mt-1">
                      {collection.resource_count} {collection.resource_count === 1 ? 'resource' : 'resources'}
                    </div>
                  </div>
                  
                  {isSelected && (
                    <div className="flex-shrink-0 ml-3">
                      <div className="w-5 h-5 rounded-full bg-accent-blue-500 flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    </div>
                  )}
                </button>
              );
            })
          )}
        </div>

        {/* Selection Summary */}
        {selectedCollectionIds.size > 0 && (
          <div className="bg-accent-blue-500/10 border border-accent-blue-500/30 rounded-lg p-3">
            <p className="text-sm text-accent-blue-300">
              {selectedCollectionIds.size} collection{selectedCollectionIds.size === 1 ? '' : 's'} selected
            </p>
          </div>
        )}
      </div>

      <ModalFooter className="mt-6">
        <Button
          type="button"
          variant="ghost"
          onClick={handleClose}
          disabled={addResourcesMutation.isPending}
        >
          Cancel
        </Button>
        <Button
          type="button"
          variant="primary"
          onClick={handleSubmit}
          loading={addResourcesMutation.isPending}
          disabled={selectedCollectionIds.size === 0}
          icon={<FolderPlus className="w-4 h-4" />}
        >
          Add to {selectedCollectionIds.size > 0 ? selectedCollectionIds.size : ''} Collection{selectedCollectionIds.size === 1 ? '' : 's'}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

export { AddToCollectionModal };
export type { AddToCollectionModalProps };
