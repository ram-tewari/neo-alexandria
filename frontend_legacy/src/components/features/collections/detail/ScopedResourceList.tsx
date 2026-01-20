import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Trash2, Plus } from 'lucide-react';
import { collectionsApi } from '../../../../lib/api/collections';
import { Button } from '../../../ui/Button/Button';
import { useToast } from '../../../../contexts/ToastContext';
import type { ResourceSummary, Resource } from '../../../../types/resource';
import { ResourceCard } from '../../../cards/ResourceCard';

// Helper to convert summary to resource for card display
const summaryToResource = (summary: ResourceSummary): Resource => ({
    ...summary,
    // Provide defaults for required fields missing in summary
    description: summary.description || null,
    creator: summary.creator || null,
    type: summary.type || 'article',
    subject: summary.subject || [],
    read_status: summary.read_status || 'unread',
    // Mock/Default values for fields not in summary but required by Resource type
    publisher: null,
    contributor: null,
    date_created: null,
    date_modified: null,
    format: null,
    identifier: null,
    source: null,
    language: null,
    coverage: null,
    rights: null,
    relation: [],
    url: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ingestion_status: 'completed',
    ingestion_error: null,
    ingestion_started_at: null,
    ingestion_completed_at: null,
    quality_score: summary.quality_score || 0,
    classification_code: summary.classification_code || null,
} as Resource);

interface ScopedResourceListProps {
    collectionId: string;
    resources: ResourceSummary[];
    onAddClick: () => void;
}

export const ScopedResourceList: React.FC<ScopedResourceListProps> = ({
    collectionId,
    resources,
    onAddClick
}) => {
    const queryClient = useQueryClient();
    const { showToast } = useToast();

    const removeMutation = useMutation({
        mutationFn: (resourceIds: string[]) => collectionsApi.removeResources(collectionId, resourceIds),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', collectionId] });
            showToast({ message: 'Resources removed from collection', variant: 'success' });
        },
        onError: () => {
            showToast({ message: 'Failed to remove resources', variant: 'error' });
        }
    });

    const handleRemove = (id: string) => {
        if (window.confirm('Remove this resource from the collection?')) {
            removeMutation.mutate([id]);
        }
    };

    if (resources.length === 0) {
        return (
            <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg border-2 border-dashed border-gray-200 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400 mb-4">No resources in this collection yet.</p>
                <Button onClick={onAddClick}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Resources
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Resources ({resources.length})
                </h3>
                <Button onClick={onAddClick} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Resources
                </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {resources.map(resource => (
                    <div key={resource.id} className="relative group">
                        <ResourceCard
                            resource={summaryToResource(resource)}
                            viewMode="grid"
                        />
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                            <Button
                                variant="danger"
                                size="sm"
                                className="h-8 w-8 p-0 rounded-full shadow-md flex items-center justify-center bg-red-500 hover:bg-red-600 text-white"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemove(resource.id);
                                }}
                                title="Remove from collection"
                            >
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
