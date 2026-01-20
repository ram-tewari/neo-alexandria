# Requirements Document - Phase 0: SPA Foundation

## Introduction

Phase 0 establishes the foundational architecture for the Neo Alexandria 2.0 Single Page Application (SPA). This phase focuses on creating a robust authentication flow, proper API integration, and a scalable feature-sliced architecture that will support future development.

## Glossary

- **SPA**: Single Page Application - A web application that loads a single HTML page and dynamically updates content
- **OAuth2**: Open Authorization 2.0 - Industry-standard protocol for authorization
- **Token Refresh**: Automatic renewal of expired access tokens using refresh tokens
- **AuthGuard**: Route protection mechanism that enforces authentication requirements
- **Feature-Sliced**: Architecture pattern organizing code by business features rather than technical layers

## Requirements

### Requirement 1: Project Scaffolding

**User Story:** As a developer, I want a properly configured React + Vite + TypeScript project, so that I have a solid foundation for building the SPA.

#### Acceptance Criteria

1. THE System SHALL use React 18, Vite 5, and TypeScript 5 as the core framework
2. THE System SHALL use TanStack Router for file-based or code-based routing
3. THE System SHALL use Zustand for global state management
4. THE System SHALL use TanStack Query v5 for server state management
5. THE System SHALL use shadcn/ui with Tailwind CSS for UI components
6. THE System SHALL use Lucide React for icons
7. THE System SHALL implement a feature-sliced directory structure

### Requirement 2: API Integration Layer

**User Story:** As a developer, I want a centralized Axios client with automatic token management, so that all API requests are properly authenticated and token refresh is handled transparently.

#### Acceptance Criteria

1. THE System SHALL create an Axios instance configured with the backend base URL from environment variables
2. WHEN a request is made, THE System SHALL attach the access token from localStorage as a Bearer token
3. WHEN a 401 response is received, THE System SHALL attempt to refresh the token using the refresh endpoint
4. WHEN token refresh succeeds, THE System SHALL update localStorage and retry the original request
5. WHEN token refresh fails, THE System SHALL clear authentication state and redirect to login
6. WHEN a 429 response is received, THE System SHALL extract retry-after information and reject with a custom error
7. THE System SHALL prevent infinite retry loops by tracking retry attempts

### Requirement 3: Authentication State Management

**User Story:** As a user, I want my authentication state to persist across page refreshes, so that I don't have to log in repeatedly.

#### Acceptance Criteria

1. THE Auth_Store SHALL maintain accessToken, refreshToken, and user profile state
2. THE Auth_Store SHALL persist tokens to localStorage
3. THE Auth_Store SHALL provide an isAuthenticated computed property
4. THE Auth_Store SHALL provide setAuth and logout actions
5. WHEN logout is called, THE System SHALL clear all tokens from localStorage and state

### Requirement 4: OAuth2 Social Login

**User Story:** As a user, I want to sign in using Google or GitHub, so that I can access the application without creating a new account.

#### Acceptance Criteria

1. THE Login_Page SHALL display "Sign in to Neo Alexandria" heading
2. THE Login_Page SHALL provide a "Continue with Google" button
3. THE Login_Page SHALL provide a "Continue with GitHub" button
4. WHEN a social login button is clicked, THE System SHALL redirect to the backend OAuth2 provider endpoint
5. WHEN OAuth2 callback returns, THE System SHALL extract tokens and store them in the auth store

### Requirement 5: Route Protection

**User Story:** As a developer, I want protected routes that require authentication, so that unauthorized users cannot access sensitive application features.

#### Acceptance Criteria

1. THE System SHALL implement an AuthGuard layout route
2. WHEN an unauthenticated user accesses a protected route, THE System SHALL redirect to /login
3. WHEN an authenticated user accesses a protected route, THE System SHALL render the route content
4. THE System SHALL provide a public /login route
5. THE System SHALL provide a protected /dashboard route

### Requirement 6: Token Refresh Validation

**User Story:** As a developer, I want to validate that token refresh works correctly, so that I can ensure users won't be logged out unexpectedly.

#### Acceptance Criteria

1. THE Dashboard SHALL include a "Test Token Refresh" button
2. WHEN the test button is clicked, THE System SHALL corrupt the access token in localStorage
3. WHEN the test button is clicked, THE System SHALL trigger an API request to /auth/me
4. THE System SHALL automatically detect the 401 error and refresh the token
5. THE System SHALL successfully complete the original request after token refresh
6. THE Network_Tab SHALL show the refresh flow: failed request → refresh call → retry request

### Requirement 7: UI Component Library

**User Story:** As a developer, I want a consistent set of UI components, so that the application has a cohesive design system.

#### Acceptance Criteria

1. THE System SHALL initialize shadcn/ui with the Slate theme
2. THE System SHALL include Button, Card, Input, Label, and Toast components
3. THE System SHALL use Tailwind CSS for styling
4. THE System SHALL use CSS variables for theming
5. THE System SHALL use Lucide React for all icons
