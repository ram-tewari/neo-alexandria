import { useAuthStore } from '../store';

/**
 * Custom hook for accessing authentication state and actions
 * 
 * Provides convenient access to:
 * - Authentication state (accessToken, refreshToken, user, isAuthenticated)
 * - Authentication actions (setAuth, logout)
 * - Convenience methods (login is an alias for setAuth)
 * 
 * @example
 * ```tsx
 * const { isAuthenticated, user, login, logout } = useAuth();
 * 
 * // Check if user is authenticated
 * if (isAuthenticated) {
 *   console.log('User:', user);
 * }
 * 
 * // Login with tokens and user data
 * login({ accessToken: 'token', refreshToken: 'refresh' }, userData);
 * 
 * // Logout
 * logout();
 * ```
 */
export const useAuth = () => {
  const store = useAuthStore();

  return {
    // State
    accessToken: store.accessToken,
    refreshToken: store.refreshToken,
    user: store.user,
    isAuthenticated: store.isAuthenticated,

    // Actions
    setAuth: store.setAuth,
    logout: store.logout,
    checkTokenExpiration: store.checkTokenExpiration,

    // Convenience methods
    login: store.setAuth, // Alias for setAuth
  };
};
