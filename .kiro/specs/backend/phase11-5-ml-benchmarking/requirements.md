# Requirements Document

## Introduction

Phase 11.5 establishes a comprehensive ML testing, benchmarking, and documentation system for Neo Alexandria. The system evaluates all machine learning algorithms (Phases 8-11), measures performance against established baselines, generates detailed metric reports, and documents findings in a standardized format for reproducibility and continuous improvement.

## Glossary

- **ML Benchmarking System**: Automated testing infrastructure that evaluates machine learning algorithm performance using standardized metrics and datasets
- **Classification Service**: ML service that categorizes resources into taxonomy nodes using fine-tuned DistilBERT
- **NCF Model**: Neural Collaborative Filtering model used for user-item recommendation predictions
- **Sparse Embedding Service**: Service that generates sparse vector representations for efficient semantic search
- **G-Eval Service**: Summarization quality evaluator using GPT-based evaluation metrics
- **NDCG**: Normalized Discounted Cumulative Gain, a ranking quality metric
- **Hit Rate@K**: Proportion of test cases where at least one relevant item appears in top-K recommendations
- **BERTScore**: Semantic similarity metric between generated and reference text using BERT embeddings
- **Baseline Threshold**: Minimum acceptable performance level that must be maintained
- **Target Threshold**: Aspirational performance level indicating excellent algorithm performance
- **Test Dataset**: Curated collection of labeled examples used for reproducible evaluation
- **Benchmark Runner**: Orchestration system that executes all benchmark suites and generates reports
- **Performance Regression**: Degradation in algorithm performance compared to previous benchmark runs

## Requirements

### Requirement 1: ML Testing Infrastructure

**User Story:** As a machine learning engineer, I want a standardized directory structure for ML benchmarks, so that all testing components are organized and discoverable.

#### Acceptance Criteria

1. WHEN the ML Benchmarking System is initialized, THE system SHALL create a directory structure at `tests/ml_benchmarks/` containing subdirectories for datasets, test modules, and utilities
2. THE ML Benchmarking System SHALL provide a `conftest.py` file with benchmark-specific fixtures for model loading and test data management
3. THE ML Benchmarking System SHALL organize test datasets in `tests/ml_benchmarks/datasets/` with separate JSON files for each ML component
4. THE ML Benchmarking System SHALL include a `benchmark_runner.py` module that orchestrates all benchmark suites
5. THE ML Benchmarking System SHALL include a `report_generator.py` module that produces markdown-formatted benchmark reports

### Requirement 2: Classification Algorithm Benchmarking

**User Story:** As a machine learning engineer, I want comprehensive metrics for the classification service, so that I can evaluate taxonomy classification accuracy and identify weak performance areas.

#### Acceptance Criteria

1. WHEN evaluating the Classification Service, THE ML Benchmarking System SHALL compute overall accuracy and assert it exceeds the baseline threshold of 0.75
2. WHEN evaluating the Classification Service, THE ML Benchmarking System SHALL compute macro-averaged precision, recall, and F1 score with a baseline F1 threshold of 0.70
3. WHEN evaluating the Classification Service, THE ML Benchmarking System SHALL generate per-class performance metrics identifying classes with F1 scores below 0.60
4. WHEN evaluating the Classification Service, THE ML Benchmarking System SHALL measure confidence calibration by binning predictions and computing accuracy per confidence range
5. WHEN evaluating the Classification Service, THE ML Benchmarking System SHALL compute top-K accuracy for K values of 1, 3, and 5
6. THE ML Benchmarking System SHALL use a Test Dataset containing 200 balanced samples across 10 taxonomy classes

### Requirement 3: Collaborative Filtering Benchmarking

**User Story:** As a machine learning engineer, I want to measure recommendation quality using industry-standard metrics, so that I can validate the NCF Model performance.

#### Acceptance Criteria

1. WHEN evaluating the NCF Model, THE ML Benchmarking System SHALL compute NDCG@10 and assert it exceeds the baseline threshold of 0.30
2. WHEN evaluating the NCF Model, THE ML Benchmarking System SHALL compute Hit Rate@10 and assert it exceeds the baseline threshold of 0.40
3. WHEN evaluating the NCF Model, THE ML Benchmarking System SHALL compute Mean Reciprocal Rank (MRR) for all test users
4. WHEN evaluating the NCF Model, THE ML Benchmarking System SHALL measure cold start performance for users with fewer than 5 interactions
5. THE ML Benchmarking System SHALL use a Test Dataset containing 50 users, 200 items, and 1000 interactions with 20% held-out for testing

### Requirement 4: Search Quality Benchmarking

**User Story:** As a machine learning engineer, I want to evaluate three-way hybrid search performance, so that I can compare FTS5, dense, sparse, and hybrid approaches.

#### Acceptance Criteria

1. WHEN evaluating search quality, THE ML Benchmarking System SHALL compute NDCG@20 for the hybrid search system and assert it exceeds the baseline threshold of 0.60
2. WHEN evaluating search quality, THE ML Benchmarking System SHALL compute Precision@10 and Recall@10 for query-document relevance
3. WHEN evaluating search quality, THE ML Benchmarking System SHALL measure query latency at p50, p95, and p99 percentiles
4. WHEN evaluating search quality, THE ML Benchmarking System SHALL compare NDCG scores across FTS5-only, dense-only, sparse-only, and hybrid configurations
5. THE ML Benchmarking System SHALL use a Test Dataset containing 50 queries with graded relevance judgments (0-3 scale)

### Requirement 5: Summarization Quality Benchmarking

**User Story:** As a machine learning engineer, I want to evaluate summarization quality using multiple metrics, so that I can ensure generated summaries meet quality standards.

#### Acceptance Criteria

1. WHEN evaluating the G-Eval Service, THE ML Benchmarking System SHALL compute G-Eval scores for coherence, consistency, fluency, and relevance dimensions
2. WHEN evaluating the G-Eval Service, THE ML Benchmarking System SHALL compute ROUGE-1, ROUGE-2, and ROUGE-L scores
3. WHEN evaluating the G-Eval Service, THE ML Benchmarking System SHALL compute BERTScore F1 and assert it exceeds the baseline threshold of 0.70
4. WHEN evaluating the G-Eval Service, THE ML Benchmarking System SHALL measure compression ratio and assert it falls within the 5-15% target range
5. THE ML Benchmarking System SHALL use a Test Dataset containing text-summary pairs with reference summaries

### Requirement 6: Performance Benchmarking

**User Story:** As a machine learning engineer, I want to measure inference latency for all ML services, so that I can ensure real-time performance requirements are met.

#### Acceptance Criteria

1. WHEN measuring Classification Service performance, THE ML Benchmarking System SHALL assert inference latency at p95 is below 100ms
2. WHEN measuring NCF Model performance, THE ML Benchmarking System SHALL assert prediction latency per user at p95 is below 50ms
3. WHEN measuring search performance, THE ML Benchmarking System SHALL assert three-way hybrid query latency at p95 is below 200ms
4. WHEN measuring Sparse Embedding Service performance, THE ML Benchmarking System SHALL assert embedding generation latency at p95 is below 500ms
5. THE ML Benchmarking System SHALL execute each performance test 100 times and report p50, p95, and p99 latency percentiles

### Requirement 7: Test Dataset Management

**User Story:** As a machine learning engineer, I want standardized test datasets with metadata, so that benchmarks are reproducible and representative of production workloads.

#### Acceptance Criteria

1. THE ML Benchmarking System SHALL store each Test Dataset as a JSON file with a metadata section containing dataset name, creation date, sample count, and description
2. WHEN creating classification Test Datasets, THE ML Benchmarking System SHALL include text samples with true labels, taxonomy node IDs, and difficulty ratings
3. WHEN creating recommendation Test Datasets, THE ML Benchmarking System SHALL include user-item interactions with timestamps and held-out test cases
4. WHEN creating search Test Datasets, THE ML Benchmarking System SHALL include queries with graded relevance judgments for multiple documents
5. THE ML Benchmarking System SHALL document class distribution and data balance characteristics in Test Dataset metadata

### Requirement 8: Automated Benchmark Execution

**User Story:** As a machine learning engineer, I want to run all benchmarks with a single command, so that I can efficiently evaluate system-wide ML performance.

#### Acceptance Criteria

1. WHEN the Benchmark Runner is invoked, THE system SHALL execute classification, collaborative filtering, search, summarization, and performance benchmark suites sequentially
2. WHEN the Benchmark Runner completes, THE system SHALL generate a comprehensive markdown report containing all metrics and comparisons
3. THE Benchmark Runner SHALL complete all benchmark suites in less than 30 minutes
4. WHEN any benchmark fails to meet baseline thresholds, THE Benchmark Runner SHALL report the failure with specific metric values and thresholds
5. THE Benchmark Runner SHALL support command-line arguments for running individual benchmark suites or generating reports only

### Requirement 9: Benchmark Reporting

**User Story:** As a machine learning engineer, I want detailed benchmark reports with actionable recommendations, so that I can identify performance issues and improvement opportunities.

#### Acceptance Criteria

1. WHEN generating a benchmark report, THE system SHALL include an executive summary table with key metrics, baseline thresholds, and pass/fail status
2. WHEN generating a benchmark report, THE system SHALL include per-algorithm sections with detailed metric breakdowns
3. WHEN generating a benchmark report, THE system SHALL identify performance regressions by comparing current results to previous benchmark runs
4. WHEN generating a benchmark report, THE system SHALL provide actionable recommendations for algorithms failing to meet target thresholds
5. THE system SHALL save benchmark reports to `docs/ML_BENCHMARKS.md` with timestamp and system configuration metadata

### Requirement 10: Continuous Integration Support

**User Story:** As a machine learning engineer, I want benchmarks to run automatically in CI/CD pipelines, so that performance regressions are detected before deployment.

#### Acceptance Criteria

1. THE ML Benchmarking System SHALL support execution via pytest with standard test discovery
2. WHEN running in CI environments, THE ML Benchmarking System SHALL use pre-trained model checkpoints to avoid training overhead
3. WHEN model checkpoints are unavailable, THE ML Benchmarking System SHALL skip tests gracefully with informative messages
4. THE ML Benchmarking System SHALL set fixed random seeds for reproducible results across runs
5. THE ML Benchmarking System SHALL support weekly automated benchmark runs with report generation

### Requirement 11: Test Isolation and Safety

**User Story:** As a machine learning engineer, I want benchmarks to run safely without affecting production systems, so that testing does not cause unintended side effects.

#### Acceptance Criteria

1. THE ML Benchmarking System SHALL mock external API calls to OpenAI and other third-party services during benchmark execution
2. THE ML Benchmarking System SHALL use isolated test databases that do not modify production data
3. THE ML Benchmarking System SHALL set timeouts of 30 minutes maximum for complete benchmark suite execution
4. THE ML Benchmarking System SHALL save intermediate results to prevent data loss during long-running benchmarks
5. THE ML Benchmarking System SHALL use model files smaller than 1GB to ensure fast benchmark execution

### Requirement 12: Documentation and Reproducibility

**User Story:** As a machine learning engineer, I want comprehensive documentation of benchmarking methodology, so that results are reproducible and interpretable.

#### Acceptance Criteria

1. THE ML Benchmarking System SHALL provide a `docs/ML_BENCHMARKS.md` document describing benchmarking methodology, test datasets, and evaluation frequency
2. THE ML Benchmarking System SHALL document hardware specifications, software versions, and model configurations used for benchmarks
3. THE ML Benchmarking System SHALL include current benchmark results with timestamps in the documentation
4. THE ML Benchmarking System SHALL document baseline and target thresholds for each metric with justification
5. THE ML Benchmarking System SHALL provide reproduction steps for running benchmarks locally
