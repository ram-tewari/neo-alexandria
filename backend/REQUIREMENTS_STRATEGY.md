# Requirements Management Strategy

## Overview

Phase 19 introduces a **base + extension strategy** for managing Python dependencies across Cloud API and Edge Worker deployments. This prevents "dependency hell" where different environments have conflicting versions of the same package.

## The Problem: Dependency Hell

**Before (Separate Files)**:
```
requirements-cloud.txt:
  fastapi==0.104.1
  upstash-redis==0.15.0
  gitpython==3.1.40

requirements-edge.txt:
  fastapi==0.104.1
  upstash-redis==0.15.0  # Oops, forgot to update this!
  gitpython==3.1.41      # Different version!
  torch==2.1.0
```

**Problem**: When updating a shared dependency like `gitpython`, you must remember to update it in BOTH files. Forgetting leads to version mismatches and "works on my machine" bugs.

## The Solution: Base + Extension

**Structure**:
```
requirements-base.txt       # Shared dependencies
requirements-cloud.txt      # Extends base + cloud-specific
requirements-edge.txt       # Extends base + edge-specific
```

**requirements-base.txt** (shared):
```
fastapi==0.104.1
upstash-redis==0.15.0
gitpython==3.1.40
pydantic==2.5.0
python-dotenv==1.0.0
```

**requirements-cloud.txt** (extends base):
```
-r requirements-base.txt    # Inherit all base dependencies
psycopg2-binary==2.9.9      # Cloud-specific
qdrant-client==1.7.0        # Cloud-specific
```

**requirements-edge.txt** (extends base):
```
-r requirements-base.txt    # Inherit all base dependencies
torch==2.1.0                # Edge-specific
torch-geometric==2.4.0      # Edge-specific
tree-sitter==0.20.4         # Edge-specific
qdrant-client==1.7.0        # Edge-specific
numpy==1.24.3               # Edge-specific
psycopg2-binary==2.9.9      # Edge-specific
```

## Benefits

### 1. Single Source of Truth
Update shared dependencies **once** in `requirements-base.txt`, both environments inherit automatically.

### 2. Version Consistency
Impossible to have version mismatches for shared dependencies.

### 3. Clear Separation
Easy to see which dependencies are shared vs. environment-specific.

### 4. Maintainability
When adding a new shared dependency, add it to base.txt only.

## Usage

### Installing Dependencies

**Cloud API** (Render deployment):
```bash
pip install -r requirements-cloud.txt
```

This installs:
- All base dependencies (fastapi, upstash-redis, etc.)
- Cloud-specific dependencies (psycopg2-binary, qdrant-client)
- **NO** torch or heavy ML libraries

**Edge Worker** (local laptop):
```bash
pip install -r requirements-edge.txt
```

This installs:
- All base dependencies (fastapi, upstash-redis, etc.)
- Edge-specific dependencies (torch, torch-geometric, tree-sitter, etc.)
- Full ML stack for GPU processing

### Updating Dependencies

**Updating Shared Dependency**:
```bash
# Edit requirements-base.txt
fastapi==0.104.1  →  fastapi==0.105.0

# Both cloud and edge inherit the update automatically
```

**Adding Cloud-Specific Dependency**:
```bash
# Edit requirements-cloud.txt
# Add new line (do NOT add to base.txt)
some-cloud-only-package==1.0.0
```

**Adding Edge-Specific Dependency**:
```bash
# Edit requirements-edge.txt
# Add new line (do NOT add to base.txt)
some-ml-package==2.0.0
```

**Adding Shared Dependency**:
```bash
# Edit requirements-base.txt
# Add new line
new-shared-package==1.0.0

# Both cloud and edge inherit automatically
```

## Decision Tree

When adding a new dependency, ask:

```
Is this dependency used by BOTH cloud and edge?
├─ YES → Add to requirements-base.txt
└─ NO → Is it cloud-specific or edge-specific?
    ├─ Cloud → Add to requirements-cloud.txt
    └─ Edge → Add to requirements-edge.txt
```

## Examples

### Shared Dependencies (base.txt)
- `fastapi` - Both use FastAPI framework
- `upstash-redis` - Both connect to Redis queue
- `gitpython` - Both may need Git operations
- `pydantic` - Both use Pydantic models
- `python-dotenv` - Both load environment variables

### Cloud-Only Dependencies (cloud.txt)
- `psycopg2-binary` - Database driver (cloud uses Neon)
- `qdrant-client` - Vector search (cloud serves queries)

### Edge-Only Dependencies (edge.txt)
- `torch` - Deep learning (edge trains models)
- `torch-geometric` - Graph neural networks (edge only)
- `tree-sitter` - Code parsing (edge only)
- `numpy` - Scientific computing (edge only)

## Verification

### Check Version Consistency
```bash
# List all installed packages
pip freeze

# Verify base packages match in both environments
pip show fastapi  # Should be same version in cloud and edge
```

### Test Cloud Installation
```bash
# Should succeed without torch
pip install -r requirements-cloud.txt
python -c "import fastapi; print('✓ Cloud OK')"
python -c "import torch"  # Should fail
```

### Test Edge Installation
```bash
# Should succeed with torch
pip install -r requirements-edge.txt
python -c "import torch; print('✓ Edge OK')"
```

## Common Pitfalls

### ❌ DON'T: Duplicate Dependencies
```
# requirements-base.txt
fastapi==0.104.1

# requirements-cloud.txt
-r requirements-base.txt
fastapi==0.104.1  # ❌ Duplicate! Already in base
```

### ❌ DON'T: Forget -r Directive
```
# requirements-cloud.txt
# ❌ Missing: -r requirements-base.txt
psycopg2-binary==2.9.9
```

### ❌ DON'T: Update Only One File
```
# ❌ Updated base but forgot to test cloud/edge
# requirements-base.txt
fastapi==0.105.0  # Updated

# Must test both:
pip install -r requirements-cloud.txt  # Test cloud
pip install -r requirements-edge.txt   # Test edge
```

### ✅ DO: Update Base, Test Both
```
# 1. Update base
# requirements-base.txt
fastapi==0.105.0

# 2. Test cloud
pip install -r requirements-cloud.txt
pytest tests/test_cloud_api.py

# 3. Test edge
pip install -r requirements-edge.txt
pytest tests/test_edge_worker.py
```

## CI/CD Integration

### GitHub Actions
```yaml
jobs:
  test-cloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install cloud dependencies
        run: pip install -r requirements-cloud.txt
      - name: Test cloud API
        run: pytest tests/test_cloud_api.py

  test-edge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install edge dependencies
        run: pip install -r requirements-edge.txt
      - name: Test edge worker (CPU)
        run: pytest tests/test_edge_worker.py --device=cpu
```

## Migration Guide

### From Separate Files to Base + Extension

**Before**:
```
requirements-cloud.txt (50 lines)
requirements-edge.txt (80 lines)
# 30 lines duplicated between files
```

**After**:
```
requirements-base.txt (30 lines - shared)
requirements-cloud.txt (3 lines - extends base + 20 cloud-specific)
requirements-edge.txt (3 lines - extends base + 50 edge-specific)
# Zero duplication
```

**Steps**:
1. Identify shared dependencies (appear in both files)
2. Move shared dependencies to `requirements-base.txt`
3. Add `-r requirements-base.txt` to cloud and edge files
4. Remove duplicates from cloud and edge files
5. Test both installations
6. Update documentation

## Summary

The base + extension strategy:
- ✅ Prevents version mismatches
- ✅ Reduces duplication
- ✅ Simplifies maintenance
- ✅ Makes dependencies explicit
- ✅ Scales to multiple environments

**Golden Rule**: Update shared dependencies once in base.txt, both environments inherit automatically.
