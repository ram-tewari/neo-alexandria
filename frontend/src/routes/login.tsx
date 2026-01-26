import { createFileRoute } from '@tanstack/react-router';
import { LoginForm } from '@/features/auth/components/LoginForm';

/**
 * Login route component
 * 
 * Displays OAuth2 login form with Google and GitHub options.
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
