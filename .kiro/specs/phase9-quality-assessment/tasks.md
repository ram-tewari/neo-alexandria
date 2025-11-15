# Implementation Plan

- [x] 1. Extend Resource Model for Multi-Dimensional Quality





  - Add quality dimension fields (accuracy, completeness, consistency, timeliness, relevance) to Resource model
  - Add weighted overall quality field and quality_weights JSON field
  - Add summarization quality fields (coherence, consistency, fluency, relevance, completeness, conciseness, bertscore, overall)
  - Add anomaly detection fields (is_quality_outlier, outlier_score, outlier_reasons)
  - Add quality metadata fields (quality_last_computed, quality_computation_version, needs_quality_review)
  - Maintain backward compatibility with existing quality_score field
  - _Requirements: 1.1, 1.8, 1.9_

- [x] 2. Create Database Migration for Quality Fields




  - Generate Alembic migration script for new quality columns
  - Add all quality dimension columns with nullable constraint
  - Add summary quality columns with nullable constraint
  - Add anomaly detection columns with nullable constraint
  - Add quality metadata columns with nullable constraint
  - Create index on quality_overall for filtering queries
  - Create index on is_quality_outlier for outlier queries
  - Create index on needs_quality_review for review queue queries
  - Add check constraints ensuring quality scores are between 0.0 and 1.0
  - Test migration with upgrade and downgrade operations
  - _Requirements: 1.1, 1.8_


- [x] 3. Implement Quality Service Core




- [x] 3.1 Create QualityService class with initialization


  - Create app/services/quality_service.py module
  - Implement __init__ method accepting db session and quality_version parameter
  - Define default quality dimension weights dictionary
  - _Requirements: 1.1, 2.1_

- [x] 3.2 Implement compute_quality method


  - Implement main compute_quality method accepting resource_id and optional custom weights
  - Validate custom weights sum to 1.0 and include all five dimensions
  - Call dimension computation methods for accuracy, completeness, consistency, timeliness, relevance
  - Compute weighted overall score using dimension scores and weights
  - Update resource with all dimension scores, overall score, weights JSON, timestamp, and version
  - Update legacy quality_score field for backward compatibility
  - Commit changes to database
  - Return dictionary with all dimension scores and overall score
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.1, 2.2, 2.3, 2.4, 2.5, 10.1_

- [x] 3.3 Implement _compute_accuracy dimension method


  - Calculate citation validity score from Phase 6 citation data (20% weight)
  - Calculate source credibility score based on domain reputation (15% weight)
  - Calculate scholarly metadata score from DOI/PMID/arXiv presence (15% weight)
  - Calculate author metadata score from author field presence (10% weight)
  - Use neutral baseline of 0.5 for resources without citations
  - Return accuracy score between 0.0 and 1.0
  - _Requirements: 1.1, 1.3, 11.1_


- [x] 3.4 Implement _compute_completeness dimension method

  - Calculate required fields score (title, content, url) with 30% weight
  - Calculate important fields score (summary, tags, authors, publication_year) with 30% weight
  - Calculate scholarly fields score (doi, journal, affiliations, funding_sources) with 20% weight
  - Calculate multi-modal content score (equations, tables, figures) with 20% weight
  - Return completeness score between 0.0 and 1.0
  - _Requirements: 1.1, 1.3, 11.1_


- [x] 3.5 Implement _compute_consistency dimension method

  - Calculate title-content alignment using keyword overlap (15% weight)
  - Calculate summary-content alignment using compression ratio heuristic (15% weight)
  - Use optimistic baseline of 0.7 assuming consistency unless proven otherwise
  - Return consistency score between 0.0 and 1.0
  - _Requirements: 1.1, 1.3, 11.1_


- [x] 3.6 Implement _compute_timeliness dimension method

  - Calculate publication recency score using decay function (20 year half-life)
  - Add ingestion recency bonus (10%) for resources ingested within 30 days
  - Use neutral baseline of 0.5 for undated content
  - Return timeliness score between 0.0 and 1.0
  - _Requirements: 1.1, 1.3, 11.1_

- [x] 3.7 Implement _compute_relevance dimension method


  - Calculate classification confidence score from Phase 8.5 taxonomy data (20% weight)
  - Calculate citation count score using logarithmic scaling from Phase 6 data (30% weight)
  - Use neutral baseline of 0.5
  - Return relevance score between 0.0 and 1.0
  - _Requirements: 1.1, 1.3, 11.1_

- [x] 4. Implement Outlier Detection




- [x] 4. Implement Outlier Detection

- [x] 4.1 Implement detect_quality_outliers method

  - Query resources with quality scores in configurable batches (default 1000)
  - Validate minimum 10 resources for statistical validity
  - Build feature matrix from 5 quality dimensions plus 4 summary dimensions when available
  - Train Isolation Forest with contamination=0.1, n_estimators=100, random_state=42
  - Predict anomaly scores for all resources (lower scores = more anomalous)
  - Identify outliers where prediction equals -1
  - Call _identify_outlier_reasons for each outlier
  - Update resources with is_quality_outlier flag, outlier_score, outlier_reasons JSON, and needs_quality_review flag
  - Commit updates to database
  - Return count of detected outliers
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 10.3_


- [x] 4.2 Implement _identify_outlier_reasons helper method

  - Check each quality dimension against threshold of 0.3
  - Append dimension name to reasons list if below threshold (e.g., "low_accuracy")
  - Check summary quality dimensions if available
  - Return list of outlier reason strings
  - _Requirements: 4.7_

- [x] 5. Implement Quality Degradation Monitoring





  - Implement monitor_quality_degradation method accepting time_window_days parameter (default 30)
  - Calculate cutoff date as current time minus time window
  - Query resources with quality_last_computed before cutoff date
  - For each resource, store old quality score and recompute using compute_quality
  - Compare old and new quality scores to detect degradation threshold of 20% drop
  - Calculate degradation percentage for degraded resources
  - Set needs_quality_review flag for degraded resources
  - Commit updates to database
  - Return list of degradation reports with resource_id, title, old_quality, new_quality, degradation_pct
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
-

- [x] 6. Implement Summarization Evaluator Service




- [x] 6.1 Create SummarizationEvaluator class


  - Create app/services/summarization_evaluator.py module
  - Implement __init__ method accepting db session and optional openai_api_key
  - Configure OpenAI API key if provided
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 6.2 Implement G-Eval metrics


  - Implement g_eval_coherence method using GPT-4 to score logical flow on 1-5 scale
  - Implement g_eval_consistency method using GPT-4 to score factual alignment on 1-5 scale
  - Implement g_eval_fluency method using GPT-4 to score grammatical correctness on 1-5 scale
  - Implement g_eval_relevance method using GPT-4 to score key information capture on 1-5 scale
  - Format prompts according to G-Eval paper specifications
  - Normalize scores from 1-5 range to 0.0-1.0 range using formula (rating - 1) / 4
  - Use fallback score of 0.7 when OpenAI API unavailable or errors occur
  - Handle API errors gracefully with try-except blocks
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 11.2, 11.3_


- [x] 6.3 Implement FineSurE metrics

  - Implement finesure_completeness method measuring key information coverage
  - Extract words from reference and summary, remove stopwords
  - Calculate overlap ratio expecting 15% coverage for good summaries
  - Implement finesure_conciseness method measuring information density
  - Calculate compression ratio and score based on optimal range of 5-15%
  - Return scores between 0.0 and 1.0
  - _Requirements: 3.5, 3.6_

- [x] 6.4 Implement BERTScore metric


  - Implement bertscore_f1 method using bert_score library
  - Configure model_type as microsoft/deberta-xlarge-mnli for high quality
  - Extract F1 score from BERTScore results
  - Use fallback score of 0.5 on errors
  - Handle exceptions gracefully
  - _Requirements: 3.7, 11.4_

- [x] 6.5 Implement evaluate_summary method


  - Fetch resource and validate summary exists
  - Extract summary and reference text (content or title)
  - Conditionally compute G-Eval scores if use_g_eval flag true and API key available
  - Use fallback scores of 0.7 for G-Eval metrics when unavailable
  - Compute FineSurE completeness and conciseness scores
  - Compute BERTScore F1 score
  - Calculate composite summary quality using weighted average: coherence 20%, consistency 20%, fluency 15%, relevance 15%, completeness 15%, conciseness 5%, bertscore 10%
  - Update resource with all summary quality scores and overall score
  - Commit changes to database
  - Return dictionary with all summary quality metrics
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 10.2, 11.2, 11.3, 11.4_
- [x] 7. Create Quality API Endpoints








- [x] 7. Create Quality API Endpoints

- [x] 7.1 Implement quality details endpoint

  - Create GET /resources/{id}/quality-details endpoint in app/routers/quality.py
  - Fetch resource and validate existence
  - Return QualityDetailsResponse with all dimension scores, overall score, weights, metadata, outlier status
  - _Requirements: 6.1_


- [x] 7.2 Implement quality recalculation endpoint
  - Create POST /quality/recalculate endpoint accepting QualityRecalculateRequest
  - Validate request contains either resource_id or resource_ids
  - Validate custom weights if provided (sum to 1.0, all dimensions present)
  - Trigger background task for quality computation
  - Return 202 Accepted status
  - _Requirements: 6.2_

- [x] 7.3 Implement outliers listing endpoint

  - Create GET /quality/outliers endpoint with pagination parameters
  - Query resources where is_quality_outlier is true
  - Apply optional filters for min_outlier_score and specific reasons
  - Return paginated OutlierResponse list with total count
  - _Requirements: 6.3_

- [x] 7.4 Implement degradation report endpoint

  - Create GET /quality/degradation endpoint accepting time_window_days parameter
  - Call quality_service.monitor_quality_degradation with time window
  - Return DegradationReport with degraded resources list
  - _Requirements: 6.4_

- [x] 7.5 Implement summary evaluation endpoint

  - Create POST /summaries/{id}/evaluate endpoint with use_g_eval query parameter
  - Trigger background task for summary evaluation
  - Return 202 Accepted status
  - _Requirements: 6.5_

- [x] 7.6 Implement quality distribution endpoint

  - Create GET /quality/distribution endpoint accepting bins and dimension parameters
  - Query quality scores for specified dimension
  - Calculate histogram distribution with configurable bins
  - Calculate statistics (mean, median, standard deviation)
  - Return distribution data and statistics
  - _Requirements: 6.6_

- [x] 7.7 Implement quality trends endpoint

  - Create GET /quality/trends endpoint accepting granularity, date range, and dimension parameters
  - Query quality scores grouped by time period (daily, weekly, monthly)
  - Calculate average quality and resource count per period
  - Return time series data points
  - _Requirements: 6.7_

- [x] 7.8 Implement dimension averages endpoint

  - Create GET /quality/dimensions endpoint
  - Query and calculate average, min, max for each quality dimension across all resources
  - Return dimension statistics and total resource count
  - _Requirements: 6.8_

- [x] 7.9 Implement review queue endpoint

  - Create GET /quality/review-queue endpoint with pagination and sorting parameters
  - Query resources where needs_quality_review is true
  - Sort by outlier_score, quality_overall, or updated_at
  - Return paginated review queue with resource details
  - _Requirements: 6.9_

- [x] 8. Integrate Quality Assessment into Workflows






- [x] 8.1 Integrate with resource ingestion pipeline





  - Modify process_ingestion function in resource_service.py to call quality_service.compute_quality after content extraction
  - Ensure quality computation occurs after embedding generation and ML classification
  - Handle quality computation errors gracefully without blocking ingestion
  - _Requirements: 7.1_

- [x] 8.2 Integrate with resource update workflow


  - Modify update_resource function to trigger quality recomputation when content or metadata changes
  - Track fields that affect quality (title, description, subject, content, metadata)
  - Call quality_service.compute_quality when quality-affecting fields change
  - _Requirements: 7.1_

- [x] 8.3 Integrate with summary generation workflow


  - Modify summary generation completion handler to trigger summarization evaluation
  - Call summarization_evaluator.evaluate_summary after summary is generated
  - Use use_g_eval=False by default to avoid API costs
  - _Requirements: 7.2_

- [x] 8.4 Set up scheduled outlier detection


  - Create scheduled task configuration for daily outlier detection
  - Implement background job calling quality_service.detect_quality_outliers
  - Configure batch size and scheduling frequency
  - _Requirements: 7.3_

- [x] 8.5 Set up scheduled degradation monitoring

  - Create scheduled task configuration for weekly quality degradation monitoring
  - Implement background job calling quality_service.monitor_quality_degradation
  - Configure time window and alert thresholds
  - _Requirements: 7.4_

- [x] 9. Enhance Recommendation Service with Quality Integration





- [x] 9.1 Add quality filtering to generate_user_profile_vector

  - Modify query to exclude resources with is_quality_outlier=true
  - Add optional min_quality parameter to filter by quality_overall threshold
  - _Requirements: 8.1, 8.2_


- [x] 9.2 Add quality boosting to score_candidates

  - Apply configurable quality boost factor (1.2x) for high-quality resources (quality_overall > 0.8)
  - Modify final_score calculation to incorporate quality_overall weighting
  - _Requirements: 8.3_


- [x] 9.3 Add quality filtering to generate_recommendations

  - Add min_quality parameter to API with default None
  - Filter candidates by quality_overall if min_quality specified
  - Exclude outliers from final recommendations
  - _Requirements: 8.4_

- [x] 10. Create Pydantic Schemas


  - Create QualityDetailsResponse schema with all quality fields
  - Create QualityRecalculateRequest schema with validation for weights
  - Create OutlierResponse schema for outlier listing
  - Create DegradationReport schema for degradation reporting
  - Create SummaryEvaluationResponse schema for summary evaluation results
  - Add schemas to app/schemas/quality.py module
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 11. Write Comprehensive Tests

- [x] 11.1 Write unit tests for quality dimension methods
  - Test _compute_accuracy with various citation and metadata scenarios
  - Test _compute_completeness with different metadata coverage levels
  - Test _compute_consistency with title-content alignment cases
  - Test _compute_timeliness with different publication years and ingestion dates
  - Test _compute_relevance with classification and citation data
  - Test compute_quality with default and custom weights
  - Test weight validation for custom weights
  - _Requirements: 9.1, 9.2_
  - _File: backend/tests/test_quality_dimensions.py_

- [x] 11.2 Write unit tests for outlier detection
  - Test detect_quality_outliers with known anomalous data
  - Test _identify_outlier_reasons with various dimension scores
  - Test insufficient data handling (< 10 resources)
  - Test feature matrix construction with missing scores
  - _Requirements: 9.1, 9.3_
  - _File: backend/tests/test_outlier_detection_unit.py_

- [x] 11.3 Write unit tests for summarization evaluator
  - Test G-Eval methods with mocked OpenAI API responses
  - Test FineSurE completeness and conciseness calculations
  - Test BERTScore computation with mocked bert_score library
  - Test evaluate_summary composite score calculation
  - Test fallback behavior when API unavailable
  - _Requirements: 9.1, 9.4, 9.5, 9.6, 9.7_
  - _File: backend/tests/test_summarization_evaluator_unit.py_

- [x] 11.4 Write unit tests for quality degradation monitoring
  - Test monitor_quality_degradation with historical data
  - Test degradation threshold detection (20% drop)
  - Test review flag setting for degraded resources
  - _Requirements: 9.1, 9.7_
  - _File: backend/tests/test_quality_degradation_unit.py_

- [x] 11.5 Write integration tests for quality workflows
  - Test end-to-end quality assessment from resource creation to score storage
  - Test summarization evaluation workflow with summary generation
  - Test outlier detection workflow with batch resources
  - Test quality degradation monitoring with time-based scenarios
  - Test integration with Phase 6 citations, Phase 6.5 scholarly metadata, Phase 8.5 ML classification
  - _Requirements: 9.2_
  - _File: backend/tests/test_quality_workflows_integration.py_

- [x] 11.6 Write API endpoint tests
  - Test all quality API endpoints with valid and invalid inputs
  - Test pagination and filtering for outliers and review queue endpoints
  - Test background task triggering for recalculation and evaluation endpoints
  - Test error handling for missing resources and invalid parameters
  - _Requirements: 9.8_
  - _File: backend/tests/test_quality_api_endpoints.py_

- [x] 11.7 Write performance tests
  - Test quality computation latency for single resource (<1 second)
  - Test batch quality computation throughput (100 resources/minute)
  - Test outlier detection performance (1000 resources in <30 seconds)
  - Test summarization evaluation latency with and without G-Eval
  - _Requirements: 9.8, 10.1, 10.2, 10.3, 10.4_
  - _File: backend/tests/test_quality_performance.py_

- [x] 12. Update Documentation

- [x] 12.1 Update README.md with Phase 9 overview





  - Add Phase 9 section describing multi-dimensional quality assessment
  - Include quick start guide for quality assessment features
  - Document quality dimension meanings and default weights
  - _Requirements: 12.1_

- [x] 12.2 Update API_DOCUMENTATION.md with quality endpoints





  - Document all quality API endpoints with request/response examples
  - Include GET /resources/{id}/quality-details endpoint
  - Include POST /quality/recalculate endpoint
  - Include GET /quality/outliers endpoint
  - Include GET /quality/degradation endpoint
  - Include POST /summaries/{id}/evaluate endpoint
  - Include GET /quality/distribution endpoint
  - Include GET /quality/trends endpoint
  - Include GET /quality/dimensions endpoint
  - Include GET /quality/review-queue endpoint
  - _Requirements: 12.2_

- [x] 12.3 Update DEVELOPER_GUIDE.md with quality service architecture



  - Document QualityService class and methods
  - Document SummarizationEvaluator class and methods
  - Explain quality dimension computation algorithms
  - Document outlier detection with Isolation Forest
  - Document quality degradation monitoring
  - Include extension points for custom quality dimensions
  - Document integration patterns with existing services
  - _Requirements: 12.3_

- [x] 12.4 Update CHANGELOG.md with Phase 9 additions


  - Add Phase 9 section with version 1.2.0
  - Document all new features and enhancements
  - List new API endpoints
  - Document database schema changes
  - Note any breaking changes (none expected)
  - _Requirements: 12.4_

- [x] 12.5 Add inline code documentation
  - Ensure all QualityService methods have comprehensive docstrings
  - Ensure all SummarizationEvaluator methods have comprehensive docstrings
  - Document algorithm details in method docstrings
  - Add usage examples in docstrings where helpful
  - _Requirements: 12.5_
