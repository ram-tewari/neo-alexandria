/**
 * API Types and Interfaces
 * 
 * Core type definitions for API requests and responses
 */

export type ReadStatus = 'unread' | 'in_progress' | 'completed' | 'archived';
export type IngestionStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ViewMode = 'grid' | 'list' | 'headlines' | 'masonry';

export interface APIResponse<T> {
  data: T;
  meta?: {
    timestamp: string;
    version: string;
  };
}

export interface APIListResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
}

export interface APIError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

export interface RequestConfig {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  params?: Record<string, any>;
  data?: any;
  headers?: Record<string, string>;
}

export type QueryParams = Record<string, string | number | boolean | string[] | undefined>;
