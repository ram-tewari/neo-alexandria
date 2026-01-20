import { createFileRoute, Outlet, Navigate } from '@tanstack/react-router';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';

/**
 * Protected layout route component (AuthGuard)
 * 
 * Wraps protected routes and ensures user is authenticated.
 * Redirects to login if not authenticated.
 * Renders layout with Sidebar, Header, and nested routes.
 */
const AuthLayout = () => {
  const { isAuthenticated } = useAuth();

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Render protected layout
  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

/**
 * Protected layout route definition
 */
export const Route = createFileRoute('/_auth')({
  component: AuthLayout,
});
