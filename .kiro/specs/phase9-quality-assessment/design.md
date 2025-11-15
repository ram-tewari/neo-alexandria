# Phase 9 Design Document: Enhanced Quality Assessment & Summarization Evaluation

## Overview

Phase 9 transforms Neo Alexandria's basic quality scoring system into a comprehensive multi-dimensional quality assessment framework. The system evaluates resources across five independent quality dimensions (accuracy, completeness, consistency, timeliness, relevance), implements state-of-the-art summarization evaluation using G-Eval, FineSurE, and BERTScore metrics, and provides automated outlier detection with quality degradation monitoring to maintain system health over time.

### Key Objectives

- Achieve 90%+ detection rate for low-quality content
- G-Eval correlation >0.85 with human quality judgments
- Quality computation latency <1 second per resource (excluding G-Eval)
- Automated quality degradation detection >95% accuracy
- Multi-dimensional scoring provides actionable insights for curators
- Support configurable quality dimension weights for domain customization

### Technology Stack

- **ML Framework**: scikit-learn (Isolation Forest for anomaly detection)
- **NLP Metrics**: BERTScore (microsoft/deberta-xlarge-mnli)
- **LLM Evaluation**: OpenAI GPT-4 (G-Eval framework)
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **API**: FastAPI with background tasks
- **Dependencies**: bert-score, openai, scikit-learn, numpy

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  /quality/*  |  /summaries/*/evaluate  |  /quality/review   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Quality    │  │Summarization │  │ Recommendation│     │
│  │   Service    │  │  Evaluator   │  │   Service     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Resource    │  │  Citation    │  │  Taxonomy    │     │
│  │  (enhanced)  │  │  (Phase 6)   │  │ (Phase 8.5)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 External Services                            │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  OpenAI API  │  │  BERTScore   │                        │
│  │  (G-Eval)    │  │   Models     │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Multi-Dimensional Quality Assessment Flow
```
Resource → Compute Accuracy → Compute Completeness → Compute Consistency
                                                              ↓
                                                    Compute Timeliness
                                                              ↓
                                                    Compute Relevance
                                                              ↓
                                            Weighted Overall Score
                                                              ↓
                                                    Store All Dimensions
```

#### Summarization Evaluation Flow
```
Resource with Summary → G-Eval (Coherence, Consistency, Fluency, Relevance)
                                                              ↓
                                            FineSurE (Completeness, Conciseness)
                                                              ↓
                                                    BERTScore F1
                                                              ↓
                                            Composite Summary Quality
                                                              ↓
                                                    Store All Metrics
```

#### Outlier Detection Flow
```
Batch Resources → Build Feature Matrix → Train Isolation Forest
                                                              ↓
                                                    Predict Anomaly Scores
                                                              ↓
                                            Flag Outliers (score < threshold)
                                                              ↓
                                            Identify Outlier Reasons
                                                              ↓
                                                    Set Review Flags
```


## Components and Interfaces

### 1. Enhanced Resource Model

#### New Quality Fields

The Resource model is extended with comprehensive quality metadata fields:

**Multi-Dimensional Quality Scores (0.0-1.0 each):**
- `quality_accuracy` (float, nullable): Factual correctness, citation validity, source credibility
- `quality_completeness` (float, nullable): Metadata coverage, content depth, scholarly fields
- `quality_consistency` (float, nullable): Internal coherence, no contradictions
- `quality_timeliness` (float, nullable): Recency, publication date relevance
- `quality_relevance` (float, nullable): Topical alignment, user value

**Weighted Overall Quality:**
- `quality_overall` (float, nullable): Weighted average of dimensions
- `quality_weights` (str, nullable): JSON storing applied weights

**Summarization Quality (if summary exists):**
- `summary_coherence` (float, nullable): G-Eval coherence score
- `summary_consistency` (float, nullable): G-Eval consistency score
- `summary_fluency` (float, nullable): G-Eval fluency score
- `summary_relevance` (float, nullable): G-Eval relevance score
- `summary_completeness` (float, nullable): FineSurE completeness
- `summary_conciseness` (float, nullable): FineSurE conciseness
- `summary_bertscore` (float, nullable): BERTScore F1
- `summary_quality_overall` (float, nullable): Composite summary quality

**Anomaly Detection:**
- `is_quality_outlier` (bool, nullable): Flagged by Isolation Forest
- `outlier_score` (float, nullable): Anomaly score (lower = more anomalous)
- `outlier_reasons` (str, nullable): JSON array of reasons

**Quality Metadata:**
- `quality_last_computed` (datetime, nullable): Last computation timestamp
- `quality_computation_version` (str, nullable): Algorithm version (e.g., "v2.0")
- `needs_quality_review` (bool, nullable): Human review flag

**Indexes:**
- `idx_resources_quality_overall`: ON (quality_overall) - for quality filtering
- `idx_resources_outlier`: ON (is_quality_outlier) - for outlier queries
- `idx_resources_needs_review`: ON (needs_quality_review) - for review queue

**Backward Compatibility:**
- Existing `quality_score` field maintained and updated with `quality_overall` value
- All new fields nullable to support incremental migration

### 2. Quality Service

#### QualityService Class

Core service for multi-dimensional quality assessment with outlier detection and degradation monitoring.

**Initialization:**
```python
def __init__(
    self,
    db: Session,
    quality_version: str = "v2.0"
)
```

**Configuration:**
```python
default_weights = {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
}
```

**Key Methods:**

##### compute_quality()
Computes multi-dimensional quality scores for a resource.

**Parameters:**
- `resource_id` (str): Resource UUID to assess
- `weights` (Dict[str, float], optional): Custom dimension weights

**Algorithm:**
1. Fetch resource from database
2. Validate weights (if provided) sum to 1.0
3. Compute each dimension score:
   - `_compute_accuracy()`: Citation validity, source credibility, scholarly metadata
   - `_compute_completeness()`: Metadata coverage, content depth, multi-modal content
   - `_compute_consistency()`: Title-content alignment, summary-content alignment
   - `_compute_timeliness()`: Publication recency, ingestion date
   - `_compute_relevance()`: Classification confidence, citation count
4. Compute weighted overall: Σ(weight_i × dimension_i)
5. Update resource with all scores, weights, timestamp, version
6. Update legacy quality_score for backward compatibility
7. Commit to database

**Returns:** Dict with all dimension scores and overall score

**Performance:** <1 second per resource

**Example Return:**
```python
{
    "accuracy": 0.75,
    "completeness": 0.82,
    "consistency": 0.88,
    "timeliness": 0.65,
    "relevance": 0.79,
    "overall": 0.77
}
```

##### _compute_accuracy()
Computes accuracy dimension score.

**Factors:**
1. **Citation Validity (20%)**: Ratio of valid citations (Phase 6 integration)
2. **Source Credibility (15%)**: Domain reputation (.edu, .gov, .org, arxiv.org, doi.org)
3. **Scholarly Metadata (15%)**: Presence of DOI, PMID, arXiv ID (Phase 6.5)
4. **Author Metadata (10%)**: Presence of author information

**Baseline:** 0.5 (neutral for resources without citations)

**Algorithm:**
```python
score = 0.5  # Neutral baseline
if citations exist:
    valid_ratio = valid_citations / total_citations
    score += 0.2 * valid_ratio
if credible_domain:
    score += 0.15
if has_academic_identifier:
    score += 0.15
if has_authors:
    score += 0.10
return min(score, 1.0)
```

**Returns:** Float 0.0-1.0

##### _compute_completeness()
Computes completeness dimension score.

**Factors:**
1. **Required Fields (30%)**: title, content, url
2. **Important Fields (30%)**: summary, tags, authors, publication_year
3. **Scholarly Fields (20%)**: doi, journal, affiliations, funding_sources
4. **Multi-modal Content (20%)**: equations, tables, figures

**Algorithm:**
```python
score = 0.0
# Required fields
filled_required = count(title, content, url)
score += 0.3 * (filled_required / 3)
# Important fields
filled_important = count(summary, tags, authors, publication_year)
score += 0.3 * (filled_important / 4)
# Scholarly fields
filled_scholarly = count(doi, journal, affiliations, funding_sources)
score += 0.2 * (filled_scholarly / 4)
# Multi-modal
multimodal_score = (has_equations + has_tables + has_figures) / 3
score += 0.2 * multimodal_score
return score
```

**Returns:** Float 0.0-1.0

##### _compute_consistency()
Computes consistency dimension score.

**Factors:**
1. **Title-Content Alignment (15%)**: Keyword overlap between title and content
2. **Summary-Content Alignment (15%)**: Semantic similarity (BERTScore integration)

**Baseline:** 0.7 (optimistic - assume consistent unless proven otherwise)

**Algorithm:**
```python
score = 0.7  # Optimistic baseline
# Title-content alignment
title_words = set(title.lower().split())
content_words = set(content.lower().split()[:500])
overlap = len(title_words & content_words) / len(title_words)
score += 0.15 * overlap
# Summary-content alignment
if summary exists:
    compression_ratio = len(summary.split()) / len(content.split())
    if 0.05 <= compression_ratio <= 0.15:  # Good summary length
        score += 0.15
return min(score, 1.0)
```

**Returns:** Float 0.0-1.0

##### _compute_timeliness()
Computes timeliness dimension score.

**Factors:**
1. **Publication Recency**: Decay function based on publication year
2. **Ingestion Recency (10%)**: Bonus for recently ingested content

**Decay Function:**
- Current year: 1.0
- 10 years old: 0.5
- 20+ years old: 0.0

**Algorithm:**
```python
score = 0.5  # Neutral for undated content
if publication_year exists:
    age_years = current_year - publication_year
    if age_years <= 0:
        recency_score = 1.0
    else:
        recency_score = max(0.0, 1.0 - (age_years / 20))
    score = recency_score
# Ingestion recency bonus
if ingested_within_30_days:
    score += 0.1
return min(score, 1.0)
```

**Returns:** Float 0.0-1.0

##### _compute_relevance()
Computes relevance dimension score.

**Factors:**
1. **Classification Confidence (20%)**: Average confidence from Phase 8.5 ML classification
2. **Citation Count (30%)**: Logarithmic scaling of inbound citations (Phase 6)
3. **User Engagement**: Placeholder for future annotation count

**Baseline:** 0.5 (neutral)

**Algorithm:**
```python
score = 0.5  # Neutral baseline
# Classification confidence
if taxonomy_classifications exist:
    avg_confidence = mean([tc.confidence for tc in classifications])
    score += 0.2 * avg_confidence
# Citation count (logarithmic)
if inbound_citations exist:
    citation_count = len(inbound_citations)
    citation_score = min(0.3, log10(citation_count + 1) / 10)
    score += citation_score
return min(score, 1.0)
```

**Returns:** Float 0.0-1.0


##### detect_quality_outliers()
Uses Isolation Forest to detect quality outliers across all resources.

**Parameters:**
- `batch_size` (int): Processing batch size (default: 1000)

**Algorithm:**
1. Query resources with quality scores (limit: batch_size)
2. Require minimum 10 resources for statistical validity
3. Build feature matrix:
   - 5 quality dimensions (accuracy, completeness, consistency, timeliness, relevance)
   - 4 summary scores if available (coherence, consistency, fluency, relevance)
4. Train Isolation Forest:
   - contamination=0.1 (expect 10% outliers)
   - n_estimators=100
   - random_state=42 (reproducibility)
5. Predict anomaly scores (lower = more anomalous)
6. Identify outliers (prediction == -1)
7. For each outlier:
   - Identify specific reasons (dimensions with scores <0.3)
   - Set is_quality_outlier=True
   - Store outlier_score
   - Store outlier_reasons as JSON
   - Set needs_quality_review=True
8. Commit updates to database

**Performance:** <30 seconds for 1000 resources

**Side Effects:** Updates resource quality flags in database

**Example Outlier Reasons:**
```python
["low_accuracy", "low_completeness", "low_summary_coherence"]
```

##### _identify_outlier_reasons()
Identifies which quality dimensions are causing outlier status.

**Heuristic:** Dimensions with scores <0.3 or >0.95 are unusual

**Algorithm:**
```python
reasons = []
if quality_accuracy < 0.3:
    reasons.append("low_accuracy")
if quality_completeness < 0.3:
    reasons.append("low_completeness")
if quality_consistency < 0.3:
    reasons.append("low_consistency")
if quality_timeliness < 0.3:
    reasons.append("low_timeliness")
if quality_relevance < 0.3:
    reasons.append("low_relevance")
if summary_coherence < 0.3:
    reasons.append("low_summary_coherence")
return reasons
```

**Returns:** List[str] of outlier reasons

##### monitor_quality_degradation()
Detects quality degradation over time by comparing historical scores.

**Parameters:**
- `time_window_days` (int): Lookback period (default: 30)

**Algorithm:**
1. Compute cutoff date: now - time_window_days
2. Query resources with quality_last_computed < cutoff
3. For each resource:
   - Store old_quality = quality_overall
   - Recompute quality using compute_quality()
   - Get new_quality = quality_overall
   - If old_quality - new_quality > 0.2 (20% drop):
     - Calculate degradation_pct
     - Add to degraded_resources list
     - Set needs_quality_review=True
4. Commit updates
5. Return degradation report

**Use Cases:**
- Broken links (accuracy drops)
- Outdated content (timeliness drops)
- Metadata corruption (completeness drops)

**Returns:** List[Dict] with degradation details

**Example Return:**
```python
[
    {
        "resource_id": "uuid",
        "title": "Resource Title",
        "old_quality": 0.85,
        "new_quality": 0.62,
        "degradation_pct": 27.1
    }
]
```

### 3. Summarization Evaluator Service

#### SummarizationEvaluator Class

Evaluates summary quality using state-of-the-art metrics: G-Eval, FineSurE, and BERTScore.

**Initialization:**
```python
def __init__(
    self,
    db: Session,
    openai_api_key: str = None
)
```

**Key Methods:**

##### evaluate_summary()
Comprehensive summary evaluation using all metrics.

**Parameters:**
- `resource_id` (str): Resource UUID to evaluate
- `use_g_eval` (bool): Whether to use G-Eval (requires OpenAI API, slow)

**Algorithm:**
1. Fetch resource with summary
2. Validate summary exists
3. Extract summary and reference (content or title)
4. If use_g_eval and API key available:
   - Compute G-Eval coherence
   - Compute G-Eval consistency
   - Compute G-Eval fluency
   - Compute G-Eval relevance
5. Else: Use fallback scores (0.7)
6. Compute FineSurE completeness
7. Compute FineSurE conciseness
8. Compute BERTScore F1
9. Compute composite summary quality:
   - 20% coherence
   - 20% consistency
   - 15% fluency
   - 15% relevance
   - 15% completeness
   - 5% conciseness
   - 10% BERTScore
10. Update resource with all scores
11. Commit to database

**Returns:** Dict with all summary quality scores

**Performance:** 
- Without G-Eval: <2 seconds
- With G-Eval: <10 seconds (OpenAI API latency)

**Example Return:**
```python
{
    "coherence": 0.85,
    "consistency": 0.88,
    "fluency": 0.92,
    "relevance": 0.80,
    "completeness": 0.75,
    "conciseness": 0.90,
    "bertscore": 0.82,
    "overall": 0.84
}
```

##### g_eval_coherence()
G-Eval coherence: Evaluates if summary flows logically.

**Method:** Uses GPT-4 to score coherence on 1-5 scale, normalized to 0.0-1.0

**Prompt Pattern (from G-Eval paper):**
```
You will be given a summary. Your task is to rate the summary on coherence.

Evaluation Criteria:
Coherence (1-5) - the collective quality of all sentences. The summary should be 
well-structured and well-organized. The summary should not just be a heap of related 
information, but should build from sentence to sentence to a coherent body of 
information about a topic.

Evaluation Steps:
1. Read the summary carefully.
2. Rate the summary for coherence on a scale of 1 to 5.

Summary:
{summary}

Provide only the numeric rating (1-5):
```

**Algorithm:**
1. Format prompt with summary
2. Call OpenAI ChatCompletion API (model: gpt-4, temperature: 0.0)
3. Extract numeric rating from response
4. Normalize: (rating - 1) / 4 → 0.0-1.0 range

**Returns:** Float 0.0-1.0

**Fallback:** 0.5 if API unavailable or error

##### g_eval_consistency()
G-Eval consistency: Evaluates factual alignment with reference document.

**Method:** Uses GPT-4 to check for hallucinations and contradictions

**Prompt Pattern:**
```
You will be given a summary and a reference document. Your task is to rate the 
summary on consistency with the reference.

Evaluation Criteria:
Consistency (1-5) - the factual alignment between the summary and the reference 
document. A factually consistent summary contains only statements that are entailed 
by the source document. Penalize summaries that contain hallucinated facts.

Evaluation Steps:
1. Read the reference document and summary carefully.
2. Check each statement in the summary against the reference.
3. Rate the summary for consistency on a scale of 1 to 5.

Reference Document:
{reference[:2000]}

Summary:
{summary}

Provide only the numeric rating (1-5):
```

**Algorithm:**
1. Format prompt with reference (truncated to 2000 chars) and summary
2. Call OpenAI ChatCompletion API
3. Extract and normalize rating

**Returns:** Float 0.0-1.0

##### g_eval_fluency()
G-Eval fluency: Evaluates grammatical correctness and readability.

**Prompt Pattern:**
```
You will be given a summary. Your task is to rate the summary on fluency.

Evaluation Criteria:
Fluency (1-5) - the quality of individual sentences. Are the sentences grammatically 
correct, easy to read, and well-formed?

Evaluation Steps:
1. Read the summary carefully.
2. Rate the summary for fluency on a scale of 1 to 5.

Summary:
{summary}

Provide only the numeric rating (1-5):
```

**Returns:** Float 0.0-1.0

##### g_eval_relevance()
G-Eval relevance: Evaluates if summary captures key information.

**Prompt Pattern:**
```
You will be given a summary and reference document. Your task is to rate the 
summary on relevance.

Evaluation Criteria:
Relevance (1-5) - selection of important content from the source. The summary 
should include only important information from the source document. Penalize 
summaries which contain redundancies and excess information.

Evaluation Steps:
1. Read the reference document and summary.
2. Identify key information in the reference.
3. Check if summary captures this key information.
4. Rate the summary for relevance on a scale of 1 to 5.

Reference Document:
{reference[:2000]}

Summary:
{summary}

Provide only the numeric rating (1-5):
```

**Returns:** Float 0.0-1.0

##### finesure_completeness()
FineSurE completeness: Measures coverage of key information.

**Method:** Simplified implementation using term overlap

**Algorithm:**
1. Extract words from reference and summary
2. Remove stopwords (the, a, an, and, or, but, is, are, was, were, in, on, at, to, for)
3. Compute overlap: len(summary_words ∩ reference_words)
4. Compute completeness: min(1.0, overlap / (len(reference_words) * 0.15))
   - Expect 15% coverage for good summaries

**Production Enhancement:** Use extractive summarization to identify key sentences

**Returns:** Float 0.0-1.0

##### finesure_conciseness()
FineSurE conciseness: Measures information density.

**Method:** Compression ratio analysis

**Algorithm:**
1. Compute compression_ratio = len(summary) / len(reference)
2. Optimal range: 0.05-0.15 (5-15% of original length)
3. Scoring:
   - If 0.05 ≤ ratio ≤ 0.15: return 1.0
   - If ratio < 0.05: return ratio / 0.05 (too short)
   - If ratio > 0.15: return max(0.0, 1.0 - (ratio - 0.15) / 0.35) (too long)

**Returns:** Float 0.0-1.0

##### bertscore_f1()
Computes BERTScore F1 for semantic similarity.

**Method:** Uses BERT embeddings for token-level semantic comparison

**Algorithm:**
1. Call bert_score() function with:
   - candidates: [summary]
   - references: [reference]
   - lang: "en"
   - model_type: "microsoft/deberta-xlarge-mnli"
2. Extract F1 score from results

**Advantages over ROUGE:**
- Captures semantic similarity (not just lexical overlap)
- Robust to paraphrasing
- Better correlation with human judgments

**Returns:** Float 0.0-1.0

**Fallback:** 0.5 if error occurs


### 4. API Endpoints

#### Quality Assessment Endpoints

##### GET /resources/{id}/quality-details
Retrieves full quality dimension breakdown for a resource.

**Response:**
```json
{
  "resource_id": "uuid",
  "quality_dimensions": {
    "accuracy": 0.75,
    "completeness": 0.82,
    "consistency": 0.88,
    "timeliness": 0.65,
    "relevance": 0.79
  },
  "quality_overall": 0.77,
  "quality_weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  },
  "quality_last_computed": "2025-11-10T12:00:00Z",
  "quality_computation_version": "v2.0",
  "is_quality_outlier": false,
  "needs_quality_review": false
}
```

##### POST /quality/recalculate
Triggers quality recomputation for one or more resources.

**Request Body:**
```json
{
  "resource_id": "uuid",  // Optional: single resource
  "resource_ids": ["uuid1", "uuid2"],  // Optional: batch
  "weights": {  // Optional: custom weights
    "accuracy": 0.35,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.10,
    "relevance": 0.10
  }
}
```

**Response:** 202 Accepted (background task)

**Background Task:** Computes quality for specified resources

##### GET /quality/outliers
Returns paginated list of detected quality outliers.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 50)
- `min_outlier_score` (float): Filter by anomaly score
- `reason` (str): Filter by specific outlier reason

**Response:**
```json
{
  "total": 42,
  "page": 1,
  "limit": 50,
  "outliers": [
    {
      "resource_id": "uuid",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "needs_quality_review": true
    }
  ]
}
```

##### GET /quality/degradation
Returns quality degradation report for specified time window.

**Query Parameters:**
- `time_window_days` (int): Lookback period (default: 30)

**Response:**
```json
{
  "time_window_days": 30,
  "degraded_count": 15,
  "degraded_resources": [
    {
      "resource_id": "uuid",
      "title": "Resource Title",
      "old_quality": 0.85,
      "new_quality": 0.62,
      "degradation_pct": 27.1
    }
  ]
}
```

##### POST /summaries/{id}/evaluate
Triggers summary quality evaluation for a resource.

**Query Parameters:**
- `use_g_eval` (bool): Whether to use G-Eval (default: false)

**Response:** 202 Accepted (background task)

**Background Task:** Evaluates summary using all metrics

##### GET /quality/distribution
Returns quality score distribution histogram.

**Query Parameters:**
- `bins` (int): Number of histogram bins (default: 10)
- `dimension` (str): Specific dimension or "overall" (default: "overall")

**Response:**
```json
{
  "dimension": "overall",
  "bins": 10,
  "distribution": [
    {"range": "0.0-0.1", "count": 5},
    {"range": "0.1-0.2", "count": 12},
    {"range": "0.2-0.3", "count": 28},
    {"range": "0.3-0.4", "count": 45},
    {"range": "0.4-0.5", "count": 67},
    {"range": "0.5-0.6", "count": 89},
    {"range": "0.6-0.7", "count": 102},
    {"range": "0.7-0.8", "count": 78},
    {"range": "0.8-0.9", "count": 45},
    {"range": "0.9-1.0", "count": 23}
  ],
  "statistics": {
    "mean": 0.65,
    "median": 0.68,
    "std_dev": 0.18
  }
}
```

##### GET /quality/trends
Returns quality trends over time.

**Query Parameters:**
- `granularity` (str): "daily", "weekly", "monthly" (default: "weekly")
- `start_date` (date): Start of time range
- `end_date` (date): End of time range
- `dimension` (str): Specific dimension or "overall" (default: "overall")

**Response:**
```json
{
  "dimension": "overall",
  "granularity": "weekly",
  "data_points": [
    {"period": "2025-W01", "avg_quality": 0.72, "resource_count": 145},
    {"period": "2025-W02", "avg_quality": 0.74, "resource_count": 167},
    {"period": "2025-W03", "avg_quality": 0.71, "resource_count": 189}
  ]
}
```

##### GET /quality/dimensions
Returns average scores per dimension across all resources.

**Response:**
```json
{
  "dimensions": {
    "accuracy": {"avg": 0.75, "min": 0.12, "max": 0.98},
    "completeness": {"avg": 0.68, "min": 0.25, "max": 0.95},
    "consistency": {"avg": 0.82, "min": 0.45, "max": 0.99},
    "timeliness": {"avg": 0.58, "min": 0.10, "max": 0.95},
    "relevance": {"avg": 0.71, "min": 0.30, "max": 0.92}
  },
  "overall": {"avg": 0.71, "min": 0.28, "max": 0.96},
  "total_resources": 1247
}
```

##### GET /quality/review-queue
Returns resources flagged for quality review with priority ranking.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 50)
- `sort_by` (str): "outlier_score", "quality_overall", "updated_at" (default: "outlier_score")

**Response:**
```json
{
  "total": 87,
  "page": 1,
  "limit": 50,
  "review_queue": [
    {
      "resource_id": "uuid",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "is_quality_outlier": true,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "quality_last_computed": "2025-11-10T12:00:00Z"
    }
  ]
}
```

### 5. Pydantic Schemas

#### QualityDetailsResponse
```python
class QualityDetailsResponse(BaseModel):
    resource_id: str
    quality_dimensions: Dict[str, float]
    quality_overall: float
    quality_weights: Dict[str, float]
    quality_last_computed: datetime
    quality_computation_version: str
    is_quality_outlier: bool
    needs_quality_review: bool
    outlier_score: Optional[float] = None
    outlier_reasons: Optional[List[str]] = None
```

#### QualityRecalculateRequest
```python
class QualityRecalculateRequest(BaseModel):
    resource_id: Optional[str] = None
    resource_ids: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None
    
    @validator('weights')
    def validate_weights(cls, v):
        if v is not None:
            if set(v.keys()) != {"accuracy", "completeness", "consistency", "timeliness", "relevance"}:
                raise ValueError("Must specify all five dimensions")
            if abs(sum(v.values()) - 1.0) > 0.01:
                raise ValueError("Weights must sum to 1.0")
        return v
```

#### OutlierResponse
```python
class OutlierResponse(BaseModel):
    resource_id: str
    title: str
    quality_overall: float
    outlier_score: float
    outlier_reasons: List[str]
    needs_quality_review: bool
```

#### DegradationReport
```python
class DegradationReport(BaseModel):
    time_window_days: int
    degraded_count: int
    degraded_resources: List[Dict[str, Any]]
```

#### SummaryEvaluationResponse
```python
class SummaryEvaluationResponse(BaseModel):
    resource_id: str
    summary_quality: Dict[str, float]  # All metrics
    summary_quality_overall: float
```

## Data Models

### Quality Dimension Weights

Default weights reflect typical knowledge management priorities:

```python
{
    "accuracy": 0.30,      # Highest priority: factual correctness
    "completeness": 0.25,  # Second: metadata richness
    "consistency": 0.20,   # Third: internal coherence
    "timeliness": 0.15,    # Fourth: recency
    "relevance": 0.10      # Fifth: topical alignment
}
```

**Domain Customization Examples:**

**Academic Research:**
```python
{
    "accuracy": 0.40,      # Critical for research
    "completeness": 0.30,  # Metadata essential
    "consistency": 0.15,
    "timeliness": 0.10,
    "relevance": 0.05
}
```

**News/Current Events:**
```python
{
    "accuracy": 0.25,
    "completeness": 0.15,
    "consistency": 0.15,
    "timeliness": 0.35,    # Recency critical
    "relevance": 0.10
}
```

**Educational Content:**
```python
{
    "accuracy": 0.30,
    "completeness": 0.20,
    "consistency": 0.25,   # Clarity important
    "timeliness": 0.10,
    "relevance": 0.15
}
```

### Outlier Detection Feature Matrix

Isolation Forest uses 5-9 features depending on data availability:

**Always Present (5 features):**
1. quality_accuracy
2. quality_completeness
3. quality_consistency
4. quality_timeliness
5. quality_relevance

**Optional (4 features, if summary exists):**
6. summary_coherence
7. summary_consistency
8. summary_fluency
9. summary_relevance

**Feature Scaling:** Not required for Isolation Forest (tree-based algorithm)

**Contamination Parameter:** 0.1 (expect 10% outliers)
- Adjustable based on domain and data quality expectations

### Quality Computation Versioning

**Version Format:** `v{major}.{minor}`

**Version History:**
- `v1.0`: Legacy single quality_score
- `v2.0`: Multi-dimensional quality assessment (Phase 9)

**Tracking Benefits:**
- A/B testing different algorithms
- Rollback capability
- Historical analysis
- Algorithm evolution documentation

**Storage:** `quality_computation_version` field in Resource model


## Error Handling

### Quality Computation Errors

**Missing Resource:**
```python
if not resource:
    raise ValueError(f"Resource {resource_id} not found")
```

**Invalid Weights:**
```python
if weights and abs(sum(weights.values()) - 1.0) > 0.01:
    raise ValueError("Weights must sum to 1.0")
if weights and set(weights.keys()) != {"accuracy", "completeness", "consistency", "timeliness", "relevance"}:
    raise ValueError("Must specify all five dimensions")
```

**Missing Data Graceful Handling:**
```python
# Use neutral baseline scores for missing data
if not resource.citations:
    accuracy_score = 0.5  # Neutral baseline
if not resource.publication_year:
    timeliness_score = 0.5  # Neutral baseline
```

### Summarization Evaluation Errors

**No Summary:**
```python
if not resource.summary:
    return {"error": "Resource has no summary"}
```

**OpenAI API Errors:**
```python
try:
    response = openai.ChatCompletion.create(...)
except Exception as e:
    print(f"G-Eval error: {e}")
    return 0.5  # Fallback score
```

**BERTScore Errors:**
```python
try:
    P, R, F1 = bert_score([summary], [reference], ...)
    return float(F1[0])
except Exception as e:
    print(f"BERTScore error: {e}")
    return 0.5  # Fallback score
```

### Outlier Detection Errors

**Insufficient Data:**
```python
if len(resources) < 10:
    print("Not enough resources for outlier detection (need 10+)")
    return
```

**Feature Matrix Construction Errors:**
```python
# Handle missing dimension scores
feature_vector = [
    resource.quality_accuracy or 0.5,
    resource.quality_completeness or 0.5,
    resource.quality_consistency or 0.5,
    resource.quality_timeliness or 0.5,
    resource.quality_relevance or 0.5
]
```

### API Endpoint Errors

**Invalid Parameters:**
```python
@app.get("/quality/outliers")
def get_outliers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    min_outlier_score: Optional[float] = Query(None, ge=-1.0, le=1.0)
):
    ...
```

**Resource Not Found:**
```python
resource = get_resource(db, resource_id)
if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")
```

**Background Task Failures:**
```python
try:
    quality_service.compute_quality(resource_id)
except Exception as e:
    logger.error(f"Quality computation failed for {resource_id}: {e}")
    # Don't propagate error to user (background task)
```

## Testing Strategy

### Unit Tests

**Quality Dimension Tests:**
- `test_compute_accuracy()`: Citation validity, source credibility, scholarly metadata
- `test_compute_completeness()`: Metadata coverage, multi-modal content
- `test_compute_consistency()`: Title-content alignment, summary-content alignment
- `test_compute_timeliness()`: Publication recency, decay function
- `test_compute_relevance()`: Classification confidence, citation count
- `test_compute_quality()`: Weighted overall score computation
- `test_custom_weights()`: Custom weight validation and application

**Summarization Evaluation Tests:**
- `test_g_eval_coherence()`: Mock OpenAI API, verify prompt format
- `test_g_eval_consistency()`: Mock OpenAI API, verify factual checking
- `test_g_eval_fluency()`: Mock OpenAI API, verify grammar assessment
- `test_g_eval_relevance()`: Mock OpenAI API, verify key information capture
- `test_finesure_completeness()`: Term overlap calculation
- `test_finesure_conciseness()`: Compression ratio scoring
- `test_bertscore_f1()`: Mock bert_score library, verify semantic similarity
- `test_evaluate_summary()`: Composite score computation

**Outlier Detection Tests:**
- `test_detect_quality_outliers()`: Isolation Forest training and prediction
- `test_identify_outlier_reasons()`: Dimension threshold detection
- `test_insufficient_data()`: Minimum resource requirement
- `test_feature_matrix_construction()`: Handle missing scores

**Quality Degradation Tests:**
- `test_monitor_quality_degradation()`: Historical comparison
- `test_degradation_threshold()`: 20% drop detection
- `test_review_flag_setting()`: Automatic flagging

### Integration Tests

**End-to-End Quality Assessment:**
1. Create resource with metadata
2. Trigger quality computation
3. Verify all dimension scores stored
4. Check weighted overall score
5. Verify backward compatibility (quality_score updated)

**Summarization Evaluation Workflow:**
1. Create resource with summary
2. Trigger summary evaluation
3. Verify G-Eval scores (or fallbacks)
4. Verify FineSurE scores
5. Verify BERTScore
6. Check composite score

**Outlier Detection Workflow:**
1. Create batch of resources with varying quality
2. Compute quality for all
3. Run outlier detection
4. Verify outliers flagged
5. Check outlier reasons identified
6. Verify review flags set

**Quality Degradation Monitoring:**
1. Create resources with quality scores
2. Wait or manipulate timestamps
3. Modify resource content (simulate degradation)
4. Run degradation monitoring
5. Verify degraded resources identified
6. Check review flags set

**Integration with Existing Systems:**
- **Phase 6 Citations**: Verify citation validity affects accuracy score
- **Phase 6.5 Scholarly Metadata**: Verify DOI/PMID affects accuracy and completeness
- **Phase 8.5 ML Classification**: Verify classification confidence affects relevance score
- **Resource Ingestion**: Verify quality computed automatically after ingestion

### Performance Tests

**Quality Computation Speed:**
- Single resource: <1 second (excluding G-Eval)
- Batch (100 resources): <100 seconds
- Verify no N+1 query issues

**Summarization Evaluation Speed:**
- Without G-Eval: <2 seconds per resource
- With G-Eval: <10 seconds per resource (OpenAI API latency)
- BERTScore: <3 seconds per resource

**Outlier Detection Speed:**
- 1000 resources: <30 seconds
- Feature matrix construction: <5 seconds
- Isolation Forest training: <10 seconds
- Prediction: <5 seconds

**API Endpoint Response Times:**
- GET /quality/details: <100ms
- GET /quality/outliers: <200ms (paginated)
- GET /quality/distribution: <500ms (aggregation)
- GET /quality/trends: <1 second (time-series aggregation)

### Edge Case Tests

**Missing Data Handling:**
- Resource with no citations
- Resource with no publication year
- Resource with no summary
- Resource with minimal metadata

**Extreme Values:**
- All quality dimensions = 0.0
- All quality dimensions = 1.0
- Mixed extreme values

**Custom Weights:**
- All weight on one dimension
- Equal weights across all dimensions
- Invalid weights (don't sum to 1.0)

**Outlier Detection:**
- All resources identical (no outliers)
- All resources different (many outliers)
- Gradual quality distribution

## Implementation Considerations

### Database Migration Strategy

**Phase 1: Schema Extension**
1. Create Alembic migration for new quality fields
2. All fields nullable for backward compatibility
3. Add indexes on quality_overall, is_quality_outlier, needs_quality_review
4. Test migration on development database

**Phase 2: Backfill Existing Resources**
1. Batch process existing resources (1000 at a time)
2. Compute quality for each resource
3. Monitor performance and adjust batch size
4. Run during low-traffic period

**Phase 3: Enable Automatic Computation**
1. Integrate quality computation into ingestion pipeline
2. Add quality recomputation on resource updates
3. Schedule periodic outlier detection (daily)
4. Schedule periodic degradation monitoring (weekly)

**Rollback Plan:**
- Keep legacy quality_score field functional
- New fields nullable (can be ignored)
- No breaking changes to existing APIs

### OpenAI API Integration

**API Key Management:**
- Store in environment variable: `OPENAI_API_KEY`
- Optional: System works without G-Eval if key not provided
- Fallback to neutral scores (0.7) when API unavailable

**Rate Limiting:**
- OpenAI API: 3,500 requests/minute (GPT-4)
- Batch summary evaluations with delays
- Use background tasks to avoid blocking

**Cost Optimization:**
- G-Eval optional (use_g_eval flag)
- Cache evaluation results
- Only re-evaluate when summary changes
- Consider using GPT-3.5-turbo for cost savings (lower accuracy)

**Error Handling:**
- Retry on transient errors (3 attempts)
- Fallback to neutral scores on persistent errors
- Log all API errors for monitoring

### BERTScore Model Management

**Model Selection:**
- Primary: `microsoft/deberta-xlarge-mnli` (high accuracy)
- Alternative: `microsoft/deberta-base-mnli` (faster, lower accuracy)
- Fallback: `bert-base-uncased` (widely available)

**Model Caching:**
- Models downloaded on first use
- Cached in `~/.cache/huggingface/`
- ~1.5GB for deberta-xlarge-mnli

**GPU Acceleration:**
- Automatically uses GPU if available
- Significant speedup (10x+)
- Batch processing more efficient on GPU

**Memory Management:**
- deberta-xlarge-mnli requires ~6GB GPU memory
- Use deberta-base-mnli for limited memory
- CPU fallback always available

### Isolation Forest Configuration

**Hyperparameters:**
- `contamination=0.1`: Expect 10% outliers
- `n_estimators=100`: Number of trees
- `random_state=42`: Reproducibility

**Tuning Considerations:**
- Increase contamination if more outliers expected
- Increase n_estimators for more stable predictions
- Monitor false positive/negative rates

**Feature Engineering:**
- Current: Raw quality scores
- Future: Add derived features (score variance, temporal patterns)
- Consider feature scaling if adding non-score features

### Quality Degradation Monitoring

**Scheduling:**
- Run weekly via cron job or background task scheduler
- Process in batches to avoid memory issues
- Send alerts for significant degradation

**Threshold Tuning:**
- Current: 20% drop triggers alert
- Adjust based on domain and false positive rate
- Consider different thresholds per dimension

**Alert Mechanisms:**
- Log degraded resources
- Email notifications to administrators
- Dashboard alerts
- Integration with monitoring systems (Prometheus, Grafana)

### Integration with Recommendation System

**Quality Filtering:**
```python
# Exclude low-quality resources
query = query.filter(Resource.quality_overall >= 0.5)

# Exclude outliers
query = query.filter(Resource.is_quality_outlier == False)
```

**Quality Boosting:**
```python
# Boost high-quality resources in ranking
if resource.quality_overall > 0.8:
    relevance_score *= 1.2  # 20% boost
```

**Quality-Aware Recommendations:**
```python
# Weight recommendations by quality
final_score = similarity_score * (0.7 + 0.3 * quality_overall)
```

### Performance Optimization

**Database Indexes:**
- `idx_resources_quality_overall`: Fast quality filtering
- `idx_resources_outlier`: Fast outlier queries
- `idx_resources_needs_review`: Fast review queue queries

**Query Optimization:**
- Use SELECT specific columns (avoid SELECT *)
- Batch updates for resource counts
- Use database aggregation for statistics

**Caching:**
- Cache quality distribution (refresh hourly)
- Cache quality trends (refresh daily)
- Cache dimension averages (refresh hourly)

**Background Processing:**
- Quality computation: Background task
- Outlier detection: Scheduled job
- Degradation monitoring: Scheduled job
- Summary evaluation: Background task

### Monitoring and Observability

**Metrics to Track:**
- Quality computation latency (p50, p95, p99)
- Outlier detection rate
- Degradation detection rate
- G-Eval API success rate
- BERTScore computation time
- Review queue size

**Logging:**
- Log all quality computations
- Log outlier detections with reasons
- Log degradation events
- Log API errors (OpenAI, BERTScore)

**Alerting:**
- Alert on high outlier rate (>20%)
- Alert on quality degradation spike
- Alert on API failures
- Alert on performance degradation

### Future Enhancements

**Phase 9.5: Advanced Quality Features**
- User feedback integration (thumbs up/down on quality)
- Quality prediction for new resources (before full computation)
- Quality-based content recommendations
- Quality improvement suggestions

**Phase 10: Quality Dashboard**
- Interactive quality visualization
- Outlier review interface
- Quality trend analysis
- Dimension comparison charts

**Phase 11: Automated Quality Improvement**
- Automatic metadata enrichment for low completeness
- Citation validation and correction
- Content freshness updates
- Broken link detection and repair

