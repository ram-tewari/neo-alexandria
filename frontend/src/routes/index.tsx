import { createFileRoute, Navigate } from '@tanstack/react-router';
import { useAuth } from '@/features/auth/hooks/useAuth';

/**
 * Index route component
 * 
 * Root route that redirects based on authentication status.
 * Authenticated users go to /dashboard, unauthenticated users go to /login.
 */
const IndexRoute = () => {
  const { isAuthenticated } = useAuth();

  // Redirect based on authentication status
  if (isAuthenticated) {
    return <Navigate to="/dashboard" />;
  }

  return <Navigate to="/login" />;
};

/**
 * Index route definition
 */
export const Route = createFileRoute('/')({
  component: IndexRoute,
});
