import { apiRequest } from './apiUtils';
import type {
    Collection,
    CollectionCreate,
    CollectionUpdate,
    CollectionDetail,
    CollectionListParams,
    SmartCollectionDefinition
} from '../../types/collection';
import type { Resource } from '../../types/resource';

const BASE_PATH = '/collections';

export const collectionsApi = {
    /**
     * Get all collections
     */
    getCollections: async (params?: CollectionListParams): Promise<Collection[]> => {
        const searchParams = new URLSearchParams();
        if (params?.page) searchParams.append('page', params.page.toString());
        if (params?.limit) searchParams.append('limit', params.limit.toString());
        if (params?.owner_id) searchParams.append('owner_id', params.owner_id);
        if (params?.visibility) searchParams.append('visibility', params.visibility);

        const queryString = searchParams.toString();
        const url = queryString ? `${BASE_PATH}?${queryString}` : BASE_PATH;

        return apiRequest<Collection[]>(url);
    },

    /**
     * Get a single collection by ID with details
     */
    getCollection: async (id: string): Promise<CollectionDetail> => {
        return apiRequest<CollectionDetail>(`${BASE_PATH}/${id}`);
    },

    /**
     * Create a new collection
     */
    createCollection: async (data: CollectionCreate): Promise<Collection> => {
        return apiRequest<Collection>(BASE_PATH, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Update a collection
     */
    updateCollection: async (id: string, data: CollectionUpdate): Promise<Collection> => {
        return apiRequest<Collection>(`${BASE_PATH}/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * Delete a collection
     */
    deleteCollection: async (id: string): Promise<void> => {
        return apiRequest<void>(`${BASE_PATH}/${id}`, {
            method: 'DELETE'
        });
    },

    /**
     * Add resources to a collection
     */
    addResources: async (collectionId: string, resourceIds: string[]): Promise<void> => {
        return apiRequest<void>(`${BASE_PATH}/${collectionId}/resources`, {
            method: 'PUT',
            body: JSON.stringify({
                action: 'add',
                resource_ids: resourceIds
            })
        });
    },

    /**
     * Remove resources from a collection
     */
    removeResources: async (collectionId: string, resourceIds: string[]): Promise<void> => {
        return apiRequest<void>(`${BASE_PATH}/${collectionId}/resources`, {
            method: 'PUT',
            body: JSON.stringify({
                action: 'remove',
                resource_ids: resourceIds
            })
        });
    },

    /**
     * Get recommendations for a collection
     */
    getCollectionRecommendations: async (id: string): Promise<Resource[]> => {
        return apiRequest<Resource[]>(`${BASE_PATH}/${id}/recommendations`);
    },

    /**
     * Preview smart collection results
     */
    previewSmartCollection: async (definition: SmartCollectionDefinition): Promise<Resource[]> => {
        return apiRequest<Resource[]>(`${BASE_PATH}/preview-smart`, {
            method: 'POST',
            body: JSON.stringify(definition)
        });
    }
};
