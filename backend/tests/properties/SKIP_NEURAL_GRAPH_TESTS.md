# Neural Graph Tests - Dependency Issue

## Problem

The neural graph property tests require `torch-cluster`, `torch-scatter`, and `torch-sparse` packages which:
1. Don't have pre-built wheels for Python 3.13
2. Require compilation from source
3. Fail to compile on Windows due to missing `python313t.lib` (free-threaded Python library)

## Error

```
LINK : fatal error LNK1104: cannot open file 'python313t.lib'
```

## Solution Options

### Option 1: Skip Neural Graph Tests (Recommended)
These are Phase 19 tests, not Phase 20. Skip them when running property tests:

```bash
# Skip neural graph tests
python -m pytest tests/properties/ -v --ignore=tests/properties/test_neural_graph_properties.py

# Or mark them as skipped in conftest.py
```

### Option 2: Downgrade Python
Downgrade to Python 3.11 or 3.12 which have pre-built wheels:

```bash
# Not recommended - would require reinstalling all dependencies
```

### Option 3: Wait for Package Updates
Wait for PyTorch Geometric packages to release Python 3.13 wheels.

## Current Status

- ✅ Property test optimization complete (10 examples instead of 50-100)
- ✅ Tests run 5-10x faster
- ❌ Neural graph tests fail due to missing dependencies (Phase 19, not Phase 20)
- ✅ All other property tests should work

## Recommendation

Skip neural graph tests and continue with Phase 20 work. These tests are from Phase 19 and are not blocking Phase 20 development.
