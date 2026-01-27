/**
 * CollectionPicker Component
 * 
 * Dialog for selecting one or more collections.
 * Supports inline collection creation without leaving the dialog.
 * 
 * Features:
 * - Search collections by name
 * - Multi-select or single-select mode
 * - Inline collection creation
 * - Visual selection indicators
 * - Keyboard navigation (Enter to confirm, Escape to cancel)
 * - Loading states
 * - Empty state handling
 * 
 * @example
 * ```tsx
 * <CollectionPicker 
 *   open={isOpen}
 *   onOpenChange={setIsOpen}
 *   onSelect={(ids) => console.log('Selected:', ids)}
 *   multiSelect={true}
 * />
 * ```
 */

import { useState } from 'react';
import { Check, Plus, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Skeleton } from '@/components/loading/Skeleton';
import { useCollections } from '@/lib/hooks/useCollections';
import type { Collection } from '@/types/library';

/**
 * Props for the CollectionPicker component
 */
interface CollectionPickerProps {
  /** Whether the dialog is open */
  open: boolean;
  /** Callback when dialog open state changes */
  onOpenChange: (open: boolean) => void;
  /** Callback when collections are selected */
  onSelect: (collectionIds: string[]) => void;
  /** Pre-selected collection IDs */
  selectedIds?: string[];
  /** Allow selecting multiple collections */
  multiSelect?: boolean;
  /** Dialog title */
  title?: string;
  /** Optional CSS class name for styling */
  className?: string;
}
export function CollectionPicker({
  open,
  onOpenChange,
  onSelect,
  selectedIds = [],
  multiSelect = true,
  title = 'Select Collections',
  className = '',
}: CollectionPickerProps) {
  const { collections, isLoading, createCollection, isCreating } = useCollections();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedIds));
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');

  const filteredCollections = collections.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const toggleSelection = (collectionId: string) => {
    const newSelection = new Set(selected);
    if (newSelection.has(collectionId)) {
      newSelection.delete(collectionId);
    } else {
      if (!multiSelect) {
        newSelection.clear();
      }
      newSelection.add(collectionId);
    }
    setSelected(newSelection);
  };

  const handleSave = () => {
    onSelect(Array.from(selected));
    onOpenChange(false);
  };

  const handleCreateInline = () => {
    if (!newCollectionName.trim()) return;

    createCollection(
      { name: newCollectionName, is_public: false },
      {
        onSuccess: (data) => {
          setNewCollectionName('');
          setShowCreateForm(false);
          // Auto-select the newly created collection
          const newSelection = new Set(selected);
          newSelection.add(data.id);
          setSelected(newSelection);
        },
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !multiSelect && selected.size === 1) {
      handleSave();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={`max-w-md ${className}`}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search collections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="pl-9"
          />
        </div>

        {/* Collection List */}
        <ScrollArea className="h-64 border rounded-md">
          {isLoading ? (
            <div className="p-4 space-y-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredCollections.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <p>No collections found</p>
              {searchQuery && (
                <p className="text-sm mt-1">Try a different search term</p>
              )}
            </div>
          ) : (
            <div className="p-2">
              {filteredCollections.map((collection) => (
                <div
                  key={collection.id}
                  className={`flex items-center gap-3 p-3 rounded-md cursor-pointer hover:bg-accent transition-colors ${
                    selected.has(collection.id) ? 'bg-accent' : ''
                  }`}
                  onClick={() => toggleSelection(collection.id)}
                >
                  <div
                    className={`flex items-center justify-center w-5 h-5 border-2 rounded ${
                      selected.has(collection.id)
                        ? 'bg-primary border-primary'
                        : 'border-muted-foreground'
                    }`}
                  >
                    {selected.has(collection.id) && (
                      <Check className="h-3 w-3 text-primary-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{collection.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {collection.resource_count} {collection.resource_count === 1 ? 'document' : 'documents'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* Inline Create Form */}
        {showCreateForm ? (
          <div className="space-y-2 p-3 border rounded-md bg-muted/50">
            <Label htmlFor="new-collection-name">New Collection Name</Label>
            <div className="flex gap-2">
              <Input
                id="new-collection-name"
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
                placeholder="Enter name..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleCreateInline();
                  if (e.key === 'Escape') setShowCreateForm(false);
                }}
                autoFocus
              />
              <Button
                size="sm"
                onClick={handleCreateInline}
                disabled={!newCollectionName.trim() || isCreating}
              >
                {isCreating ? 'Creating...' : 'Create'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false);
                  setNewCollectionName('');
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCreateForm(true)}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-1" />
            Create New Collection
          </Button>
        )}

        {/* Footer */}
        <DialogFooter>
          <div className="flex items-center justify-between w-full">
            <span className="text-sm text-muted-foreground">
              {selected.size} selected
            </span>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={selected.size === 0}>
                {multiSelect ? 'Add to Collections' : 'Select'}
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
