# Neo Alexandria 2.0 - Frontend

React-based single-page application (SPA) for Neo Alexandria 2.0, an advanced knowledge management system.

## Tech Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool and dev server
- **TanStack Router 6** - Type-safe routing
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Lucide React** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Application-level code
│   │   └── providers/          # React context providers
│   │       ├── QueryProvider.tsx
│   │       └── AuthProvider.tsx
│   ├── components/             # Reusable components
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── ui/                 # shadcn/ui components
│   ├── core/                   # Core utilities
│   │   ├── api/                # API client configuration
│   │   │   └── client.ts       # Axios instance with interceptors
│   │   └── types/              # TypeScript type definitions
│   │       ├── auth.ts
│   │       └── api.ts
│   ├── features/               # Feature modules
│   │   └── auth/               # Authentication feature
│   │       ├── components/     # Auth-specific components
│   │       ├── hooks/          # Auth hooks
│   │       └── store.ts        # Auth state management
│   ├── lib/                    # Utility functions
│   │   └── utils.ts
│   ├── routes/                 # TanStack Router routes
│   │   ├── __root.tsx          # Root layout
│   │   ├── index.tsx           # Home page (redirects)
│   │   ├── login.tsx           # Login page
│   │   ├── auth.callback.tsx   # OAuth callback handler
│   │   ├── _auth.tsx           # Protected layout
│   │   └── _auth.dashboard.tsx # Dashboard page
│   ├── App.tsx                 # App component (legacy)
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
├── components.json             # shadcn/ui configuration
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── tailwind.config.js          # Tailwind CSS configuration
```

## Available Scripts

### Development

```bash
# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Testing

```bash
# Run tests (when implemented)
npm test
```

## Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API base URL
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** Vite requires environment variables to be prefixed with `VITE_` to be exposed to the client.

## Development Workflow

### 1. Initial Setup

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update VITE_API_BASE_URL if needed
```

### 2. Start Development

```bash
# Start backend server (in separate terminal)
cd ../backend
uvicorn app.main:app --reload

# Start frontend dev server
npm run dev
```

### 3. Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Authentication Flow

### OAuth2 Login

1. User clicks "Continue with Google" or "Continue with GitHub"
2. Frontend redirects to backend OAuth endpoint (`/auth/google` or `/auth/github`)
3. Backend redirects to OAuth provider (Google/GitHub)
4. User authorizes application
5. OAuth provider redirects back to backend with authorization code
6. Backend exchanges code for tokens and user info
7. Backend redirects to frontend callback (`/auth/callback?access_token=...&refresh_token=...`)
8. Frontend stores tokens and fetches user profile
9. Frontend redirects to dashboard

### Token Management

- **Access Token**: Short-lived JWT stored in localStorage and Axios headers
- **Refresh Token**: Long-lived token for obtaining new access tokens
- **Automatic Refresh**: Axios interceptor detects 401 errors and refreshes tokens automatically
- **Token Storage**: Tokens persisted in localStorage and Zustand store

### Route Protection

- Protected routes use `_auth.tsx` layout route
- Layout checks authentication status
- Unauthenticated users redirected to `/login`
- Authenticated users can access protected routes

## Key Features

### Implemented (Phase 0)

- ✅ OAuth2 authentication (Google, GitHub)
- ✅ Automatic token refresh on 401 errors
- ✅ Protected routes with auth guard
- ✅ Persistent authentication state
- ✅ User profile display
- ✅ Responsive layout with sidebar and header
- ✅ Toast notifications
- ✅ Rate limit error handling (429)

### Planned

- 📋 Resource library UI
- 📋 Search interface
- 📋 Collection management
- 📋 Knowledge graph visualization
- 📋 Annotations and highlights
- 📋 Recommendations

## Troubleshooting

### "Cannot connect to backend"

**Problem:** Frontend cannot reach backend API

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `VITE_API_BASE_URL` in `.env` file
3. Ensure no CORS issues (backend should allow `http://localhost:5173`)
4. Check browser console for network errors

### "OAuth redirect not working"

**Problem:** OAuth flow fails or redirects to wrong URL

**Solutions:**
1. Verify OAuth credentials configured in backend `.env`
2. Check OAuth callback URL matches backend configuration
3. Ensure backend redirect URL includes frontend callback: `http://localhost:5173/auth/callback`
4. Check browser console for errors during redirect

### "Token refresh not working"

**Problem:** Token refresh fails or causes infinite loops

**Solutions:**
1. Check refresh token exists in localStorage: `localStorage.getItem('refresh_token')`
2. Verify backend `/auth/refresh` endpoint is working
3. Check Axios interceptor logic in `src/core/api/client.ts`
4. Look for `_retry` flag to prevent infinite loops
5. Test with "Test Token Refresh" button on dashboard

### "Protected routes not working"

**Problem:** Can access protected routes without authentication

**Solutions:**
1. Verify `_auth.tsx` layout route is checking authentication
2. Check auth state in Zustand store: `useAuthStore.getState()`
3. Ensure tokens are stored in localStorage
4. Check browser console for navigation errors

### "Styles not loading"

**Problem:** Tailwind CSS or component styles not applied

**Solutions:**
1. Verify Tailwind CSS is configured: `tailwind.config.js`
2. Check `index.css` imports Tailwind directives
3. Restart dev server: `npm run dev`
4. Clear browser cache and hard reload

### "TypeScript errors"

**Problem:** Type errors in IDE or build

**Solutions:**
1. Ensure all dependencies installed: `npm install`
2. Check `tsconfig.json` path aliases configured
3. Restart TypeScript server in IDE
4. Run type check: `npx tsc --noEmit`

## Testing Token Refresh

The dashboard includes a "Test Token Refresh" button to validate the automatic token refresh flow:

1. Log in successfully
2. Navigate to `/dashboard`
3. Open browser DevTools → Network tab
4. Click "Test Token Refresh" button
5. Observe the network requests:
   - Failed `/auth/me` (401 Unauthorized)
   - `/auth/refresh` (200 OK)
   - Retry `/auth/me` (200 OK)
6. Verify success toast appears
7. Verify dashboard still works after refresh

## Code Style

- Use TypeScript for all new files
- Follow React hooks best practices
- Use functional components (no class components)
- Prefer named exports over default exports
- Use Tailwind CSS for styling (avoid inline styles)
- Add JSDoc comments for exported functions
- Use meaningful variable and function names

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run linter: `npm run lint`
4. Commit changes: `git commit -m "feat: add my feature"`
5. Push branch: `git push origin feature/my-feature`
6. Create pull request

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Vite Documentation](https://vitejs.dev)
- [TanStack Router](https://tanstack.com/router)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://github.com/pmndrs/zustand)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)

## License

See root LICENSE file.
