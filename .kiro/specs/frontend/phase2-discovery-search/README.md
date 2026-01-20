# Phase 2: Discovery & Search - Specification

## Status: Ready for Implementation

**Created**: January 8, 2026  
**Last Updated**: January 8, 2026  
**Owner**: Frontend Team  
**Priority**: High

## Overview

Phase 2 implements the "Consumer" side of Neo Alexandria, enabling users to discover and search their knowledge base using advanced Hybrid Search and personalized recommendations.

## Quick Links

- [Requirements](./requirements.md) - 15 detailed requirements with acceptance criteria
- [Design](./design.md) - Architecture, components, and technical specifications
- [Tasks](./tasks.md) - Step-by-step implementation guide with 9 phases

## Key Features

### 1. Hybrid Search Engine
- Real-time search with 300ms debounce
- Combines semantic (vector) and keyword (BM25) search
- Configurable hybrid weight (0.0-1.0)
- Quality score filtering
- Search method toggle (Hybrid vs Semantic)

### 2. Score Visualization
- Hybrid score badge with percentage display
- Interactive tooltip with score breakdown
- Visual indicators for semantic, keyword, and composite scores
- Color-coded relevance (Green >80%, Yellow 60-80%, Gray <60%)

### 3. Personalized Recommendations
- "For You" feed when search is empty
- Reason badges explaining recommendations
- Responsive grid layout
- Cached for 10 minutes

### 4. Advanced Features
- URL state synchronization (shareable search links)
- Mobile-responsive with filter drawer
- Keyboard shortcuts (Cmd+K / Ctrl+K)
- WCAG 2.1 AA accessibility
- Error handling and retry logic

## Tech Stack

**Required**:
- React 18 with hooks (useState, useReducer)
- TanStack Query v5 for data fetching
- shadcn/ui components (Slider, Badge, HoverCard, Skeleton, Separator, Switch, Sheet)
- Lucide React icons
- TypeScript 5 (strict mode)

**Architecture**:
- Feature-based structure (`src/features/search`, `src/features/recommendations`)
- Custom hooks for state management (`useSearch`, `useDebounce`)
- API layer with proper error handling
- URL state synchronization with React Router

## Implementation Timeline

**Estimated Duration**: 5 weeks

- **Week 1**: Foundation (types, API, hooks)
- **Week 2**: Core components (input, filters, results)
- **Week 3**: Integration (route, layout, recommendations)
- **Week 4**: Polish & testing (accessibility, performance)
- **Week 5**: Documentation & launch

## Success Metrics

- Search usage: 80% of users perform at least one search per session
- Search success rate: 70% of searches result in a click
- Filter usage: 30% of users adjust filters
- Recommendation engagement: 20% of users click recommendations
- Performance: P95 search latency < 500ms
- Accessibility: Lighthouse score >90
- Mobile usage: 40% of searches from mobile devices

## Dependencies

### Required
- ✅ Phase 0: SPA Foundation (authentication, routing, layout)
- ✅ Phase 1: Ingestion Management (resources exist in database)
- ⚠️ Backend: Search API (POST /api/v1/search)
- ⚠️ Backend: Recommendations API (GET /api/v1/recommendations)

### Optional
- Analytics system for tracking search usage
- Error monitoring (Sentry or similar)

## Getting Started

### For Implementers

1. **Read the requirements**: Start with [requirements.md](./requirements.md)
2. **Review the design**: Understand architecture in [design.md](./design.md)
3. **Follow the tasks**: Implement step-by-step using [tasks.md](./tasks.md)
4. **Test incrementally**: Write tests alongside implementation
5. **Get feedback**: Review after each phase

### For Reviewers

1. **Check requirements**: Verify all 15 requirements are met
2. **Review acceptance criteria**: Ensure all criteria satisfied
3. **Test functionality**: Manual testing of user flows
4. **Check accessibility**: Keyboard navigation and screen reader
5. **Verify performance**: Lighthouse audit and bundle size

## File Structure

```
src/
├── features/
│   ├── search/
│   │   ├── api.ts                    # Search API client
│   │   ├── types.ts                  # TypeScript interfaces
│   │   ├── hooks/
│   │   │   ├── useSearch.ts          # Main search state machine
│   │   │   └── useDebounce.ts        # Debounce utility hook
│   │   └── components/
│   │       ├── SearchInput.tsx       # Large search input field
│   │       ├── FilterPanel.tsx       # Quality + Method filters
│   │       ├── SearchResultItem.tsx  # Individual result card
│   │       └── HybridScoreBadge.tsx  # Score visualization
│   └── recommendations/
│       ├── api.ts                    # Recommendations API client
│       ├── types.ts                  # TypeScript interfaces
│       └── components/
│           └── RecommendationsWidget.tsx  # "For You" feed
├── routes/
│   └── _auth.search.tsx              # Main search route
└── lib/
    └── hooks/
        └── useDebounce.ts            # Shared debounce hook
```

## Testing Strategy

### Unit Tests
- useDebounce hook
- useSearch hook
- API functions
- Type guards

### Component Tests
- SearchInput interactions
- FilterPanel state changes
- SearchResultItem rendering
- HybridScoreBadge tooltip

### Integration Tests
- Full search flow
- Filter application
- URL synchronization
- Error handling

### E2E Tests (Optional)
- User search journey
- Filter user journey
- Recommendations journey

## Known Limitations

- Search limited to 20 results per query (pagination in future phase)
- No search history or saved searches (future phase)
- No advanced filters (date range, author, tags) (future phase)
- No search suggestions or autocomplete (future phase)
- No faceted search (future phase)

## Future Enhancements (Phase 3+)

- Search history and saved searches
- Advanced filters (date range, author, tags)
- Search suggestions and autocomplete
- Faceted search (category filters)
- Export search results
- Voice search
- Multi-language search
- Search analytics dashboard

## Questions?

- Check [requirements.md](./requirements.md) for detailed specifications
- Check [design.md](./design.md) for technical architecture
- Check [tasks.md](./tasks.md) for implementation steps
- Refer to [AGENTS.md](../../../AGENTS.md) for documentation routing

## Approval

- [ ] Requirements approved by Product Owner
- [ ] Design approved by Tech Lead
- [ ] Tasks reviewed by Development Team
- [ ] Ready for implementation

---

**Next Steps**: Begin implementation with Task 1.1 (Search Type Definitions)
