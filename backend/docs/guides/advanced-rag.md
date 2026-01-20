# Advanced RAG Architecture Guide

> **Phase 17.5** - Advanced Retrieval-Augmented Generation

## Overview

Neo Alexandria 2.0's Advanced RAG Architecture provides sophisticated retrieval strategies that go beyond simple semantic search. This guide explains the key concepts, retrieval strategies, and usage patterns for building high-quality RAG applications.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Document Chunking](#document-chunking)
3. [Parent-Child Retrieval](#parent-child-retrieval)
4. [GraphRAG](#graphrag)
5. [HyDE and Reverse HyDE](#hyde-and-reverse-hyde)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)

---

## Core Concepts

### What is Advanced RAG?

Traditional RAG (Retrieval-Augmented Generation) retrieves relevant documents and passes them to an LLM for answer generation. Advanced RAG enhances this with:

1. **Hierarchical Retrieval**: Search at chunk level, return parent context
2. **Graph-Based Retrieval**: Leverage knowledge graphs for relationship-aware search
3. **Synthetic Questions**: Match queries against generated questions for better recall
4. **Hybrid Strategies**: Combine multiple retrieval methods for optimal results

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADVANCED RAG PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query                                                     │
│      │                                                          │
│      ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Retrieval Strategy Selection                   │   │
│  │  • Parent-Child  • GraphRAG  • Question-Based  • Hybrid  │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                         │
│       ┌───────────────┼───────────────┬────────────────┐        │
│       │               │               │                │        │
│       ▼               ▼               ▼                ▼        │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │ Chunk   │   │  Graph   │   │ Question │   │  Hybrid  │      │
│  │ Search  │   │ Traverse │   │  Match   │   │  Fusion  │      │
│  └────┬────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘      │
│       │             │              │              │            │
│       └─────────────┴──────────────┴──────────────┘            │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Context Expansion                           │   │
│  │  • Parent Resources  • Surrounding Chunks  • Graph Paths │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Ranking & Deduplication                     │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                         │
│                       ▼                                         │
│                  Final Results                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Document Chunking

### Why Chunking?

Chunking breaks large documents into smaller, semantically coherent pieces for:

1. **Better Retrieval**: Smaller chunks = more precise matching
2. **Context Control**: Fit within LLM context windows
3. **Granular Search**: Find specific passages, not entire documents
4. **Efficient Embeddings**: Generate embeddings for manageable text sizes

### Chunking Strategies

#### 1. Semantic Chunking

Splits on sentence boundaries while respecting target chunk size:

```python
# Automatic semantic chunking during ingestion
POST /api/resources/{resource_id}/chunks
{
  "strategy": "semantic",
  "chunk_size": 512,
  "overlap": 50
}
```

**Advantages**:
- Preserves semantic coherence
- Natural language boundaries
- Better for narrative text

**Use Cases**:
- Academic papers
- Articles and blog posts
- Books and long-form content

#### 2. Fixed-Size Chunking

Splits at fixed character count with overlap:

```python
POST /api/resources/{resource_id}/chunks
{
  "strategy": "fixed",
  "chunk_size": 1000,
  "overlap": 100
}
```

**Advantages**:
- Predictable chunk sizes
- Simple implementation
- Fast processing

**Use Cases**:
- Technical documentation
- Reference materials
- Structured content

#### 3. AST-Based Chunking (Phase 18)

Splits code at function/class boundaries using Tree-Sitter:

```python
POST /api/resources/{resource_id}/chunks
{
  "strategy": "ast",
  "parser_type": "code_python",
  "chunk_size": 2000
}
```

**Advantages**:
- Respects code structure
- Complete functions/classes
- Preserves context

**Use Cases**:
- Source code files
- Code documentation
- Technical tutorials with code

### Chunk Metadata

Chunks store flexible metadata for different content types:

**PDF Documents**:
```json
{
  "page": 5,
  "coordinates": [100, 200]
}
```

**Code Files**:
```json
{
  "start_line": 42,
  "end_line": 67,
  "function_name": "calculate_loss",
  "file_path": "src/model.py"
}
```

---

## Parent-Child Retrieval

### Concept

Parent-child retrieval searches at the chunk level but returns parent resources with surrounding context. This provides:

1. **Precision**: Find exact passages
2. **Context**: Include surrounding information
3. **Efficiency**: Search small chunks, return full context

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                  PARENT-CHILD RETRIEVAL                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query: "What is gradient descent?"                    │
│      │                                                      │
│      ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 1: Chunk-Level Search                          │   │
│  │  • Generate query embedding                           │   │
│  │  • Search DocumentChunk table                         │   │
│  │  • Find top-k most similar chunks                     │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 2: Parent Expansion                            │   │
│  │  • For each chunk, get parent Resource               │   │
│  │  • Include surrounding chunks (context_window)        │   │
│  │  • Deduplicate when multiple chunks from same parent │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 3: Context Assembly                            │   │
│  │  • Chunk 4: "...optimization algorithms..."          │   │
│  │  • Chunk 5: "Gradient descent is an iterative..."    │   │
│  │  • Chunk 6: "...converges to local minimum..."       │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│                  Return Results                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### API Usage

```python
POST /api/search/advanced
{
  "query": "What is gradient descent?",
  "strategy": "parent-child",
  "top_k": 5,
  "context_window": 2  // Include 2 chunks before and after
}

# Response
{
  "results": [
    {
      "resource_id": "uuid-123",
      "title": "Introduction to Machine Learning",
      "matched_chunks": [
        {
          "chunk_id": "uuid-456",
          "content": "Gradient descent is an iterative optimization algorithm...",
          "chunk_index": 5,
          "score": 0.92
        }
      ],
      "context_chunks": [
        {
          "chunk_index": 4,
          "content": "...optimization algorithms are fundamental..."
        },
        {
          "chunk_index": 6,
          "content": "...converges to a local minimum..."
        }
      ]
    }
  ]
}
```

### Configuration

```python
# In app/config/settings.py
PARENT_CHILD_CONTEXT_WINDOW = 2  # Chunks before/after
PARENT_CHILD_MAX_CHUNKS = 10     # Max chunks per parent
```

---

## GraphRAG

### Concept

GraphRAG (Graph-based Retrieval-Augmented Generation) leverages knowledge graphs to find related information through entity relationships. This enables:

1. **Relationship-Aware Search**: Find connected concepts
2. **Multi-Hop Reasoning**: Traverse graph paths
3. **Contradiction Discovery**: Identify conflicting information
4. **Explainable Results**: Show relationship paths

### Knowledge Graph Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐                                               │
│  │ Gradient │                                               │
│  │ Descent  │                                               │
│  │(Concept) │                                               │
│  └────┬─────┘                                               │
│       │                                                     │
│       │ EXTENDS                                             │
│       ▼                                                     │
│  ┌──────────┐         SUPPORTS        ┌──────────────┐      │
│  │Stochastic│◄───────────────────────│  Adam        │      │
│  │Gradient  │                        │ Optimizer    │      │
│  │Descent   │                        │ (Method)     │      │
│  └────┬─────┘                        └──────────────┘      │
│       │                                                     │
│       │ CONTRADICTS                                         │
│       ▼                                                     │
│  ┌──────────┐                                               │
│  │ Newton's │                                               │
│  │  Method  │                                               │
│  │ (Method) │                                               │
│  └──────────┘                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Entity Types

- **Concept**: Abstract ideas, theories, algorithms
- **Person**: Authors, researchers, historical figures
- **Organization**: Institutions, companies, research groups
- **Method**: Techniques, methodologies, approaches

### Relationship Types

**Academic Relations**:
- `CONTRADICTS`: Entity A contradicts entity B
- `SUPPORTS`: Entity A supports entity B
- `EXTENDS`: Entity A extends entity B
- `CITES`: Entity A cites entity B

**Code Relations** (Phase 18):
- `CALLS`: Function A calls function B
- `IMPORTS`: Module A imports module B
- `DEFINES`: File A defines class/function B

### How GraphRAG Works

```
┌─────────────────────────────────────────────────────────────┐
│                      GRAPHRAG RETRIEVAL                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query: "What are alternatives to gradient descent?"   │
│      │                                                      │
│      ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 1: Entity Extraction                           │   │
│  │  • Extract entities from query: "gradient descent"   │   │
│  │  • Match against GraphEntity table                   │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 2: Graph Traversal                             │   │
│  │  • Find relationships: EXTENDS, CONTRADICTS          │   │
│  │  • Traverse to related entities                      │   │
│  │  • Compute path weights                              │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 3: Chunk Retrieval via Provenance              │   │
│  │  • Get provenance_chunk_id from relationships        │   │
│  │  • Retrieve associated DocumentChunks                │   │
│  │  • Rank by graph weight + embedding similarity      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 4: Result Assembly                             │   │
│  │  • Include graph paths for explainability            │   │
│  │  • Show relationship types                           │   │
│  │  • Provide confidence scores                         │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│                       ▼                                     │
│                  Return Results                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### API Usage

```python
POST /api/search/advanced
{
  "query": "What are alternatives to gradient descent?",
  "strategy": "graphrag",
  "top_k": 5,
  "relation_types": ["EXTENDS", "CONTRADICTS"],
  "max_hops": 2
}

# Response
{
  "results": [
    {
      "chunk_id": "uuid-789",
      "content": "Stochastic Gradient Descent (SGD) extends gradient descent...",
      "score": 0.88,
      "graph_path": [
        {
          "source": "Gradient Descent",
          "relation": "EXTENDS",
          "target": "Stochastic Gradient Descent",
          "weight": 0.9
        }
      ]
    },
    {
      "chunk_id": "uuid-101",
      "content": "Newton's method contradicts gradient descent by using second-order...",
      "score": 0.85,
      "graph_path": [
        {
          "source": "Gradient Descent",
          "relation": "CONTRADICTS",
          "target": "Newton's Method",
          "weight": 0.8
        }
      ]
    }
  ]
}
```

### Contradiction Discovery

Find contradictory information in the knowledge graph:

```python
POST /api/search/advanced
{
  "query": "gradient descent",
  "strategy": "graphrag",
  "relation_types": ["CONTRADICTS"],
  "discover_contradictions": true
}

# Response includes contradictory claims with provenance
{
  "contradictions": [
    {
      "entity_a": "Gradient Descent",
      "entity_b": "Newton's Method",
      "relationship": "CONTRADICTS",
      "evidence_chunks": [
        {
          "chunk_id": "uuid-101",
          "content": "Newton's method uses second-order derivatives..."
        }
      ]
    }
  ]
}
```

---

## HyDE and Reverse HyDE

### HyDE (Hypothetical Document Embeddings)

**Traditional HyDE**:
1. User asks a question
2. LLM generates a hypothetical answer
3. Embed the hypothetical answer
4. Search for similar documents

**Problem**: Requires LLM call for every query (slow, expensive)

### Reverse HyDE

**Our Approach**:
1. Pre-generate questions for each chunk
2. Embed the questions
3. User asks a question
4. Match against question embeddings
5. Retrieve associated chunks

**Advantages**:
- No LLM call at query time
- Fast retrieval
- Better recall for question-like queries

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    REVERSE HYDE RETRIEVAL                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Indexing Phase (Offline):                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  For each DocumentChunk:                             │   │
│  │  1. Generate 1-3 synthetic questions                 │   │
│  │  2. Store in SyntheticQuestion table                 │   │
│  │  3. Generate embeddings for questions                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Query Phase (Online):                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  User Query: "How does gradient descent work?"       │   │
│  │      │                                                │   │
│  │      ▼                                                │   │
│  │  1. Generate query embedding                          │   │
│  │  2. Search SyntheticQuestion embeddings              │   │
│  │  3. Find top-k matching questions                    │   │
│  │  4. Retrieve associated chunks                       │   │
│  │  5. Rank by question similarity                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Synthetic Question Generation

**Pattern-Based Generation**:
```python
# Heuristic patterns
"What is {key_concept}?"
"How does {key_concept} work?"
"Why is {key_concept} important?"
"When should you use {key_concept}?"
```

**LLM-Based Generation** (optional):
```python
# Prompt engineering
"Generate 3 questions that this text could answer:
{chunk_content}

Questions should be:
- Specific and relevant
- Natural language
- Answerable from the text"
```

### API Usage

```python
# Enable synthetic question generation
POST /api/resources/{resource_id}/chunks
{
  "strategy": "semantic",
  "generate_questions": true
}

# Query using Reverse HyDE
POST /api/search/advanced
{
  "query": "How does gradient descent work?",
  "strategy": "question",
  "top_k": 5
}

# Hybrid: Combine with semantic search
POST /api/search/advanced
{
  "query": "How does gradient descent work?",
  "strategy": "hybrid",
  "methods": ["semantic", "question"],
  "weights": [0.6, 0.4]
}
```

### Configuration

```python
# In app/config/settings.py
SYNTHETIC_QUESTIONS_ENABLED = True
QUESTIONS_PER_CHUNK = 3
QUESTION_GENERATION_METHOD = "pattern"  # or "llm"
```

---

## Usage Examples

### Example 1: Basic Parent-Child Retrieval

```python
import requests

# Chunk a resource
response = requests.post(
    "http://localhost:8000/api/resources/uuid-123/chunks",
    json={
        "strategy": "semantic",
        "chunk_size": 512,
        "overlap": 50
    }
)

# Search with parent-child retrieval
response = requests.post(
    "http://localhost:8000/api/search/advanced",
    json={
        "query": "What is machine learning?",
        "strategy": "parent-child",
        "top_k": 5,
        "context_window": 2
    }
)

results = response.json()
for result in results["results"]:
    print(f"Resource: {result['title']}")
    print(f"Matched Chunk: {result['matched_chunks'][0]['content']}")
    print(f"Context: {len(result['context_chunks'])} surrounding chunks")
```

### Example 2: GraphRAG with Contradiction Discovery

```python
# Extract entities and relationships from chunks
response = requests.post(
    "http://localhost:8000/api/graph/extract/uuid-456"
)

# Search using GraphRAG
response = requests.post(
    "http://localhost:8000/api/search/advanced",
    json={
        "query": "gradient descent optimization",
        "strategy": "graphrag",
        "relation_types": ["EXTENDS", "SUPPORTS", "CONTRADICTS"],
        "max_hops": 2,
        "discover_contradictions": true
    }
)

results = response.json()
for result in results["results"]:
    print(f"Chunk: {result['content']}")
    print(f"Graph Path: {result['graph_path']}")
    
if "contradictions" in results:
    print("\nContradictions Found:")
    for contradiction in results["contradictions"]:
        print(f"{contradiction['entity_a']} CONTRADICTS {contradiction['entity_b']}")
```

### Example 3: Hybrid Retrieval Strategy

```python
# Combine multiple strategies
response = requests.post(
    "http://localhost:8000/api/search/advanced",
    json={
        "query": "How to optimize neural networks?",
        "strategy": "hybrid",
        "methods": ["parent-child", "graphrag", "question"],
        "weights": [0.4, 0.3, 0.3],
        "top_k": 10
    }
)

results = response.json()
print(f"Total results: {len(results['results'])}")
print(f"Methods used: {results['metadata']['methods_used']}")
print(f"Fusion strategy: {results['metadata']['fusion_strategy']}")
```

---

## Best Practices

### 1. Chunking Strategy Selection

**Use Semantic Chunking for**:
- Academic papers
- Narrative content
- Long-form articles

**Use Fixed-Size Chunking for**:
- Technical documentation
- Reference materials
- Structured content

**Use AST Chunking for** (Phase 18):
- Source code
- Code documentation
- Technical tutorials with code

### 2. Context Window Tuning

**Small Context Window (1-2 chunks)**:
- Precise answers
- Minimal noise
- Fast retrieval

**Large Context Window (3-5 chunks)**:
- More context
- Better for complex queries
- Slower retrieval

### 3. GraphRAG Optimization

**Entity Extraction**:
- Use LLM for better accuracy
- Use spaCy for speed
- Hybrid approach for balance

**Relationship Types**:
- Start with academic relations
- Add code relations for Phase 18
- Custom relations for domain-specific needs

### 4. Hybrid Strategy Weights

**Query-Dependent Weights**:
```python
# Factual queries: favor parent-child
weights = [0.6, 0.2, 0.2]  # [parent-child, graphrag, question]

# Exploratory queries: favor graphrag
weights = [0.2, 0.6, 0.2]

# Question-like queries: favor question-based
weights = [0.2, 0.2, 0.6]
```

### 5. Performance Optimization

**Indexing**:
- Chunk resources asynchronously
- Generate questions in background
- Extract entities in batches

**Retrieval**:
- Cache query embeddings
- Limit graph traversal depth
- Use pagination for large result sets

### 6. Quality Monitoring

**Track Metrics**:
- Retrieval latency
- Result relevance
- User feedback
- Contradiction discovery rate

**Use RAG Evaluation**:
```python
POST /api/evaluation/submit
{
  "query": "What is gradient descent?",
  "expected_answer": "An optimization algorithm...",
  "generated_answer": "Gradient descent is...",
  "retrieved_chunk_ids": ["uuid-1", "uuid-2"],
  "faithfulness_score": 0.92,
  "answer_relevance_score": 0.88,
  "context_precision_score": 0.85
}
```

---

## Related Documentation

- [RAG Evaluation Guide](rag-evaluation.md) - Quality metrics and monitoring
- [Migration Guide](naive-to-advanced-rag.md) - Upgrading from naive RAG
- [Database Architecture](../architecture/database.md) - Advanced RAG tables
- [Search API](../api/search.md) - Advanced search endpoints
- [Graph API](../api/graph.md) - Graph operations
