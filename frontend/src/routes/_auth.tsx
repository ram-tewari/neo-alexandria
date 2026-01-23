import { createFileRoute, Outlet } from '@tanstack/react-router';
// import { useAuth } from '@/features/auth/hooks/useAuth';
import { WorkbenchLayout } from '@/layouts/WorkbenchLayout';

/**
 * Protected layout route component (AuthGuard)
 * 
 * Wraps protected routes and ensures user is authenticated.
 * Redirects to login if not authenticated.
 * Renders WorkbenchLayout with sidebar, header, and nested routes.
 * 
 * NOTE: Auth check temporarily disabled for Phase 1 workbench testing
 */
const AuthLayout = () => {
  // const { isAuthenticated } = useAuth();

  // // Redirect to login if not authenticated
  // if (!isAuthenticated) {
  //   return <Navigate to="/login" />;
  // }

  // Render protected layout with workbench (auth check disabled for Phase 1)
  return (
    <WorkbenchLayout>
      <Outlet />
    </WorkbenchLayout>
  );
};

/**
 * Protected layout route definition
 */
export const Route = createFileRoute('/_auth')({
  component: AuthLayout,
});
