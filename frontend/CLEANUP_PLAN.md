# Frontend Cleanup Plan

## What to Keep (Auth Only)

### Core Auth Files
- `src/features/auth/` - Entire auth feature directory
- `src/routes/login.tsx` - Login page
- `src/routes/auth.callback.tsx` - OAuth callback
- `src/routes/_auth.tsx` - Auth layout wrapper
- `src/app/providers/AuthProvider.tsx` - Auth provider

### Supporting Files
- `src/core/api/client.ts` - API client (needed for auth)
- `src/lib/utils.ts` - Utility functions
- `src/components/ui/` - UI primitives (we'll rebuild with new MCP servers)

### Config Files (Keep)
- `package.json`
- `tsconfig.json`
- `vite.config.ts`
- `tailwind.config.js`
- `postcss.config.js`

## What to Delete

### Old Feature Code
- `src/features/search/` - Will rebuild from scratch
- `src/features/recommendations/` - Will rebuild from scratch
- `src/features/resources/` - Will rebuild from scratch
- `src/features/monitoring/` - Will rebuild from scratch

### Old Routes
- `src/routes/_auth.dashboard.tsx` - Will rebuild
- `src/routes/_auth.resources.tsx` - Will rebuild
- `src/routes/_auth.search.tsx` - Will rebuild
- `src/routes/index.tsx` - Will rebuild

### Old Components
- `src/components/layout/` - Will rebuild with new design

### Old Types (except auth)
- `src/core/types/resource.ts` - Will rebuild based on new backend

## Cleanup Commands

```bash
# Delete old features (except auth)
rm -rf frontend/src/features/search
rm -rf frontend/src/features/recommendations
rm -rf frontend/src/features/resources
rm -rf frontend/src/features/monitoring

# Delete old routes (except auth)
rm frontend/src/routes/_auth.dashboard.tsx
rm frontend/src/routes/_auth.resources.tsx
rm frontend/src/routes/_auth.search.tsx
rm frontend/src/routes/index.tsx
rm frontend/src/routes/-_auth.resources.test.tsx

# Delete old layout
rm -rf frontend/src/components/layout

# Delete old types (except what auth needs)
rm frontend/src/core/types/resource.ts

# Delete old specs
rm -rf .kiro/specs/frontend/phase2-discovery-search
```

## Post-Cleanup Structure

```
frontend/src/
├── app/
│   └── providers/
│       └── AuthProvider.tsx ✅
├── features/
│   └── auth/ ✅
├── routes/
│   ├── __root.tsx ✅
│   ├── _auth.tsx ✅
│   ├── login.tsx ✅
│   └── auth.callback.tsx ✅
├── core/
│   └── api/
│       └── client.ts ✅
├── lib/
│   └── utils.ts ✅
├── components/
│   └── ui/ ✅ (will enhance with MCP servers)
└── main.tsx ✅
```

## Next Steps After Cleanup

1. Update `src/routes/__root.tsx` to remove references to deleted routes
2. Create new route structure based on Phase 1 spec
3. Start building Phase 1: Core Workbench & Navigation
