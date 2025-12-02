# Design Document: Phase 11.5 ML Benchmarking and Testing Infrastructure

## Overview

Phase 11.5 establishes a comprehensive ML testing, benchmarking, and documentation system for Neo Alexandria. The system provides automated evaluation of all machine learning algorithms (classification, collaborative filtering, search, summarization) with standardized metrics, performance baselines, and detailed reporting capabilities.

### Key Design Goals

1. **Reproducibility**: Fixed random seeds, versioned test datasets, documented methodology
2. **Automation**: Single-command execution, CI/CD integration, scheduled runs
3. **Actionability**: Clear pass/fail criteria, performance regressions, improvement recommendations
4. **Safety**: Mocked external APIs, isolated test databases, timeout protection
5. **Performance**: <30 minute total runtime, cached models, batch processing

### Success Metrics

- All ML algorithms tested with standard evaluation metrics
- Benchmark scores documented with confidence intervals
- Performance baselines established for regression testing
- Automated benchmark suite runs in <30 minutes
- Documentation includes reproduction steps
- Test coverage >85% for ML services

## Architecture

### Directory Structure

```
backend/
├── tests/
│   ├── ml_benchmarks/              # ML benchmark test suite
│   │   ├── __init__.py
│   │   ├── conftest.py             # Benchmark-specific fixtures
│   │   ├── datasets/               # Test datasets (JSON)
│   │   │   ├── __init__.py
│   │   │   ├── classification_test.json
│   │   │   ├── recommendation_test.json
│   │   │   ├── search_relevance.json
│   │   │   └── summarization_test.json
│   │   ├── test_classification_metrics.py
│   │   ├── test_collaborative_filtering_metrics.py
│   │   ├── test_sparse_embeddings_metrics.py
│   │   ├── test_search_quality_metrics.py
│   │   ├── test_summarization_quality_metrics.py
│   │   ├── benchmark_runner.py     # Orchestration
│   │   └── report_generator.py     # Markdown reports
│   ├── performance/                # Performance benchmarks
│   │   ├── __init__.py
│   │   ├── test_ml_latency.py
│   │   ├── test_ml_throughput.py
│   │   └── test_ml_memory.py
│   └── integration/
│       └── test_ml_end_to_end.py
├── docs/
│   └── ML_BENCHMARKS.md            # Benchmark results documentation
└── models/
    ├── classification/
    │   └── benchmark_v1/           # Pre-trained checkpoint
    └── ncf_benchmark_v1.pt         # NCF checkpoint
```


## Components and Interfaces

### 1. Test Dataset Management

**Purpose**: Provide standardized, versioned test datasets for reproducible evaluation.

**Dataset Format** (JSON):
```json
{
  "metadata": {
    "dataset_name": "classification_benchmark_v1",
    "created_at": "2025-11-15",
    "num_samples": 200,
    "description": "Balanced test set for taxonomy classification"
  },
  "samples": [
    {
      "text": "Introduction to neural networks...",
      "true_labels": ["machine-learning", "deep-learning"],
      "taxonomy_node_ids": ["ml-node-1", "dl-node-2"],
      "difficulty": "easy"
    }
  ],
  "class_distribution": {
    "machine-learning": 25,
    "deep-learning": 20
  }
}
```

**Key Design Decisions**:
- JSON format for human readability and version control
- Metadata section for dataset provenance and characteristics
- Balanced class distributions to avoid bias
- Difficulty ratings for stratified analysis
- Separate files per ML component for modularity

### 2. Benchmark Test Fixtures (conftest.py)

**Purpose**: Provide reusable fixtures for model loading, test data, and database setup.

**Key Fixtures**:

```python
@pytest.fixture
def classification_test_data():
    """Load classification test dataset from JSON."""
    dataset_path = Path(__file__).parent / "datasets" / "classification_test.json"
    with open(dataset_path) as f:
        return json.load(f)

@pytest.fixture
def trained_classifier(db_session):
    """
    Load pre-trained classification model.
    
    In CI: Uses checkpoint from models/classification/benchmark_v1
    Locally: Can retrain if needed
    Skips test if model unavailable
    """
    service = MLClassificationService(db_session, model_version="benchmark_v1")
    model_path = Path("models/classification/benchmark_v1")
    
    if not model_path.exists():
        pytest.skip("Benchmark model not available. Run training first.")
    
    service._load_model()
    return service

@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API calls for summarization tests."""
    with patch('openai.ChatCompletion.create') as mock:
        mock.return_value = {
            "choices": [{"message": {"content": "Mocked summary"}}]
        }
        yield mock
```

**Design Rationale**:
- Fixtures handle model loading complexity
- Graceful skipping when models unavailable (CI flexibility)
- Mocked external APIs for safety and speed
- Shared database fixtures from main conftest.py


### 3. Classification Metrics Test Suite

**Purpose**: Evaluate taxonomy classification performance with comprehensive metrics.

**Metrics Evaluated**:
- **Accuracy**: Overall correctness (baseline: 0.75, target: 0.85)
- **Precision/Recall/F1**: Per-class and macro-averaged (baseline F1: 0.70, target: 0.85)
- **Confusion Matrix**: Per-class error analysis
- **Top-K Accuracy**: Proportion where true label in top K predictions (K=1,3,5)
- **Confidence Calibration**: High-confidence predictions should be >90% accurate

**Test Structure**:
```python
class TestClassificationMetrics:
    def test_overall_accuracy(self, trained_classifier, classification_test_data):
        """Assert accuracy > 0.75 baseline."""
        
    def test_precision_recall_f1(self, trained_classifier, classification_test_data):
        """Assert F1 > 0.70 baseline."""
        
    def test_per_class_performance(self, trained_classifier, classification_test_data):
        """Identify weak classes (F1 < 0.6)."""
        
    def test_confidence_calibration(self, trained_classifier, classification_test_data):
        """Assert high-confidence (>0.9) predictions are >85% accurate."""
        
    def test_top_k_accuracy(self, trained_classifier, classification_test_data):
        """Assert top-5 accuracy significantly better than top-1."""
```

**Design Rationale**:
- sklearn.metrics for standard implementations
- Separate tests for each metric (granular failure reporting)
- Baseline assertions prevent regressions
- Detailed logging for debugging (print statements in tests)
- Weak class identification guides data collection

### 4. Collaborative Filtering Metrics Test Suite

**Purpose**: Evaluate NCF recommendation quality using ranking metrics.

**Metrics Evaluated**:
- **NDCG@10**: Normalized Discounted Cumulative Gain (baseline: 0.30, target: 0.50)
- **Hit Rate@10**: Proportion with ≥1 relevant item in top-10 (baseline: 0.40, target: 0.60)
- **MRR**: Mean Reciprocal Rank
- **Precision@K / Recall@K**: Standard ranking metrics
- **Cold Start Performance**: Success rate for users with <5 interactions

**Test Structure**:
```python
class TestCollaborativeFilteringMetrics:
    def test_ndcg_at_10(self, trained_ncf_model, recommendation_test_data):
        """Assert NDCG@10 > 0.30 baseline."""
        
    def test_hit_rate_at_10(self, trained_ncf_model, recommendation_test_data):
        """Assert Hit Rate@10 > 0.40 baseline."""
        
    def test_cold_start_performance(self, trained_ncf_model, recommendation_test_data):
        """Assert cold start success rate > 0.5."""
```

**Design Rationale**:
- sklearn.metrics.ndcg_score for NDCG calculation
- Held-out test set (20% of interactions) for evaluation
- Cold start testing critical for real-world performance
- Batch prediction for efficiency


### 5. Search Quality Metrics Test Suite

**Purpose**: Evaluate three-way hybrid search (FTS5 + Dense + Sparse) performance.

**Metrics Evaluated**:
- **NDCG@20**: Ranking quality with graded relevance (baseline: 0.60, target: 0.75)
- **Precision@10 / Recall@10**: Standard IR metrics
- **Query Latency**: p50, p95, p99 percentiles (target: p95 < 200ms)
- **Component Comparison**: FTS5-only vs Dense-only vs Sparse-only vs Hybrid

**Test Structure**:
```python
class TestSearchQualityMetrics:
    def test_hybrid_search_ndcg(self, search_service, search_relevance_data):
        """Assert hybrid NDCG@20 > 0.60 baseline."""
        
    def test_component_comparison(self, search_service, search_relevance_data):
        """Compare NDCG across FTS5, dense, sparse, hybrid."""
        
    def test_query_latency(self, search_service, search_relevance_data):
        """Assert p95 latency < 200ms."""
```

**Design Rationale**:
- Graded relevance judgments (0-3 scale) for NDCG
- 50 diverse queries covering different search intents
- Latency measured over 100 runs per query
- Component comparison validates hybrid approach

### 6. Summarization Quality Metrics Test Suite

**Purpose**: Evaluate G-Eval summarization quality across multiple dimensions.

**Metrics Evaluated**:
- **G-Eval Scores**: Coherence, consistency, fluency, relevance (GPT-based)
- **ROUGE Scores**: ROUGE-1, ROUGE-2, ROUGE-L (n-gram overlap)
- **BERTScore**: Semantic similarity (baseline: 0.70, target: 0.85)
- **Compression Ratio**: Summary length / original length (target: 5-15%)

**Test Structure**:
```python
class TestSummarizationQualityMetrics:
    def test_bertscore(self, summarization_service, summarization_test_data, mock_openai_api):
        """Assert BERTScore F1 > 0.70 baseline."""
        
    def test_rouge_scores(self, summarization_service, summarization_test_data, mock_openai_api):
        """Compute ROUGE-1, ROUGE-2, ROUGE-L."""
        
    def test_compression_ratio(self, summarization_service, summarization_test_data, mock_openai_api):
        """Assert compression ratio in 5-15% range."""
```

**Design Rationale**:
- Mocked OpenAI API for cost and speed
- BERTScore for semantic similarity (better than ROUGE alone)
- Compression ratio ensures summaries are concise
- G-Eval provides human-aligned quality scores


### 7. Performance Benchmarks

**Purpose**: Measure inference latency and throughput for all ML services.

**Metrics Evaluated**:
- **Classification Inference**: p95 < 100ms
- **NCF Prediction**: p95 < 50ms per user
- **Search Query**: p95 < 200ms (three-way hybrid)
- **Embedding Generation**: p95 < 500ms

**Test Structure**:
```python
class TestMLLatency:
    def test_classification_latency(self, trained_classifier):
        """Run 100 predictions, assert p95 < 100ms."""
        latencies = []
        for _ in range(100):
            start = time.time()
            trained_classifier.predict("Sample text", top_k=5)
            latencies.append((time.time() - start) * 1000)
        
        p95 = np.percentile(latencies, 95)
        assert p95 < 100.0, f"p95 latency {p95:.2f}ms exceeds 100ms"
```

**Design Rationale**:
- 100 runs per test for statistical significance
- Percentile metrics (p50, p95, p99) capture tail latency
- Separate tests for each service (granular failure reporting)
- Warm-up runs excluded from measurements

### 8. Benchmark Runner (Orchestration)

**Purpose**: Execute all benchmark suites and generate comprehensive reports.

**Architecture**:
```python
class BenchmarkRunner:
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = output_dir
        self.results = {}
    
    def run_all_benchmarks(self) -> Dict:
        """
        Run all benchmark suites sequentially.
        
        Returns:
            Dictionary with results from all suites
        """
        self.results = {
            "classification": self._run_classification(),
            "collaborative_filtering": self._run_cf(),
            "search": self._run_search(),
            "summarization": self._run_summarization(),
            "performance": self._run_performance()
        }
        
        self._generate_report()
        return self.results
    
    def _run_classification(self) -> Dict:
        """Run classification benchmarks via pytest."""
        result = pytest.main([
            "tests/ml_benchmarks/test_classification_metrics.py",
            "-v", "--tb=short", "--json-report", "--json-report-file=classification_results.json"
        ])
        return self._parse_pytest_results("classification_results.json")
    
    def _generate_report(self):
        """Generate markdown report."""
        generator = ReportGenerator(self.results)
        report = generator.generate()
        
        output_path = Path(self.output_dir) / "ML_BENCHMARKS.md"
        with open(output_path, "w") as f:
            f.write(report)
```

**Design Rationale**:
- Sequential execution (avoid resource contention)
- pytest integration for standard test discovery
- JSON output for programmatic parsing
- Timeout protection (30 minutes max)
- Intermediate result saving (prevent data loss)


### 9. Report Generator

**Purpose**: Generate comprehensive markdown reports with actionable insights.

**Report Structure**:
```markdown
# Neo Alexandria ML Benchmark Report

**Generated**: 2025-11-15T10:30:00Z
**Hardware**: Intel i7-9700K, 32GB RAM, NVIDIA RTX 3080
**Software**: PyTorch 2.2.1, Transformers 4.38.2

## Executive Summary

| Algorithm | Key Metric | Score | Baseline | Target | Status |
|-----------|------------|-------|----------|--------|--------|
| Classification | F1 Score | 0.87 | 0.70 | 0.85 | ✅ |
| NCF | NDCG@10 | 0.52 | 0.30 | 0.50 | ✅ |
| Search | NDCG@20 | 0.68 | 0.60 | 0.75 | ✅ |
| Summarization | BERTScore | 0.82 | 0.70 | 0.85 | ✅ |

## Classification (Phase 8.5)

### Metrics
- **Accuracy**: 0.87 (✅ Above target 0.85)
- **F1 Score**: 0.86 (✅ Above target 0.85)
- **Precision**: 0.88
- **Recall**: 0.84
- **Inference Time**: 82ms p95 (✅ Below target 100ms)

### Per-Class Performance
| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| machine-learning | 0.92 | 0.88 | 0.90 | 25 |
| quantum-computing | 0.65 | 0.58 | 0.61 | 18 |

### Recommendations
1. ⚠️ Weak performance on "Quantum Computing" class (F1=0.58)
   - **Action**: Add 50 more training examples
2. ✅ All latency targets met

## Performance Regressions

No regressions detected since last benchmark run (2025-11-08).

## Reproduction Steps

```bash
# Run all benchmarks
pytest tests/ml_benchmarks/ -v --tb=short

# Generate report
python tests/ml_benchmarks/benchmark_runner.py --output docs/ML_BENCHMARKS.md
```
```

**Design Rationale**:
- Executive summary for quick overview
- Per-algorithm detailed sections
- Actionable recommendations (not just metrics)
- Regression detection (compare to previous runs)
- Reproduction steps for transparency


## Data Models

### Test Dataset Schema

**Classification Test Dataset**:
```json
{
  "metadata": {
    "dataset_name": "string",
    "created_at": "ISO8601 date",
    "num_samples": "integer",
    "num_classes": "integer",
    "description": "string"
  },
  "samples": [
    {
      "text": "string (resource content)",
      "true_labels": ["string (label names)"],
      "taxonomy_node_ids": ["string (node IDs)"],
      "difficulty": "easy|medium|hard"
    }
  ],
  "class_distribution": {
    "label_name": "integer (count)"
  }
}
```

**Recommendation Test Dataset**:
```json
{
  "metadata": {
    "dataset_name": "string",
    "created_at": "ISO8601 date",
    "num_users": "integer",
    "num_items": "integer",
    "num_interactions": "integer"
  },
  "interactions": [
    {
      "user_id": "string",
      "resource_id": "string",
      "interaction_type": "view|annotation|collection_add",
      "strength": "float (0-1)",
      "timestamp": "ISO8601 date"
    }
  ],
  "held_out_test": [
    {
      "user_id": "string",
      "resource_id": "string",
      "is_relevant": "boolean"
    }
  ]
}
```

**Search Relevance Dataset**:
```json
{
  "metadata": {
    "dataset_name": "string",
    "created_at": "ISO8601 date",
    "num_queries": "integer"
  },
  "queries": [
    {
      "query_id": "string",
      "query_text": "string",
      "relevance_judgments": {
        "resource_id": "integer (0-3, 0=not relevant, 3=highly relevant)"
      }
    }
  ]
}
```

### Benchmark Results Schema

```python
@dataclass
class BenchmarkResult:
    """Result from a single benchmark test."""
    test_name: str
    metric_name: str
    score: float
    baseline: float
    target: float
    passed: bool
    timestamp: datetime
    details: Dict[str, Any]  # Additional metrics, per-class results, etc.

@dataclass
class BenchmarkSuiteResult:
    """Results from a complete benchmark suite."""
    suite_name: str  # "classification", "collaborative_filtering", etc.
    results: List[BenchmarkResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time_seconds: float
    recommendations: List[str]
```


## Error Handling

### Model Loading Failures

**Scenario**: Pre-trained model checkpoint not found.

**Handling**:
```python
@pytest.fixture
def trained_classifier(db_session):
    service = MLClassificationService(db_session, model_version="benchmark_v1")
    model_path = Path("models/classification/benchmark_v1")
    
    if not model_path.exists():
        pytest.skip("Benchmark model not available. Run training first.")
    
    try:
        service._load_model()
    except Exception as e:
        pytest.skip(f"Failed to load model: {str(e)}")
    
    return service
```

**Rationale**: Graceful skipping allows CI to run without models, local developers can train models separately.

### Test Data Validation

**Scenario**: Test dataset has invalid format or missing fields.

**Handling**:
```python
def validate_classification_dataset(data: Dict) -> None:
    """Validate classification test dataset schema."""
    required_fields = ["metadata", "samples", "class_distribution"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["samples"], list) or len(data["samples"]) == 0:
        raise ValueError("Dataset must contain at least one sample")
    
    for i, sample in enumerate(data["samples"]):
        required_sample_fields = ["text", "true_labels", "taxonomy_node_ids"]
        for field in required_sample_fields:
            if field not in sample:
                raise ValueError(f"Sample {i} missing required field: {field}")
```

**Rationale**: Early validation prevents cryptic test failures, provides clear error messages.

### External API Failures

**Scenario**: OpenAI API call fails during summarization tests.

**Handling**:
```python
@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API with fallback error handling."""
    with patch('openai.ChatCompletion.create') as mock:
        def side_effect(*args, **kwargs):
            # Simulate occasional API failures
            if random.random() < 0.05:  # 5% failure rate
                raise openai.error.APIError("Simulated API failure")
            return {"choices": [{"message": {"content": "Mocked summary"}}]}
        
        mock.side_effect = side_effect
        yield mock

def test_summarization_with_retry(summarization_service, mock_openai_api):
    """Test summarization with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = summarization_service.summarize("Long text...")
            break
        except openai.error.APIError:
            if attempt == max_retries - 1:
                pytest.fail("Summarization failed after 3 retries")
            time.sleep(1)
```

**Rationale**: Mocking prevents real API calls, retry logic handles transient failures.

### Timeout Protection

**Scenario**: Benchmark suite hangs or takes too long.

**Handling**:
```python
@pytest.mark.timeout(1800)  # 30 minutes
def test_full_benchmark_suite():
    """Run all benchmarks with timeout protection."""
    runner = BenchmarkRunner()
    results = runner.run_all_benchmarks()
    assert results is not None
```

**Rationale**: Prevents CI from hanging indefinitely, enforces <30 minute constraint.


## Testing Strategy

### Unit Tests

**Scope**: Individual metric calculations, dataset validation, report generation.

**Examples**:
- `test_ndcg_calculation()`: Verify NDCG@K computation with known inputs
- `test_dataset_validation()`: Ensure invalid datasets raise appropriate errors
- `test_report_formatting()`: Verify markdown report structure

**Rationale**: Isolate metric calculation logic from ML model dependencies.

### Integration Tests

**Scope**: End-to-end benchmark execution with real models and test datasets.

**Examples**:
- `test_classification_benchmark_suite()`: Run all classification tests
- `test_benchmark_runner_execution()`: Verify orchestration and report generation
- `test_ci_integration()`: Simulate CI environment (no models, graceful skipping)

**Rationale**: Validate complete workflow from test execution to report generation.

### Performance Tests

**Scope**: Latency and throughput measurements for ML services.

**Examples**:
- `test_classification_latency()`: Measure p50, p95, p99 inference time
- `test_search_throughput()`: Measure queries per second
- `test_memory_usage()`: Monitor memory consumption during batch processing

**Rationale**: Ensure real-time performance requirements are met.

### Regression Tests

**Scope**: Compare current benchmark results to previous runs.

**Examples**:
- `test_no_accuracy_regression()`: Assert accuracy hasn't decreased by >5%
- `test_no_latency_regression()`: Assert p95 latency hasn't increased by >20%

**Rationale**: Detect performance degradation before deployment.

### Test Execution Strategy

1. **Local Development**:
   ```bash
   # Run specific benchmark suite
   pytest tests/ml_benchmarks/test_classification_metrics.py -v
   
   # Run all benchmarks
   pytest tests/ml_benchmarks/ -v --tb=short
   
   # Generate report
   python tests/ml_benchmarks/benchmark_runner.py
   ```

2. **CI/CD Pipeline**:
   ```yaml
   # .github/workflows/ml_benchmarks.yml
   name: ML Benchmarks
   on:
     schedule:
       - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
     workflow_dispatch:  # Manual trigger
   
   jobs:
     benchmarks:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Download model checkpoints
           run: |
             aws s3 cp s3://neo-alexandria-models/benchmark_v1/ models/ --recursive
         - name: Run benchmarks
           run: |
             pytest tests/ml_benchmarks/ -v --tb=short --json-report
         - name: Generate report
           run: |
             python tests/ml_benchmarks/benchmark_runner.py
         - name: Commit report
           run: |
             git add docs/ML_BENCHMARKS.md
             git commit -m "Update ML benchmark results"
             git push
   ```

3. **Pre-Deployment Validation**:
   ```bash
   # Run benchmarks before merging to main
   pytest tests/ml_benchmarks/ -v --tb=short
   
   # Fail if any baseline not met
   if [ $? -ne 0 ]; then
     echo "Benchmarks failed. Do not merge."
     exit 1
   fi
   ```


## Performance Considerations

### Model Loading Optimization

**Challenge**: Loading large models (DistilBERT, NCF) is slow.

**Solution**:
- Cache loaded models in fixtures (session scope)
- Use pre-trained checkpoints (avoid training in tests)
- Lazy loading (only load when needed)

```python
@pytest.fixture(scope="session")
def trained_classifier_session():
    """Session-scoped classifier (loaded once per test session)."""
    service = MLClassificationService(db_session, model_version="benchmark_v1")
    service._load_model()
    return service
```

**Impact**: Reduces test suite runtime from ~45 minutes to <30 minutes.

### Batch Processing

**Challenge**: Predicting scores for 1000s of items individually is slow.

**Solution**:
- Batch predictions in NCF model (vectorized operations)
- Batch embedding generation (process multiple texts at once)

```python
def get_top_recommendations_batch(self, user_ids: List[str], candidate_ids: List[str], limit: int = 20):
    """Batch prediction for multiple users."""
    # Create user-item pairs
    user_indices = [self.user_id_to_idx[uid] for uid in user_ids for _ in candidate_ids]
    item_indices = [self.item_id_to_idx[cid] for _ in user_ids for cid in candidate_ids]
    
    # Single forward pass
    with torch.no_grad():
        scores = self.model(torch.LongTensor(user_indices), torch.LongTensor(item_indices))
    
    # Group by user
    results = {}
    for i, user_id in enumerate(user_ids):
        start_idx = i * len(candidate_ids)
        end_idx = start_idx + len(candidate_ids)
        user_scores = scores[start_idx:end_idx]
        results[user_id] = list(zip(candidate_ids, user_scores.cpu().numpy()))
    
    return results
```

**Impact**: 10x speedup for recommendation benchmarks.

### Memory Management

**Challenge**: Loading multiple large models causes OOM errors.

**Solution**:
- Sequential benchmark execution (not parallel)
- Explicit model cleanup after each suite
- GPU memory clearing (if using CUDA)

```python
def _run_classification(self):
    """Run classification benchmarks with cleanup."""
    result = pytest.main(["tests/ml_benchmarks/test_classification_metrics.py"])
    
    # Cleanup
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    gc.collect()
    
    return result
```

**Impact**: Prevents OOM errors on machines with <16GB RAM.

### Caching Strategy

**Challenge**: Repeated embedding generation is expensive.

**Solution**:
- Cache user embeddings with TTL (5 minutes)
- Cache test dataset parsing (session scope)
- Cache metric calculations for identical inputs

```python
@lru_cache(maxsize=1000)
def compute_ndcg(true_relevance: Tuple[int], predicted_scores: Tuple[float], k: int) -> float:
    """Cached NDCG computation."""
    return ndcg_score([list(true_relevance)], [list(predicted_scores)], k=k)
```

**Impact**: 30% reduction in benchmark runtime.


## Security and Safety

### External API Mocking

**Requirement**: Never call real OpenAI API during tests.

**Implementation**:
```python
@pytest.fixture(autouse=True)
def mock_all_external_apis():
    """Auto-mock all external APIs for safety."""
    with patch('openai.ChatCompletion.create') as mock_openai, \
         patch('requests.get') as mock_requests:
        
        mock_openai.return_value = {"choices": [{"message": {"content": "Mocked"}}]}
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {}
        
        yield
```

**Rationale**: Prevents accidental API costs, ensures tests run offline.

### Database Isolation

**Requirement**: Tests must not modify production database.

**Implementation**:
```python
@pytest.fixture
def isolated_test_db():
    """Create isolated test database."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    engine = create_engine(f"sqlite:///{temp_db.name}")
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    os.unlink(temp_db.name)
```

**Rationale**: Prevents data corruption, allows parallel test execution.

### Model Checkpoint Verification

**Requirement**: Verify model checkpoints are not corrupted.

**Implementation**:
```python
def verify_model_checkpoint(model_path: Path) -> bool:
    """Verify model checkpoint integrity."""
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        
        required_keys = ['model_state_dict', 'user_id_to_idx', 'item_id_to_idx']
        for key in required_keys:
            if key not in checkpoint:
                logger.error(f"Missing key in checkpoint: {key}")
                return False
        
        # Verify state dict can be loaded
        model = NCFModel(
            num_users=checkpoint['num_users'],
            num_items=checkpoint['num_items']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        
        return True
    except Exception as e:
        logger.error(f"Checkpoint verification failed: {str(e)}")
        return False
```

**Rationale**: Prevents cryptic errors from corrupted checkpoints.

### Timeout Protection

**Requirement**: Prevent infinite loops or hanging tests.

**Implementation**:
```python
# pytest.ini
[pytest]
timeout = 1800  # 30 minutes global timeout
timeout_method = thread
```

**Rationale**: Ensures CI doesn't hang, enforces performance constraints.

### Resource Limits

**Requirement**: Prevent excessive memory or CPU usage.

**Implementation**:
```python
import resource

def set_resource_limits():
    """Set memory and CPU limits for tests."""
    # Limit memory to 8GB
    resource.setrlimit(resource.RLIMIT_AS, (8 * 1024 * 1024 * 1024, -1))
    
    # Limit CPU time to 25 minutes
    resource.setrlimit(resource.RLIMIT_CPU, (1500, -1))

# Call at test session start
@pytest.fixture(scope="session", autouse=True)
def setup_resource_limits():
    set_resource_limits()
```

**Rationale**: Prevents runaway processes, protects CI infrastructure.


## Documentation Requirements

### ML_BENCHMARKS.md Structure

```markdown
# Neo Alexandria ML Benchmark Report

**Generated**: [ISO8601 timestamp]
**Hardware**: [CPU, RAM, GPU specs]
**Software**: [PyTorch version, Transformers version, Python version]
**Commit**: [Git commit hash]

## Executive Summary

[Table with all algorithms, key metrics, baselines, targets, status]

## Benchmarking Methodology

### Test Datasets
- **Classification**: 200 labeled examples, 10 classes, balanced distribution
- **Recommendation**: 50 users, 200 items, 1000 interactions, 20% held-out
- **Search**: 50 queries, graded relevance (0-3 scale)
- **Summarization**: 30 text-summary pairs with reference summaries

### Evaluation Frequency
- **Automated**: Weekly (Sunday 2 AM UTC)
- **Manual**: Before major releases
- **Regression Testing**: On every PR to main branch

### Hardware Specifications
- **CPU**: Intel i7-9700K (8 cores, 3.6 GHz)
- **RAM**: 32GB DDR4
- **GPU**: NVIDIA RTX 3080 (10GB VRAM)
- **Storage**: NVMe SSD

### Software Versions
- **Python**: 3.11.5
- **PyTorch**: 2.2.1
- **Transformers**: 4.38.2
- **scikit-learn**: 1.4.0

## Current Results (as of [date])

### Classification (Phase 8.5)
[Detailed metrics, per-class performance, recommendations]

### Collaborative Filtering (Phase 11)
[Detailed metrics, cold start performance, recommendations]

### Search Quality (Phase 4)
[Detailed metrics, component comparison, recommendations]

### Summarization Quality (Phase 9)
[Detailed metrics, compression ratio, recommendations]

### Performance Benchmarks
[Latency percentiles, throughput metrics]

## Performance Regressions

[List of any regressions detected, or "No regressions detected"]

## Recommendations

[Prioritized list of actionable improvements]

## Reproduction Steps

```bash
# Clone repository
git clone https://github.com/neo-alexandria/neo-alexandria.git
cd neo-alexandria

# Install dependencies
pip install -r backend/requirements.txt

# Download model checkpoints
python scripts/download_benchmark_models.py

# Run benchmarks
pytest tests/ml_benchmarks/ -v --tb=short

# Generate report
python tests/ml_benchmarks/benchmark_runner.py --output docs/ML_BENCHMARKS.md
```

## Appendix

### Baseline and Target Thresholds

| Metric | Baseline | Target | Justification |
|--------|----------|--------|---------------|
| Classification F1 | 0.70 | 0.85 | Industry standard for text classification |
| NDCG@10 | 0.30 | 0.50 | Typical for implicit feedback systems |
| Search NDCG@20 | 0.60 | 0.75 | High-quality search engines achieve 0.7+ |
| BERTScore | 0.70 | 0.85 | Strong semantic similarity |

### Change Log

- **2025-11-15**: Initial benchmark suite implementation
- **2025-11-08**: Added cold start performance tests
- **2025-11-01**: Implemented regression detection
```

### Developer Guide Updates

Add section to `backend/docs/DEVELOPER_GUIDE.md`:

```markdown
## ML Benchmarking

### Running Benchmarks Locally

```bash
# Run all benchmarks
pytest tests/ml_benchmarks/ -v --tb=short

# Run specific suite
pytest tests/ml_benchmarks/test_classification_metrics.py -v

# Generate report
python tests/ml_benchmarks/benchmark_runner.py
```

### Creating Test Datasets

1. **Collect Representative Samples**: Ensure balanced class distribution
2. **Label Carefully**: Use multiple annotators for quality
3. **Validate Schema**: Run `validate_dataset.py` before committing
4. **Version Control**: Commit datasets to Git with descriptive names

### Adding New Benchmarks

1. Create test file in `tests/ml_benchmarks/test_<component>_metrics.py`
2. Define fixtures in `conftest.py`
3. Implement metric calculations using sklearn or custom functions
4. Add assertions with baseline and target thresholds
5. Update `benchmark_runner.py` to include new suite
6. Document in `ML_BENCHMARKS.md`

### Interpreting Results

- **Green (✅)**: Metric exceeds target threshold
- **Yellow (⚠️)**: Metric meets baseline but below target
- **Red (❌)**: Metric below baseline (regression)

### Troubleshooting

**Issue**: Model checkpoint not found
**Solution**: Download checkpoints with `python scripts/download_benchmark_models.py`

**Issue**: Tests timeout
**Solution**: Reduce test dataset size or increase timeout in `pytest.ini`

**Issue**: OOM errors
**Solution**: Run suites sequentially, reduce batch size, or use smaller models
```


## Implementation Phases

### Phase 1: Infrastructure Setup (Days 1-2)
- Create directory structure (`tests/ml_benchmarks/`, `tests/performance/`)
- Implement `conftest.py` with base fixtures
- Set up test database isolation
- Configure pytest settings (timeouts, markers)

### Phase 2: Test Dataset Creation (Days 3-4)
- Create classification test dataset (200 samples, 10 classes)
- Create recommendation test dataset (50 users, 200 items, 1000 interactions)
- Create search relevance dataset (50 queries with graded judgments)
- Create summarization test dataset (30 text-summary pairs)
- Implement dataset validation utilities

### Phase 3: Classification Benchmarks (Days 5-6)
- Implement `test_classification_metrics.py`
- Add accuracy, precision, recall, F1 tests
- Add confidence calibration tests
- Add top-K accuracy tests
- Add per-class performance analysis

### Phase 4: Collaborative Filtering Benchmarks (Days 7-8)
- Implement `test_collaborative_filtering_metrics.py`
- Add NDCG@10, Hit Rate@10, MRR tests
- Add cold start performance tests
- Add precision@K and recall@K tests

### Phase 5: Search Quality Benchmarks (Days 9-10)
- Implement `test_search_quality_metrics.py`
- Add NDCG@20 tests for hybrid search
- Add component comparison tests (FTS5, dense, sparse, hybrid)
- Add query latency tests

### Phase 6: Summarization Quality Benchmarks (Days 11-12)
- Implement `test_summarization_quality_metrics.py`
- Add BERTScore tests
- Add ROUGE score tests
- Add compression ratio tests
- Mock OpenAI API calls

### Phase 7: Performance Benchmarks (Days 13-14)
- Implement `test_ml_latency.py`
- Add classification inference latency tests
- Add NCF prediction latency tests
- Add search query latency tests
- Add embedding generation latency tests

### Phase 8: Orchestration and Reporting (Days 15-16)
- Implement `benchmark_runner.py`
- Implement `report_generator.py`
- Add regression detection logic
- Add recommendation generation
- Create `ML_BENCHMARKS.md` template

### Phase 9: CI/CD Integration (Days 17-18)
- Create GitHub Actions workflow
- Set up model checkpoint storage (S3 or Git LFS)
- Configure weekly automated runs
- Add pre-deployment validation
- Test CI pipeline end-to-end

### Phase 10: Documentation and Polish (Days 19-20)
- Update `DEVELOPER_GUIDE.md` with benchmarking section
- Create troubleshooting guide
- Add reproduction steps to `ML_BENCHMARKS.md`
- Write example usage documentation
- Final testing and bug fixes

## Dependencies

### Python Packages
```
# Core testing
pytest>=7.4.0
pytest-timeout>=2.1.0
pytest-json-report>=1.5.0

# ML metrics
scikit-learn>=1.4.0
numpy>=1.24.0

# NLP metrics
rouge-score>=0.1.2
bert-score>=0.3.13

# Existing dependencies
torch>=2.2.0
transformers>=4.38.0
sqlalchemy>=2.0.0
```

### External Resources
- Pre-trained model checkpoints (DistilBERT, NCF)
- Test datasets (JSON files, ~10MB total)
- Benchmark result history (for regression detection)

### System Requirements
- **Minimum**: 8GB RAM, 4 CPU cores, 10GB disk space
- **Recommended**: 16GB RAM, 8 CPU cores, 20GB disk space, GPU (optional)

## Risks and Mitigations

### Risk 1: Model Checkpoints Too Large for Git
**Impact**: Slow clones, repository bloat
**Mitigation**: Use Git LFS or S3 for model storage, download on-demand

### Risk 2: Test Datasets Become Stale
**Impact**: Benchmarks don't reflect production performance
**Mitigation**: Quarterly dataset refresh, sample from production data

### Risk 3: Benchmarks Take Too Long
**Impact**: Developers skip running benchmarks
**Mitigation**: Optimize with caching, batch processing, parallel execution where safe

### Risk 4: Baseline Thresholds Too Strict
**Impact**: Frequent false positives, developer frustration
**Mitigation**: Set conservative baselines initially, adjust based on empirical data

### Risk 5: External API Costs
**Impact**: Expensive test runs (OpenAI API)
**Mitigation**: Mock all external APIs, use cached responses

## Success Criteria

1. ✅ All 12 requirements from requirements.md implemented
2. ✅ Benchmark suite runs in <30 minutes
3. ✅ Test coverage >85% for ML services
4. ✅ CI/CD integration working (weekly automated runs)
5. ✅ Documentation complete (ML_BENCHMARKS.md, DEVELOPER_GUIDE.md)
6. ✅ Zero production API calls during tests
7. ✅ Regression detection functional (compares to previous runs)
8. ✅ Actionable recommendations generated for failing tests

## Future Enhancements

### Phase 11.6: Advanced Benchmarking
- A/B testing framework for model comparisons
- Fairness and bias metrics
- Explainability metrics (SHAP, LIME)
- Multi-language support for classification

### Phase 11.7: Real-Time Monitoring
- Production metric tracking (Prometheus integration)
- Alerting for performance degradation
- Dashboard for live benchmark results (Grafana)
- Automated model retraining triggers

### Phase 11.8: Benchmark Optimization
- Distributed benchmark execution (Ray, Dask)
- GPU acceleration for batch processing
- Incremental benchmarking (only changed components)
- Benchmark result caching and deduplication
