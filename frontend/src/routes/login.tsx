import { createFileRoute, Navigate } from '@tanstack/react-router';

/**
 * Login route component
 * 
 * TEMPORARY: Redirects to workbench for Phase 1 testing
 * TODO: Restore LoginForm when authentication is needed
 */
const LoginRoute = () => {
  return <Navigate to="/repositories" />;
};

/**
 * Login route definition
 */
export const Route = createFileRoute('/login')({
  component: LoginRoute,
});
