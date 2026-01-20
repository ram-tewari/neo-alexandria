import React from 'react';
import { CollectionCard } from './CollectionCard';
import type { Collection } from '../../../../types/collection';
import { collectionsApi } from '../../../../lib/api/collections';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '../../../../contexts/ToastContext';

interface CollectionGridProps {
    collections: Collection[];
    viewMode: 'grid' | 'list';
}

export const CollectionGrid: React.FC<CollectionGridProps> = ({
    collections,
    viewMode
}) => {
    const queryClient = useQueryClient();
    const { showToast } = useToast();

    const handleRename = async (id: string) => {
        // TODO: Implement rename modal/inline edit
        console.log('Rename', id);
    };

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this collection? This action cannot be undone.')) {
            try {
                await collectionsApi.deleteCollection(id);
                queryClient.invalidateQueries({ queryKey: ['collections'] });
                showToast({ message: 'Collection deleted successfully', variant: 'success' });
            } catch (error) {
                showToast({ message: 'Failed to delete collection', variant: 'error' });
            }
        }
    };

    if (collections.length === 0) {
        return (
            <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg border-2 border-dashed border-gray-200 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400">No collections found. Create one to get started!</p>
            </div>
        );
    }

    return (
        <div className={
            viewMode === 'grid'
                ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                : "flex flex-col gap-3"
        }>
            {collections.map(collection => (
                <CollectionCard
                    key={collection.id}
                    collection={collection}
                    viewMode={viewMode}
                    onRename={handleRename}
                    onDelete={handleDelete}
                />
            ))}
        </div>
    );
};
