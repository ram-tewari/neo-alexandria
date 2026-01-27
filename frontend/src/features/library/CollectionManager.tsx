/**
 * CollectionManager Component
 * 
 * Provides complete CRUD operations for managing collections.
 * Displays a list of collections with statistics, tags, and action buttons.
 * 
 * Features:
 * - Create new collections with name, description, tags, and visibility
 * - Edit existing collections
 * - Delete collections with confirmation
 * - View collection statistics (document count)
 * - Public/private visibility indicators
 * - Tag display with overflow handling
 * - Loading and error states
 * - Optimistic updates via TanStack Query
 * 
 * @example
 * ```tsx
 * <CollectionManager 
 *   onCollectionSelect={(collection) => console.log(collection)}
 * />
 * ```
 */

import { useState } from 'react';
import { Plus, Edit, Trash2, FolderOpen, Lock, Unlock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Skeleton } from '@/components/loading/Skeleton';
import { useCollections } from '@/lib/hooks/useCollections';
import { useCollectionsStore } from '@/stores/collections';
import type { Collection, CollectionCreate, CollectionUpdate } from '@/types/library';

/**
 * Props for the CollectionManager component
 */
interface CollectionManagerProps {
  /** Callback when a collection is selected */
  onCollectionSelect?: (collection: Collection) => void;
  /** Optional CSS class name for styling */
  className?: string;
}
export function CollectionManager({
  onCollectionSelect,
  className = '',
}: CollectionManagerProps) {
  const {
    collections,
    isLoading,
    error,
    createCollection,
    updateCollection,
    deleteCollection,
    isCreating,
    isUpdating,
    isDeleting,
  } = useCollections();

  const { selectCollection } = useCollectionsStore();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedForEdit, setSelectedForEdit] = useState<Collection | null>(null);
  const [selectedForDelete, setSelectedForDelete] = useState<Collection | null>(null);

  const [formData, setFormData] = useState<CollectionCreate>({
    name: '',
    description: '',
    tags: [],
    is_public: false,
  });

  const handleCreate = () => {
    if (!formData.name.trim()) return;

    createCollection(formData, {
      onSuccess: () => {
        setIsCreateDialogOpen(false);
        setFormData({ name: '', description: '', tags: [], is_public: false });
      },
    });
  };

  const handleEdit = () => {
    if (!selectedForEdit || !formData.name.trim()) return;

    const updates: CollectionUpdate = {
      name: formData.name,
      description: formData.description,
      tags: formData.tags,
      is_public: formData.is_public,
    };

    updateCollection(
      { collectionId: selectedForEdit.id, updates },
      {
        onSuccess: () => {
          setIsEditDialogOpen(false);
          setSelectedForEdit(null);
          setFormData({ name: '', description: '', tags: [], is_public: false });
        },
      }
    );
  };

  const handleDelete = () => {
    if (!selectedForDelete) return;

    deleteCollection(selectedForDelete.id, {
      onSuccess: () => {
        setIsDeleteDialogOpen(false);
        setSelectedForDelete(null);
      },
    });
  };

  const openEditDialog = (collection: Collection) => {
    setSelectedForEdit(collection);
    setFormData({
      name: collection.name,
      description: collection.description || '',
      tags: collection.tags || [],
      is_public: collection.is_public,
    });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (collection: Collection) => {
    setSelectedForDelete(collection);
    setIsDeleteDialogOpen(true);
  };

  const handleCollectionClick = (collection: Collection) => {
    selectCollection(collection);
    onCollectionSelect?.(collection);
  };

  if (isLoading) {
    return (
      <div className={`collection-manager flex flex-col h-full ${className}`}>
        <div className="p-4 border-b">
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="p-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`collection-manager flex flex-col h-full ${className}`}>
        <div className="p-4">
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load collections. Please try again.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className={`collection-manager flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Collections</h3>
            <Badge variant="secondary">{collections.length}</Badge>
          </div>
          <Button
            size="sm"
            onClick={() => setIsCreateDialogOpen(true)}
            disabled={isCreating}
          >
            <Plus className="h-4 w-4 mr-1" />
            New
          </Button>
        </div>
      </div>

      {/* Collection List */}
      <ScrollArea className="flex-1">
        {collections.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <FolderOpen className="h-12 w-12 text-muted-foreground opacity-50 mb-2" />
            <p className="text-muted-foreground">No collections yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Create your first collection to organize documents
            </p>
          </div>
        ) : (
          <div className="p-4 space-y-2">
            {collections.map((collection) => (
              <div
                key={collection.id}
                className="p-3 border rounded-lg hover:bg-accent cursor-pointer transition-colors"
                onClick={() => handleCollectionClick(collection)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm truncate">
                        {collection.name}
                      </span>
                      {collection.is_public ? (
                        <Unlock className="h-3 w-3 text-muted-foreground" title="Public" />
                      ) : (
                        <Lock className="h-3 w-3 text-muted-foreground" title="Private" />
                      )}
                    </div>
                    {collection.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                        {collection.description}
                      </p>
                    )}
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-xs">
                        {collection.resource_count} {collection.resource_count === 1 ? 'document' : 'documents'}
                      </Badge>
                      {collection.tags && collection.tags.length > 0 && (
                        <>
                          {collection.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {collection.tags.length > 3 && (
                            <span className="text-xs text-muted-foreground">
                              +{collection.tags.length - 3} more
                            </span>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        openEditDialog(collection);
                      }}
                      disabled={isUpdating}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        openDeleteDialog(collection);
                      }}
                      disabled={isDeleting}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Create Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Collection</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="create-name">Name *</Label>
              <Input
                id="create-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My Collection"
              />
            </div>
            <div>
              <Label htmlFor="create-description">Description</Label>
              <Textarea
                id="create-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description"
                rows={3}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="create-public"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              />
              <Label htmlFor="create-public">Make public</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={!formData.name.trim() || isCreating}>
              {isCreating ? 'Creating...' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Collection</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Name *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit-public"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              />
              <Label htmlFor="edit-public">Make public</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={!formData.name.trim() || isUpdating}>
              {isUpdating ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Collection</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete "{selectedForDelete?.name}"? This action cannot be undone.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
