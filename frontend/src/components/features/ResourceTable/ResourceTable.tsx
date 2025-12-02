/**
 * ResourceTable component
 * Displays resources in a table layout
 * Supports both legacy Resource and new ResourceRead types
 */

import React from 'react';
import type { Resource, ResourceRead } from '../../../lib/api/types';

interface ResourceTableProps {
  resources: (Resource | ResourceRead)[];
  onResourceClick?: (resource: Resource | ResourceRead) => void;
}

/**
 * Type guard to check if resource is legacy Resource type
 */
function isLegacyResource(resource: Resource | ResourceRead): resource is Resource {
  return 'resource_type' in resource && 'tags' in resource;
}

/**
 * Table layout for displaying resources
 */
export const ResourceTable: React.FC<ResourceTableProps> = ({
  resources,
  onResourceClick,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const typeLabels: Record<string, string> = {
    article: 'Article',
    video: 'Video',
    book: 'Book',
    paper: 'Paper',
    pdf: 'PDF',
    epub: 'EPUB',
  };

  if (resources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          No resources found
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Start by adding your first resource
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
              Title
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
              Type
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
              Tags
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">
              Date Added
            </th>
          </tr>
        </thead>
        <tbody>
          {resources.map((resource) => {
            const isLegacy = isLegacyResource(resource);
            const type = isLegacy 
              ? resource.resource_type 
              : (resource.type?.toLowerCase() || resource.format?.toLowerCase() || 'unknown');
            const tags = isLegacy ? resource.tags : (resource.subject || []);
            const dateAdded = isLegacy ? resource.created_at : resource.date_created;
            
            return (
              <tr
                key={resource.id}
                onClick={() => onResourceClick?.(resource)}
                className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors duration-150"
              >
                <td className="px-4 py-3">
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {resource.title}
                  </div>
                  {resource.description && (
                    <div className="text-xs text-gray-600 dark:text-gray-400 truncate max-w-md">
                      {resource.description}
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {typeLabels[type] || type}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {tags.slice(0, 2).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 text-xs font-medium rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                      >
                        {tag}
                      </span>
                    ))}
                    {tags.length > 2 && (
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        +{tags.length - 2}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {formatDate(dateAdded)}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
