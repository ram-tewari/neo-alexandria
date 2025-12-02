# Design Document

## Overview

Phase 10.5 implements a systematic approach to code standardization and bug fixes across the Neo-Alexandria backend. The design follows a root-cause analysis methodology where each failing test is categorized by its underlying issue type, and fixes are applied systematically to address the root cause rather than symptoms.

The approach prioritizes high-impact fixes (model field inconsistencies, UUID serialization) that affect multiple tests, then addresses category-specific issues. Each fix category has a defined diagnostic process, fix pattern, and verification strategy.

## Architecture

### Fix Categorization System

The design organizes all 75 failing tests and 24 errors into 14 distinct categories:

1. **Model Field Inconsistencies** - Tests using non-existent model fields
2. **UUID Serialization** - UUID objects in JSON responses
3. **SQLAlchemy Query Issues** - Improper list parameter binding
4. **Pytest Fixture Usage** - Direct fixture calls instead of dependency injection
5. **Missing Dependencies** - Uninstalled packages
6. **Regex Errors** - Invalid regex patterns
7. **Test Assertion Mismatches** - Tests expecting wrong response structures
8. **Async Ingestion Failures** - Unhandled errors in ingestion pipeline
9. **Database Constraints** - Missing required fields
10. **Performance Thresholds** - Unrealistic performance expectations
11. **ML Tensor Errors** - Models on meta device
12. **API Endpoint Issues** - Wrong status codes
13. **Security Vulnerabilities** - Hardcoded secrets, SQL injection risks
14. **Code Quality** - General best practice violations

### Systematic Fix Workflow

Each test fix follows a five-step process:

```
1. Read Error Message → 2. Identify Category → 3. Fix Root Cause → 4. Verify → 5. Document
```

This ensures consistent, thorough fixes that don't introduce new issues.

### Priority Ordering

Fixes are applied in priority order based on impact:

**High Priority (Affects 20+ tests):**
- Model field inconsistencies
- UUID serialization
- Test assertion mismatches

**Medium Priority (Affects 5-20 tests):**
- SQLAlchemy query issues
- Pytest fixture usage
- Missing dependencies
- Database constraints

**Low Priority (Affects <5 tests):**
- Regex errors
- Performance thresholds
- ML tensor errors
- API endpoint issues

## Components and Interfaces

### 1. Model Field Validator

**Purpose:** Ensure all model instantiations use valid fields

**Interface:**
```python
def validate_model_fields(model_class: Type, field_dict: dict) -> dict:
    """
    Validates that all fields in field_dict exist in model_class.
    
    Args:
        model_class: SQLAlchemy model class (e.g., Resource)
        field_dict: Dictionary of field names and values
    
    Returns:
        Validated field dictionary
        
    Raises:
        ValueError: If any field doesn't exist in model
    """
```

**Implementation Strategy:**
- Read app/models.py to extract valid field names for each model
- Create a mapping of model_class → valid_fields
- Search codebase for all model instantiations
- Validate and fix field usage

### 2. UUID Serialization Helper

**Purpose:** Ensure all UUIDs are converted to strings in JSON responses

**Interface:**
```python
def serialize_uuid(value: Union[UUID, str]) -> str:
    """
    Converts UUID to string for JSON serialization.
    
    Args:
        value: UUID object or string
        
    Returns:
        String representation of UUID
    """
```

**Implementation Strategy:**
- Search for all API endpoint return statements
- Identify UUID objects in response dictionaries
- Wrap with str() conversion
- Update Pydantic schemas to use string types

### 3. Query Safety Checker

**Purpose:** Ensure SQLAlchemy queries use proper methods

**Interface:**
```python
def validate_query_safety(query_code: str) -> List[str]:
    """
    Checks query code for unsafe patterns.
    
    Args:
        query_code: String containing SQLAlchemy query code
        
    Returns:
        List of issues found (empty if safe)
    """
```

**Implementation Strategy:**
- Search for .filter() calls with == operator
- Identify list comparisons
- Replace with .in_() or .contains() methods
- Add validation for parameterized queries

### 4. Fixture Dependency Injector

**Purpose:** Convert direct fixture calls to dependency injection

**Interface:**
```python
def convert_fixture_usage(test_function: str) -> str:
    """
    Converts direct fixture calls to parameter-based injection.
    
    Args:
        test_function: String containing test function code
        
    Returns:
        Updated test function code
    """
```

**Implementation Strategy:**
- Identify fixture calls with parentheses
- Add fixture name to function parameters
- Remove parentheses from fixture usage
- Update parametrize decorators with indirect=True

### 5. Dependency Validator

**Purpose:** Ensure all imports are from installed packages

**Interface:**
```python
def validate_dependencies(import_statements: List[str]) -> List[str]:
    """
    Validates that all imported packages are installed.
    
    Args:
        import_statements: List of import statements
        
    Returns:
        List of missing packages
    """
```

**Implementation Strategy:**
- Extract all import statements from codebase
- Check against installed packages (pip list)
- Add missing packages to requirements.txt
- Mock external API libraries in tests

### 6. Test Assertion Aligner

**Purpose:** Align test assertions with actual API responses

**Interface:**
```python
def align_test_assertions(test_code: str, endpoint_code: str) -> str:
    """
    Updates test assertions to match actual API response structure.
    
    Args:
        test_code: String containing test code
        endpoint_code: String containing API endpoint code
        
    Returns:
        Updated test code with corrected assertions
    """
```

**Implementation Strategy:**
- For each failing test, locate corresponding endpoint
- Extract actual response structure from endpoint code
- Update test assertions to match reality
- Document any API changes needed

## Data Models

### Fix Record

Tracks each fix applied during the standardization process:

```python
@dataclass
class FixRecord:
    test_name: str
    category: str  # One of 14 categories
    root_cause: str
    fix_applied: str
    files_modified: List[str]
    verification_status: str  # "passed" | "failed" | "pending"
    timestamp: datetime
```

### Model Field Registry

Maps models to their valid fields:

```python
MODEL_FIELDS = {
    "Resource": [
        "id", "title", "url", "content", "content_type",
        "created_at", "updated_at", "embedding", "status"
        # ... complete list from models.py
    ],
    "TaxonomyNode": [
        "id", "name", "slug", "level", "path",
        "created_at", "updated_at", "parent_id"
        # ... complete list from models.py
    ],
    "Citation": [
        "id", "resource_id", "cited_resource_id",
        "created_at", "updated_at", "citation_type"
        # ... complete list from models.py
    ]
}
```

### Test Category Mapping

Maps each failing test to its category:

```python
TEST_CATEGORIES = {
    "test_quality_dimensions.py::test_calculate_accuracy": "model_field",
    "test_quality_api_endpoints.py::test_recalculate": "uuid_serialization",
    "test_phase10_integration.py::test_full_workflow": "assertion_mismatch",
    # ... complete mapping for all 75 tests
}
```

## Error Handling

### Validation Errors

**Strategy:** Fail fast with clear error messages

```python
class ModelFieldError(Exception):
    """Raised when invalid model field is used"""
    def __init__(self, model: str, field: str, valid_fields: List[str]):
        self.message = f"Invalid field '{field}' for {model}. Valid fields: {valid_fields}"
        super().__init__(self.message)
```

### Fix Application Errors

**Strategy:** Rollback and report when fixes fail

```python
try:
    apply_fix(test_name, fix_strategy)
    verify_fix(test_name)
except FixApplicationError as e:
    rollback_changes()
    log_fix_failure(test_name, str(e))
    raise
```

### Test Verification Errors

**Strategy:** Retry with alternative fix strategies

```python
for strategy in fix_strategies:
    try:
        apply_fix(test_name, strategy)
        if verify_fix(test_name):
            break
    except Exception as e:
        log_attempt(test_name, strategy, str(e))
        continue
else:
    escalate_to_manual_review(test_name)
```

## Testing Strategy

### Fix Verification Process

Each fix must pass a three-level verification:

**Level 1: Individual Test**
```bash
pytest tests/test_file.py::test_name -v
```

**Level 2: Related Tests**
```bash
pytest tests/test_file.py -v
```

**Level 3: Full Test Suite**
```bash
pytest tests/ -v --tb=short --maxfail=5
```

### Regression Prevention

**Strategy:** Run full test suite after each category of fixes

```python
def verify_no_regressions(baseline_passing: Set[str], current_passing: Set[str]):
    """
    Ensures fixes don't break previously passing tests.
    
    Args:
        baseline_passing: Set of test names that passed before fixes
        current_passing: Set of test names that pass after fixes
        
    Raises:
        RegressionError: If any previously passing test now fails
    """
    newly_failing = baseline_passing - current_passing
    if newly_failing:
        raise RegressionError(f"Fixes broke {len(newly_failing)} tests: {newly_failing}")
```

### Test Coverage Maintenance

**Strategy:** Ensure fixes don't reduce test coverage

- Run coverage before fixes: `pytest --cov=app tests/`
- Run coverage after fixes: `pytest --cov=app tests/`
- Compare coverage percentages
- Investigate any coverage decreases

## Implementation Phases

### Phase 1: Discovery and Categorization (Manual)

1. Run full test suite and capture all failures
2. Categorize each failure into one of 14 categories
3. Create TEST_CATEGORIES mapping
4. Identify high-priority categories

### Phase 2: Model Field Standardization (Automated)

1. Extract valid fields from app/models.py
2. Search for all model instantiations
3. Validate field usage
4. Fix invalid field references
5. Verify fixes

### Phase 3: UUID and Query Fixes (Automated)

1. Search for UUID objects in API responses
2. Add str() conversions
3. Search for unsafe query patterns
4. Replace with safe methods
5. Verify fixes

### Phase 4: Test Infrastructure Fixes (Semi-Automated)

1. Fix fixture usage patterns
2. Add missing dependencies
3. Fix regex patterns
4. Update test assertions
5. Verify fixes

### Phase 5: Application Logic Fixes (Manual)

1. Fix ingestion error handling
2. Add missing database fields
3. Adjust performance thresholds
4. Fix ML model initialization
5. Fix API endpoint logic
6. Verify fixes

### Phase 6: Security and Quality Audit (Manual)

1. Search for hardcoded secrets
2. Validate input sanitization
3. Check query parameterization
4. Review error handling
5. Document findings

### Phase 7: Final Verification (Automated)

1. Run full test suite
2. Verify all 75 tests pass
3. Check for regressions
4. Validate test coverage
5. Generate fix report

## Design Decisions and Rationales

### Decision 1: Category-Based Approach

**Rationale:** Grouping fixes by category allows for systematic application of similar fixes, reducing the chance of missing related issues. It also enables parallel work on independent categories.

### Decision 2: Root Cause Focus

**Rationale:** Fixing root causes rather than symptoms prevents the same issues from recurring in new code. It also reduces the total number of fixes needed since one root cause fix often resolves multiple test failures.

### Decision 3: Verification at Multiple Levels

**Rationale:** Three-level verification (individual test, related tests, full suite) catches both direct fix issues and unintended side effects. This prevents the "whack-a-mole" problem where fixing one test breaks another.

### Decision 4: Automated Where Possible

**Rationale:** Automating repetitive fixes (model fields, UUID conversion) reduces human error and speeds up the process. Manual fixes are reserved for cases requiring judgment (performance thresholds, API logic).

### Decision 5: Documentation Requirements

**Rationale:** Requiring documentation for non-obvious fixes (performance thresholds, design decisions) ensures future developers understand why changes were made and don't inadvertently revert them.

### Decision 6: Security-First Approach

**Rationale:** Addressing security issues (hardcoded secrets, SQL injection) as part of standardization ensures the codebase is production-ready and prevents security debt from accumulating.

## Dependencies

### Required Tools

- pytest (test execution)
- pytest-cov (coverage measurement)
- ruff or flake8 (code quality checking)
- mypy (type checking)

### Required Knowledge

- SQLAlchemy ORM patterns
- FastAPI response serialization
- Pytest fixture system
- Python regex syntax
- Async/await patterns

### External Dependencies

All external dependencies must be added to requirements.txt:
- openai (for G-EVAL tests)
- bert-score (for summarization evaluation)
- Any other missing packages identified during fix process

## Success Criteria

Phase 10.5 is complete when:

1. ✅ All 75 failing tests pass
2. ✅ All 24 errors are resolved
3. ✅ No regressions in previously passing tests
4. ✅ Test coverage is maintained or improved
5. ✅ No security vulnerabilities remain
6. ✅ All code follows established patterns
7. ✅ All fixes are documented
8. ✅ requirements.txt is complete and accurate
9. ✅ All model instantiations use valid fields
10. ✅ All API responses properly serialize UUIDs
11. ✅ All database queries use safe methods
12. ✅ All tests use fixtures correctly
13. ✅ All regex patterns are valid
14. ✅ All test assertions match API reality

## Monitoring and Validation

### Continuous Validation

After fixes are applied, implement continuous validation:

```python
# Pre-commit hook
def validate_code_standards():
    """Run before each commit to catch issues early"""
    check_no_hardcoded_secrets()
    check_model_field_usage()
    check_uuid_serialization()
    check_query_safety()
    run_fast_tests()
```

### Metrics Tracking

Track key metrics throughout the fix process:

- Number of tests passing (target: 100%)
- Number of errors (target: 0)
- Test coverage percentage (target: maintain or improve)
- Number of security issues (target: 0)
- Average test execution time (target: minimize)

### Reporting

Generate a comprehensive fix report at completion:

```markdown
# Phase 10.5 Fix Report

## Summary
- Tests Fixed: 75/75 (100%)
- Errors Resolved: 24/24 (100%)
- Files Modified: X
- Lines Changed: Y

## Fixes by Category
1. Model Field Inconsistencies: 15 tests fixed
2. UUID Serialization: 12 tests fixed
...

## Security Issues Resolved
- Hardcoded secrets removed: 0 found
- SQL injection risks: 0 found
...

## Verification Results
- Individual tests: ✅ All passing
- Full test suite: ✅ All passing
- Regression check: ✅ No regressions
- Coverage: ✅ Maintained at X%
```
