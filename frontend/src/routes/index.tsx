import { createFileRoute, Navigate } from '@tanstack/react-router';

/**
 * Index route - redirects to /repositories
 * 
 * Note: TanStack Router will automatically resolve this to /_auth/repositories
 * since repositories is a child route of _auth
 */
export const Route = createFileRoute('/')({
  component: () => <Navigate to="/repositories" />,
});
