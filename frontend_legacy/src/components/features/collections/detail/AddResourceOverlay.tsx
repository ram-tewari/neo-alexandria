import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, Plus, Check } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '../../../ui/Button/Button';
import { Input } from '../../../ui/Input/Input';
import { LoadingSpinner } from '../../../common/LoadingSpinner';
import { collectionsApi } from '../../../../lib/api/collections';
import { resourcesApi } from '../../../../lib/api/resources';
import { useToast } from '../../../../contexts/ToastContext';

interface AddResourceOverlayProps {
    isOpen: boolean;
    onClose: () => void;
    collectionId: string;
    existingResourceIds: string[];
}

export const AddResourceOverlay: React.FC<AddResourceOverlayProps> = ({
    isOpen,
    onClose,
    collectionId,
    existingResourceIds
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const queryClient = useQueryClient();
    const { showToast } = useToast();

    const { data: searchResults, isLoading } = useQuery({
        queryKey: ['resourceSearch', searchQuery],
        queryFn: async () => {
            const response = await resourcesApi.list({
                q: searchQuery,
                limit: 10
            });
            return response.items;
        },
        enabled: searchQuery.length > 2
    });

    const addMutation = useMutation({
        mutationFn: (resourceIds: string[]) => collectionsApi.addResources(collectionId, resourceIds),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['collection', collectionId] });
            showToast({ message: 'Resource added to collection', variant: 'success' });
        },
        onError: () => {
            showToast({ message: 'Failed to add resource', variant: 'error' });
        }
    });

    const handleAdd = (id: string) => {
        addMutation.mutate([id]);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm"
                        onClick={onClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, x: '100%' }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white dark:bg-gray-900 shadow-2xl border-l border-gray-200 dark:border-gray-800"
                    >
                        <div className="flex flex-col h-full">
                            <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Add Resources</h2>
                                <button
                                    onClick={onClose}
                                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <Input
                                        placeholder="Search for resources..."
                                        className="pl-10"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        autoFocus
                                    />
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4">
                                {isLoading ? (
                                    <div className="flex justify-center py-8">
                                        <LoadingSpinner size="md" />
                                    </div>
                                ) : searchQuery.length < 3 ? (
                                    <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                                        Type at least 3 characters to search
                                    </div>
                                ) : !searchResults || searchResults.length === 0 ? (
                                    <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                                        No resources found
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {searchResults.map((resource: any) => {
                                            const isAdded = existingResourceIds.includes(resource.id);
                                            return (
                                                <div
                                                    key={resource.id}
                                                    className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-500 dark:hover:border-blue-500 transition-colors"
                                                >
                                                    <div>
                                                        <h3 className="font-medium text-gray-900 dark:text-white">{resource.title}</h3>
                                                        <p className="text-xs text-gray-500 dark:text-gray-400">{resource.type}</p>
                                                    </div>
                                                    {isAdded ? (
                                                        <span className="flex items-center text-green-600 text-sm font-medium">
                                                            <Check className="w-4 h-4 mr-1" />
                                                            Added
                                                        </span>
                                                    ) : (
                                                        <Button
                                                            size="sm"
                                                            variant="ghost"
                                                            onClick={() => handleAdd(resource.id)}
                                                            disabled={addMutation.isPending}
                                                        >
                                                            <Plus className="w-4 h-4" />
                                                        </Button>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
