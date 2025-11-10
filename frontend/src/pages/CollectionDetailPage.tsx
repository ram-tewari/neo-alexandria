// Neo Alexandria 2.0 Frontend - Collection Detail Page
// View and manage a specific collection with its resources

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCollection, useRemoveResourcesFromCollection, useDeleteCollection } from '@/hooks/useCollections';
import { useAppStore } from '@/store';
import { toast } from '@/store/toastStore';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { CollectionCard } from '@/components/collections/CollectionCard';
import { CollectionRecommendations } from '@/components/collections/CollectionRecommendations';
import { 
  FolderOpen, 
  ArrowLeft, 
  Edit, 
  Trash2,
  Lock,
  Users,
  Globe,
  Grid3x3,
  List as ListIcon,
  X
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatRelativeTime, formatNumber } from '@/utils/format';
import type { Resource } from '@/types/api';

type ViewMode = 'grid' | 'list';

const CollectionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const userId = useAppStore((state) => state.userId) || 'demo-user';
  
  // State
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedResources, setSelectedResources] = useState<Set<string>>(new Set());

  // Fetch collection
  const { data: collection, isLoading, error } = useCollection(id!, userId);

  // Mutations
  const removeResourcesMutation = useRemoveResourcesFromCollection();
  const deleteCollectionMutation = useDeleteCollection();

  // Visibility icon mapping
  const visibilityIcons = {
    private: <Lock className="w-4 h-4" />,
    shared: <Users className="w-4 h-4" />,
    public: <Globe className="w-4 h-4" />,
  };

  // Handle resource selection
  const toggleResourceSelection = (resourceId: string) => {
    setSelectedResources((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(resourceId)) {
        newSet.delete(resourceId);
      } else {
        newSet.add(resourceId);
      }
      return newSet;
    });
  };

  // Handle removing resources
  const handleRemoveResources = async () => {
    if (selectedResources.size === 0) return;

    if (!window.confirm(`Remove ${selectedResources.size} resource(s) from this collection?`)) {
      return;
    }

    try {
      await removeResourcesMutation.mutateAsync({
        collectionId: id!,
        resourceIds: Array.from(selectedResources),
        userId,
      });

      toast.success(
        'Resources removed',
        `${selectedResources.size} resource(s) removed from collection`
      );
      setSelectedResources(new Set());
    } catch (error: any) {
      toast.error('Failed to remove resources', error?.response?.data?.detail || error.message);
    }
  };

  // Handle deleting collection
  const handleDeleteCollection = async () => {
    if (!window.confirm(`Delete "${collection?.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteCollectionMutation.mutateAsync({ id: id!, userId });
      toast.success('Collection deleted', `"${collection?.name}" has been deleted`);
      navigate('/collections');
    } catch (error: any) {
      toast.error('Failed to delete collection', error?.response?.data?.detail || error.message);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-charcoal-grey-900">
        <div className="container mx-auto px-4 py-8">
          <Card variant="glass">
            <CardContent className="p-6">
              <LoadingSkeleton lines={5} />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error || !collection) {
    return (
      <div className="min-h-screen bg-charcoal-grey-900 flex items-center justify-center">
        <div className="text-center">
          <FolderOpen className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-lg font-medium text-charcoal-grey-50 mb-2">
            Collection Not Found
          </h3>
          <p className="text-sm text-charcoal-grey-400 mb-4">
            {error?.message || 'The collection you are looking for does not exist'}
          </p>
          <Button onClick={() => navigate('/collections')}>
            Back to Collections
          </Button>
        </div>
      </div>
    );
  }

  const resources = collection.resources || [];

  return (
    <div className="min-h-screen bg-charcoal-grey-900">
      <div className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-4"
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/collections')}
            icon={<ArrowLeft className="w-4 h-4" />}
          >
            Back to Collections
          </Button>
        </motion.div>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card variant="glass" className="mb-6">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-12 h-12 rounded-lg bg-accent-blue-500/10 flex items-center justify-center">
                      <FolderOpen className="w-6 h-6 text-accent-blue-400" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-charcoal-grey-50">
                        {collection.name}
                      </h1>
                      <div className="flex items-center space-x-3 mt-1">
                        <span
                          className={cn(
                            'inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium',
                            collection.visibility === 'private' && 'bg-charcoal-grey-700 text-charcoal-grey-300',
                            collection.visibility === 'shared' && 'bg-neutral-blue-900/50 text-neutral-blue-300',
                            collection.visibility === 'public' && 'bg-accent-blue-900/50 text-accent-blue-300'
                          )}
                        >
                          {visibilityIcons[collection.visibility]}
                          <span className="capitalize">{collection.visibility}</span>
                        </span>
                        <span className="text-sm text-charcoal-grey-500">
                          Created {formatRelativeTime(collection.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {collection.description && (
                    <p className="text-charcoal-grey-400 mt-3">
                      {collection.description}
                    </p>
                  )}

                  <div className="flex items-center space-x-4 mt-4 text-sm text-charcoal-grey-500">
                    <span>
                      {formatNumber(collection.resource_count)} {collection.resource_count === 1 ? 'resource' : 'resources'}
                    </span>
                    {collection.subcollections && collection.subcollections.length > 0 && (
                      <span>
                        {collection.subcollections.length} {collection.subcollections.length === 1 ? 'subcollection' : 'subcollections'}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    icon={<Edit className="w-4 h-4" />}
                    onClick={() => toast.info('Edit collection', 'Edit functionality coming soon')}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    icon={<Trash2 className="w-4 h-4" />}
                    onClick={handleDeleteCollection}
                    loading={deleteCollectionMutation.isPending}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Subcollections */}
            {collection.subcollections && collection.subcollections.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mb-6"
              >
                <h2 className="text-lg font-semibold text-charcoal-grey-50 mb-3">
                  Subcollections
                </h2>
                <div className="space-y-3">
                  {collection.subcollections.map((subcollection) => (
                    <CollectionCard key={subcollection.id} collection={subcollection} />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Resources Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-charcoal-grey-50">
                  Resources
                </h2>

                <div className="flex items-center space-x-2">
                  {selectedResources.size > 0 && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={handleRemoveResources}
                      loading={removeResourcesMutation.isPending}
                      icon={<X className="w-4 h-4" />}
                    >
                      Remove {selectedResources.size}
                    </Button>
                  )}

                  <div className="flex items-center bg-charcoal-grey-800 rounded-lg p-1">
                    <Button
                      variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('grid')}
                      icon={<Grid3x3 className="w-4 h-4" />}
                      className="rounded-r-none"
                    />
                    <Button
                      variant={viewMode === 'list' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('list')}
                      icon={<ListIcon className="w-4 h-4" />}
                      className="rounded-l-none"
                    />
                  </div>
                </div>
              </div>

              {resources.length === 0 ? (
                <Card variant="glass">
                  <CardContent className="text-center py-12">
                    <FolderOpen className="w-16 h-16 mx-auto mb-4 text-charcoal-grey-600" />
                    <h3 className="text-lg font-medium text-charcoal-grey-50 mb-2">
                      No resources yet
                    </h3>
                    <p className="text-charcoal-grey-400 mb-6">
                      Add resources to this collection from your library
                    </p>
                    <Button
                      variant="primary"
                      onClick={() => navigate('/library')}
                    >
                      Browse Library
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className={cn(
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 gap-4'
                    : 'space-y-3'
                )}>
                  {resources.map((resource: Resource) => (
                    <ResourceCardSimple
                      key={resource.id}
                      resource={resource}
                      viewMode={viewMode}
                      selected={selectedResources.has(resource.id)}
                      onToggleSelect={() => toggleResourceSelection(resource.id)}
                    />
                  ))}
                </div>
              )}
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <CollectionRecommendations collectionId={id!} />
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Simplified Resource Card for collection detail view
interface ResourceCardSimpleProps {
  resource: Resource;
  viewMode: ViewMode;
  selected: boolean;
  onToggleSelect: () => void;
}

const ResourceCardSimple: React.FC<ResourceCardSimpleProps> = ({
  resource,
  viewMode,
  selected,
  onToggleSelect,
}) => {
  const navigate = useNavigate();

  return (
    <Card
      variant="glass"
      hover
      className={cn(
        'cursor-pointer',
        selected && 'ring-2 ring-accent-blue-500'
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggleSelect}
            onClick={(e) => e.stopPropagation()}
            className="mt-1 w-4 h-4 text-accent-blue-500 rounded border-charcoal-grey-600 focus:ring-accent-blue-500"
          />
          
          <div
            className="flex-1 min-w-0"
            onClick={() => navigate(`/resources/${resource.id}`)}
          >
            <h4 className="text-sm font-medium text-charcoal-grey-50 mb-1 line-clamp-2 hover:text-accent-blue-400 transition-colors">
              {resource.title}
            </h4>
            {resource.description && (
              <p className="text-xs text-charcoal-grey-400 line-clamp-2 mb-2">
                {resource.description}
              </p>
            )}
            <div className="flex items-center space-x-3 text-xs text-charcoal-grey-500">
              {resource.quality_score !== undefined && (
                <span>Quality: {(resource.quality_score * 100).toFixed(0)}%</span>
              )}
              <span>{formatRelativeTime(resource.updated_at)}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export { CollectionDetailPage };
