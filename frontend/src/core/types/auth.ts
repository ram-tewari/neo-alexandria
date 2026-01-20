/**
 * Authentication type definitions
 */

/**
 * User profile information
 */
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  provider: string;
}

/**
 * OAuth token response
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * Authentication state
 */
export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
}
