import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/core/api/client';
import type { UserProfile } from '@/core/types/auth';

/**
 * Decode JWT token and check if it's expired
 */
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= exp;
  } catch {
    return true; // If we can't decode, consider it expired
  }
}

/**
 * Authentication state interface
 */
export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
}

/**
 * Authentication actions interface
 */
export interface AuthActions {
  setAuth: (tokens: { accessToken: string; refreshToken: string }, user: AuthState['user']) => void;
  logout: () => void;
  checkTokenExpiration: () => void;
}

/**
 * Combined auth store type
 */
export type AuthStore = AuthState & AuthActions;

/**
 * Initial authentication state
 */
const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  isAuthenticated: false,
};

/**
 * Zustand auth store with persistence
 */
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      /**
       * Set authentication state
       * Updates tokens, user, and Axios default Authorization header
       */
      setAuth: (tokens, user) => {
        // Update localStorage
        localStorage.setItem('access_token', tokens.accessToken);
        localStorage.setItem('refresh_token', tokens.refreshToken);

        // Update Axios default Authorization header
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${tokens.accessToken}`;

        // Update store state
        set({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
          user,
          isAuthenticated: true,
        });
      },

      /**
       * Clear authentication state
       * Removes tokens, user, and clears Axios default Authorization header
       */
      logout: () => {
        // Remove from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        // Clear Axios default Authorization header
        delete apiClient.defaults.headers.common['Authorization'];

        // Reset store state
        set(initialState);
      },

      /**
       * Check if access token is expired and logout if needed
       */
      checkTokenExpiration: () => {
        const state = useAuthStore.getState();
        if (state.accessToken && isTokenExpired(state.accessToken)) {
          // Token is expired, logout user
          state.logout();
          // Redirect to login
          window.location.href = '/login';
        }
      },
    }),
    {
      name: 'neo-alexandria-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // After rehydration, restore Axios header and isAuthenticated if token exists
        if (state?.accessToken) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${state.accessToken}`;
          // Ensure isAuthenticated is set correctly after rehydration
          state.isAuthenticated = true;
        }
      },
    }
  )
);
