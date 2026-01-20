import React from 'react';
import { BarChart2, TrendingUp, Tag, Activity } from 'lucide-react';
import { Card } from '../../../ui/Card/Card';
import type { CollectionStats } from '../../../../types/collection';

interface CollectionStatsProps {
    stats: CollectionStats;
}

export const CollectionStatsDashboard: React.FC<CollectionStatsProps> = ({ stats }) => {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card padding="sm" className="flex items-center gap-4">
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                    <BarChart2 className="w-5 h-5" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Total Resources</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">{stats.resourceCount}</p>
                </div>
            </Card>

            <Card padding="sm" className="flex items-center gap-4">
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg text-green-600 dark:text-green-400">
                    <Activity className="w-5 h-5" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Avg. Quality</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">{stats.avgQuality}%</p>
                </div>
            </Card>

            <Card padding="sm" className="flex items-center gap-4">
                <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-purple-600 dark:text-purple-400">
                    <TrendingUp className="w-5 h-5" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Last Activity</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-[120px]">
                        {new Date(stats.lastUpdated).toLocaleDateString()}
                    </p>
                </div>
            </Card>

            <Card padding="sm" className="flex items-center gap-4">
                <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg text-orange-600 dark:text-orange-400">
                    <Tag className="w-5 h-5" />
                </div>
                <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Top Tag</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-[120px]">
                        {stats.topTags[0] || 'None'}
                    </p>
                </div>
            </Card>
        </div>
    );
};
