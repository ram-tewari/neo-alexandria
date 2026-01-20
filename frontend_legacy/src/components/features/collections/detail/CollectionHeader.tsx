import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MoreVertical, Share2, Settings, Calendar, FileText } from 'lucide-react';
import { Button } from '../../../ui/Button/Button';
import { Card } from '../../../ui/Card/Card';
import type { CollectionDetail } from '../../../../types/collection';

interface CollectionHeaderProps {
    collection: CollectionDetail;
}

export const CollectionHeader: React.FC<CollectionHeaderProps> = ({ collection }) => {
    const navigate = useNavigate();

    return (
        <div className="space-y-4">
            <Button
                variant="ghost"
                size="sm"
                className="pl-0 hover:bg-transparent hover:text-blue-600 dark:hover:text-blue-400"
                onClick={() => navigate('/collections')}
            >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Collections
            </Button>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        {collection.name}
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 max-w-2xl">
                        {collection.description || 'No description provided.'}
                    </p>

                    <div className="flex items-center gap-4 mt-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                            <FileText className="w-4 h-4" />
                            <span>{collection.resource_count} resources</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>Updated {new Date(collection.updated_at).toLocaleDateString()}</span>
                        </div>
                        <div className="px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-xs font-medium uppercase tracking-wide">
                            {collection.visibility}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Button variant="secondary" size="sm">
                        <Share2 className="w-4 h-4 mr-2" />
                        Share
                    </Button>
                    <Button variant="secondary" size="sm">
                        <Settings className="w-4 h-4 mr-2" />
                        Settings
                    </Button>
                    <Button variant="ghost" size="sm" className="px-2">
                        <MoreVertical className="w-4 h-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
};
