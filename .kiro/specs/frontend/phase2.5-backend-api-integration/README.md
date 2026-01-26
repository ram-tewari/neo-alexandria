# Phase 2.5: Backend API Integration

## Status
🚧 **Not Started** - Spec Complete, Ready for Implementation

## Overview
Phase 2.5 connects the frontend components built in Phase 1 (Workbench & Navigation) and Phase 2 (Living Code Editor) to the live backend API at `https://pharos.onrender.com`. This phase replaces all mock data with real backend calls, adds proper error handling, and ensures the frontend can operate with production data.

## What This Phase Delivers

### Core Functionality
- ✅ Configured API client with authentication and retry logic
- ✅ Phase 1 components connected to backend (user info, resources, health)
- ✅ Phase 2 components connected to backend (editor, chunks, annotations, quality)
- ✅ Real-time data synchronization with optimistic updates
- ✅ Comprehensive error handling with user-friendly messages
- ✅ Loading states for all async operations
- ✅ TypeScript types matching backend schemas

### API Endpoints Integrated

**Phase 1 (6 endpoints)**:
- `/api/auth/me` - Current user info
- `/api/auth/rate-limit` - Rate limit status
- `/api/auth/health` - Auth health check
- `/resources` - List resources
- `/resources/health` - Resources health
- `/api/monitoring/health` - System health

**Phase 2 (29 endpoints)**:
- Resource & Chunks (5): `/resources/{id}`, `/resources/{id}/chunks`, `/chunks/{id}`, etc.
- Annotations (8): CRUD + search (fulltext, semantic, tags) + export (markdown, json)
- Quality (8): Recalculate, outliers, degradation, distribution, trends, dimensions, review queue
- Graph (1): `/api/graph/hover` - Hover information

**Total: 35 endpoints integrated**

## Dependencies

### Prerequisites
- Phase 1 components implemented ✅
- Phase 2 components implemented ✅
- Backend API deployed at `https://pharos.onrender.com` ✅
- Environment variables configured (`.env`) ✅
- **Admin token for testing** ✅ (see [AUTH_SETUP.md](./AUTH_SETUP.md))

### Required Libraries
- `axios` - HTTP client
- `@tanstack/react-query` - Data fetching and caching
- `zustand` - State management (already installed)
- `zod` (optional) - Runtime type validation

## Before You Start

**⚠️ IMPORTANT**: You need a valid authentication token to test against the production backend.

See [AUTH_SETUP.md](./AUTH_SETUP.md) for instructions on setting up your admin token.

**Quick Setup**:
1. Run `python backend/scripts/create_admin_token.py`
2. Copy the token to browser localStorage
3. Start implementing Phase 2.5!

## Key Design Decisions

### 1. TanStack Query for Data Fetching
**Why**: Provides built-in caching, request deduplication, optimistic updates, and retry logic. Reduces boilerplate compared to manual fetch management.

### 2. Optimistic Updates for Mutations
**Why**: Improves perceived performance by updating UI immediately, then confirming with backend. Reverts on failure.

### 3. Exponential Backoff for Retries
**Why**: Prevents overwhelming the backend during outages. Gives transient errors time to resolve.

### 4. Separate API Client Modules
**Why**: Keeps code organized by feature domain (workbench, editor). Makes it easy to find and update endpoints.

### 5. TypeScript Types from Backend Schemas
**Why**: Ensures type safety across frontend-backend boundary. Catches schema mismatches at compile time.

## Implementation Strategy

### Phase 1: Foundation (Tasks 1-4)
1. Configure API client with interceptors
2. Define TypeScript types
3. Integrate Phase 1 endpoints
4. Verify workbench displays real data

### Phase 2: Editor Core (Tasks 5-7)
1. Integrate resource and chunk endpoints
2. Update editor and chunk stores
3. Verify Monaco editor loads real content

### Phase 3: Annotations & Quality (Tasks 6-8)
1. Integrate annotation CRUD and search
2. Integrate quality analytics endpoints
3. Verify annotations persist and quality badges display

### Phase 4: Polish (Tasks 9-14)
1. Add hover API integration
2. Implement comprehensive error handling
3. Update test mocks
4. Write property-based and integration tests
5. Final verification

## Testing Strategy

### Unit Tests
- API client interceptors and retry logic
- TanStack Query hooks (caching, invalidation)
- Zustand store actions
- Error handling utilities

### Integration Tests
- Complete annotation lifecycle (create → read → update → delete)
- Resource loading flow (fetch → display → chunks)
- Quality data flow (fetch → recalculate → refresh)
- Error recovery (failure → retry → success)
- Authentication flow (login → fetch user → access resources)

### Property-Based Tests
- Authentication token persistence
- Optimistic update consistency
- Cache invalidation correctness
- Error code mapping
- Loading state visibility
- Debounce consistency

## Success Criteria

- [ ] All Phase 1 components display real data from backend
- [ ] All Phase 2 components display real data from backend
- [ ] Repository switcher shows actual repositories
- [ ] Monaco editor loads real file content
- [ ] Semantic chunks display real AST-based chunks
- [ ] Quality badges show real quality scores
- [ ] Annotations are persisted to backend
- [ ] All API calls include proper error handling
- [ ] Loading states are shown during API calls
- [ ] All tests pass (unit, integration, property-based)

## Files Modified

### New Files
- `frontend/src/core/api/client.ts` - Core API client
- `frontend/src/lib/api/workbench.ts` - Phase 1 API client
- `frontend/src/lib/api/editor.ts` - Phase 2 API client (update existing)
- `frontend/src/lib/hooks/useWorkbenchData.ts` - Phase 1 query hooks
- `frontend/src/lib/hooks/useEditorData.ts` - Phase 2 query hooks
- `frontend/src/types/api.ts` - API type definitions
- `frontend/src/components/ErrorToast.tsx` - Error toast component
- `frontend/src/components/ErrorMessage.tsx` - Inline error component
- `frontend/src/components/RetryButton.tsx` - Retry button component

### Modified Files
- `frontend/.env` - Add API base URL and configuration
- `frontend/src/stores/editor.ts` - Use real API data
- `frontend/src/stores/annotation.ts` - Use real API data
- `frontend/src/stores/chunk.ts` - Use real API data
- `frontend/src/stores/quality.ts` - Use real API data
- `frontend/src/stores/repository.ts` - Use real API data
- `frontend/src/test/mocks/handlers.ts` - Update MSW handlers
- All Phase 1 and Phase 2 components - Add loading/error states

## Related Documentation

- [Phase 1 Spec](.kiro/specs/frontend/phase1-workbench-navigation/)
- [Phase 2 Spec](.kiro/specs/frontend/phase2-living-code-editor/)
- [Backend API Documentation](../../../backend/docs/ACTUAL_ENDPOINTS.md)
- [Frontend Roadmap](.kiro/specs/frontend/ROADMAP.md)

## Next Steps

1. Review and approve this spec
2. Start implementation with Task 1 (API Client Foundation)
3. Follow incremental approach with checkpoints
4. Test thoroughly at each checkpoint
5. Deploy to staging for end-to-end testing

## Questions?

- **Q: Why not use native fetch instead of axios?**
  - A: Axios provides better error handling, request/response interceptors, and automatic JSON parsing. It's also more widely used and has better TypeScript support.

- **Q: Why TanStack Query instead of SWR or RTK Query?**
  - A: TanStack Query has the best TypeScript support, most flexible caching, and excellent devtools. It's also framework-agnostic.

- **Q: Should we implement all optional test tasks?**
  - A: For MVP, you can skip optional tasks. However, property-based tests and integration tests are highly recommended for production readiness.

- **Q: How do we handle API versioning?**
  - A: The backend API is currently unversioned. If versioning is added later, we'll update the base URL to include `/v1/` or similar.

- **Q: What about WebSocket support for real-time updates?**
  - A: Not in scope for Phase 2.5. This will be addressed in a future phase if needed.
