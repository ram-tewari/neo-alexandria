# RAG Evaluation Guide

> **Phase 17.5** - Quality Metrics and Monitoring for Advanced RAG

## Overview

This guide explains how to evaluate and monitor the quality of your RAG (Retrieval-Augmented Generation) system using RAGAS metrics. Proper evaluation ensures your retrieval strategies are working effectively and helps identify areas for improvement.

## Table of Contents

1. [Why Evaluate RAG?](#why-evaluate-rag)
2. [RAGAS Metrics](#ragas-metrics)
3. [Submitting Evaluation Data](#submitting-evaluation-data)
4. [Interpreting Metrics](#interpreting-metrics)
5. [Monitoring and Tracking](#monitoring-and-tracking)
6. [Best Practices](#best-practices)

---

## Why Evaluate RAG?

RAG systems have multiple failure modes:

1. **Retrieval Failures**: Wrong documents retrieved
2. **Context Failures**: Retrieved documents don't contain answer
3. **Generation Failures**: LLM generates incorrect answer despite good context
4. **Hallucination**: LLM invents information not in retrieved context

Traditional metrics (BLEU, ROUGE) don't capture these nuances. RAGAS (Retrieval-Augmented Generation Assessment) provides specialized metrics for RAG evaluation.

---

## RAGAS Metrics

### 1. Faithfulness Score

**What it measures**: Does the generated answer stay faithful to the retrieved context?

**Range**: 0.0 to 1.0 (higher is better)

**Calculation**:
```
Faithfulness = (Number of claims supported by context) / (Total claims in answer)
```

**Example**:

```python
# Retrieved Context
"Gradient descent is an optimization algorithm that iteratively 
adjusts parameters to minimize a loss function."

# Generated Answer
"Gradient descent is an optimization algorithm that uses derivatives 
to find the minimum of a function. It was invented by Isaac Newton."

# Analysis
Claims in answer:
1. "Gradient descent is an optimization algorithm" ✓ (supported)
2. "Uses derivatives to find minimum" ✓ (implied by context)
3. "Invented by Isaac Newton" ✗ (not in context - hallucination)

Faithfulness = 2/3 = 0.67
```

**Interpretation**:
- **> 0.9**: Excellent - answer is highly faithful
- **0.7 - 0.9**: Good - minor unsupported claims
- **0.5 - 0.7**: Fair - some hallucination present
- **< 0.5**: Poor - significant hallucination

### 2. Answer Relevance Score

**What it measures**: How relevant is the generated answer to the user's query?

**Range**: 0.0 to 1.0 (higher is better)

**Calculation**:
```
Answer Relevance = Semantic similarity between query and answer
```

**Example**:

```python
# Query
"What is gradient descent?"

# Answer A (High Relevance)
"Gradient descent is an optimization algorithm that minimizes 
a loss function by iteratively adjusting parameters."
# Score: 0.95

# Answer B (Low Relevance)
"Machine learning uses various optimization techniques. Neural 
networks require training data and compute resources."
# Score: 0.45
```

**Interpretation**:
- **> 0.9**: Excellent - directly answers the question
- **0.7 - 0.9**: Good - relevant but may include extra info
- **0.5 - 0.7**: Fair - partially relevant
- **< 0.5**: Poor - off-topic or tangential

### 3. Context Precision Score

**What it measures**: How much of the retrieved context is actually relevant to answering the query?

**Range**: 0.0 to 1.0 (higher is better)

**Calculation**:
```
Context Precision = (Relevant chunks) / (Total retrieved chunks)
```

**Example**:

```python
# Query: "What is gradient descent?"

# Retrieved Chunks
Chunk 1: "Gradient descent is an optimization algorithm..." ✓ (relevant)
Chunk 2: "The learning rate controls step size..." ✓ (relevant)
Chunk 3: "Neural networks were invented in 1943..." ✗ (not relevant)
Chunk 4: "Python is a programming language..." ✗ (not relevant)
Chunk 5: "Stochastic gradient descent is a variant..." ✓ (relevant)

Context Precision = 3/5 = 0.60
```

**Interpretation**:
- **> 0.8**: Excellent - most retrieved context is relevant
- **0.6 - 0.8**: Good - some noise but mostly relevant
- **0.4 - 0.6**: Fair - significant irrelevant content
- **< 0.4**: Poor - retrieval is not working well

### 4. Context Recall Score (Optional)

**What it measures**: How much of the information needed to answer the query was retrieved?

**Range**: 0.0 to 1.0 (higher is better)

**Note**: Requires ground truth answer for comparison.

**Calculation**:
```
Context Recall = (Information in context that's in ground truth) / (Total information in ground truth)
```

---

## Submitting Evaluation Data

### API Endpoint

```
POST /api/evaluation/submit
```

### Request Schema

```python
{
  "query": str,                      # User's original query
  "expected_answer": str,            # Ground truth answer (optional)
  "generated_answer": str,           # LLM's generated answer
  "retrieved_chunk_ids": List[str],  # IDs of retrieved chunks
  "faithfulness_score": float,       # 0.0 to 1.0 (optional)
  "answer_relevance_score": float,   # 0.0 to 1.0 (optional)
  "context_precision_score": float,  # 0.0 to 1.0 (optional)
  "context_recall_score": float      # 0.0 to 1.0 (optional)
}
```

### Example: Manual Evaluation

```python
import requests

# Submit evaluation data
response = requests.post(
    "http://localhost:8000/api/evaluation/submit",
    json={
        "query": "What is gradient descent?",
        "expected_answer": "An optimization algorithm that minimizes loss functions.",
        "generated_answer": "Gradient descent is an iterative optimization algorithm...",
        "retrieved_chunk_ids": ["uuid-1", "uuid-2", "uuid-3"],
        "faithfulness_score": 0.92,
        "answer_relevance_score": 0.88,
        "context_precision_score": 0.75
    }
)

print(response.json())
# {
#   "evaluation_id": "uuid-eval-123",
#   "created_at": "2024-01-15T10:30:00Z",
#   "status": "success"
# }
```

### Example: Automated Evaluation

```python
from app.modules.quality.service import RAGEvaluationService

# Initialize service
eval_service = RAGEvaluationService(db_session)

# Evaluate a RAG response
evaluation = eval_service.evaluate_rag_response(
    query="What is gradient descent?",
    generated_answer="Gradient descent is an optimization algorithm...",
    retrieved_chunks=[chunk1, chunk2, chunk3],
    expected_answer="An optimization algorithm..."  # optional
)

print(f"Faithfulness: {evaluation.faithfulness_score}")
print(f"Relevance: {evaluation.answer_relevance_score}")
print(f"Precision: {evaluation.context_precision_score}")
```

---

## Interpreting Metrics

### Overall RAG Quality

Combine metrics to assess overall quality:

```python
# Weighted average
overall_score = (
    0.4 * faithfulness_score +
    0.3 * answer_relevance_score +
    0.3 * context_precision_score
)
```

**Quality Levels**:
- **> 0.85**: Excellent - production ready
- **0.70 - 0.85**: Good - minor improvements needed
- **0.55 - 0.70**: Fair - significant improvements needed
- **< 0.55**: Poor - major issues to address

### Diagnosing Issues

#### Low Faithfulness (< 0.7)

**Problem**: LLM is hallucinating or adding unsupported information

**Solutions**:
1. Improve prompt engineering (emphasize "only use provided context")
2. Use more conservative LLM temperature (0.1 - 0.3)
3. Implement citation requirements
4. Use smaller, more focused context windows

#### Low Answer Relevance (< 0.7)

**Problem**: Generated answer doesn't address the query

**Solutions**:
1. Improve query understanding in prompt
2. Use query expansion or reformulation
3. Fine-tune LLM on domain-specific Q&A
4. Implement answer validation

#### Low Context Precision (< 0.6)

**Problem**: Retrieval is returning too much irrelevant content

**Solutions**:
1. Tune retrieval parameters (top_k, similarity threshold)
2. Improve chunking strategy (smaller, more focused chunks)
3. Use hybrid retrieval (combine semantic + keyword)
4. Implement re-ranking
5. Try GraphRAG for relationship-aware retrieval

### Metric Patterns

#### Pattern 1: High Faithfulness, Low Relevance

```
Faithfulness: 0.95
Relevance: 0.45
Precision: 0.80
```

**Diagnosis**: LLM is faithful to context, but context doesn't answer the query

**Solution**: Improve retrieval strategy

#### Pattern 2: High Relevance, Low Faithfulness

```
Faithfulness: 0.55
Relevance: 0.90
Precision: 0.75
```

**Diagnosis**: LLM understands query but adds unsupported information

**Solution**: Improve prompt engineering, reduce temperature

#### Pattern 3: Low Precision, High Faithfulness

```
Faithfulness: 0.90
Relevance: 0.85
Precision: 0.40
```

**Diagnosis**: Retrieval returns too much noise, but LLM filters it well

**Solution**: Improve retrieval precision (may not be urgent)

---

## Monitoring and Tracking

### Viewing Metrics

#### Get Aggregate Metrics

```python
GET /api/evaluation/metrics?days=7

# Response
{
  "period": "7 days",
  "total_evaluations": 150,
  "average_scores": {
    "faithfulness": 0.87,
    "answer_relevance": 0.82,
    "context_precision": 0.71
  },
  "score_distribution": {
    "excellent": 45,  # > 0.85
    "good": 68,       # 0.70 - 0.85
    "fair": 30,       # 0.55 - 0.70
    "poor": 7         # < 0.55
  }
}
```

#### Get Evaluation History

```python
GET /api/evaluation/history?limit=50&offset=0

# Response
{
  "evaluations": [
    {
      "id": "uuid-eval-1",
      "query": "What is gradient descent?",
      "faithfulness_score": 0.92,
      "answer_relevance_score": 0.88,
      "context_precision_score": 0.75,
      "created_at": "2024-01-15T10:30:00Z"
    },
    ...
  ],
  "total": 150,
  "page": 1,
  "per_page": 50
}
```

### Tracking Over Time

```python
import matplotlib.pyplot as plt
import requests

# Fetch metrics for last 30 days
response = requests.get("http://localhost:8000/api/evaluation/metrics?days=30")
data = response.json()

# Plot trends
dates = [eval["created_at"] for eval in data["daily_metrics"]]
faithfulness = [eval["avg_faithfulness"] for eval in data["daily_metrics"]]
relevance = [eval["avg_relevance"] for eval in data["daily_metrics"]]

plt.plot(dates, faithfulness, label="Faithfulness")
plt.plot(dates, relevance, label="Relevance")
plt.legend()
plt.title("RAG Quality Metrics Over Time")
plt.show()
```

### Setting Up Alerts

```python
# Example: Alert on low quality
def check_quality_alerts(db_session):
    recent_evals = get_recent_evaluations(db_session, hours=24)
    
    avg_faithfulness = sum(e.faithfulness_score for e in recent_evals) / len(recent_evals)
    
    if avg_faithfulness < 0.7:
        send_alert(
            title="Low RAG Faithfulness",
            message=f"Average faithfulness score: {avg_faithfulness:.2f}",
            severity="warning"
        )
```

---

## Best Practices

### 1. Continuous Evaluation

**Don't**: Only evaluate once during development

**Do**: Continuously evaluate in production

```python
# Evaluate every RAG response
@app.post("/api/chat")
async def chat(query: str, db: Session = Depends(get_db)):
    # Generate response
    answer, chunks = generate_rag_response(query)
    
    # Evaluate quality
    evaluation = evaluate_rag_response(
        query=query,
        answer=answer,
        chunks=chunks
    )
    
    # Log for monitoring
    log_evaluation(evaluation)
    
    return {"answer": answer, "quality": evaluation}
```

### 2. Sample-Based Evaluation

**For high-volume systems**: Evaluate a sample of responses

```python
import random

# Evaluate 10% of responses
if random.random() < 0.1:
    evaluation = evaluate_rag_response(...)
    log_evaluation(evaluation)
```

### 3. Human-in-the-Loop

**Combine automated metrics with human feedback**:

```python
# Allow users to rate responses
@app.post("/api/feedback")
async def submit_feedback(
    evaluation_id: str,
    user_rating: int,  # 1-5 stars
    comments: str
):
    # Store feedback
    update_evaluation(evaluation_id, user_rating, comments)
    
    # Use for model improvement
    if user_rating <= 2:
        flag_for_review(evaluation_id)
```

### 4. A/B Testing

**Compare retrieval strategies**:

```python
# Test parent-child vs GraphRAG
def ab_test_retrieval(query: str):
    strategy = random.choice(["parent-child", "graphrag"])
    
    results = search_advanced(query, strategy=strategy)
    answer = generate_answer(results)
    
    evaluation = evaluate_rag_response(query, answer, results)
    evaluation.metadata["strategy"] = strategy
    
    log_evaluation(evaluation)
    return answer
```

### 5. Benchmark Datasets

**Create a test set of queries with ground truth answers**:

```python
# benchmark_queries.json
[
  {
    "query": "What is gradient descent?",
    "expected_answer": "An optimization algorithm...",
    "expected_chunks": ["uuid-1", "uuid-2"]
  },
  ...
]

# Run benchmark
def run_benchmark(benchmark_file: str):
    with open(benchmark_file) as f:
        queries = json.load(f)
    
    results = []
    for item in queries:
        answer, chunks = generate_rag_response(item["query"])
        evaluation = evaluate_rag_response(
            query=item["query"],
            answer=answer,
            chunks=chunks,
            expected_answer=item["expected_answer"]
        )
        results.append(evaluation)
    
    # Report aggregate metrics
    print(f"Average Faithfulness: {sum(r.faithfulness_score for r in results) / len(results)}")
    print(f"Average Relevance: {sum(r.answer_relevance_score for r in results) / len(results)}")
```

### 6. Metric Thresholds

**Set minimum quality thresholds**:

```python
# Reject low-quality responses
def generate_rag_response_with_quality_check(query: str):
    answer, chunks = generate_rag_response(query)
    evaluation = evaluate_rag_response(query, answer, chunks)
    
    if evaluation.faithfulness_score < 0.7:
        # Retry with different strategy
        answer, chunks = generate_rag_response(query, strategy="graphrag")
        evaluation = evaluate_rag_response(query, answer, chunks)
    
    if evaluation.faithfulness_score < 0.7:
        # Return fallback response
        return "I don't have enough information to answer that question."
    
    return answer
```

### 7. Cost-Quality Tradeoff

**Balance evaluation cost with coverage**:

```python
# Expensive: Evaluate every response with LLM-based metrics
# Cheap: Evaluate sample with heuristic metrics

def smart_evaluation(query: str, answer: str, chunks: List):
    # Always compute cheap metrics
    relevance = compute_semantic_similarity(query, answer)
    precision = compute_context_precision(chunks)
    
    # Conditionally compute expensive metrics
    if relevance < 0.7 or precision < 0.6:
        # Low quality - worth detailed analysis
        faithfulness = compute_faithfulness_with_llm(answer, chunks)
    else:
        faithfulness = None
    
    return Evaluation(
        answer_relevance_score=relevance,
        context_precision_score=precision,
        faithfulness_score=faithfulness
    )
```

---

## Related Documentation

- [Advanced RAG Guide](advanced-rag.md) - Retrieval strategies
- [Migration Guide](naive-to-advanced-rag.md) - Upgrading from naive RAG
- [Quality API](../api/quality.md) - Evaluation endpoints
- [Search API](../api/search.md) - Advanced search endpoints

---

## Appendix: Metric Calculation Details

### Faithfulness Calculation

```python
def calculate_faithfulness(answer: str, context: str) -> float:
    """
    Calculate faithfulness score using claim verification.
    
    Steps:
    1. Extract claims from answer
    2. For each claim, check if supported by context
    3. Return ratio of supported claims
    """
    claims = extract_claims(answer)
    supported = 0
    
    for claim in claims:
        if is_supported_by_context(claim, context):
            supported += 1
    
    return supported / len(claims) if claims else 1.0
```

### Answer Relevance Calculation

```python
def calculate_answer_relevance(query: str, answer: str) -> float:
    """
    Calculate answer relevance using semantic similarity.
    
    Uses cosine similarity between query and answer embeddings.
    """
    query_embedding = generate_embedding(query)
    answer_embedding = generate_embedding(answer)
    
    similarity = cosine_similarity(query_embedding, answer_embedding)
    return similarity
```

### Context Precision Calculation

```python
def calculate_context_precision(
    query: str,
    chunks: List[str],
    threshold: float = 0.5
) -> float:
    """
    Calculate context precision by checking chunk relevance.
    
    Steps:
    1. For each chunk, compute relevance to query
    2. Count chunks above relevance threshold
    3. Return ratio of relevant chunks
    """
    query_embedding = generate_embedding(query)
    relevant = 0
    
    for chunk in chunks:
        chunk_embedding = generate_embedding(chunk)
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        
        if similarity >= threshold:
            relevant += 1
    
    return relevant / len(chunks) if chunks else 1.0
```
