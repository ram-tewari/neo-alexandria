import React, { useState } from 'react';
import { TaxonomyTree } from '@/components/taxonomy/TaxonomyTree';
import { ClassificationInterface } from '@/components/taxonomy/ClassificationInterface';
import { useTaxonomy, useTaxonomyStats } from '@/hooks/useTaxonomy';
import { Layers, Brain } from 'lucide-react';

export const Taxonomy: React.FC = () => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>();
  const [activeTab, setActiveTab] = useState<'tree' | 'classification'>('tree');
  const { data: taxonomy = [], isLoading } = useTaxonomy();
  const { data: stats } = useTaxonomyStats();

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading taxonomy...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Taxonomy & Classification
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Organize and classify your knowledge
            </p>
          </div>

          {stats && (
            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Categories: </span>
                <span className="font-medium text-gray-900 dark:text-white">{stats.totalCategories}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Max Depth: </span>
                <span className="font-medium text-gray-900 dark:text-white">{stats.maxDepth}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Uncategorized: </span>
                <span className="font-medium text-orange-600 dark:text-orange-400">{stats.uncategorizedResources}</span>
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('tree')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'tree'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <Layers className="w-4 h-4" />
            Taxonomy Tree
          </button>
          <button
            onClick={() => setActiveTab('classification')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'classification'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <Brain className="w-4 h-4" />
            ML Classification
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'tree' ? (
          <div className="max-w-4xl">
            <TaxonomyTree
              nodes={taxonomy}
              selectedId={selectedNodeId}
              onNodeSelect={setSelectedNodeId}
            />
          </div>
        ) : (
          <div className="max-w-6xl">
            <ClassificationInterface />
          </div>
        )}
      </div>
    </div>
  );
};
