# Quality Module

## Overview

The Quality module provides comprehensive multi-dimensional quality assessment for resources in Neo Alexandria. It evaluates content quality, metadata completeness, citation quality, and tracks quality degradation over time.

## Purpose

- Assess resource quality across multiple dimensions
- Detect quality outliers for curation review
- Monitor quality degradation over time
- Evaluate summarization quality
- Provide quality-based filtering and ranking

## Module Structure

```
quality/
├── __init__.py          # Public interface and module metadata
├── router.py            # FastAPI endpoints for quality operations
├── service.py           # Core quality assessment logic
├── evaluator.py         # Summarization quality evaluation
├── schema.py            # Pydantic schemas for quality data
├── handlers.py          # Event handlers for quality triggers
├── README.md            # This file
└── tests/               # Module-specific tests
    ├── test_service.py
    ├── test_evaluator.py
    ├── test_router.py
    └── test_handlers.py
```

## Public Interface

### Router
- `quality_router`: FastAPI router with all quality endpoints

### Services
- `QualityService`: Main service for quality assessment
  - `assess_quality(resource_id)`: Compute quality metrics
  - `get_quality_metrics(resource_id)`: Retrieve quality assessment
  - `detect_outliers()`: Find quality outliers
  - `track_degradation()`: Monitor quality changes

- `SummarizationEvaluator`: Evaluate summarization quality
  - `evaluate_summary(original, summary)`: Assess summary quality
  - `compute_rouge_scores()`: Calculate ROUGE metrics
  - `compute_semantic_similarity()`: Measure semantic alignment

### Schemas
- `QualityAssessment`: Complete quality assessment
- `QualityMetrics`: Individual quality metrics
- `QualityDimensions`: Multi-dimensional quality scores
- `QualityOutlier`: Outlier detection result
- `QualityDegradation`: Degradation tracking data

## Events

### Emitted Events

#### quality.computed
Emitted when quality assessment is completed.
```python
{
    "resource_id": int,
    "quality_score": float,
    "dimensions": {
        "content_quality": float,
        "metadata_completeness": float,
        "citation_quality": float
    },
    "timestamp": str
}
```

#### quality.outlier_detected
Emitted when a quality outlier is detected.
```python
{
    "resource_id": int,
    "quality_score": float,
    "outlier_type": str,  # "low" or "high"
    "threshold": float,
    "timestamp": str
}
```

#### quality.degradation_detected
Emitted when quality degradation is detected.
```python
{
    "resource_id": int,
    "previous_score": float,
    "current_score": float,
    "degradation_amount": float,
    "timestamp": str
}
```

### Subscribed Events

#### resource.created
Triggers initial quality computation for new resources.

#### resource.updated
Triggers quality recomputation when resources are modified.

## API Endpoints

### Quality Assessment
- `POST /quality/assess/{resource_id}` - Compute quality metrics
- `GET /quality/{resource_id}` - Get quality assessment
- `GET /quality/outliers` - List quality outliers
- `GET /quality/degradation` - Track quality degradation

### Summarization Evaluation
- `POST /quality/evaluate-summary` - Evaluate summary quality
- `GET /quality/summary-metrics/{resource_id}` - Get summary metrics

### Quality Monitoring
- `GET /quality/statistics` - Get quality statistics
- `GET /quality/trends` - Get quality trends over time
- `POST /quality/recompute-all` - Recompute all quality scores

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event emission and subscription
- `shared.base_model`: Base model classes
- `shared.embeddings`: Embedding generation for semantic similarity
- `shared.ai_core`: AI operations for quality assessment

### External Libraries
- `numpy`: Numerical computations
- `scikit-learn`: Machine learning metrics
- `rouge-score`: ROUGE metrics for summarization

## Usage Examples

### Assess Resource Quality
```python
from app.modules.quality import QualityService

quality_service = QualityService(db)
assessment = await quality_service.assess_quality(resource_id=123)
print(f"Quality Score: {assessment.overall_score}")
```

### Evaluate Summary Quality
```python
from app.modules.quality import SummarizationEvaluator

evaluator = SummarizationEvaluator()
metrics = evaluator.evaluate_summary(
    original_text="...",
    summary_text="..."
)
print(f"ROUGE-1: {metrics.rouge1}")
```

### Subscribe to Quality Events
```python
from app.shared.event_bus import event_bus

@event_bus.subscribe("quality.outlier_detected")
async def handle_outlier(payload):
    resource_id = payload["resource_id"]
    # Add to curation review queue
    await add_to_review_queue(resource_id)
```

## Quality Dimensions

### Content Quality (0-1)
- Text coherence and readability
- Grammar and spelling
- Information density
- Structural organization

### Metadata Completeness (0-1)
- Required fields present
- Optional fields populated
- Metadata accuracy
- Taxonomy classification

### Citation Quality (0-1)
- Citation count
- Citation accuracy
- Citation relevance
- Citation network position

## Testing

Run module-specific tests:
```bash
pytest backend/app/modules/quality/tests/ -v
```

Run with coverage:
```bash
pytest backend/app/modules/quality/tests/ --cov=app.modules.quality --cov-report=html
```

## Migration Notes

This module was extracted from:
- `app/routers/quality.py` → `modules/quality/router.py`
- `app/services/quality_service.py` → `modules/quality/service.py`
- `app/services/summarization_evaluator.py` → `modules/quality/evaluator.py`
- Quality schemas from `app/schemas/quality.py` → `modules/quality/schema.py`

All imports have been updated to use the shared kernel and avoid direct dependencies on other domain modules.

## Version History

- **1.0.0** (Phase 14): Initial extraction as vertical slice module
  - Moved from layered architecture
  - Added event-driven communication
  - Integrated with shared kernel
