// Neo Alexandria 2.0 Frontend - Collections Page
// View and manage collections

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCollections } from '@/hooks/useCollections';
import { useAppStore } from '@/store';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { CollectionCard } from '@/components/collections/CollectionCard';
import { CreateCollectionModal } from '@/components/collections/CreateCollectionModal';
import { 
  FolderOpen, 
  Plus, 
  Search,
  Sparkles,
  FolderTree
} from 'lucide-react';
import { formatNumber } from '@/utils/format';
import type { Collection } from '@/services/api/collections';

const CollectionsPage: React.FC = () => {
  const userId = useAppStore((state) => state.userId) || 'demo-user';
  
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch collections
  const { data, isLoading, error, refetch } = useCollections({ user_id: userId });
  const collections = data?.items || [];
  const totalCollections = data?.total || 0;

  // Filter collections by search query
  const filteredCollections = useMemo(() => {
    if (!searchQuery.trim()) {
      return collections;
    }

    const query = searchQuery.toLowerCase();
    return collections.filter(
      (collection) =>
        collection.name.toLowerCase().includes(query) ||
        collection.description?.toLowerCase().includes(query)
    );
  }, [collections, searchQuery]);

  // Build hierarchical structure
  type CollectionWithChildren = Collection & { children: CollectionWithChildren[] };
  
  const hierarchicalCollections = useMemo(() => {
    const collectionsMap = new Map<string, CollectionWithChildren>();
    const rootCollections: CollectionWithChildren[] = [];

    // First pass: create map with children arrays
    filteredCollections.forEach((collection) => {
      collectionsMap.set(collection.id, { ...collection, children: [] });
    });

    // Second pass: build hierarchy
    filteredCollections.forEach((collection) => {
      const collectionWithChildren = collectionsMap.get(collection.id)!;
      
      if (collection.parent_id && collectionsMap.has(collection.parent_id)) {
        // Add to parent's children
        const parent = collectionsMap.get(collection.parent_id)!;
        parent.children.push(collectionWithChildren);
      } else {
        // Root level collection
        rootCollections.push(collectionWithChildren);
      }
    });

    return rootCollections;
  }, [filteredCollections]);

  // Render collection tree recursively
  const renderCollectionTree = (
    collections: CollectionWithChildren[],
    depth: number = 0
  ): React.ReactNode => {
    return collections.map((collection) => (
      <div key={collection.id}>
        <CollectionCard collection={collection} depth={depth} />
        {collection.children.length > 0 && (
          <div className="mt-2">
            {renderCollectionTree(collection.children, depth + 1)}
          </div>
        )}
      </div>
    ));
  };

  if (error) {
    return (
      <div className="min-h-screen bg-charcoal-grey-900 flex items-center justify-center">
        <div className="text-center">
          <FolderOpen className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-lg font-medium text-charcoal-grey-50 mb-2">
            Error Loading Collections
          </h3>
          <p className="text-sm text-charcoal-grey-400 mb-4">
            {error?.message || 'An error occurred'}
          </p>
          <Button onClick={() => refetch()}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-charcoal-grey-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
        >
          <div>
            <h1 className="text-3xl font-bold text-charcoal-grey-50">Collections</h1>
            <p className="text-charcoal-grey-400 mt-1">
              {totalCollections > 0
                ? `${formatNumber(totalCollections)} collection${totalCollections === 1 ? '' : 's'}`
                : 'Organize your resources into collections'}
            </p>
          </div>

          <Button
            variant="primary"
            size="md"
            onClick={() => setShowCreateModal(true)}
            icon={<Plus className="w-4 h-4" />}
          >
            Create Collection
          </Button>
        </motion.div>

        {/* Search Bar */}
        {collections.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card variant="glass" className="mb-6">
              <CardContent className="p-4">
                <Input
                  placeholder="Search collections..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  leftIcon={<Search className="w-4 h-4" />}
                  className="w-full"
                />
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Collections Content */}
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <Card key={i} variant="glass">
                <CardContent className="p-4">
                  <LoadingSkeleton lines={3} />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredCollections.length === 0 ? (
          searchQuery ? (
            <EmptySearchState searchQuery={searchQuery} onClearSearch={() => setSearchQuery('')} />
          ) : (
            <EmptyCollectionsState onCreateCollection={() => setShowCreateModal(true)} />
          )
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            {renderCollectionTree(hierarchicalCollections)}
          </motion.div>
        )}
      </div>

      {/* Create Collection Modal */}
      <CreateCollectionModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

// Empty state when no collections exist
interface EmptyCollectionsStateProps {
  onCreateCollection: () => void;
}

const EmptyCollectionsState: React.FC<EmptyCollectionsStateProps> = ({ onCreateCollection }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3 }}
  >
    <Card variant="glass">
      <CardContent className="text-center py-16">
        <div className="text-charcoal-grey-400 mb-4">
          <FolderTree className="w-20 h-20 mx-auto mb-4 text-accent-blue-500" />
          <h3 className="text-2xl font-medium text-charcoal-grey-50 mb-2">
            No collections yet
          </h3>
          <p className="text-charcoal-grey-400 max-w-sm mx-auto mb-8">
            Create your first collection to organize your resources by topic, project, or any way you like.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            variant="primary"
            onClick={onCreateCollection}
            icon={<Plus className="w-4 h-4" />}
          >
            Create Your First Collection
          </Button>
          <Button
            variant="outline"
            onClick={() => window.location.href = '/library'}
            icon={<Sparkles className="w-4 h-4" />}
          >
            Browse Library
          </Button>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

// Empty state when search returns no results
interface EmptySearchStateProps {
  searchQuery: string;
  onClearSearch: () => void;
}

const EmptySearchState: React.FC<EmptySearchStateProps> = ({ searchQuery, onClearSearch }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3 }}
  >
    <Card variant="glass">
      <CardContent className="text-center py-12">
        <Search className="w-16 h-16 mx-auto mb-4 text-charcoal-grey-600" />
        <h3 className="text-xl font-medium text-charcoal-grey-50 mb-2">
          No collections found
        </h3>
        <p className="text-charcoal-grey-400 mb-6">
          No collections match "{searchQuery}"
        </p>
        <Button variant="outline" onClick={onClearSearch}>
          Clear Search
        </Button>
      </CardContent>
    </Card>
  </motion.div>
);

export { CollectionsPage };
