/**
 * ResourceCard component
 * Displays a single resource in card format
 * Supports both legacy Resource and new ResourceRead types
 * Supports batch selection mode with checkboxes
 */

import React from 'react';
import { Card } from '../../ui/Card';
import { Checkbox } from '../../ui/Checkbox/Checkbox';
import type { Resource, ResourceRead } from '../../../lib/api/types';

interface ResourceCardProps {
  resource: Resource | ResourceRead;
  onClick?: (resource: Resource | ResourceRead) => void;
  /** Whether batch mode is active */
  batchMode?: boolean;
  /** Whether this resource is selected in batch mode */
  isSelected?: boolean;
  /** Callback when selection changes in batch mode */
  onToggleSelection?: (id: string) => void;
  /** Card padding size */
  padding?: 'sm' | 'md' | 'lg';
}

/**
 * Type guard to check if resource is legacy Resource type
 */
function isLegacyResource(resource: Resource | ResourceRead): resource is Resource {
  return 'resource_type' in resource && 'tags' in resource;
}

/**
 * Card component for displaying a resource
 */
export const ResourceCard: React.FC<ResourceCardProps> = ({ 
  resource, 
  onClick,
  batchMode = false,
  isSelected = false,
  onToggleSelection,
  padding = 'md',
}) => {
  const typeIcons: Record<string, string> = {
    article: '📄',
    video: '🎥',
    book: '📚',
    paper: '📑',
    pdf: '📄',
    epub: '📖',
    default: '📄',
  };

  // Extract common fields with fallbacks for both types
  const title = resource.title;
  const description = resource.description;
  
  // Handle type icon
  let typeIcon = '📄';
  if (isLegacyResource(resource)) {
    typeIcon = typeIcons[resource.resource_type] || typeIcons.default;
  } else {
    const type = resource.type?.toLowerCase() || resource.format?.toLowerCase() || 'default';
    typeIcon = typeIcons[type] || typeIcons.default;
  }
  
  // Handle tags/subjects
  const tags = isLegacyResource(resource) 
    ? resource.tags 
    : (resource.subject || []);

  // Get resource ID
  const resourceId = resource.id;

  // Handle card click - in batch mode, toggle selection; otherwise call onClick
  const handleCardClick = (e: React.MouseEvent) => {
    if (batchMode && onToggleSelection) {
      e.stopPropagation();
      // Shift+Click is handled by the parent component via index
      onToggleSelection(resourceId);
    } else {
      onClick?.(resource);
    }
  };

  // Handle checkbox click - prevent event bubbling
  const handleCheckboxChange = (checked: boolean) => {
    if (onToggleSelection) {
      onToggleSelection(resourceId);
    }
  };

  return (
    <Card
      hoverable
      padding={padding}
      className={`cursor-pointer ${batchMode && isSelected ? 'ring-2 ring-blue-500' : ''}`}
      onClick={handleCardClick}
    >
      <div className="flex items-start gap-3">
        {batchMode && (
          <div onClick={(e) => e.stopPropagation()}>
            <Checkbox
              checked={isSelected}
              onChange={handleCheckboxChange}
              aria-label={`Select ${title}`}
            />
          </div>
        )}
        <div className="text-3xl">{typeIcon}</div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate mb-1">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
              {description}
            </p>
          )}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 text-xs font-medium rounded-md bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                >
                  {tag}
                </span>
              ))}
              {tags.length > 3 && (
                <span className="px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                  +{tags.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
