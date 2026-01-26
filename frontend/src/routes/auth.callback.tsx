import { useEffect } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { apiClient } from '@/core/api/client';
import type { UserProfile } from '@/core/types/auth';

/**
 * OAuth callback route component
 * 
 * Handles the OAuth2 callback after successful authentication.
 * Extracts tokens from URL params, fetches user profile, and redirects to dashboard.
 */
const AuthCallbackComponent = () => {
  const navigate = useNavigate();
  const { access_token, refresh_token } = Route.useSearch();
  const { setAuth } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check if tokens exist
        if (!access_token || !refresh_token) {
          console.error('Missing tokens in callback URL');
          navigate({ to: '/login', search: { error: 'authentication_failed' } });
          return;
        }

        // Clear any existing auth state before setting new tokens
        // This ensures old tokens don't interfere with the new OAuth session
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('neo-alexandria-auth');
        delete apiClient.defaults.headers.common['Authorization'];

        // Fetch user profile with new token
        const response = await apiClient.get<UserProfile>('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });

        // Set auth state with new tokens and user data
        setAuth(
          { accessToken: access_token, refreshToken: refresh_token },
          response.data
        );

        // Redirect to repositories page
        navigate({ to: '/repositories' });
      } catch (error) {
        console.error('OAuth callback error:', error);
        navigate({ to: '/login', search: { error: 'authentication_failed' } });
      }
    };

    handleCallback();
  }, [access_token, refresh_token, setAuth, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
        <p className="mt-4 text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
};

/**
 * Auth callback route definition
 */
export const Route = createFileRoute('/auth/callback')({
  component: AuthCallbackComponent,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      access_token: (search.access_token as string) || '',
      refresh_token: (search.refresh_token as string) || '',
      error: (search.error as string) || undefined,
    };
  },
});
