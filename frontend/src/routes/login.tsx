import { createFileRoute } from '@tanstack/react-router';
import { LoginForm } from '@/features/auth/components/LoginForm';

/**
 * Login route component
 * 
 * Public route that displays the OAuth login form.
 * No authentication required to access this route.
 */
const LoginRoute = () => {
  return <LoginForm />;
};

/**
 * Login route definition
 */
export const Route = createFileRoute('/login')({
  component: LoginRoute,
});
