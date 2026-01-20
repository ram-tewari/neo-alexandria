/**
 * Collection Store
 * 
 * Zustand store for collection state management
 */

import { create } from 'zustand';
import { collectionsAPI } from '@/services/api';
import type {
  Collection,
  CollectionDetail,
  CollectionCreate,
  CollectionUpdate,
  CollectionNode,
} from '@/types/collection';

interface CollectionStore {
  // State
  collections: Collection[];
  activeCollection: CollectionDetail | null;
  collectionTree: CollectionNode[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchCollections: () => Promise<void>;
  selectCollection: (id: string) => Promise<void>;
  createCollection: (data: CollectionCreate) => Promise<Collection>;
  updateCollection: (id: string, data: CollectionUpdate) => Promise<void>;
  deleteCollection: (id: string) => Promise<void>;
  addResourcesToCollection: (collectionId: string, resourceIds: string[]) => Promise<void>;
  removeResourcesFromCollection: (collectionId: string, resourceIds: string[]) => Promise<void>;
  buildCollectionTree: () => void;
  toggleCollectionExpanded: (id: string) => void;
  reset: () => void;
}

const initialState = {
  collections: [],
  activeCollection: null,
  collectionTree: [],
  isLoading: false,
  error: null,
};

/**
 * Build hierarchical tree from flat collection list
 */
function buildTree(collections: Collection[]): CollectionNode[] {
  const map = new Map<string, CollectionNode>();
  const roots: CollectionNode[] = [];

  // Create nodes
  collections.forEach((collection) => {
    map.set(collection.id, {
      ...collection,
      children: [],
      isExpanded: false,
      depth: 0,
    });
  });

  // Build tree structure
  collections.forEach((collection) => {
    const node = map.get(collection.id)!;

    if (collection.parent_id) {
      const parent = map.get(collection.parent_id);
      if (parent) {
        parent.children.push(node);
        node.depth = parent.depth + 1;
      } else {
        // Parent not found, treat as root
        roots.push(node);
      }
    } else {
      roots.push(node);
    }
  });

  // Sort children by name
  const sortChildren = (nodes: CollectionNode[]) => {
    nodes.sort((a, b) => a.name.localeCompare(b.name));
    nodes.forEach((node) => sortChildren(node.children));
  };

  sortChildren(roots);

  return roots;
}

export const useCollectionStore = create<CollectionStore>((set, get) => ({
  ...initialState,

  fetchCollections: async () => {
    set({ isLoading: true, error: null });

    try {
      const response = await collectionsAPI.list();
      const collections = response.data;

      set({
        collections,
        isLoading: false,
      });

      // Build tree after fetching
      get().buildCollectionTree();
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch collections',
        isLoading: false,
      });
    }
  },

  selectCollection: async (id: string) => {
    set({ isLoading: true, error: null });

    try {
      const collection = await collectionsAPI.get(id);
      set({ activeCollection: collection, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch collection',
        isLoading: false,
      });
    }
  },

  createCollection: async (data: CollectionCreate) => {
    try {
      const newCollection = await collectionsAPI.create(data);

      const { collections } = get();
      set({ collections: [...collections, newCollection] });

      // Rebuild tree
      get().buildCollectionTree();

      return newCollection;
    } catch (error: any) {
      set({ error: error.message || 'Failed to create collection' });
      throw error;
    }
  },

  updateCollection: async (id: string, data: CollectionUpdate) => {
    try {
      const updated = await collectionsAPI.update(id, data);

      const { collections, activeCollection } = get();
      const updatedCollections = collections.map((c) =>
        c.id === id ? updated : c
      );

      set({ collections: updatedCollections });

      if (activeCollection?.id === id) {
        set({ activeCollection: { ...activeCollection, ...updated } });
      }

      // Rebuild tree
      get().buildCollectionTree();
    } catch (error: any) {
      set({ error: error.message || 'Failed to update collection' });
      throw error;
    }
  },

  deleteCollection: async (id: string) => {
    try {
      await collectionsAPI.delete(id);

      const { collections, activeCollection } = get();
      const updatedCollections = collections.filter((c) => c.id !== id);

      set({ collections: updatedCollections });

      if (activeCollection?.id === id) {
        set({ activeCollection: null });
      }

      // Rebuild tree
      get().buildCollectionTree();
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete collection' });
      throw error;
    }
  },

  addResourcesToCollection: async (collectionId: string, resourceIds: string[]) => {
    try {
      await collectionsAPI.addResources(collectionId, resourceIds);

      // Refresh active collection if it's the one we're adding to
      const { activeCollection } = get();
      if (activeCollection?.id === collectionId) {
        await get().selectCollection(collectionId);
      }

      // Refresh collections list to update counts
      await get().fetchCollections();
    } catch (error: any) {
      set({ error: error.message || 'Failed to add resources to collection' });
      throw error;
    }
  },

  removeResourcesFromCollection: async (collectionId: string, resourceIds: string[]) => {
    try {
      await collectionsAPI.removeResources(collectionId, resourceIds);

      // Refresh active collection if it's the one we're removing from
      const { activeCollection } = get();
      if (activeCollection?.id === collectionId) {
        await get().selectCollection(collectionId);
      }

      // Refresh collections list to update counts
      await get().fetchCollections();
    } catch (error: any) {
      set({ error: error.message || 'Failed to remove resources from collection' });
      throw error;
    }
  },

  buildCollectionTree: () => {
    const { collections } = get();
    const tree = buildTree(collections);
    set({ collectionTree: tree });
  },

  toggleCollectionExpanded: (id: string) => {
    const { collectionTree } = get();

    const toggleNode = (nodes: CollectionNode[]): CollectionNode[] => {
      return nodes.map((node) => {
        if (node.id === id) {
          return { ...node, isExpanded: !node.isExpanded };
        }
        if (node.children.length > 0) {
          return { ...node, children: toggleNode(node.children) };
        }
        return node;
      });
    };

    const updatedTree = toggleNode(collectionTree);
    set({ collectionTree: updatedTree });
  },

  reset: () => {
    set(initialState);
  },
}));
