# Implementation Plan

- [x] 1. Set up ML benchmarking infrastructure





  - Create `tests/ml_benchmarks/` directory structure with subdirectories for datasets, test modules, and utilities
  - Create `tests/performance/` directory for performance-specific tests
  - Implement `tests/ml_benchmarks/__init__.py` with package initialization
  - _Requirements: 1.1, 1.2, 1.3_


- [x] 1.1 Create benchmark-specific test fixtures

  - Implement `tests/ml_benchmarks/conftest.py` with fixtures for model loading, test data management, and database isolation
  - Add `classification_test_data()` fixture that loads and parses classification test dataset JSON
  - Add `recommendation_test_data()` fixture that loads and parses recommendation test dataset JSON
  - Add `search_relevance_data()` fixture that loads and parses search relevance dataset JSON
  - Add `summarization_test_data()` fixture that loads and parses summarization test dataset JSON
  - Add `trained_classifier()` fixture that loads pre-trained classification model with graceful skipping if unavailable
  - Add `trained_ncf_model()` fixture that loads pre-trained NCF model with graceful skipping if unavailable
  - Add `mock_openai_api()` fixture that mocks OpenAI API calls for summarization tests
  - Add `isolated_test_db()` fixture that creates temporary SQLite database for test isolation
  - _Requirements: 1.2, 11.1, 11.2_


- [x] 2. Create standardized test datasets




  - Create `tests/ml_benchmarks/datasets/` directory
  - Implement `tests/ml_benchmarks/datasets/__init__.py` with dataset utilities

  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2.1 Create classification test dataset

  - Create `tests/ml_benchmarks/datasets/classification_test.json` with 200 balanced samples across 10 taxonomy classes
  - Include metadata section with dataset name, creation date, sample count, class count, and description
  - Include samples with text, true_labels, taxonomy_node_ids, and difficulty ratings
  - Include class_distribution section documenting sample counts per class
  - Ensure balanced distribution (15-25 samples per class)
  - _Requirements: 2.6, 7.1, 7.2_


- [x] 2.2 Create recommendation test dataset

  - Create `tests/ml_benchmarks/datasets/recommendation_test.json` with 50 users, 200 items, 1000 interactions
  - Include metadata section with dataset name, creation date, user count, item count, interaction count
  - Include interactions array with user_id, resource_id, interaction_type, strength, timestamp
  - Include held_out_test array (20% of interactions) with user_id, resource_id, is_relevant for evaluation
  - _Requirements: 3.5, 7.1, 7.3_


- [x] 2.3 Create search relevance test dataset

  - Create `tests/ml_benchmarks/datasets/search_relevance.json` with 50 queries and graded relevance judgments
  - Include metadata section with dataset name, creation date, query count
  - Include queries array with query_id, query_text, and relevance_judgments dict mapping resource_ids to relevance scores (0-3 scale)
  - Ensure diverse query types (keyword, semantic, multi-term)
  - _Requirements: 4.5, 7.1, 7.4_

- [x] 2.4 Create summarization test dataset


  - Create `tests/ml_benchmarks/datasets/summarization_test.json` with 30 text-summary pairs
  - Include metadata section with dataset name, creation date, sample count
  - Include samples array with original_text, reference_summary, and expected_compression_ratio
  - Ensure diverse text lengths (500-2000 words)
  - _Requirements: 5.5, 7.1, 7.5_
-


- [x] 3. Implement classification benchmark tests



  - Create `tests/ml_benchmarks/test_classification_metrics.py` with TestClassificationMetrics class
  - Import required libraries: pytest, json, sklearn.metrics, numpy, pathlib
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 3.1 Implement overall accuracy test


  - Write `test_overall_accuracy()` method that predicts labels for all test samples
  - Compute accuracy using sklearn.metrics.accuracy_score
  - Assert accuracy > 0.75 baseline threshold
  - Log accuracy score and target comparison
  - _Requirements: 2.1_


- [x] 3.2 Implement precision, recall, F1 test

  - Write `test_precision_recall_f1()` method that computes macro-averaged metrics
  - Use sklearn.metrics.precision_recall_fscore_support with average='macro'
  - Assert F1 score > 0.70 baseline threshold
  - Log precision, recall, F1 scores with target comparisons
  - _Requirements: 2.2_



- [ ] 3.3 Implement per-class performance test
  - Write `test_per_class_performance()` method that generates classification report
  - Use sklearn.metrics.classification_report with output_dict=True
  - Log per-class precision, recall, F1, and support
  - Identify and log weak classes with F1 < 0.6

  - _Requirements: 2.3_


- [ ] 3.4 Implement confidence calibration test
  - Write `test_confidence_calibration()` method that bins predictions by confidence
  - Create bins: 0.9-1.0, 0.7-0.9, 0.5-0.7, 0.0-0.5
  - Compute accuracy within each confidence bin

  - Assert high-confidence (>0.9) predictions are >85% accurate

  - _Requirements: 2.4_

- [ ] 3.5 Implement top-K accuracy test
  - Write `test_top_k_accuracy()` method that checks if true label in top-K predictions

  - Compute top-1, top-3, and top-5 accuracy
  - Assert top-5 accuracy is significantly higher than top-1 (>10% improvement)
  - Log all top-K accuracy scores
  - _Requirements: 2.5_

- [x] 4. Implement collaborative filtering benchmark tests




  - Create `tests/ml_benchmarks/test_collaborative_filtering_metrics.py` with TestCollaborativeFilteringMetrics class
  - Import required libraries: pytest, json, numpy, sklearn.metrics.ndcg_score, pathlib
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 Implement NDCG@10 test

  - Write `test_ndcg_at_10()` method that computes NDCG for held-out test cases
  - Group test cases by user_id
  - For each user, predict scores for all candidate items
  - Compute NDCG@10 using sklearn.metrics.ndcg_score with k=10
  - Assert average NDCG@10 > 0.30 baseline threshold
  - _Requirements: 3.1_


- [x] 4.2 Implement Hit Rate@10 test

  - Write `test_hit_rate_at_10()` method that checks for relevant items in top-10
  - For each user, get top-10 predictions
  - Check if any relevant item appears in top-10
  - Compute hit rate as proportion of users with hits
  - Assert hit rate > 0.40 baseline threshold
  - _Requirements: 3.2_


- [x] 4.3 Implement cold start performance test

  - Write `test_cold_start_performance()` method that filters users with <5 interactions
  - Attempt predictions for cold start users
  - Measure success rate (proportion of users with valid predictions)
  - Assert cold start success rate > 0.5
  - Log number of cold start users and success rate
  - _Requirements: 3.4_

- [x] 5. Implement search quality benchmark tests



  - Create `tests/ml_benchmarks/test_search_quality_metrics.py` with TestSearchQualityMetrics class
  - Import required libraries: pytest, json, numpy, sklearn.metrics, time, pathlib
  - _Requirements: 4.1, 4.2, 4.3, 4.4_


- [x] 5.1 Implement hybrid search NDCG@20 test

  - Write `test_hybrid_search_ndcg()` method that evaluates three-way hybrid search
  - For each query, execute hybrid search and get top-20 results
  - Map results to relevance judgments from test dataset
  - Compute NDCG@20 using sklearn.metrics.ndcg_score with k=20
  - Assert average NDCG@20 > 0.60 baseline threshold
  - _Requirements: 4.1_

- [x] 5.2 Implement precision and recall at K test

  - Write `test_precision_recall_at_10()` method that computes IR metrics
  - For each query, get top-10 results
  - Compute precision@10 and recall@10 based on relevance judgments
  - Log average precision and recall across all queries
  - _Requirements: 4.2_


- [x] 5.3 Implement query latency test


  - Write `test_query_latency()` method that measures search performance
  - Execute each query 100 times and record latencies
  - Compute p50, p95, p99 latency percentiles
  - Assert p95 latency < 200ms
  - Log latency distribution
  - _Requirements: 4.3_




- [x] 5.4 Implement component comparison test

  - Write `test_component_comparison()` method that compares search approaches
  - Execute queries using FTS5-only, dense-only, sparse-only, and hybrid configurations
  - Compute NDCG@20 for each approach
  - Log comparison table showing relative performance
  - Assert hybrid approach achieves highest NDCG
  - _Requirements: 4.4_

-

- [x] 6. Implement summarization quality benchmark tests



  - Create `tests/ml_benchmarks/test_summarization_quality_metrics.py` with TestSummarizationQualityMetrics class
  - Import required libraries: pytest, json, numpy, rouge_score, bert_score, pathlib
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6.1 Implement BERTScore test

  - Write `test_bertscore()` method that computes semantic similarity
  - Generate summaries for all test samples using mocked OpenAI API
  - Compute BERTScore F1 between generated and reference summaries
  - Assert average BERTScore F1 > 0.70 baseline threshold
  - Log BERTScore precision, recall, and F1
  - _Requirements: 5.3_


- [x] 6.2 Implement ROUGE scores test

  - Write `test_rouge_scores()` method that computes n-gram overlap metrics
  - Generate summaries for all test samples
  - Compute ROUGE-1, ROUGE-2, and ROUGE-L scores
  - Log all ROUGE scores with averages
  - _Requirements: 5.2_



- [x] 6.3 Implement compression ratio test

  - Write `test_compression_ratio()` method that measures summary conciseness
  - For each sample, compute ratio of summary length to original text length
  - Assert average compression ratio is between 0.05 and 0.15 (5-15%)
  - Log compression ratio distribution
  - _Requirements: 5.4_

- [x] 7. Implement performance benchmark tests





  - Create `tests/performance/test_ml_latency.py` with TestMLLatency class
  - Import required libraries: pytest, time, numpy
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
-

- [x] 7.1 Implement classification inference latency test




  - Write `test_classification_latency()` method that measures prediction time
  - Execute 100 classification predictions with sample texts
  - Record latency for each prediction in milliseconds
  - Compute p50, p95, p99 latency percentiles

  - Assert p95 latency < 100ms
  - _Requirements: 6.1, 6.5_

- [x] 7.2 Implement NCF prediction latency test

  - Write `test_ncf_prediction_latency()` method that measures recommendation time
  - Execute 100 NCF predictions for user-item pairs
  - Record latency for each prediction in milliseconds

  - Compute p50, p95, p99 latency percentiles
  - Assert p95 latency < 50ms per user
  - _Requirements: 6.2, 6.5_


- [x] 7.3 Implement search query latency test

  - Write `test_search_query_latency()` method that measures three-way hybrid search time
  - Execute 100 search queries with diverse query texts

  - Record latency for each query in milliseconds
  - Compute p50, p95, p99 latency percentiles
  - Assert p95 latency < 200ms
  - _Requirements: 6.3, 6.5_



- [x] 7.4 Implement embedding generation latency test




  - Write `test_embedding_generation_latency()` method that measures sparse embedding time
  - Execute 100 embedding generations with sample texts
  - Record latency for each generation in milliseconds
  - Compute p50, p95, p99 latency percentiles
  - Assert p95 latency < 500ms
  - _Requirements: 6.4, 6.5_

- [x] 8. Implement benchmark orchestration




  - Create `tests/ml_benchmarks/benchmark_runner.py` with BenchmarkRunner class
  - Import required libraries: pytest, json, pathlib, datetime, subprocess
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


- [x] 8.1 Implement benchmark suite execution

  - Write `run_all_benchmarks()` method that executes all benchmark suites sequentially
  - Execute classification benchmarks via pytest.main() with JSON output
  - Execute collaborative filtering benchmarks via pytest.main() with JSON output
  - Execute search quality benchmarks via pytest.main() with JSON output
  - Execute summarization quality benchmarks via pytest.main() with JSON output
  - Execute performance benchmarks via pytest.main() with JSON output
  - Parse JSON results from each suite
  - _Requirements: 8.1, 8.2_


- [x] 8.2 Implement result aggregation

  - Write `_parse_pytest_results()` method that parses pytest JSON output
  - Extract test names, metric values, pass/fail status, execution times
  - Aggregate results into BenchmarkSuiteResult dataclass instances
  - Compute total tests, passed tests, failed tests per suite
  - _Requirements: 8.1, 8.4_

- [x] 8.3 Implement timeout and cleanup


  - Add timeout protection (30 minutes max) using pytest-timeout
  - Implement `_cleanup_after_suite()` method that clears GPU memory and runs garbage collection
  - Call cleanup after each suite execution
  - _Requirements: 8.3, 11.4_


- [x] 8.4 Implement command-line interface

  - Add argparse for command-line arguments (--output, --suite, --report-only)
  - Support running individual suites (--suite classification)
  - Support report generation only (--report-only) without running tests
  - Add main() function for CLI entry point
  - _Requirements: 8.5_

- [x] 9. Implement report generation





  - Create `tests/ml_benchmarks/report_generator.py` with ReportGenerator class
  - Import required libraries: datetime, pathlib, typing
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [x] 9.1 Implement executive summary generation

  - Write `_generate_executive_summary()` method that creates summary table
  - Include columns: Algorithm, Key Metric, Score, Baseline, Target, Status
  - Use ✅ for passing (above target), ⚠️ for warning (above baseline, below target), ❌ for failing (below baseline)
  - Format as markdown table
  - _Requirements: 9.1_


- [x] 9.2 Implement per-algorithm sections

  - Write `_generate_classification_section()` method with detailed classification metrics
  - Write `_generate_cf_section()` method with detailed collaborative filtering metrics
  - Write `_generate_search_section()` method with detailed search quality metrics
  - Write `_generate_summarization_section()` method with detailed summarization metrics
  - Write `_generate_performance_section()` method with latency percentiles
  - Include metric breakdowns, per-class/per-query results, and visualizations (ASCII art)
  - _Requirements: 9.2_


- [x] 9.3 Implement regression detection

  - Write `_detect_regressions()` method that compares current results to previous runs
  - Load previous benchmark results from `docs/ML_BENCHMARKS_HISTORY.json`
  - Compare key metrics (accuracy, F1, NDCG, BERTScore, latencies)
  - Flag regressions where metrics decreased by >5% or latencies increased by >20%
  - Generate regression report section
  - _Requirements: 9.3_


- [x] 9.4 Implement recommendation generation

  - Write `_generate_recommendations()` method that creates actionable improvement suggestions
  - For failing tests, suggest specific actions (add training data, tune hyperparameters, optimize code)
  - Prioritize recommendations by impact (high/medium/low)
  - Format as numbered list with clear action items
  - _Requirements: 9.4_


- [x] 9.5 Implement report assembly and saving

  - Write `generate()` method that assembles complete markdown report
  - Include header with timestamp, hardware specs, software versions, git commit hash
  - Include executive summary, methodology, current results, regressions, recommendations, reproduction steps
  - Write report to `docs/ML_BENCHMARKS.md`
  - Save results to `docs/ML_BENCHMARKS_HISTORY.json` for regression tracking
  - _Requirements: 9.5_

- [x] 10. Create documentation





  - Update `backend/docs/DEVELOPER_GUIDE.md` with ML benchmarking section
  - Create initial `backend/docs/ML_BENCHMARKS.md` with template structure

  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 10.1 Document benchmarking methodology

  - Add section to ML_BENCHMARKS.md describing test datasets, evaluation frequency, hardware/software specs
  - Document baseline and target thresholds for each metric with justifications
  - Include information about EARS patterns and INCOSE quality rules used in requirements
  - _Requirements: 12.1, 12.2, 12.4_


- [x] 10.2 Document reproduction steps

  - Add section to ML_BENCHMARKS.md with step-by-step instructions for running benchmarks locally
  - Include commands for installing dependencies, downloading model checkpoints, running tests, generating reports
  - Document environment setup (Python version, virtual environment, GPU requirements)
  - _Requirements: 12.5_


- [x] 10.3 Update developer guide

  - Add "ML Benchmarking" section to DEVELOPER_GUIDE.md
  - Document how to run benchmarks locally, create test datasets, add new benchmarks, interpret results
  - Include troubleshooting guide for common issues (model not found, timeouts, OOM errors)
  - _Requirements: 12.1, 12.5_

- [ ] 11. Implement CI/CD integration
  - Create `.github/workflows/ml_benchmarks.yml` workflow file
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 11.1 Configure weekly automated runs
  - Set up cron schedule for weekly runs (Sunday 2 AM UTC)
  - Add workflow_dispatch trigger for manual runs
  - Configure job to run on ubuntu-latest runner
  - _Requirements: 10.5_

- [ ] 11.2 Implement model checkpoint management
  - Add step to download pre-trained model checkpoints from S3 or Git LFS
  - Use AWS CLI or git-lfs commands to fetch models
  - Verify checkpoint integrity before running tests
  - _Requirements: 10.2_

- [ ] 11.3 Configure test execution in CI
  - Add step to install Python dependencies from requirements.txt
  - Add step to run pytest with ml_benchmarks suite
  - Configure pytest with --tb=short and --json-report flags
  - Set timeout to 30 minutes
  - _Requirements: 10.1, 10.3_

- [ ] 11.4 Implement report generation and commit
  - Add step to run benchmark_runner.py to generate markdown report
  - Add step to commit ML_BENCHMARKS.md to repository
  - Configure git user for automated commits
  - Push changes to main branch
  - _Requirements: 10.5_

- [ ] 11.5 Add pre-deployment validation
  - Create separate workflow for PR validation
  - Run benchmarks on every PR to main branch
  - Fail PR if any baseline threshold not met
  - Post benchmark results as PR comment
  - _Requirements: 10.1_
