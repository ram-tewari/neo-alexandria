import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MoreVertical, Folder, Trash2, Edit2, Share2 } from 'lucide-react';
import { Card } from '../../../ui/Card/Card';
import { Button } from '../../../ui/Button/Button';
import type { Collection } from '../../../../types/collection';

interface CollectionCardProps {
    collection: Collection;
    viewMode: 'grid' | 'list';
    onRename: (id: string) => void;
    onDelete: (id: string) => void;
}

export const CollectionCard: React.FC<CollectionCardProps> = ({
    collection,
    viewMode,
    onRename,
    onDelete
}) => {
    const navigate = useNavigate();

    const handleCardClick = () => {
        navigate(`/collections/${collection.id}`);
    };

    const handleActionClick = (e: React.MouseEvent, action: () => void) => {
        e.stopPropagation();
        action();
    };

    if (viewMode === 'list') {
        return (
            <Card
                hoverable
                className="flex items-center justify-between cursor-pointer group"
                onClick={handleCardClick}
            >
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                        <Folder className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            {collection.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            {collection.resource_count} resources • Updated {new Date(collection.updated_at).toLocaleDateString()}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleActionClick(e, () => onRename(collection.id))}
                    >
                        <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                        onClick={(e) => handleActionClick(e, () => onDelete(collection.id))}
                    >
                        <Trash2 className="w-4 h-4" />
                    </Button>
                </div>
            </Card>
        );
    }

    return (
        <Card
            hoverable
            className="flex flex-col h-full cursor-pointer group relative"
            onClick={handleCardClick}
        >
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="flex gap-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-1">
                    <button
                        className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md text-gray-500"
                        onClick={(e) => handleActionClick(e, () => onRename(collection.id))}
                    >
                        <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                        className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md text-red-500"
                        onClick={(e) => handleActionClick(e, () => onDelete(collection.id))}
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-md mb-4 flex items-center justify-center text-gray-400">
                <Folder className="w-12 h-12" />
            </div>

            <div className="flex-1">
                <h3 className="font-medium text-lg text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {collection.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                    {collection.description || 'No description'}
                </p>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-100 dark:border-gray-800">
                <span>{collection.resource_count} resources</span>
                <span>{new Date(collection.updated_at).toLocaleDateString()}</span>
            </div>
        </Card>
    );
};
