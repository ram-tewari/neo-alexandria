/**
 * API Client
 * 
 * Base HTTP client for all backend communication with type safety,
 * error handling, retry logic, and caching
 */

import type { RequestConfig, QueryParams, APIResponse } from '@/types/api';
import { APIError, handleAPIError } from './errors';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
}

export class APIClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private cache: Map<string, CacheEntry<any>>;
  private cacheTTL: number; // milliseconds
  private retryConfig: RetryConfig;

  constructor(baseURL?: string) {
    // Backend doesn't use /api prefix, so default to just the base URL
    this.baseURL = baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    this.cache = new Map();
    this.cacheTTL = 5 * 60 * 1000; // 5 minutes
    this.retryConfig = {
      maxRetries: 3,
      baseDelay: 1000, // 1 second
      maxDelay: 10000, // 10 seconds
    };
  }

  /**
   * Set authorization token
   */
  setAuthToken(token: string): void {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Clear authorization token
   */
  clearAuthToken(): void {
    delete this.defaultHeaders['Authorization'];
  }

  /**
   * Build full URL with query parameters
   */
  private buildURL(url: string, params?: QueryParams): string {
    const fullURL = url.startsWith('http') ? url : `${this.baseURL}${url}`;
    
    if (!params) {
      return fullURL;
    }

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, String(v)));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `${fullURL}?${queryString}` : fullURL;
  }

  /**
   * Generate cache key from URL and params
   */
  private getCacheKey(url: string, params?: QueryParams): string {
    return this.buildURL(url, params);
  }

  /**
   * Get cached data if available and not expired
   */
  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) {
      return null;
    }

    const now = Date.now();
    if (now - entry.timestamp > this.cacheTTL) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Store data in cache
   */
  private setCache<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Invalidate cache entries matching pattern
   */
  invalidateCache(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    const keysToDelete: string[] = [];
    this.cache.forEach((_, key) => {
      if (key.includes(pattern)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Calculate delay for exponential backoff
   */
  private getRetryDelay(attempt: number): number {
    const delay = Math.min(
      this.retryConfig.baseDelay * Math.pow(2, attempt),
      this.retryConfig.maxDelay
    );
    // Add jitter to prevent thundering herd
    return delay + Math.random() * 1000;
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: APIError): boolean {
    // Retry on network errors and 5xx server errors
    return error.isNetworkError() || error.isServerError();
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Make HTTP request with retry logic
   */
  async request<T>(config: RequestConfig): Promise<T> {
    const { url, method, params, data, headers } = config;
    const fullURL = this.buildURL(url, params);

    let lastError: APIError | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const response = await fetch(fullURL, {
          method,
          headers: {
            ...this.defaultHeaders,
            ...headers,
          },
          body: data ? JSON.stringify(data) : undefined,
        });

        // Handle non-2xx responses
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new APIError(
            response.status,
            errorData.error?.code || 'HTTP_ERROR',
            errorData.error?.message || response.statusText,
            errorData.error?.details
          );
        }

        // Parse response
        const responseData = await response.json();
        
        // Extract data from APIResponse wrapper if present
        if (responseData.data !== undefined) {
          return responseData.data as T;
        }
        
        return responseData as T;

      } catch (error) {
        lastError = handleAPIError(error);

        // Don't retry if it's not a retryable error or we've exhausted retries
        if (!this.isRetryableError(lastError) || attempt === this.retryConfig.maxRetries) {
          throw lastError;
        }

        // Wait before retrying
        const delay = this.getRetryDelay(attempt);
        await this.sleep(delay);
      }
    }

    // This should never be reached, but TypeScript needs it
    throw lastError || new APIError(0, 'UNKNOWN_ERROR', 'Request failed');
  }

  /**
   * GET request with caching
   */
  async get<T>(url: string, params?: QueryParams, useCache = true): Promise<T> {
    const cacheKey = this.getCacheKey(url, params);

    // Check cache first
    if (useCache) {
      const cached = this.getFromCache<T>(cacheKey);
      if (cached !== null) {
        return cached;
      }
    }

    const data = await this.request<T>({
      url,
      method: 'GET',
      params,
    });

    // Store in cache
    if (useCache) {
      this.setCache(cacheKey, data);
    }

    return data;
  }

  /**
   * POST request (invalidates cache)
   */
  async post<T>(url: string, data?: any, params?: QueryParams): Promise<T> {
    const result = await this.request<T>({
      url,
      method: 'POST',
      params,
      data,
    });

    // Invalidate related cache entries
    this.invalidateCache(url.split('?')[0]);

    return result;
  }

  /**
   * PUT request (invalidates cache)
   */
  async put<T>(url: string, data?: any, params?: QueryParams): Promise<T> {
    const result = await this.request<T>({
      url,
      method: 'PUT',
      params,
      data,
    });

    // Invalidate related cache entries
    this.invalidateCache(url.split('?')[0]);

    return result;
  }

  /**
   * PATCH request (invalidates cache)
   */
  async patch<T>(url: string, data?: any, params?: QueryParams): Promise<T> {
    const result = await this.request<T>({
      url,
      method: 'PATCH',
      params,
      data,
    });

    // Invalidate related cache entries
    this.invalidateCache(url.split('?')[0]);

    return result;
  }

  /**
   * DELETE request (invalidates cache)
   */
  async delete<T>(url: string, params?: QueryParams): Promise<T> {
    const result = await this.request<T>({
      url,
      method: 'DELETE',
      params,
    });

    // Invalidate related cache entries
    this.invalidateCache(url.split('?')[0]);

    return result;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
