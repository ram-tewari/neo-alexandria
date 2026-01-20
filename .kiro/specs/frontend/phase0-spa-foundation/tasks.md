# Implementation Plan: Phase 0 - SPA Foundation

## Overview

This document provides a step-by-step implementation guide for Phase 0: SPA Foundation. Each task builds on the previous one to create a complete authentication-enabled React SPA.

## Tasks

- [x] 1. Project Setup and Dependencies
  - [x] 1.1 Initialize Vite + React + TypeScript project
  - [x] 1.2 Install core dependencies (TanStack Router, TanStack Query, Zustand, Axios)
  - [x] 1.3 Install UI dependencies (Tailwind CSS, shadcn/ui, Lucide React)
  - [x] 1.4 Install shadcn/ui components (Button, Card, Input, Label, Toast)
  - [x] 1.5 Create directory structure (app, core, components, features, routes, lib)
  - [x] 1.6 Configure environment variables, Tailwind, and path aliases
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 7.1_

- [x] 2. Type Definitions and API Client Setup
  - [x] 2.1 Create auth type definitions
    - Create `src/core/types/auth.ts`
    - Define `UserProfile` interface (id, email, name, avatar_url, provider)
    - Define `TokenResponse` interface (access_token, refresh_token, token_type)
    - Define `AuthState` interface (accessToken, refreshToken, user, isAuthenticated)
  - [x] 2.2 Create API type definitions
    - Create `src/core/types/api.ts`
    - Define `ApiError` interface (detail, status, retryAfter?)
    - Define `ApiResponse<T>` generic interface (data, message?)
  - [x] 2.3 Create Axios client base configuration
    - Create `src/core/api/client.ts`
    - Import axios and create instance
    - Set baseURL from `import.meta.env.VITE_API_BASE_URL`
    - Set timeout to 30000ms
    - Set default Content-Type header to application/json
  - _Requirements: 2.1_

- [x] 3. Axios Interceptors for Token Management
  - [x] 3.1 Implement request interceptor
    - Add request interceptor to Axios instance
    - Retrieve `access_token` from localStorage
    - If token exists, attach as `Authorization: Bearer <token>`
    - Return modified config
  - [x] 3.2 Implement response interceptor - success path
    - Add response interceptor to Axios instance
    - On success, return response as-is
  - [x] 3.3 Implement response interceptor - 401 handling (token refresh)
    - Check for 401 status in error handler
    - Check if request has `_retry` flag to prevent infinite loops
    - If not a retry, set `_retry = true` on original request config
    - Retrieve `refresh_token` from localStorage
    - Call `POST /auth/refresh` with refresh_token in body
    - On success: extract new access_token, update localStorage, update Axios header, retry original request
    - On failure: clear localStorage, clear auth store, redirect to `/login`
  - [x] 3.4 Implement response interceptor - 429 handling (rate limiting)
    - Check for 429 status in error handler
    - Extract `Retry-After` header from response
    - Create custom error object with `retryAfter` property
    - Reject with custom error
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

[x] 4. Authentication State Management
  - [x] 4.1 Create Zustand auth store
    - Create `src/features/auth/store.ts`
    - Import `create` from zustand and `persist` middleware
    - Define `AuthState` interface with accessToken, refreshToken, user, isAuthenticated
    - Define `AuthActions` interface with setAuth and logout
  - [x] 4.2 Implement setAuth action
    - Update accessToken, refreshToken, and user in store
    - Update localStorage with new tokens
    - Update Axios default Authorization header
  - [x] 4.3 Implement logout action
    - Clear accessToken, refreshToken, and user from store
    - Remove tokens from localStorage
    - Clear Axios default Authorization header
  - [x] 4.4 Add persist middleware
    - Wrap store with persist middleware
    - Set storage name to 'neo-alexandria-auth'
    - Configure to persist accessToken, refreshToken, and user
    - Exclude isAuthenticated from persistence (computed property)
  - [x] 4.5 Create useAuth hook
    - Create `src/features/auth/hooks/useAuth.ts`
    - Export hook that returns auth store state and actions
    - Add convenience methods (login, logout, isAuthenticated)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. OAuth2 Login Flow and Routing
  - [x] 5.1 Create LoginForm component
    - Create `src/features/auth/components/LoginForm.tsx`
    - Import Button and Card from shadcn/ui
    - Add "Sign in to Neo Alexandria" heading
    - Add "Continue with Google" button with Google icon (from Lucide)
    - Add "Continue with GitHub" button with GitHub icon (from Lucide)
    - Style with Tailwind classes
  - [x] 5.2 Implement OAuth2 redirect logic
    - Create `handleGoogleLogin` function
    - Redirect to `${API_URL}/auth/google` using `window.location.href`
    - Create `handleGitHubLogin` function
    - Redirect to `${API_URL}/auth/github` using `window.location.href`
    - Attach functions to button onClick handlers
  - [x] 5.3 Create OAuth callback route
    - Create `src/routes/auth.callback.tsx`
    - Extract `access_token` and `refresh_token` from URL search params
    - If tokens exist: call `GET /auth/me`, call `setAuth`, redirect to `/dashboard`
    - If tokens missing: redirect to `/login` with error message
  - [x] 5.4 Configure TanStack Router
    - Create `src/routes/__root.tsx` as root layout
    - Import Outlet from TanStack Router
    - Add QueryClientProvider and Toaster to root layout
    - Create router instance in `src/main.tsx`
    - Wrap app with RouterProvider
  - [x] 5.5 Create public login route
    - Create `src/routes/login.tsx`
    - Import and render LoginForm component
    - Add route metadata (title, description)
    - Configure as public route (no auth required)
  - [x] 5.6 Create protected layout route (AuthGuard)
    - Create `src/routes/_auth.tsx` as layout route
    - Import useAuth hook
    - Check `isAuthenticated` in component
    - If false, redirect to `/login` using Navigate component
    - If true, render layout with Sidebar, Header, and Outlet
  - [x] 5.7 Create dashboard route
    - Create `src/routes/_auth.dashboard.tsx`
    - Add "Welcome to Neo Alexandria" heading
    - Add "Test Token Refresh" button (for Task 7)
    - Add logout button
    - Style with Tailwind classes
  - [x] 5.8 Create index route redirect
    - Create `src/routes/index.tsx`
    - Check `isAuthenticated`
    - If true, redirect to `/dashboard`
    - If false, redirect to `/login`
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Application Providers and Layout Components
  - [x] 6.1 Create QueryClient provider
    - Create `src/app/providers/QueryProvider.tsx`
    - Import QueryClient and QueryClientProvider from TanStack Query
    - Create QueryClient instance with default options (staleTime: 5min, cacheTime: 10min, refetchOnWindowFocus: false)
    - Wrap children with QueryClientProvider
    - Add ReactQueryDevtools in development mode
  - [x] 6.2 Create Auth provider
    - Create `src/app/providers/AuthProvider.tsx`
    - Import useAuthStore
    - Initialize auth state on mount
    - Sync localStorage with store on mount
    - Wrap children with provider
  - [x] 6.3 Update App.tsx with providers
    - Import QueryProvider and AuthProvider
    - Wrap app with providers in correct order: QueryProvider → AuthProvider → RouterProvider
    - Add Toaster component for toast notifications
  - [x] 6.4 Create Header component
    - Create `src/components/layout/Header.tsx`
    - Add app logo and title
    - Add user profile dropdown (if authenticated)
    - Add logout button in dropdown
    - Style with Tailwind classes
  - [x] 6.5 Create Sidebar component
    - Create `src/components/layout/Sidebar.tsx`
    - Add navigation links: Dashboard, Library, Search, Collections
    - Highlight active route
    - Style with Tailwind classes
  - _Requirements: 1.7, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Token Refresh Validation Feature
  - [x] 7.1 Implement test token refresh button
    - In Dashboard component, add "Test Token Refresh" button
    - On click, corrupt access_token in localStorage: `localStorage.setItem('access_token', 'corrupted-token')`
    - Immediately make API call to `GET /auth/me`
    - Display loading state during request
    - Display success/error toast after request completes
  - [x] 7.2 Add network monitoring instructions
    - Add comment in Dashboard component explaining test flow
    - Add console.log statements for debugging: "Corrupting token...", "Making API request...", "Token refresh triggered", "Request succeeded after refresh"
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 8. Testing, Documentation, and Cleanup
  - [ ] 8.1 Manual OAuth flow test
    - Start backend server
    - Start frontend dev server
    - Navigate to `/login`
    - Click "Continue with Google"
    - Verify redirect to Google OAuth
    - Complete OAuth flow
    - Verify redirect back to frontend callback
    - Verify tokens stored in localStorage
    - Verify redirect to `/dashboard`
    - Verify user profile displayed
  - [ ] 8.2 Manual token refresh test
    - Log in successfully
    - Navigate to `/dashboard`
    - Click "Test Token Refresh" button
    - Open Network tab in DevTools
    - Verify sequence: failed /auth/me (401) → /auth/refresh (200) → retry /auth/me (200)
    - Verify dashboard still works after refresh
  - [ ] 8.3 Manual logout test
    - Log in successfully
    - Navigate to `/dashboard`
    - Click logout button
    - Verify redirect to `/login`
    - Verify localStorage cleared
    - Verify cannot access `/dashboard` (redirects to login)
  - [ ] 8.4 Manual route protection test
    - Clear localStorage
    - Navigate to `/dashboard` directly
    - Verify redirect to `/login`
    - Log in
    - Verify redirect to `/dashboard`
    - Verify can access protected routes
  - [ ] 8.5 Manual 429 rate limit test
    - Log in successfully
    - Open browser console
    - Make rapid API requests (spam a button)
    - Verify 429 response in Network tab
    - Verify error toast displays with retry-after message
  - [x] 8.6 Create frontend README
    - Create `frontend/README.md`
    - Document project structure
    - Document available scripts
    - Document environment variables
    - Document development workflow
    - Add troubleshooting section
  - [x] 8.7 Add code comments and cleanup
    - Add JSDoc comments to all exported functions
    - Add inline comments for complex logic (especially Axios interceptors)
    - Add TODO comments for future improvements
    - Remove debug console.logs
    - Keep only essential logging
    - Use proper log levels (info, warn, error)
  - [x] 8.8 Update .gitignore
    - Ensure `.env` is ignored
    - Ensure `node_modules/` is ignored
    - Ensure `dist/` is ignored
    - Ensure `.DS_Store` is ignored
  - _Requirements: All (validation and documentation)_

## Completion Criteria

Phase 0 is complete when:

- [ ] All 8 tasks are checked off
- [ ] All manual tests pass
- [ ] OAuth flow works end-to-end
- [ ] Token refresh works automatically
- [ ] Route protection works correctly
- [ ] UI components render properly
- [ ] No console errors in browser
- [ ] Documentation is complete

## Next Steps

After Phase 0 completion:
1. Phase 1: Resource Library UI
2. Phase 2: Search Interface
3. Phase 3: Collection Management
4. Phase 4: Knowledge Graph Visualization
5. Phase 5: Advanced Features (Annotations, Recommendations)

## Notes

- Tasks should be completed in order to avoid dependency issues
- Each task can be completed in a single development session
- Use Git commits after each task for easy rollback
- Test frequently to catch issues early
- Refer to design.md for implementation details
