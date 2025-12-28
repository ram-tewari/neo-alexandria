# Module Tests Rewrite - Spec Complete

## Summary

This spec provides a complete plan for rewriting the failing backend module tests from scratch. The spec was created based on analysis of the actual implementation code, not the broken existing tests.

## Spec Files

1. **requirements.md** - User stories and acceptance criteria
2. **design.md** - Technical design and patterns
3. **tasks.md** - Step-by-step implementation tasks

## Key Findings from Analysis

### Root Causes of Test Failures

1. **Field Name Mismatches**
   - Old tests use `url` but Resource model uses `source` and `identifier`
   - Annotation model mismatch: router expects `start_offset`/`end_offset`/`highlighted_text` but DB uses `selection_start`/`selection_end`/`selection_text`

2. **Database Type Compatibility**
   - Boolean fields stored as INTEGER (0/1) for SQLite compatibility
   - PostgreSQL rejects Python boolean values for INTEGER columns
   - JSON fields must be stored as JSON strings, not Python objects

3. **Missing Mocking**
   - Celery tasks not mocked
   - AI services (embeddings, semantic search) not mocked
   - Background tasks attempting to run during tests

4. **Schema Validation Errors**
   - Missing required fields in payloads
   - UUID objects not converted to strings
   - Incorrect data types

## Modules to Rewrite

1. **Annotations** - 6 endpoints
2. **Collections** - 8 endpoints
3. **Curation** - 5 endpoints
4. **Graph** - 2 endpoints
5. **Quality** - 9 endpoints
6. **Scholarly** - 5 endpoints

**Total**: 35 endpoints across 6 modules

## Implementation Approach

### Phase 1: Analysis and Preparation
- ✅ Task 1: Analyze module implementations (COMPLETE)
- Task 2: Create field mapping reference

### Phase 2: Test File Rewrites
- Task 3: Rewrite Annotations tests
- Task 4: Rewrite Collections tests
- Task 5: Rewrite Curation tests
- Task 6: Rewrite Graph tests
- Task 7: Rewrite Quality tests
- Task 8: Rewrite Scholarly tests

### Phase 3: Verification and Documentation
- Task 9: Run full test suite
- Task 10: Update documentation

## Design Principles

1. **Read-First Approach** - Always read actual implementation before writing tests
2. **Complete Mocking Strategy** - Mock ALL external dependencies
3. **Database Compatibility** - Handle SQLite/PostgreSQL differences
4. **Proper Fixtures Usage** - Leverage existing test infrastructure

## Key Patterns

### Data Compatibility
```python
# Booleans as integers
payload = {"is_active": 1, "is_shared": 0}

# JSON as strings
payload = {"metadata": json.dumps({"key": "value"})}

# UUIDs as strings
payload = {"resource_id": str(resource.id)}
```

### Mocking
```python
@patch('backend.app.tasks.celery_tasks.task_name')
def test_endpoint(mock_task, client, db):
    mock_task.apply_async.return_value = MagicMock(id="task-123")
    # Test code
```

## Success Criteria

- All 6 module test files rewritten from scratch
- All tests pass on both SQLite and PostgreSQL
- No database type errors or compatibility issues
- All external dependencies properly mocked
- Test coverage > 80% for all modules
- Documentation updated and complete

## Next Steps

1. Start with Task 2: Create field mapping reference
2. Then proceed to Task 3: Rewrite Annotations tests
3. Continue through all modules in order
4. Verify and document results

## Files Created

- `.kiro/specs/module-tests-rewrite/requirements.md`
- `.kiro/specs/module-tests-rewrite/design.md`
- `.kiro/specs/module-tests-rewrite/tasks.md`
- `.kiro/specs/module-tests-rewrite/SPEC_COMPLETE.md` (this file)

## Related Documentation

- [Test Fixtures](backend/tests/modules/conftest.py)
- [API Documentation](backend/docs/api/)
- [Architecture Overview](backend/docs/architecture/overview.md)
- [Testing Guide](backend/docs/guides/testing.md)

---

**Status**: Spec complete, ready for implementation
**Created**: 2024-12-26
**Last Updated**: 2024-12-26
