// Neo Alexandria 2.0 Frontend - Resource Card Component
// Individual resource display card for library grid and list views

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  ExternalLink, 
  MoreVertical, 
  Edit, 
  Trash2, 
  Star, 
  CheckCircle,
  Eye
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { 
  formatRelativeTime, 
  formatQualityScore, 
  getQualityBadgeClass,
  getReadStatusColor,
  formatReadStatus,
  extractDomain,
  truncateText,
} from '@/utils/format';
import { useDeleteResource, useUpdateResource } from '@/hooks/useApi';
import { useAppStore } from '@/store';
import type { Resource } from '@/types/api';

interface ResourceCardProps {
  resource: Resource;
  viewMode: 'grid' | 'list';
  selected?: boolean;
  onToggleSelect?: () => void;
}

const ResourceCard: React.FC<ResourceCardProps> = ({
  resource,
  viewMode,
  selected = false,
  onToggleSelect,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const toggleResourceSelection = useAppStore(state => state.toggleResourceSelection);
  const deleteResource = useDeleteResource();
  const updateResource = useUpdateResource();

  const handleToggleSelection = () => {
    toggleResourceSelection(resource.id);
    onToggleSelect?.();
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this resource?')) {
      try {
        await deleteResource.mutateAsync(resource.id);
      } catch (error) {
        console.error('Failed to delete resource:', error);
      }
    }
  };

  const handleMarkAsRead = async () => {
    try {
      await updateResource.mutateAsync({
        resourceId: resource.id,
        updates: { read_status: 'completed' }
      });
    } catch (error) {
      console.error('Failed to update read status:', error);
    }
  };

  const handleToggleFavorite = async () => {
    // This would require a favorite field in the backend
    // For now, we can use a subject tag
    const isFavorited = resource.subject.includes('favorite');
    const newSubjects = isFavorited 
      ? resource.subject.filter(s => s !== 'favorite')
      : [...resource.subject, 'favorite'];

    try {
      await updateResource.mutateAsync({
        resourceId: resource.id,
        updates: { subject: newSubjects }
      });
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const isFavorited = resource.subject.includes('favorite');
  const domain = extractDomain(resource.url || resource.source);

  if (viewMode === 'list') {
    return (
      <Card variant="glass" hover className={cn('p-0', selected && 'ring-2 ring-primary-500')}>
        <CardContent className="p-4">
          <div className="flex items-start space-x-4">
            {/* Selection Checkbox */}
            <div className="flex-shrink-0 pt-1">
              <input
                type="checkbox"
                checked={selected}
                onChange={handleToggleSelection}
                className="w-4 h-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
              />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <Link
                      to={`/resource/${resource.id}`}
                      className="text-lg font-medium text-secondary-900 hover:text-primary-600 transition-colors truncate"
                    >
                      {resource.title}
                    </Link>
                    
                    {isFavorited && (
                      <Star className="w-4 h-4 text-yellow-500 fill-current" />
                    )}
                  </div>

                  {resource.description && (
                    <p className="text-secondary-600 text-sm mb-2 line-clamp-2">
                      {truncateText(resource.description, 200)}
                    </p>
                  )}

                  <div className="flex items-center space-x-4 text-sm text-secondary-500">
                    <span>{domain}</span>
                    <span>{formatRelativeTime(resource.updated_at)}</span>
                    <div className="flex items-center space-x-1">
                      <span>Quality:</span>
                      <span className={cn('font-medium', getQualityBadgeClass(resource.quality_score))}>
                        {formatQualityScore(resource.quality_score)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  <Badge 
                    className={getReadStatusColor(resource.read_status)}
                    size="sm"
                  >
                    {formatReadStatus(resource.read_status)}
                  </Badge>

                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowMenu(!showMenu)}
                      icon={<MoreVertical className="w-4 h-4" />}
                    />
                    
                    {showMenu && (
                      <ActionMenu
                        resource={resource}
                        onClose={() => setShowMenu(false)}
                        onDelete={handleDelete}
                        onMarkAsRead={handleMarkAsRead}
                        onToggleFavorite={handleToggleFavorite}
                        isFavorited={isFavorited}
                      />
                    )}
                  </div>
                </div>
              </div>

              {/* Tags */}
              {resource.subject.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {resource.subject.slice(0, 5).map((subject) => (
                    <Badge key={subject} variant="outline" size="sm">
                      {subject}
                    </Badge>
                  ))}
                  {resource.subject.length > 5 && (
                    <Badge variant="outline" size="sm">
                      +{resource.subject.length - 5}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Grid view
  return (
    <Card 
      variant="glass"
      hover 
      className={cn('h-full', selected && 'ring-2 ring-primary-500')}
    >
      <CardContent className="p-4 h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selected}
              onChange={handleToggleSelection}
              className="w-4 h-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
            />
            
            {isFavorited && (
              <Star className="w-4 h-4 text-yellow-500 fill-current" />
            )}
          </div>

          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowMenu(!showMenu)}
              icon={<MoreVertical className="w-4 h-4" />}
            />
            
            {showMenu && (
              <ActionMenu
                resource={resource}
                onClose={() => setShowMenu(false)}
                onDelete={handleDelete}
                onMarkAsRead={handleMarkAsRead}
                onToggleFavorite={handleToggleFavorite}
                isFavorited={isFavorited}
              />
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          <Link
            to={`/resource/${resource.id}`}
            className="block group"
          >
            <h3 className="text-lg font-medium text-secondary-900 group-hover:text-primary-600 transition-colors line-clamp-2 mb-2">
              {resource.title}
            </h3>
          </Link>

          {resource.description && (
            <p className="text-secondary-600 text-sm line-clamp-3 mb-3">
              {resource.description}
            </p>
          )}

          {/* Tags */}
          {resource.subject.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {resource.subject.slice(0, 3).map((subject) => (
                <Badge key={subject} variant="outline" size="sm">
                  {subject}
                </Badge>
              ))}
              {resource.subject.length > 3 && (
                <Badge variant="outline" size="sm">
                  +{resource.subject.length - 3}
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-secondary-200 pt-3 mt-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <Badge 
                className={getQualityBadgeClass(resource.quality_score)}
                size="sm"
              >
                {formatQualityScore(resource.quality_score)}
              </Badge>
              
              <Badge 
                className={getReadStatusColor(resource.read_status)}
                size="sm"
              >
                {formatReadStatus(resource.read_status)}
              </Badge>
            </div>

            <div className="text-secondary-500">
              {formatRelativeTime(resource.updated_at)}
            </div>
          </div>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-secondary-500">
              {domain}
            </span>

            {resource.url && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.open(resource.url, '_blank')}
                icon={<ExternalLink className="w-3 h-3" />}
              />
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Action Menu Component
interface ActionMenuProps {
  resource: Resource;
  onClose: () => void;
  onDelete: () => void;
  onMarkAsRead: () => void;
  onToggleFavorite: () => void;
  isFavorited: boolean;
}

const ActionMenu: React.FC<ActionMenuProps> = ({
  resource,
  onClose,
  onDelete,
  onMarkAsRead,
  onToggleFavorite,
  isFavorited,
}) => {
  const handleAction = (action: () => void) => {
    action();
    onClose();
  };

  return (
    <div className="absolute right-0 top-8 w-48 bg-white border border-secondary-200 rounded-lg shadow-lg z-10">
      <div className="py-1">
        <button
          onClick={() => handleAction(() => window.location.href = `/resource/${resource.id}`)}
          className="flex items-center w-full px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
        >
          <Eye className="w-4 h-4 mr-2" />
          View Details
        </button>

        <button
          onClick={() => handleAction(() => window.location.href = `/resource/${resource.id}/edit`)}
          className="flex items-center w-full px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
        >
          <Edit className="w-4 h-4 mr-2" />
          Edit
        </button>

        {resource.read_status !== 'completed' && (
          <button
            onClick={() => handleAction(onMarkAsRead)}
            className="flex items-center w-full px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Mark as Read
          </button>
        )}

        <button
          onClick={() => handleAction(onToggleFavorite)}
          className="flex items-center w-full px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
        >
          <Star className={cn('w-4 h-4 mr-2', isFavorited && 'fill-current text-yellow-500')} />
          {isFavorited ? 'Remove Favorite' : 'Add to Favorites'}
        </button>

        {resource.url && (
          <button
            onClick={() => handleAction(() => window.open(resource.url, '_blank'))}
            className="flex items-center w-full px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Open Link
          </button>
        )}

        <div className="border-t border-secondary-200 my-1" />

        <button
          onClick={() => handleAction(onDelete)}
          className="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Delete
        </button>
      </div>
    </div>
  );
};

export { ResourceCard };
