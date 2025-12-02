# Module Isolation Validation

## Overview

This document describes the module isolation validation system implemented for the vertical slice architecture refactoring (Phase 13.5).

## Purpose

The module isolation checker ensures that modules follow the vertical slice architecture principles:

1. **Shared Kernel Only**: Modules can only import from `app.shared.*` (shared kernel)
2. **No Direct Module Imports**: Modules cannot directly import from other modules
3. **No Circular Dependencies**: No circular dependency chains between modules
4. **Event-Driven Communication**: Cross-module communication must use the event bus

## Implementation

### Script: `scripts/check_module_isolation.py`

A Python script that uses AST (Abstract Syntax Tree) parsing to analyze imports in all module files.

**Features:**
- Parses Python imports using AST
- Detects direct imports between modules
- Detects circular dependencies using DFS
- Generates dependency graphs
- Provides detailed violation reports
- Returns appropriate exit codes for CI/CD integration

**Usage:**
```bash
# Basic check
python scripts/check_module_isolation.py

# Verbose mode with detailed import analysis
python scripts/check_module_isolation.py --verbose

# Show dependency graph
python scripts/check_module_isolation.py --graph

# Custom app root
python scripts/check_module_isolation.py --app-root /path/to/app
```

### CI/CD Integration

#### GitHub Actions

The module isolation check is integrated as a **dedicated job** in `.github/workflows/test.yml` that runs before all tests:

```yaml
jobs:
  module-isolation:
    name: Module Isolation Check
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Check module isolation
        run: |
          cd backend
          echo "::group::Module Isolation Check"
          python scripts/check_module_isolation.py --verbose
          echo "::endgroup::"
        continue-on-error: false
      
      - name: Generate isolation report
        if: failure()
        run: |
          cd backend
          echo '## ❌ Module Isolation Check Failed' >> $GITHUB_STEP_SUMMARY
          echo '' >> $GITHUB_STEP_SUMMARY
          echo 'Modules must communicate through events, not direct imports.' >> $GITHUB_STEP_SUMMARY
          echo 'Allowed imports: `app.shared.*` (shared kernel only)' >> $GITHUB_STEP_SUMMARY
          echo '' >> $GITHUB_STEP_SUMMARY
          echo 'Run `python backend/scripts/check_module_isolation.py --verbose --graph` locally for details.' >> $GITHUB_STEP_SUMMARY
      
      - name: Report success
        if: success()
        run: |
          echo '## ✅ Module Isolation Check Passed' >> $GITHUB_STEP_SUMMARY
          echo '' >> $GITHUB_STEP_SUMMARY
          echo 'All modules are properly isolated and follow vertical slice architecture rules.' >> $GITHUB_STEP_SUMMARY

  test:
    runs-on: ubuntu-latest
    needs: module-isolation  # Tests only run if isolation check passes
    # ... rest of test configuration
```

**Key Features:**
- **Separate Job**: Runs as a dedicated job before tests
- **Fail Fast**: Tests don't run if isolation check fails
- **Verbose Output**: Uses `--verbose` flag for detailed reporting
- **GitHub Summary**: Generates formatted reports in workflow summary
- **Grouped Output**: Uses GitHub Actions groups for better readability

#### Pre-commit Hooks

Created `.pre-commit-config.yaml` with enhanced configuration:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-module-isolation
        name: Check Module Isolation
        entry: python backend/scripts/check_module_isolation.py
        language: system
        pass_filenames: false
        files: ^backend/app/modules/.*\.py$
        description: Validates that modules follow vertical slice architecture rules
        always_run: true
        stages: [commit, push]
```

**Setup Instructions:**

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the git hook scripts:
   ```bash
   pre-commit install
   ```

3. (Optional) Run manually on all files:
   ```bash
   pre-commit run --all-files
   ```

4. (Optional) Run only isolation check:
   ```bash
   pre-commit run check-module-isolation --all-files
   ```

**Key Features:**
- **Always Run**: Checks run even if no module files changed
- **Multiple Stages**: Runs on both commit and push
- **Fail on Violation**: Prevents commits/pushes with violations
- **No Bypass**: Violations must be fixed before committing

See `.pre-commit-setup.md` in the project root for detailed setup instructions.

## Architecture Rules

### ✅ Allowed Imports

1. **Shared Kernel Imports** (from any module):
   ```python
   from app.shared.database import get_db, Base
   from app.shared.event_bus import event_bus
   from app.shared.base_model import TimestampMixin
   ```

2. **Self-Imports** (within the same module):
   ```python
   # In app/modules/collections/router.py
   from app.modules.collections.service import CollectionService
   from app.modules.collections.schema import CollectionCreate
   ```

3. **Standard Library and Third-Party**:
   ```python
   from typing import List, Optional
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   ```

### ❌ Forbidden Imports

1. **Direct Module-to-Module Imports**:
   ```python
   # In app/modules/collections/service.py
   from app.modules.resources.service import ResourceService  # ❌ VIOLATION
   ```

2. **Circular Dependencies**:
   ```python
   # Module A imports Module B
   # Module B imports Module A
   # ❌ VIOLATION
   ```

### ✅ Required Pattern: Event-Driven Communication

Instead of direct imports, use events:

```python
# ❌ Old way (direct import)
from app.modules.collections.service import CollectionService

def delete_resource(resource_id: int):
    collection_service.recompute_embedding(resource_id)

# ✅ New way (event-driven)
from app.shared.event_bus import event_bus

def delete_resource(resource_id: int):
    event_bus.emit("resource.deleted", {"resource_id": resource_id})
```

## Validation Report Format

### Success Report

```
======================================================================
MODULE ISOLATION CHECK REPORT
======================================================================

✅ NO DIRECT IMPORT VIOLATIONS

✅ NO CIRCULAR DEPENDENCIES

======================================================================
SUMMARY
======================================================================
Direct import violations: 0
Circular dependencies: 0

✅ ALL CHECKS PASSED - Modules are properly isolated!
```

### Violation Report

```
======================================================================
MODULE ISOLATION CHECK REPORT
======================================================================

❌ DIRECT IMPORT VIOLATIONS: 2
----------------------------------------------------------------------

Module 'collections' imports from:
  → resources (in modules/collections/service.py)
  → search (in modules/collections/handlers.py)

❌ CIRCULAR DEPENDENCIES: 1
----------------------------------------------------------------------

Cycle 1: collections → resources → collections

======================================================================
SUMMARY
======================================================================
Direct import violations: 2
Circular dependencies: 1

❌ FAILED - 3 violation(s) found

Modules must communicate through events, not direct imports.
Allowed imports: app.shared.* (shared kernel only)
```

## Troubleshooting

### False Positives

If the checker reports violations that are actually valid:

1. **Check if it's a shared kernel import**: Ensure imports from `app.shared.*` are properly detected
2. **Check if it's a self-import**: Imports within the same module should be allowed
3. **Review the import path**: Ensure the import path matches the expected pattern

### Adding New Modules

When adding a new module:

1. Create the module under `app/modules/<module_name>/`
2. Only import from `app.shared.*`
3. Use events for cross-module communication
4. Run the checker: `python scripts/check_module_isolation.py`

### Fixing Violations

1. **Identify the violation**: Run with `--verbose` to see detailed import analysis
2. **Replace direct imports with events**:
   - Define event types in the emitting module
   - Emit events instead of calling methods
   - Subscribe to events in the receiving module
3. **Verify the fix**: Run the checker again

## Benefits

### Architecture Enforcement
1. **Automated Validation**: Automatically validates architectural rules on every commit and PR
2. **Fail Fast**: Violations are caught before code review, saving time
3. **Consistent Standards**: Ensures all developers follow the same architecture rules

### Developer Experience
4. **Early Detection**: Pre-commit hooks catch violations before commit
5. **Clear Feedback**: Detailed reports show exactly what needs to be fixed
6. **Local Testing**: Developers can run checks locally before pushing

### Code Quality
7. **Prevents Drift**: Stops architectural degradation over time
8. **Enforces Decoupling**: Ensures modules remain loosely coupled
9. **Maintainability**: Makes codebase easier to understand and modify

### CI/CD Integration
10. **Separate Job**: Dedicated CI job provides clear visibility
11. **Blocks Merges**: PRs with violations cannot be merged
12. **GitHub Summaries**: Formatted reports in workflow summaries
13. **No False Passes**: Tests don't run if architecture is violated

## Related Documentation

- **Architecture Diagram**: `docs/ARCHITECTURE_DIAGRAM.md`
- **Event-Driven Refactoring**: `docs/EVENT_DRIVEN_REFACTORING.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **Scripts README**: `scripts/README.md`

## Future Enhancements

Potential improvements to the isolation checker:

1. **Performance Metrics**: Track module coupling metrics over time
2. **Visualization**: Generate visual dependency graphs
3. **Custom Rules**: Allow configuration of additional validation rules
4. **IDE Integration**: Provide real-time feedback in IDEs
5. **Auto-Fix**: Suggest or automatically apply fixes for common violations
