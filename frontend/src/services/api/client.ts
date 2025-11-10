import axios, { AxiosInstance, AxiosError } from 'axios';

// Create axios instance with configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth tokens if available
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Handle unauthorized - could redirect to login
      console.error('Unauthorized access');
      // Optional: Clear auth token and redirect
      // localStorage.removeItem('auth_token');
      // window.location.href = '/login';
    }
    
    if (error.response?.status === 403) {
      console.error('Forbidden access');
    }
    
    if (error.response?.status === 404) {
      console.error('Resource not found');
    }
    
    if (error.response?.status && error.response.status >= 500) {
      console.error('Server error');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
