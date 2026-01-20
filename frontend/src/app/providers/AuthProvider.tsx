import { ReactNode, useEffect } from 'react';
import { useAuthStore } from '@/features/auth/store';
import { apiClient } from '@/core/api/client';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider initializes authentication state on mount,
 * syncs localStorage with the auth store, and periodically
 * checks for token expiration.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const { accessToken, checkTokenExpiration } = useAuthStore();

  useEffect(() => {
    // Initialize auth state from localStorage on mount
    const storedAccessToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');

    if (storedAccessToken && storedRefreshToken) {
      // Sync Axios header with stored token
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedAccessToken}`;
    }

    // Check token expiration immediately on mount
    checkTokenExpiration();

    // Set up periodic token expiration check (every minute)
    const intervalId = setInterval(() => {
      checkTokenExpiration();
    }, 60000); // 60 seconds

    // Cleanup interval on unmount
    return () => clearInterval(intervalId);
  }, [checkTokenExpiration]);

  return <>{children}</>;
}
