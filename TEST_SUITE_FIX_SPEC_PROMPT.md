# Test Suite Comprehensive Fix - Spec Generation Prompt

## Context
The Neo Alexandria 2.0 application has 1,867 tests with 386 failures and 102 errors after fixing import path issues. The application needs all genuine coding errors fixed to ensure the website functions perfectly.

## Current Test Results
- ✅ 1,351 tests passed (72.4%)
- ❌ 386 tests failed (20.7%)
- ⚠️ 102 errors (5.5%)
- ⏭️ 41 skipped (2.2%)

## Critical Issues to Fix

### 1. Database Model Field Mismatches
**Problem**: Tests are using invalid keyword arguments that don't exist in the SQLAlchemy models.

**Examples**:
- `Resource(url=...)` - Resource model doesn't have a `url` field (should use `source` or `identifier`)
- `Resource(resource_type=...)` - Should be `type` (Dublin Core field)
- `User(hashed_password=...)` - Invalid field name

**Affected Tests**: ~80+ tests across phase8, phase9, integration/workflows

**Fix Required**: 
- Update all test fixtures to use correct model field names
- Map old field names to correct Dublin Core fields:
  - `url` → `source` or `identifier`
  - `resource_type` → `type`
  - Check User model for correct password field name

### 2. Service Method Signature Changes
**Problem**: Service methods have different signatures than tests expect.

**Examples**:
- `CollectionService.create_collection()` missing required `description` parameter
- `CollectionService.add_resources()` method doesn't exist (tests expect it)
- `recommendation_service.generate_recommendations_with_graph_fusion()` has different parameters

**Affected Tests**: ~50+ tests in phase7_collections, phase11_recommendations

**Fix Required**:
- Update service method signatures to match test expectations OR
- Update test calls to match current service implementations
- Document the correct API for each service

### 3. Missing Database Tables/Migrations
**Problem**: Tests fail with "no such table" errors.

**Tables Missing**:
- `resources` (core table)
- `taxonomy_nodes`
- `users`
- `annotations`
- `classification_codes`
- `alembic_version`

**Affected Tests**: ~100+ tests across all phases

**Fix Required**:
- Ensure database migrations are run before tests
- Update test fixtures to create necessary tables
- Fix conftest.py database setup to run migrations
- Verify alembic migration scripts are complete

### 4. Monitoring/Metrics Initialization Issues
**Problem**: Prometheus metrics objects are None, causing AttributeError on `.inc()` calls.

**Error**: `AttributeError: 'NoneType' object has no attribute 'inc'`

**Affected Tests**: ~40+ tests in phase1_ingestion, workflows

**Fix Required**:
- Initialize monitoring metrics properly in test environment
- Mock metrics in tests or provide test-safe implementations
- Check `backend/app/monitoring.py` initialization

### 5. Event System API Changes
**Problem**: EventBus API has changed but tests use old methods.

**Examples**:
- Tests call `event_bus.clear_listeners()` but method is `clear_history()`
- Tests access `event_bus._subscribers` but it's a private implementation detail
- Event class missing `correlation_id` attribute

**Affected Tests**: ~30+ tests in test_event_system.py, test_event_hooks.py

**Fix Required**:
- Update EventBus to provide public API for test cleanup
- Update Event class to include correlation_id if needed
- Update all tests to use current EventBus API

### 6. Missing Python Dependencies
**Problem**: Tests import modules that aren't installed.

**Missing Modules**:
- `trio` (async testing framework)
- `openai` (for G-Eval quality metrics)
- `plotly` (for visualization)

**Affected Tests**: ~15+ tests

**Fix Required**:
- Add missing dependencies to requirements.txt or requirements-dev.txt
- Make these optional dependencies with graceful fallbacks
- Skip tests when optional dependencies aren't available

### 7. Quality Service API Changes
**Problem**: Quality analyzer methods have been renamed or removed.

**Examples**:
- `ContentQualityAnalyzer.content_readability()` doesn't exist
- `ContentQualityAnalyzer.overall_quality_score()` doesn't exist
- Quality dimension calculations return different structures

**Affected Tests**: ~25+ tests in phase9_quality

**Fix Required**:
- Restore missing methods or update tests to use new API
- Ensure quality score calculations are consistent
- Update test assertions to match actual return values

### 8. Classification Service Issues
**Problem**: ML classification service has implementation gaps.

**Examples**:
- `ClassificationTrainer.train()` method doesn't exist (should be different name)
- Semi-supervised learning methods expect different return types
- Model loading/checkpoint paths are incorrect

**Affected Tests**: ~40+ tests in phase8_classification

**Fix Required**:
- Implement missing ClassificationTrainer methods
- Fix checkpoint directory structure
- Update semi-supervised learning workflow

### 9. Recommendation Service Refactoring
**Problem**: Recommendation service was refactored but tests not updated.

**Examples**:
- `generate_user_profile_vector()` signature changed (missing user_id parameter)
- Methods removed: `_compute_gini_coefficient()`, `apply_novelty_boost()`
- Return types changed for recommendation methods

**Affected Tests**: ~20+ tests in phase5_graph, phase11_recommendations

**Fix Required**:
- Update all recommendation service method calls
- Restore removed utility methods or update tests
- Fix user profile generation workflow

### 10. Graph Service Implementation Gaps
**Problem**: Graph construction and LBD discovery features incomplete.

**Examples**:
- `LBDService.open_discovery()` method doesn't exist
- Edge type filtering not working correctly
- Multi-layer graph construction incomplete

**Affected Tests**: ~15+ tests in phase10_graph_intelligence

**Fix Required**:
- Implement missing LBD discovery methods
- Complete graph construction features
- Fix edge weight calculations

## Spec Requirements

Create a comprehensive spec that:

1. **Categorizes all failures** by root cause (model fields, service APIs, database, etc.)

2. **Prioritizes fixes** by impact:
   - P0: Breaks core functionality (database, models, critical services)
   - P1: Breaks major features (collections, search, recommendations)
   - P2: Breaks advanced features (ML classification, quality analysis)
   - P3: Missing optional features (visualization, advanced metrics)

3. **Provides detailed fix plans** for each category:
   - Exact code changes needed
   - Files to modify
   - Test updates required
   - Migration scripts needed

4. **Ensures backward compatibility** where possible:
   - Deprecation warnings for old APIs
   - Adapter layers for changed interfaces
   - Migration guides for breaking changes

5. **Includes verification steps**:
   - How to verify each fix works
   - Integration test scenarios
   - Performance impact assessment

6. **Documents the correct APIs**:
   - Service method signatures
   - Model field names
   - Event system usage
   - Quality metrics structure

## Success Criteria

- All 1,867 tests pass (or are properly skipped with clear reasons)
- No genuine coding errors remain
- All core features work end-to-end
- Database schema is complete and migrations work
- Service APIs are consistent and documented
- Website functions perfectly in production

## Output Format

Generate a spec with:
- **requirements.md**: What needs to be fixed and why
- **design.md**: How to fix each category of issues
- **tasks.md**: Step-by-step implementation tasks with file paths and code snippets

## Additional Context

- Application: Neo Alexandria 2.0 (scholarly resource management system)
- Stack: FastAPI, SQLAlchemy, PostgreSQL/SQLite, React frontend
- Architecture: Event-driven, modular vertical slices
- Test Framework: pytest with fixtures and mocks
- Current working directory: Project root with backend/ and frontend/ folders
