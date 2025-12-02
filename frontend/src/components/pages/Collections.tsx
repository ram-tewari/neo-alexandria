import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Plus, Search, Filter, Grid, List as ListIcon } from 'lucide-react';
import { collectionsApi } from '../../lib/api/collections';
import { Card } from '../ui/Card/Card';
import { Button } from '../ui/Button/Button';
import { Input } from '../ui/Input/Input';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { CollectionGrid } from '../features/collections/list/CollectionGrid';
import { CreateCollectionModal } from '../features/collections/list/CreateCollectionModal';
import { pageTransition } from '../../lib/utils/animations';

export const Collections: React.FC = () => {
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    const { data: collections, isLoading, error } = useQuery({
        queryKey: ['collections'],
        queryFn: () => collectionsApi.getCollections()
    });

    const filteredCollections = collections?.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (error) {
        return (
            <div className="p-6 text-center text-red-500">
                Failed to load collections. Please try again.
            </div>
        );
    }

    return (
        <motion.div
            className="p-6 max-w-7xl mx-auto space-y-6"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Collections</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Organize your resources into curated lists and smart collections
                    </p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    New Collection
                </Button>
            </div>

            {/* Toolbar */}
            <Card className="flex flex-col md:flex-row gap-4 items-center justify-between sticky top-0 z-10">
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                        placeholder="Search collections..."
                        className="pl-10"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className="flex items-center gap-2 w-full md:w-auto">
                    <Button variant="ghost" size="sm">
                        <Filter className="w-4 h-4 mr-2" />
                        Filter
                    </Button>
                    <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-2" />
                    <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-2 rounded-md transition-colors ${viewMode === 'grid'
                                    ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600 dark:text-blue-400'
                                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
                                }`}
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-2 rounded-md transition-colors ${viewMode === 'list'
                                    ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600 dark:text-blue-400'
                                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
                                }`}
                        >
                            <ListIcon className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </Card>

            {/* Content */}
            {isLoading ? (
                <div className="flex justify-center py-12">
                    <LoadingSpinner size="lg" />
                </div>
            ) : (
                <CollectionGrid
                    collections={filteredCollections || []}
                    viewMode={viewMode}
                />
            )}

            <CreateCollectionModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            />
        </motion.div>
    );
};
