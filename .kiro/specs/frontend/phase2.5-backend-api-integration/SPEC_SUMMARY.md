# Phase 2.5: Backend API Integration - Spec Summary

## Status
🚧 **Ready for Implementation** - Spec Complete

## Quick Overview

Phase 2.5 bridges the gap between your beautifully implemented Phase 1 and Phase 2 frontend components and the live backend API at `https://pharos.onrender.com`. This phase replaces all mock data with real backend calls, ensuring your frontend works with production data.

## What Gets Wired Up

### Phase 1 Components → Backend (6 endpoints)
- **WorkbenchLayout** → User info, system health
- **RepositorySwitcher** → Real repository list
- **CommandPalette** → Health status, rate limits

### Phase 2 Components → Backend (29 endpoints)
- **MonacoEditorWrapper** → Real file content
- **SemanticChunkOverlay** → Real AST-based chunks
- **QualityBadgeGutter** → Real quality scores
- **AnnotationGutter/Panel** → Persistent annotations (CRUD + search + export)
- **HoverCardProvider** → Real hover information
- **ChunkMetadataPanel** → Real chunk metadata

## Key Technologies

- **axios** - HTTP client with interceptors and retry logic
- **@tanstack/react-query** - Data fetching, caching, optimistic updates
- **TypeScript** - Full type safety across frontend-backend boundary
- **MSW** - Updated test mocks matching backend schemas

## Implementation Phases

1. **Foundation** (Tasks 1-4) - Configure API client, define types, integrate Phase 1
2. **Editor Core** (Tasks 5-7) - Integrate resources and chunks
3. **Annotations & Quality** (Tasks 6-8) - Integrate CRUD, search, quality analytics
4. **Polish** (Tasks 9-14) - Hover, error handling, tests, verification

## Success Criteria

✅ Repository switcher shows actual repositories from backend  
✅ Monaco editor loads real file content  
✅ Semantic chunks display real AST-based chunks  
✅ Quality badges show real quality scores  
✅ Annotations persist to backend and sync across sessions  
✅ All API calls have proper error handling  
✅ Loading states display during API calls  
✅ All tests pass (unit, integration, property-based)  

## Files to Create/Modify

### New Files (9)
- `frontend/src/core/api/client.ts` - Core API client
- `frontend/src/lib/api/workbench.ts` - Phase 1 API client
- `frontend/src/lib/hooks/useWorkbenchData.ts` - Phase 1 query hooks
- `frontend/src/lib/hooks/useEditorData.ts` - Phase 2 query hooks
- `frontend/src/types/api.ts` - API type definitions
- `frontend/src/components/ErrorToast.tsx` - Error toast
- `frontend/src/components/ErrorMessage.tsx` - Inline error
- `frontend/src/components/RetryButton.tsx` - Retry button

### Modified Files (10+)
- `frontend/.env` - Add API base URL
- `frontend/src/lib/api/editor.ts` - Update existing stubs
- `frontend/src/stores/*.ts` - All stores (editor, annotation, chunk, quality, repository)
- `frontend/src/test/mocks/handlers.ts` - Update MSW handlers
- All Phase 1 & 2 components - Add loading/error states

## Testing Strategy

- **Unit Tests**: API client, interceptors, retry logic, hooks
- **Integration Tests**: Complete workflows (annotation CRUD, resource loading, error recovery)
- **Property-Based Tests**: 8 correctness properties (optimistic updates, cache invalidation, etc.)
- **MSW Updates**: All handlers match backend schemas

## Timeline Estimate

- **Foundation**: 1-2 days
- **Phase 1 Integration**: 1 day
- **Phase 2 Integration**: 2-3 days
- **Error Handling & Tests**: 2 days
- **Total**: 6-8 days

## Dependencies

✅ Phase 1 components implemented  
✅ Phase 2 components implemented  
✅ Backend API deployed at `https://pharos.onrender.com`  
✅ All 35 endpoints available and documented  

## Next Steps

1. Review this spec and approve
2. Start with Task 1: Configure API Client Foundation
3. Follow incremental approach with 4 checkpoints
4. Test thoroughly at each checkpoint
5. Deploy to staging for end-to-end testing

## Questions?

See the full spec documents:
- [requirements.md](./requirements.md) - 10 requirements with acceptance criteria
- [design.md](./design.md) - Complete technical design with 8 correctness properties
- [tasks.md](./tasks.md) - 14 top-level tasks with 40+ sub-tasks
- [README.md](./README.md) - Detailed overview and FAQ

---

**Ready to wire up your frontend to the backend? Let's make it real! 🚀**
