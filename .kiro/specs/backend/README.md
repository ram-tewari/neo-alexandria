# Backend Specifications

Backend specifications for Neo Alexandria 2.0 (Python/FastAPI).

## Specs by Category

### 🎯 Core Features (8 specs)

| Spec | Description | Status |
|------|-------------|--------|
| `phase7-collection-management` | User collections and resource organization | ✅ Complete |
| `phase7-5-annotation-system` | Text highlighting and note-taking | ✅ Complete |
| `phase8-three-way-hybrid-search` | FTS5 + Dense Vector + Sparse Vector search | ✅ Complete |
| `phase8-5-ml-classification` | ML-based taxonomy classification | ✅ Complete |
| `phase9-quality-assessment` | Multi-dimensional quality scoring | ✅ Complete |
| `phase10-advanced-graph-intelligence` | Knowledge graph and citation networks | ✅ Complete |
| `phase11-hybrid-recommendation-engine` | Personalized content recommendations | ✅ Complete |
| `phase13-postgresql-migration` | PostgreSQL database support | ✅ Complete |

### 🏗️ Architecture & Refactoring (4 specs)

| Spec | Description | Status |
|------|-------------|--------|
| `phase10-5-code-standardization` | Code quality standards and linting | ✅ Complete |
| `phase12-fowler-refactoring` | Martin Fowler refactoring patterns | ✅ Complete |
| `phase12-5-event-driven-architecture` | Event system and async hooks | ✅ Complete |
| `phase13-5-vertical-slice-refactor` | Modular monolith architecture | 📋 Spec Only |

### 🤖 ML & Training (3 specs)

| Spec | Description | Status |
|------|-------------|--------|
| `ml-model-training` | ML model training infrastructure | ✅ Complete |
| `production-ml-training` | Production ML pipelines | ✅ Complete |
| `phase11-5-ml-benchmarking` | ML performance benchmarking | ✅ Complete |

### 🧪 Testing (5 specs)

| Spec | Description | Status |
|------|-------------|--------|
| `test-suite-critical-fixes` | Critical test failures | ✅ Complete |
| `test-suite-fixes` | General test improvements | ✅ Complete |
| `test-suite-fixes-phase2` | Additional test fixes | ✅ Complete |
| `test-suite-stabilization` | Test stability improvements | ✅ Complete |
| `phase12-6-test-suite-fixes` | Phase 12 test fixes | ✅ Complete |

### 🔗 Integration (1 spec)

| Spec | Description | Status |
|------|-------------|--------|
| `frontend-backend-integration` | API integration with frontend | ✅ Complete |

## Quick Start

### View a Spec
```bash
# Navigate to spec directory
cd .kiro/specs/backend/phase13-postgresql-migration

# View files
cat requirements.md
cat design.md
cat tasks.md
```

### Execute Tasks
1. Open `tasks.md` in Kiro IDE
2. Click "Start task" next to any task
3. Follow Kiro's guidance

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite / PostgreSQL
- **ORM**: SQLAlchemy 2.0.23
- **ML**: Transformers, PyTorch, sentence-transformers
- **Search**: FTS5, Vector similarity, SPLADE
- **Tasks**: Celery with Redis
- **Testing**: pytest

## Related Documentation

- [Developer Guide](../../../backend/docs/DEVELOPER_GUIDE.md)
- [Architecture Diagram](../../../backend/docs/ARCHITECTURE_DIAGRAM.md)
- [API Documentation](../../../backend/docs/API_DOCUMENTATION.md)
- [Changelog](../../../backend/docs/CHANGELOG.md)
