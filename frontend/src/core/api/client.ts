/**
 * Axios client configuration
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

/**
 * Clear authentication state
 * This is a helper to avoid circular dependencies with the auth store
 */
const clearAuthState = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('neo-alexandria-auth');
  delete apiClient.defaults.headers.common['Authorization'];
};

/**
 * Create Axios instance with base configuration
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - attach access token to all requests
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Retrieve access token from localStorage
    const accessToken = localStorage.getItem('access_token');
    
    // If token exists, attach as Bearer token
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Extended Axios request config with retry flag
 */
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

/**
 * Custom error for rate limiting
 */
export interface RateLimitError extends Error {
  retryAfter?: number;
  status: number;
}

/**
 * Response interceptor - handle success, 401 (token refresh), and 429 (rate limiting)
 */
apiClient.interceptors.response.use(
  // Success path - return response as-is
  (response) => {
    return response;
  },
  // Error path - handle 401 and 429
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig;

    // Handle 401 - Token refresh
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // Set retry flag to prevent infinite loops
      originalRequest._retry = true;

      try {
        // Retrieve refresh token from localStorage
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          // No refresh token available, clear auth and redirect
          clearAuthState();
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Call refresh endpoint
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        // Extract new access token
        const { access_token } = response.data;

        // Update localStorage
        localStorage.setItem('access_token', access_token);

        // Update Axios header for the retry request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Retry original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear auth state and redirect to login
        clearAuthState();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle 429 - Rate limiting
    if (error.response?.status === 429) {
      // Extract Retry-After header
      const retryAfter = error.response.headers['retry-after'];
      
      // Create custom error with retryAfter property
      const rateLimitError: RateLimitError = Object.assign(
        new Error('Rate limit exceeded'),
        {
          retryAfter: retryAfter ? parseInt(retryAfter, 10) : undefined,
          status: 429,
        }
      );
      
      return Promise.reject(rateLimitError);
    }

    // For all other errors, reject as-is
    return Promise.reject(error);
  }
);
