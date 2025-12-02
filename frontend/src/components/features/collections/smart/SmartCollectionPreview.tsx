import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertCircle, Loader2 } from 'lucide-react';
import { collectionsApi } from '../../../../lib/api/collections';
import { SmartCollectionDefinition } from '../../../../types/collection';
import { ResourceCard } from '../../../cards/ResourceCard';

interface SmartCollectionPreviewProps {
    definition: SmartCollectionDefinition;
}

export const SmartCollectionPreview: React.FC<SmartCollectionPreviewProps> = ({ definition }) => {
    // Debounce the definition to avoid too many API calls
    const [debouncedDefinition, setDebouncedDefinition] = React.useState(definition);

    React.useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedDefinition(definition);
        }, 500);
        return () => clearTimeout(timer);
    }, [definition]);

    const { data: resources, isLoading, error } = useQuery({
        queryKey: ['smartCollectionPreview', debouncedDefinition],
        queryFn: () => collectionsApi.previewSmartCollection(debouncedDefinition),
        enabled: debouncedDefinition.rules.length > 0,
        staleTime: 1000 * 60 // Cache for 1 minute
    });

    if (definition.rules.length === 0) {
        return null;
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-8 text-gray-500">
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Updating preview...
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center p-4 text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <AlertCircle className="w-5 h-5 mr-2" />
                Failed to load preview
            </div>
        );
    }

    if (!resources || resources.length === 0) {
        return (
            <div className="text-center p-8 text-gray-500 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                No resources match these rules.
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                    Preview ({resources.length} matches)
                </h3>
            </div>

            <div className="grid grid-cols-1 gap-3 max-h-[300px] overflow-y-auto pr-2">
                {resources.map((resource) => (
                    <ResourceCard
                        key={resource.id}
                        resource={resource}
                        viewMode="list"
                        compact
                    />
                ))}
            </div>
        </div>
    );
};
