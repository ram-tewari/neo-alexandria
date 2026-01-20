import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

/**
 * Dashboard route component
 * 
 * Main dashboard page for authenticated users.
 * Displays welcome message and provides test buttons for token refresh and logout.
 */
const DashboardComponent = () => {
  const { user, logout } = useAuth();
  const [isTestingRefresh, setIsTestingRefresh] = useState(false);

  /**
   * Test token refresh by corrupting the access token
   * 
   * Test Flow:
   * 1. Corrupt the access_token in localStorage
   * 2. Make API call to /auth/me (will fail with 401)
   * 3. Axios interceptor detects 401 and calls /auth/refresh
   * 4. New tokens are stored and original request is retried
   * 5. Request succeeds with new token
   * 
   * Open Network tab in DevTools to observe:
   * - Failed /auth/me (401)
   * - /auth/refresh (200)
   * - Retry /auth/me (200)
   */
  const handleTestTokenRefresh = async () => {
    setIsTestingRefresh(true);
    
    try {
      // Step 1: Corrupt the access token
      console.log('🔧 Corrupting token...');
      localStorage.setItem('access_token', 'corrupted-token');
      
      // Step 2: Make API request that will trigger refresh
      console.log('📡 Making API request...');
      const { apiClient } = await import('@/core/api/client');
      
      // This will fail with 401, trigger refresh, then succeed
      await apiClient.get('/auth/me');
      
      // Step 3: Success - token was refreshed automatically
      console.log('✅ Token refresh triggered');
      console.log('✅ Request succeeded after refresh');
      
      toast.success('Token refresh successful!', {
        description: 'Check the Network tab to see the refresh flow.',
      });
    } catch (error) {
      console.error('❌ Token refresh test failed:', error);
      toast.error('Token refresh failed', {
        description: 'Check console for error details.',
      });
    } finally {
      setIsTestingRefresh(false);
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">Welcome to Neo Alexandria</CardTitle>
          <CardDescription>
            {user ? `Signed in as ${user.email}` : 'Your knowledge management system'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {user && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                <strong>Name:</strong> {user.name}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Email:</strong> {user.email}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>Provider:</strong> {user.provider}
              </p>
            </div>
          )}

          <div className="flex gap-4 pt-4">
            <Button 
              onClick={handleTestTokenRefresh} 
              variant="outline"
              disabled={isTestingRefresh}
            >
              {isTestingRefresh ? 'Testing...' : 'Test Token Refresh'}
            </Button>
            <Button onClick={handleLogout} variant="destructive">
              Logout
            </Button>
          </div>

          <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-4">
            <p className="text-sm text-blue-800">
              <strong>Test Token Refresh:</strong> Click the "Test Token Refresh" button to simulate
              a token expiration. Open the Network tab in DevTools to see the automatic token refresh flow:
              failed /auth/me (401) → /auth/refresh (200) → retry /auth/me (200)
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

/**
 * Dashboard route definition
 */
export const Route = createFileRoute('/_auth/dashboard')({
  component: DashboardComponent,
});
