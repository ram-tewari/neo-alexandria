# Phase 14 Tasks Amendment - Test Fixes

**Date**: December 25, 2024  
**Status**: Tasks Updated  
**Test Results**: 94 failures, 5 passes out of 99 tests

## Summary

The Phase 14 tasks have been amended to address critical test failures discovered when running the module endpoint tests. The tests were already created (task 12.1 complete), but they revealed infrastructure issues that need to be fixed before the tests can pass.

## Test Failure Analysis

### Failure Categories

1. **Missing Imports (35 failures)**
   - `NameError: name 'ResourceStatus' is not defined`
   - Affects: annotations, curation, graph, quality, recommendations, scholarly, search, taxonomy tests
   - Root cause: Test files create resources but don't import ResourceStatus enum

2. **404 Not Found (38 failures)**
   - Endpoints returning 404 instead of expected responses
   - Affects: annotations, authority, curation, graph, monitoring, quality, recommendations, scholarly, taxonomy tests
   - Root cause: Module routers not properly registered in main.py

3. **500 Internal Server Error (8 failures)**
   - Server errors in collections, search, and recommendations modules
   - Root cause: Service initialization issues, missing dependencies

4. **SQLAlchemy Mapper Errors (11 failures)**
   - `One or more mappers failed to initialize`
   - Affects: collections module tests
   - Root cause: Circular relationship dependencies or incorrect model configuration

5. **422 Validation Errors (4 failures)**
   - Unprocessable Entity errors in collections module
   - Root cause: Schema validation issues, missing required fields or incorrect defaults

6. **Health Check Failures (2 failures)**
   - Health checks returning "unhealthy" instead of "healthy"/"ok"/"up"
   - Affects: collections and search modules
   - Root cause: Incorrect health check logic or dependency checks

## Tasks Added

### Task 12.2: Fix Critical Test Infrastructure Issues

**Parent task** covering all infrastructure fixes needed before tests can pass.

#### Task 12.2.1: Fix missing ResourceStatus imports
- Add import to 8 test files
- Simple fix, high impact (resolves 35 failures)

#### Task 12.2.2: Fix router registration in main.py
- Verify all 10 module routers are registered with correct prefixes
- Critical for resolving 38 404 errors

#### Task 12.2.3: Fix Collections module SQLAlchemy mapper errors
- Investigate and fix mapper initialization failures
- Check for circular dependencies in relationships
- Resolves 11 failures in collections tests

#### Task 12.2.4: Fix Collections module schema validation errors
- Fix 422 errors in collection creation
- Verify schema definitions match expected request format
- Resolves 4 validation failures

#### Task 12.2.5: Fix Search module internal server errors
- Investigate 500 errors in search endpoints
- Check service initialization and dependencies
- Resolves search-related 500 errors

#### Task 12.2.6: Fix Recommendations module internal server errors
- Investigate 500 errors in recommendations endpoints
- Check user profile service and NCF model loading
- Resolves recommendations-related 500 errors

#### Task 12.2.7: Fix module health check responses
- Fix health checks returning "unhealthy"
- Ensure proper status values returned
- Resolves 2 health check failures

#### Task 12.2.8: Fix test conftest.py database fixtures
- Verify database fixture setup/teardown
- Ensure all models imported before database creation
- Prevent state leakage between tests

### Task 12.3: Re-run Module Tests After Fixes
- Verify all 99 tests pass after fixes applied
- Document any remaining failures
- Create follow-up tasks if needed

### Tasks 12.4-12.7: Verify Individual Module Tests
- Granular verification tasks for critical modules
- Collections, Search, Annotations, and all others
- Ensures each module's tests pass independently

## Tasks Removed

The following tasks (12.5.2 through 12.5.13) were removed as they are now superseded:
- These tasks were for "creating" tests that already exist
- The tests were already created in task 12.1
- The issue is not missing tests, but broken infrastructure
- Keeping these tasks would be confusing and redundant

## Impact on Timeline

**Before Amendment**:
- Task 12.1: Create tests ✅ (Complete)
- Task 12.5.2-12.5.13: Create more tests (Redundant)
- Task 13: Legacy cleanup

**After Amendment**:
- Task 12.1: Create tests ✅ (Complete)
- Task 12.2: Fix test infrastructure ⏳ (New, Critical)
- Task 12.3-12.7: Verify tests pass ⏳ (New, Verification)
- Task 13: Legacy cleanup

**Estimated Effort**:
- Task 12.2.1: 30 minutes (simple imports)
- Task 12.2.2: 1 hour (router registration)
- Task 12.2.3: 2-3 hours (SQLAlchemy debugging)
- Task 12.2.4: 1 hour (schema fixes)
- Task 12.2.5: 1-2 hours (search service debugging)
- Task 12.2.6: 1-2 hours (recommendations debugging)
- Task 12.2.7: 1 hour (health check fixes)
- Task 12.2.8: 1 hour (fixture fixes)
- Task 12.3-12.7: 1 hour (verification)

**Total**: 10-14 hours of focused debugging and fixing

## Priority Order

1. **Task 12.2.1** (Quick win - fixes 35 failures)
2. **Task 12.2.2** (High impact - fixes 38 failures)
3. **Task 12.2.3** (Complex but critical - fixes 11 failures)
4. **Task 12.2.4** (Medium complexity - fixes 4 failures)
5. **Task 12.2.5-12.2.7** (Service-specific fixes)
6. **Task 12.2.8** (Infrastructure improvement)
7. **Task 12.3-12.7** (Verification)

## Success Criteria

- All 99 module endpoint tests pass
- No 404 errors (all routers registered)
- No 500 errors (all services initialized correctly)
- No SQLAlchemy mapper errors
- No validation errors
- All health checks return healthy status
- Test fixtures work reliably

## Next Steps

1. Start with task 12.2.1 (missing imports) - quick win
2. Move to task 12.2.2 (router registration) - high impact
3. Tackle task 12.2.3 (SQLAlchemy errors) - most complex
4. Complete remaining fixes in priority order
5. Run full test suite to verify all fixes
6. Proceed to task 13 (legacy cleanup) once tests pass

## Notes

- The test files themselves are well-structured and comprehensive
- The failures are infrastructure issues, not test design issues
- Fixing these issues will validate that the Phase 14 refactor is working correctly
- Once tests pass, we can confidently proceed with legacy cleanup
- This amendment makes the spec more accurate and actionable
