import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { collectionsApi } from '../../../../lib/api/collections';
import { LoadingSpinner } from '../../../common/LoadingSpinner';
import { CollectionHeader } from './CollectionHeader';
import { CollectionStatsDashboard } from './CollectionStats';
import { ScopedResourceList } from './ScopedResourceList';
import { AddResourceOverlay } from './AddResourceOverlay';
import { pageTransition } from '../../../../lib/utils/animations';

export const CollectionDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [isAddOverlayOpen, setIsAddOverlayOpen] = useState(false);

    const { data: collection, isLoading, error } = useQuery({
        queryKey: ['collection', id],
        queryFn: () => collectionsApi.getCollection(id!),
        enabled: !!id
    });

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    if (error || !collection) {
        return (
            <div className="p-6 text-center text-red-500">
                Failed to load collection. Please try again.
            </div>
        );
    }

    // Mock stats for now since backend might not return them fully populated yet
    const stats = {
        resourceCount: collection.resource_count,
        avgQuality: 85, // Mock
        lastUpdated: collection.updated_at,
        topTags: ['AI', 'Research', 'Design'] // Mock
    };

    return (
        <motion.div
            className="p-6 max-w-7xl mx-auto space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            <CollectionHeader collection={collection} />

            <CollectionStatsDashboard stats={stats} />

            <div className="space-y-4">
                <ScopedResourceList
                    collectionId={collection.id}
                    resources={collection.resources || []}
                    onAddClick={() => setIsAddOverlayOpen(true)}
                />
            </div>

            <AddResourceOverlay
                isOpen={isAddOverlayOpen}
                onClose={() => setIsAddOverlayOpen(false)}
                collectionId={collection.id}
                existingResourceIds={collection.resources?.map(r => r.id) || []}
            />
        </motion.div>
    );
};
