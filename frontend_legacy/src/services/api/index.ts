/**
 * API Services
 * 
 * Central export point for all API-related modules
 */

export { APIClient, apiClient } from './client';
export { APIError, handleAPIError, getErrorMessage, ERROR_MESSAGES } from './errors';
export { resourcesAPI } from './resources';
export { collectionsAPI } from './collections';
export { searchAPI } from './search';
export { tagsAPI } from './tags';
export type { RequestConfig, QueryParams, APIResponse, APIListResponse } from '@/types/api';
