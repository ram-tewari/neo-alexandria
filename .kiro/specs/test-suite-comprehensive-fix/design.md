# Design Document

## Overview

This design addresses the systematic resolution of 488 test failures (386 failures + 102 errors) in the Neo Alexandria 2.0 test suite. The failures are categorized into 10 root causes, each requiring specific fixes to models, services, database infrastructure, and test code. The design prioritizes fixes by impact (P0-P3) and ensures backward compatibility where possible.

### Design Principles

1. **Minimal Code Changes**: Fix only what's broken, avoid unnecessary refactoring
2. **Test-First Validation**: Verify each fix resolves specific test failures
3. **Backward Compatibility**: Preserve existing APIs where possible, use deprecation warnings for breaking changes
4. **Incremental Progress**: Fix categories independently to enable parallel work
5. **Documentation**: Update API documentation as fixes are applied

### Priority Classification

- **P0 (Critical)**: Database schema, model fields, core service APIs - breaks fundamental functionality
- **P1 (High)**: Collections, search, recommendations - breaks major features
- **P2 (Medium)**: ML classification, quality analysis - breaks advanced features
- **P3 (Low)**: Optional dependencies, visualization - breaks nice-to-have features

## Architecture

### Component Interaction Map

```
Test Suite
    ├── Test Fixtures (conftest.py) → Database Schema (models + migrations)
    ├── Test Cases → Service Layer (business logic)
    ├── Service Layer → Event Bus (inter-module communication)
    ├── Service Layer → Monitoring System (metrics)
    └── Integration Tests → Full Stack (API → Service → Database)
```

### Fix Strategy by Layer

1. **Data Layer**: Fix model fields and database migrations first (foundation)
2. **Service Layer**: Update service method signatures and implementations
3. **Infrastructure Layer**: Fix event bus, monitoring, and dependencies
4. **Test Layer**: Update test fixtures and assertions to match fixed implementations


## Components and Interfaces

### 1. Database Model Field Alignment (P0)

**Root Cause**: Tests use legacy field names that don't exist in current SQLAlchemy models.

**Affected Models**:
- `Resource`: Tests use `url` (should be `source` or `identifier`), `resource_type` (should be `type`)
- `User`: Tests use `hashed_password` (need to verify correct field name)

**Fix Strategy**:
1. Audit all SQLAlchemy models to document current field names
2. Create field mapping document: `legacy_field → current_field`
3. Update test fixtures in conftest.py files to use correct field names
4. Run targeted tests to verify each fixture fix

**Field Mappings**:
```python
# Resource model field mappings
{
    'url': 'source',           # Dublin Core: source URL
    'resource_type': 'type',   # Dublin Core: resource type
    'resource_id': 'identifier' # Dublin Core: unique identifier
}

# User model - verify actual field name
{
    'hashed_password': 'password_hash'  # or 'hashed_password' if correct
}
```

**Files to Modify**:
- `backend/tests/conftest.py` - Root test fixtures
- `backend/tests/integration/conftest.py` - Integration test fixtures
- `backend/tests/unit/phase7_collections/conftest.py` - Collection fixtures
- `backend/tests/integration/workflows/conftest.py` - Workflow fixtures
- `backend/tests/integration/phase8_classification/conftest.py` - Classification fixtures
- `backend/tests/integration/phase9_quality/conftest.py` - Quality fixtures
- All test files that create Resource/User instances directly (~80 files)

**Verification**:
- Run: `pytest backend/tests/integration/workflows/ -v`
- Run: `pytest backend/tests/unit/phase8_classification/ -v`
- Verify no "unexpected keyword argument" errors


### 2. Service Method Signature Consistency (P1)

**Root Cause**: Service APIs have evolved but tests still call old method signatures.

**Affected Services**:
- `CollectionService`: Missing `description` parameter in `create_collection()`
- `CollectionService`: Tests call `add_resources()` method that may not exist
- `RecommendationService`: `generate_recommendations_with_graph_fusion()` signature changed

**Fix Strategy**:
1. Audit each service class to document current method signatures
2. Compare with test calls to identify mismatches
3. Update service methods to accept expected parameters OR update test calls
4. Add deprecation warnings if changing public APIs

**Service API Documentation**:

```python
# CollectionService - Expected API
class CollectionService:
    def create_collection(
        self, 
        db: Session, 
        name: str, 
        description: str,  # Add if missing
        user_id: int,
        **kwargs
    ) -> Collection:
        """Create a new collection with required fields."""
        pass
    
    def add_resources_to_collection(  # Verify actual method name
        self,
        db: Session,
        collection_id: int,
        resource_ids: List[int]
    ) -> Collection:
        """Add resources to existing collection."""
        pass

# RecommendationService - Expected API
class RecommendationService:
    def generate_recommendations_with_graph_fusion(
        self,
        db: Session,
        user_id: int,
        limit: int = 10,
        diversity_weight: float = 0.3  # Verify parameters
    ) -> List[Recommendation]:
        """Generate recommendations using graph fusion."""
        pass
```

**Files to Modify**:
- `backend/app/services/collection_service.py` - Update method signatures
- `backend/app/modules/collections/service.py` - Verify modular version
- `backend/app/services/recommendation_service.py` - Update method signatures
- `backend/tests/unit/phase7_collections/` - Update test calls (~20 files)
- `backend/tests/integration/phase11_recommendations/` - Update test calls (~30 files)

**Verification**:
- Run: `pytest backend/tests/unit/phase7_collections/ -v`
- Run: `pytest backend/tests/integration/phase11_recommendations/ -v`
- Verify no "missing required argument" or "unexpected keyword argument" errors


### 3. Database Migration and Table Creation (P0)

**Root Cause**: Database tables don't exist when tests run, causing "no such table" errors.

**Missing Tables**:
- `resources` - Core resource table
- `taxonomy_nodes` - Taxonomy/classification table
- `users` - User authentication table
- `annotations` - Resource annotations table
- `classification_codes` - Classification codes table
- `alembic_version` - Migration tracking table

**Fix Strategy**:
1. Verify all Alembic migration scripts are complete and in correct order
2. Update test database setup to run migrations before tests
3. Add migration verification to conftest.py
4. Ensure test database is created fresh for each test session

**Database Setup Flow**:

```python
# In conftest.py - Test database initialization
@pytest.fixture(scope="session")
def test_db():
    """Create test database with all migrations applied."""
    # 1. Create empty database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    
    # 2. Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    
    # 3. Verify all tables exist
    inspector = inspect(engine)
    required_tables = [
        'resources', 'taxonomy_nodes', 'users', 
        'annotations', 'classification_codes', 'alembic_version'
    ]
    existing_tables = inspector.get_table_names()
    missing = set(required_tables) - set(existing_tables)
    if missing:
        raise RuntimeError(f"Missing tables: {missing}")
    
    yield engine
    
    # 4. Cleanup
    Base.metadata.drop_all(engine)
```

**Migration Verification**:
- Check all migration files in `backend/alembic/versions/`
- Ensure migrations create all required tables
- Verify foreign key relationships are correct
- Test migration upgrade/downgrade cycle

**Files to Modify**:
- `backend/tests/conftest.py` - Update database fixture
- `backend/tests/db_utils.py` - Add migration helper functions
- `backend/alembic/versions/*.py` - Verify/fix migration scripts
- `backend/alembic/env.py` - Ensure proper configuration

**Verification**:
- Run: `pytest backend/tests/ -v -k "test_" --tb=short | grep "no such table"`
- Should return zero results after fix
- Run: `alembic upgrade head` in test environment
- Verify all tables created successfully


### 4. Monitoring Metrics Initialization (P0)

**Root Cause**: Prometheus metrics objects are None in test environment, causing AttributeError on `.inc()` calls.

**Affected Metrics**:
- Counters: `ingestion_total`, `search_queries_total`, etc.
- Histograms: `request_duration_seconds`, `embedding_generation_time`, etc.
- Gauges: `active_users`, `cache_size`, etc.

**Fix Strategy**:
1. Create test-safe monitoring module that initializes all metrics
2. Use pytest fixtures to mock metrics in test environment
3. Add conditional initialization based on environment (test vs production)
4. Provide no-op metric implementations for tests

**Monitoring Architecture**:

```python
# backend/app/monitoring.py - Production metrics
from prometheus_client import Counter, Histogram, Gauge
import os

# Conditional initialization based on environment
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    # Test-safe no-op metrics
    class NoOpMetric:
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    ingestion_total = NoOpMetric()
    search_queries_total = NoOpMetric()
    request_duration_seconds = NoOpMetric()
else:
    # Real Prometheus metrics
    ingestion_total = Counter(
        'ingestion_total',
        'Total resources ingested'
    )
    search_queries_total = Counter(
        'search_queries_total',
        'Total search queries'
    )
    request_duration_seconds = Histogram(
        'request_duration_seconds',
        'Request duration in seconds'
    )

# backend/tests/conftest.py - Test fixture
@pytest.fixture(autouse=True)
def mock_metrics(monkeypatch):
    """Mock all Prometheus metrics for tests."""
    monkeypatch.setenv("TESTING", "true")
    # Reload monitoring module to use test metrics
    import importlib
    import app.monitoring
    importlib.reload(app.monitoring)
```

**Alternative: Pytest Plugin**:
```python
# backend/tests/conftest.py
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_prometheus_metrics(monkeypatch):
    """Replace all Prometheus metrics with mocks."""
    mock_metric = MagicMock()
    monkeypatch.setattr("app.monitoring.ingestion_total", mock_metric)
    monkeypatch.setattr("app.monitoring.search_queries_total", mock_metric)
    # ... mock all other metrics
```

**Files to Modify**:
- `backend/app/monitoring.py` - Add conditional initialization
- `backend/tests/conftest.py` - Add metrics mocking fixture
- All service files that use metrics - Ensure proper imports

**Verification**:
- Run: `pytest backend/tests/unit/phase1_ingestion/ -v`
- Run: `pytest backend/tests/integration/workflows/ -v`
- Verify no AttributeError on metric operations


### 5. Event System API Modernization (P1)

**Root Cause**: EventBus API has changed but tests use old methods and access private attributes.

**API Changes**:
- `clear_listeners()` → `clear_history()`
- Direct access to `_subscribers` (private) → Need public API
- Missing `correlation_id` attribute on Event class

**Fix Strategy**:
1. Update EventBus to provide public test API methods
2. Add `correlation_id` to Event class if needed
3. Update all tests to use public API
4. Deprecate old methods with warnings

**EventBus Public API Design**:

```python
# backend/app/shared/event_bus.py or backend/app/events/event_system.py
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
    
    # Existing methods
    def publish(self, event: Event) -> None:
        """Publish event to all subscribers."""
        pass
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe handler to event type."""
        pass
    
    # NEW: Public API for tests
    def clear_history(self) -> None:
        """Clear event history (for testing)."""
        self._history.clear()
    
    def get_subscribers(self, event_type: str = None) -> Dict[str, List[Callable]]:
        """Get subscribers for testing/debugging."""
        if event_type:
            return {event_type: self._subscribers.get(event_type, [])}
        return self._subscribers.copy()
    
    def get_history(self) -> List[Event]:
        """Get event history (for testing)."""
        return self._history.copy()
    
    def clear_subscribers(self, event_type: str = None) -> None:
        """Clear subscribers (for testing)."""
        if event_type:
            self._subscribers.pop(event_type, None)
        else:
            self._subscribers.clear()

# backend/app/events/event_types.py
@dataclass
class Event:
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None  # ADD if missing
    
    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())
```

**Test Update Pattern**:

```python
# OLD (broken)
event_bus.clear_listeners()
subscribers = event_bus._subscribers

# NEW (fixed)
event_bus.clear_history()
event_bus.clear_subscribers()
subscribers = event_bus.get_subscribers()
```

**Files to Modify**:
- `backend/app/shared/event_bus.py` or `backend/app/events/event_system.py` - Add public API
- `backend/app/events/event_types.py` - Add correlation_id to Event
- `backend/tests/unit/test_event_system.py` - Update all test calls (~15 tests)
- `backend/tests/integration/test_event_hooks.py` - Update all test calls (~15 tests)

**Verification**:
- Run: `pytest backend/tests/unit/test_event_system.py -v`
- Run: `pytest backend/tests/integration/test_event_hooks.py -v`
- Verify no AttributeError on EventBus methods


### 6. Python Dependency Management (P3)

**Root Cause**: Tests import optional modules that aren't installed, causing ImportError.

**Missing Modules**:
- `trio` - Async testing framework
- `openai` - For G-Eval quality metrics
- `plotly` - For visualization features

**Fix Strategy**:
1. Add missing dependencies to requirements-dev.txt
2. Use pytest.importorskip() for optional dependencies
3. Mark tests as skipped with clear reasons when dependencies missing
4. Document optional vs required dependencies

**Dependency Management**:

```python
# backend/requirements-dev.txt - Add optional dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Optional dependencies for advanced features
trio>=0.22.0  # Async testing
openai>=1.0.0  # AI quality metrics
plotly>=5.0.0  # Visualization

# backend/tests/unit/test_async_features.py - Graceful handling
import pytest

trio = pytest.importorskip("trio", reason="trio not installed")

def test_async_feature():
    """Test async feature using trio."""
    # Test code here
    pass

# backend/tests/unit/phase9_quality/test_geval_metrics.py
import pytest

openai = pytest.importorskip("openai", reason="openai not installed for G-Eval")

def test_geval_quality_metric():
    """Test G-Eval quality metrics."""
    # Test code here
    pass

# Alternative: Skip entire module if dependency missing
# At top of test file
pytest.importorskip("plotly")

# Or use skipif decorator
@pytest.mark.skipif(
    not importlib.util.find_spec("plotly"),
    reason="plotly not installed"
)
def test_visualization():
    """Test visualization features."""
    pass
```

**Documentation Update**:

```markdown
# backend/tests/README.md

## Test Dependencies

### Required Dependencies
- pytest
- pytest-asyncio
- pytest-cov
- sqlalchemy
- fastapi

### Optional Dependencies
- trio: Required for async testing features (15 tests)
- openai: Required for G-Eval quality metrics (5 tests)
- plotly: Required for visualization tests (3 tests)

To run all tests including optional features:
```bash
pip install -r requirements-dev.txt
```

To run only core tests:
```bash
pytest -m "not optional"
```
```

**Files to Modify**:
- `backend/requirements-dev.txt` - Add optional dependencies
- `backend/tests/README.md` - Document dependency requirements
- All test files using optional imports (~15 files) - Add importorskip
- `backend/pytest.ini` - Add optional marker

**Verification**:
- Run: `pytest backend/tests/ -v` (without optional deps installed)
- Verify tests are skipped with clear messages, not failed
- Run: `pip install trio openai plotly && pytest backend/tests/ -v`
- Verify previously skipped tests now run


### 7. Quality Service API Restoration (P2)

**Root Cause**: Quality analyzer methods have been renamed or removed, breaking quality tests.

**Missing/Changed Methods**:
- `ContentQualityAnalyzer.content_readability()` - Method doesn't exist
- `ContentQualityAnalyzer.overall_quality_score()` - Method doesn't exist
- Quality dimension calculations return different structures

**Fix Strategy**:
1. Audit QualityService and ContentQualityAnalyzer for current methods
2. Restore missing methods or create adapter methods
3. Update test assertions to match actual return structures
4. Document quality metrics API

**Quality Service API Design**:

```python
# backend/app/services/quality_service.py
class ContentQualityAnalyzer:
    """Analyzes content quality across multiple dimensions."""
    
    def analyze_quality(self, content: str) -> QualityMetrics:
        """Main entry point for quality analysis."""
        return QualityMetrics(
            readability=self.content_readability(content),
            completeness=self.content_completeness(content),
            accuracy=self.content_accuracy(content),
            overall_score=self.overall_quality_score(content)
        )
    
    def content_readability(self, content: str) -> ReadabilityScore:
        """Calculate readability metrics (Flesch, Gunning Fog, etc.)."""
        # If this method was removed, restore it
        flesch_score = self._calculate_flesch_reading_ease(content)
        gunning_fog = self._calculate_gunning_fog(content)
        
        return ReadabilityScore(
            flesch_reading_ease=flesch_score,
            gunning_fog_index=gunning_fog,
            grade_level=self._estimate_grade_level(flesch_score)
        )
    
    def overall_quality_score(self, content: str) -> float:
        """Calculate overall quality score (0-100)."""
        # If this method was removed, restore it
        metrics = self.analyze_quality(content)
        
        # Weighted average of dimensions
        weights = {
            'readability': 0.3,
            'completeness': 0.3,
            'accuracy': 0.4
        }
        
        score = (
            metrics.readability.flesch_reading_ease * weights['readability'] +
            metrics.completeness * weights['completeness'] +
            metrics.accuracy * weights['accuracy']
        )
        
        return min(100.0, max(0.0, score))
    
    # If methods were renamed, add backward compatibility
    def calculate_readability(self, content: str) -> ReadabilityScore:
        """Deprecated: Use content_readability() instead."""
        import warnings
        warnings.warn(
            "calculate_readability() is deprecated, use content_readability()",
            DeprecationWarning
        )
        return self.content_readability(content)

# backend/app/domain/quality.py - Data structures
@dataclass
class ReadabilityScore:
    flesch_reading_ease: float
    gunning_fog_index: float
    grade_level: int

@dataclass
class QualityMetrics:
    readability: ReadabilityScore
    completeness: float
    accuracy: float
    overall_score: float
```

**Test Update Pattern**:

```python
# Update test assertions to match actual return structure
def test_content_readability(quality_analyzer):
    content = "Sample text for analysis."
    
    # OLD (if return type changed)
    score = quality_analyzer.content_readability(content)
    assert isinstance(score, float)
    
    # NEW (if returns structured object)
    result = quality_analyzer.content_readability(content)
    assert isinstance(result, ReadabilityScore)
    assert 0 <= result.flesch_reading_ease <= 100
    assert result.grade_level > 0
```

**Files to Modify**:
- `backend/app/services/quality_service.py` - Restore missing methods
- `backend/app/domain/quality.py` - Ensure data structures match
- `backend/tests/unit/phase9_quality/test_quality_service_phase9.py` - Update assertions (~15 tests)
- `backend/tests/integration/phase9_quality/` - Update integration tests (~10 tests)

**Verification**:
- Run: `pytest backend/tests/unit/phase9_quality/ -v`
- Run: `pytest backend/tests/integration/phase9_quality/ -v`
- Verify no AttributeError on quality methods


### 8. Classification Service Implementation Completion (P2)

**Root Cause**: ML classification service has implementation gaps and missing methods.

**Missing/Broken Features**:
- `ClassificationTrainer.train()` method doesn't exist
- Semi-supervised learning methods return wrong types
- Model checkpoint paths are incorrect

**Fix Strategy**:
1. Implement missing ClassificationTrainer methods
2. Fix semi-supervised learning workflow
3. Correct checkpoint directory structure
4. Update tests to match actual ML workflow

**Classification Service Architecture**:

```python
# backend/app/services/ml_classification_service.py
class ClassificationTrainer:
    """Handles training of classification models."""
    
    def __init__(self, model_dir: str = "models/classification"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def train(
        self,
        training_data: List[TrainingExample],
        model_name: str = "default",
        epochs: int = 10,
        batch_size: int = 32
    ) -> TrainingResult:
        """Train classification model on labeled data."""
        # If this method is missing, implement it
        model = self._initialize_model()
        
        # Training loop
        for epoch in range(epochs):
            loss = self._train_epoch(model, training_data, batch_size)
        
        # Save checkpoint
        checkpoint_path = self.model_dir / f"{model_name}_checkpoint.pt"
        self._save_checkpoint(model, checkpoint_path)
        
        return TrainingResult(
            model_name=model_name,
            final_loss=loss,
            checkpoint_path=str(checkpoint_path),
            metrics=self._evaluate_model(model, training_data)
        )
    
    def train_semi_supervised(
        self,
        labeled_data: List[TrainingExample],
        unlabeled_data: List[str],
        confidence_threshold: float = 0.9
    ) -> TrainingResult:
        """Train using semi-supervised learning."""
        # Fix return type to match tests
        model = self._initialize_model()
        
        # Initial training on labeled data
        self._train_epoch(model, labeled_data, batch_size=32)
        
        # Pseudo-labeling on unlabeled data
        pseudo_labeled = self._generate_pseudo_labels(
            model, unlabeled_data, confidence_threshold
        )
        
        # Retrain with combined data
        combined_data = labeled_data + pseudo_labeled
        result = self.train(combined_data, model_name="semi_supervised")
        
        return result
    
    def load_checkpoint(self, checkpoint_path: str) -> ClassificationModel:
        """Load model from checkpoint."""
        # Fix path handling
        path = Path(checkpoint_path)
        if not path.exists():
            # Try relative to model_dir
            path = self.model_dir / checkpoint_path
        
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        return self._load_model(path)

# backend/app/domain/classification.py - Data structures
@dataclass
class TrainingExample:
    text: str
    label: str
    confidence: float = 1.0

@dataclass
class TrainingResult:
    model_name: str
    final_loss: float
    checkpoint_path: str
    metrics: Dict[str, float]
```

**Checkpoint Directory Structure**:
```
backend/
  models/
    classification/
      default_checkpoint.pt
      semi_supervised_checkpoint.pt
      metadata.json
```

**Files to Modify**:
- `backend/app/services/ml_classification_service.py` - Implement missing methods
- `backend/app/domain/classification.py` - Add data structures
- `backend/tests/unit/phase8_classification/test_ml_classification_service.py` - Update tests (~25 tests)
- `backend/tests/integration/phase8_classification/` - Update integration tests (~15 tests)

**Verification**:
- Run: `pytest backend/tests/unit/phase8_classification/ -v`
- Run: `pytest backend/tests/integration/phase8_classification/ -v`
- Verify training methods execute without errors


### 9. Recommendation Service Refactoring Alignment (P1)

**Root Cause**: Recommendation service was refactored but tests not updated to match new API.

**API Changes**:
- `generate_user_profile_vector()` missing `user_id` parameter
- Removed methods: `_compute_gini_coefficient()`, `apply_novelty_boost()`
- Return types changed for recommendation methods

**Fix Strategy**:
1. Update method signatures to include all required parameters
2. Restore removed utility methods or update tests to not use them
3. Fix return type mismatches
4. Document recommendation API

**Recommendation Service API Design**:

```python
# backend/app/services/recommendation_service.py
class RecommendationService:
    """Generates personalized recommendations."""
    
    def generate_user_profile_vector(
        self,
        db: Session,
        user_id: int,  # ADD if missing
        interaction_history: List[Interaction] = None
    ) -> np.ndarray:
        """Generate user profile vector from interaction history."""
        if interaction_history is None:
            interaction_history = self._get_user_interactions(db, user_id)
        
        # Generate embedding vector
        profile_vector = self._compute_profile_embedding(interaction_history)
        return profile_vector
    
    def generate_recommendations(
        self,
        db: Session,
        user_id: int,
        limit: int = 10,
        diversity_weight: float = 0.3
    ) -> List[RecommendationResult]:
        """Generate recommendations with diversity."""
        # Get candidate resources
        candidates = self._get_candidate_resources(db, user_id)
        
        # Score candidates
        scored = self._score_candidates(db, user_id, candidates)
        
        # Apply diversity boost
        if diversity_weight > 0:
            scored = self.apply_novelty_boost(scored, diversity_weight)
        
        # Return top N
        return sorted(scored, key=lambda x: x.score, reverse=True)[:limit]
    
    # RESTORE if removed and tests depend on it
    def _compute_gini_coefficient(self, values: List[float]) -> float:
        """Compute Gini coefficient for diversity measurement."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        
        return (2 * sum((i + 1) * val for i, val in enumerate(sorted_values))) / (n * sum(sorted_values)) - (n + 1) / n
    
    def apply_novelty_boost(
        self,
        recommendations: List[RecommendationResult],
        boost_weight: float = 0.3
    ) -> List[RecommendationResult]:
        """Apply novelty boost to recommendations."""
        # Calculate novelty scores
        for rec in recommendations:
            novelty = self._calculate_novelty(rec.resource_id)
            rec.score = rec.score * (1 - boost_weight) + novelty * boost_weight
        
        return recommendations

# backend/app/domain/recommendation.py - Data structures
@dataclass
class RecommendationResult:
    resource_id: int
    score: float
    explanation: str
    novelty_score: float = 0.0
    diversity_score: float = 0.0
```

**Test Update Pattern**:

```python
# OLD (missing user_id)
profile = recommendation_service.generate_user_profile_vector(db, interactions)

# NEW (with user_id)
profile = recommendation_service.generate_user_profile_vector(
    db, user_id=123, interaction_history=interactions
)

# If utility methods were removed, update tests
# OLD (calling removed method)
gini = recommendation_service._compute_gini_coefficient(scores)

# NEW (if method restored as public)
gini = recommendation_service.compute_gini_coefficient(scores)

# OR (if method truly removed, calculate in test)
gini = calculate_gini_coefficient(scores)  # Test helper function
```

**Files to Modify**:
- `backend/app/services/recommendation_service.py` - Update signatures, restore methods
- `backend/app/domain/recommendation.py` - Ensure data structures match
- `backend/tests/unit/phase5_graph/` - Update test calls (~10 tests)
- `backend/tests/integration/phase11_recommendations/` - Update test calls (~10 tests)

**Verification**:
- Run: `pytest backend/tests/unit/phase5_graph/ -v -k recommendation`
- Run: `pytest backend/tests/integration/phase11_recommendations/ -v`
- Verify no missing parameter or AttributeError


### 10. Graph Intelligence Feature Completion (P2)

**Root Cause**: Graph construction and LBD discovery features are incomplete.

**Missing Features**:
- `LBDService.open_discovery()` method doesn't exist
- Edge type filtering not working correctly
- Multi-layer graph construction incomplete

**Fix Strategy**:
1. Implement missing LBD discovery methods
2. Fix edge filtering logic
3. Complete multi-layer graph construction
4. Update tests to match implemented features

**Graph Service Architecture**:

```python
# backend/app/services/graph_service.py
class LBDService:
    """Literature-Based Discovery service."""
    
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
    
    def open_discovery(
        self,
        db: Session,
        start_concept: str,
        end_concept: str,
        max_path_length: int = 3
    ) -> List[DiscoveryPath]:
        """
        Perform open discovery to find connections between concepts.
        
        Open discovery (Swanson's ABC model):
        - A: Start concept
        - B: Intermediate concepts (to be discovered)
        - C: End concept
        """
        # Get graph representation
        graph = self.graph_service.build_knowledge_graph(db)
        
        # Find all paths from A to C
        paths = self._find_paths(
            graph, 
            start_concept, 
            end_concept, 
            max_path_length
        )
        
        # Score paths by novelty and relevance
        scored_paths = self._score_discovery_paths(paths)
        
        return sorted(scored_paths, key=lambda x: x.score, reverse=True)
    
    def closed_discovery(
        self,
        db: Session,
        start_concept: str,
        max_intermediate: int = 10
    ) -> List[DiscoveryPath]:
        """
        Perform closed discovery to find related concepts.
        
        Closed discovery: Find B concepts related to A.
        """
        graph = self.graph_service.build_knowledge_graph(db)
        
        # Find intermediate concepts
        intermediates = self._find_intermediate_concepts(
            graph, start_concept, max_intermediate
        )
        
        return intermediates
    
    def _find_paths(
        self,
        graph: nx.Graph,
        start: str,
        end: str,
        max_length: int
    ) -> List[List[str]]:
        """Find all paths between start and end nodes."""
        try:
            paths = list(nx.all_simple_paths(
                graph, start, end, cutoff=max_length
            ))
            return paths
        except nx.NodeNotFound:
            return []

class GraphService:
    """Core graph construction and analysis."""
    
    def build_knowledge_graph(
        self,
        db: Session,
        edge_types: List[str] = None
    ) -> nx.Graph:
        """Build knowledge graph with optional edge filtering."""
        graph = nx.Graph()
        
        # Get all resources and relationships
        resources = db.query(Resource).all()
        relationships = db.query(ResourceRelationship).all()
        
        # Add nodes
        for resource in resources:
            graph.add_node(resource.id, **resource.to_dict())
        
        # Add edges with filtering
        for rel in relationships:
            if edge_types is None or rel.relationship_type in edge_types:
                graph.add_edge(
                    rel.source_id,
                    rel.target_id,
                    type=rel.relationship_type,
                    weight=rel.weight
                )
        
        return graph
    
    def build_multi_layer_graph(
        self,
        db: Session,
        layers: List[str] = None
    ) -> Dict[str, nx.Graph]:
        """Build multi-layer graph with separate layers."""
        if layers is None:
            layers = ['citation', 'semantic', 'author', 'topic']
        
        multi_graph = {}
        
        for layer in layers:
            multi_graph[layer] = self.build_knowledge_graph(
                db, edge_types=[layer]
            )
        
        return multi_graph

# backend/app/domain/graph.py - Data structures
@dataclass
class DiscoveryPath:
    path: List[str]
    score: float
    intermediate_concepts: List[str]
    explanation: str
```

**Files to Modify**:
- `backend/app/services/graph_service.py` - Implement LBD methods
- `backend/app/domain/graph.py` - Add data structures
- `backend/tests/unit/phase10_graph_intelligence/` - Update tests (~10 tests)
- `backend/tests/integration/phase10_graph_intelligence/` - Update tests (~5 tests)

**Verification**:
- Run: `pytest backend/tests/unit/phase10_graph_intelligence/ -v`
- Run: `pytest backend/tests/integration/phase10_graph_intelligence/ -v`
- Verify LBD discovery methods work correctly


## Data Models

### Test Failure Categories

```python
@dataclass
class TestFailureCategory:
    """Categorizes test failures by root cause."""
    name: str
    priority: str  # P0, P1, P2, P3
    affected_tests: int
    root_cause: str
    fix_strategy: str
    files_to_modify: List[str]
    verification_command: str

# Example instances
FAILURE_CATEGORIES = [
    TestFailureCategory(
        name="Database Model Fields",
        priority="P0",
        affected_tests=80,
        root_cause="Tests use legacy field names",
        fix_strategy="Update fixtures to use Dublin Core fields",
        files_to_modify=["backend/tests/conftest.py", "..."],
        verification_command="pytest backend/tests/integration/workflows/ -v"
    ),
    # ... other categories
]
```

### Field Mapping Reference

```python
# Resource model field mappings
RESOURCE_FIELD_MAPPINGS = {
    'url': 'source',
    'resource_type': 'type',
    'resource_id': 'identifier',
    'title': 'title',  # unchanged
    'description': 'description',  # unchanged
}

# User model field mappings (verify actual names)
USER_FIELD_MAPPINGS = {
    'hashed_password': 'password_hash',  # or verify correct name
    'username': 'username',  # unchanged
    'email': 'email',  # unchanged
}
```

## Error Handling

### Test Failure Handling Strategy

1. **Categorize**: Group failures by root cause
2. **Prioritize**: Fix P0 (critical) before P1 (high) before P2 (medium) before P3 (low)
3. **Isolate**: Fix one category at a time to avoid cascading issues
4. **Verify**: Run targeted tests after each fix
5. **Iterate**: If fix doesn't work, analyze and adjust

### Common Error Patterns

```python
# Pattern 1: Unexpected keyword argument
# Error: TypeError: __init__() got an unexpected keyword argument 'url'
# Fix: Change 'url' to 'source' in test fixture

# Pattern 2: AttributeError on None
# Error: AttributeError: 'NoneType' object has no attribute 'inc'
# Fix: Initialize metrics or mock them in tests

# Pattern 3: No such table
# Error: sqlite3.OperationalError: no such table: resources
# Fix: Run migrations in test setup

# Pattern 4: Missing required argument
# Error: TypeError: create_collection() missing 1 required positional argument: 'description'
# Fix: Add description parameter to service call

# Pattern 5: Method doesn't exist
# Error: AttributeError: 'EventBus' object has no attribute 'clear_listeners'
# Fix: Update to use clear_history() method
```

## Testing Strategy

### Verification Approach

1. **Unit Tests First**: Fix unit tests for each component
2. **Integration Tests Second**: Fix integration tests after units pass
3. **End-to-End Tests Last**: Fix workflow tests after integration passes

### Test Execution Plan

```bash
# Phase 1: Database and Models (P0)
pytest backend/tests/unit/ -v -k "model or fixture"
pytest backend/tests/integration/ -v -k "database"

# Phase 2: Core Services (P0)
pytest backend/tests/unit/ -v -k "service"
pytest backend/tests/integration/ -v -k "service"

# Phase 3: Collections and Search (P1)
pytest backend/tests/unit/phase7_collections/ -v
pytest backend/tests/integration/phase3_search/ -v

# Phase 4: Recommendations (P1)
pytest backend/tests/integration/phase11_recommendations/ -v

# Phase 5: Quality and Classification (P2)
pytest backend/tests/unit/phase9_quality/ -v
pytest backend/tests/unit/phase8_classification/ -v

# Phase 6: Graph Intelligence (P2)
pytest backend/tests/unit/phase10_graph_intelligence/ -v

# Phase 7: Full Suite
pytest backend/tests/ -v --tb=short
```

### Success Metrics

- **Target**: 100% pass rate for non-skipped tests
- **Acceptable Skips**: Tests requiring optional dependencies (clearly marked)
- **Zero Tolerance**: No genuine coding errors remain
- **Performance**: Test suite completes in reasonable time (<10 minutes)


## Implementation Phases

### Phase 1: Foundation (P0 - Critical)
**Goal**: Fix database, models, and monitoring infrastructure

**Tasks**:
1. Database migrations and table creation
2. Model field alignment (Resource, User)
3. Monitoring metrics initialization
4. Test fixture updates

**Expected Impact**: ~180 tests fixed (database + monitoring + fixtures)

**Verification**: Core unit tests pass

### Phase 2: Core Services (P0-P1 - Critical to High)
**Goal**: Fix service method signatures and APIs

**Tasks**:
1. CollectionService API updates
2. EventBus API modernization
3. Service method signature fixes

**Expected Impact**: ~80 tests fixed (collections + events)

**Verification**: Service unit tests pass

### Phase 3: Advanced Features (P1-P2 - High to Medium)
**Goal**: Fix recommendation, quality, and classification services

**Tasks**:
1. RecommendationService refactoring alignment
2. QualityService API restoration
3. ClassificationService implementation completion

**Expected Impact**: ~85 tests fixed (recommendations + quality + classification)

**Verification**: Advanced feature tests pass

### Phase 4: Graph Intelligence (P2 - Medium)
**Goal**: Complete graph construction and LBD features

**Tasks**:
1. LBDService implementation
2. Multi-layer graph construction
3. Edge filtering fixes

**Expected Impact**: ~15 tests fixed (graph intelligence)

**Verification**: Graph intelligence tests pass

### Phase 5: Dependencies and Cleanup (P3 - Low)
**Goal**: Handle optional dependencies and final cleanup

**Tasks**:
1. Add optional dependencies to requirements
2. Add pytest.importorskip for optional modules
3. Final test suite run and verification

**Expected Impact**: ~15 tests fixed or properly skipped

**Verification**: Full test suite passes with clear skip messages

## Backward Compatibility

### API Deprecation Strategy

When changing public APIs, use deprecation warnings:

```python
import warnings

def old_method_name(self, *args, **kwargs):
    """Deprecated: Use new_method_name() instead."""
    warnings.warn(
        "old_method_name() is deprecated and will be removed in v3.0. "
        "Use new_method_name() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method_name(*args, **kwargs)
```

### Migration Guide

Document breaking changes in `backend/docs/MIGRATION_GUIDE.md`:

```markdown
## Test Suite Fixes - Breaking Changes

### Resource Model Fields
- `url` → `source` (Dublin Core field)
- `resource_type` → `type` (Dublin Core field)

### EventBus API
- `clear_listeners()` → `clear_history()` + `clear_subscribers()`
- `_subscribers` (private) → `get_subscribers()` (public)

### Quality Service
- `calculate_readability()` → `content_readability()`
- Return types changed to structured objects

### Recommendation Service
- `generate_user_profile_vector()` now requires `user_id` parameter
```

## Performance Considerations

### Test Execution Time

- **Current**: Unknown (likely >10 minutes with failures)
- **Target**: <10 minutes for full suite
- **Strategy**: 
  - Use pytest-xdist for parallel execution
  - Optimize database fixtures (session scope where possible)
  - Mock external services (embeddings, LLMs)

### Database Performance

- Use in-memory SQLite for tests (faster than disk)
- Reuse database connections across tests
- Minimize database resets between tests

```python
# pytest.ini
[pytest]
addopts = -n auto --dist loadfile
```

## Documentation Updates

### Files to Update

1. **API Documentation**: Document all service method signatures
2. **Test README**: Update test execution instructions
3. **Migration Guide**: Document breaking changes
4. **Developer Guide**: Update with new patterns

### API Documentation Template

```python
def method_name(self, param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the method does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    
    Example:
        >>> service.method_name(value1, value2)
        ReturnType(...)
    """
    pass
```
