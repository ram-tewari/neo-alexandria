# Design Document: Phase 16.7 - Missing Features Implementation

## Overview

Phase 16.7 completes the Neo Alexandria backend by implementing all features from phases 6-12 that were left incomplete during the vertical slice refactoring. This phase transforms stub implementations into fully functional services, migrates legacy code into the modular architecture, and ensures every capability specified in the original design documents is operational.

### Implementation Strategy

1. **Complete Existing Stubs**: Transform placeholder classes into full implementations
2. **Migrate Legacy Services**: Move services from `app/services/` into appropriate modules
3. **Add Missing Features**: Implement features that were never started
4. **Integrate with Events**: Ensure all services participate in event-driven architecture
5. **Comprehensive Testing**: Add unit, integration, and performance tests

### Priority Order

**Phase 1 (Critical)**: Annotation Service, Collection embeddings, ML Classification
**Phase 2 (High)**: Search service migration, Summarization evaluator, Scholarly metadata
**Phase 3 (Medium)**: Graph embeddings, LBD, User profiles, Curation workflows

## Architecture

### Module Structure After Phase 16.7

```
backend/app/modules/
├── annotations/          # COMPLETE: Full CRUD, search, export
├── collections/          # COMPLETE: Embeddings, recommendations
├── search/              # COMPLETE: Three-way hybrid, reranking
├── quality/             # COMPLETE: Summary evaluation
├── scholarly/           # COMPLETE: LaTeX, tables, metadata
├── graph/               # COMPLETE: Embeddings, LBD
├── recommendations/     # COMPLETE: User profiles
├── taxonomy/            # COMPLETE: ML classification
├── curation/            # COMPLETE: Batch operations
└── [other modules]      # Already complete
```

### Service Migration Map

```
FROM: app/services/                    TO: app/modules/
├── sparse_embedding_service.py    →  search/sparse_embeddings.py
├── reranking_service.py           →  search/reranking.py
├── reciprocal_rank_fusion_service.py → search/rrf.py
└── hybrid_search_methods.py       →  search/hybrid_methods.py
```


## Component Designs

### 1. Annotation Service (Complete Implementation)

**Location**: `backend/app/modules/annotations/service.py`

**Current State**: Stub/minimal implementation
**Target State**: Full-featured annotation system

**Key Methods to Implement**:

```python
class AnnotationService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
    
    # CRUD Operations
    def create_annotation(
        self,
        resource_id: str,
        user_id: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: str | None = None,
        tags: List[str] | None = None,
        color: str = "#FFFF00",
        collection_ids: List[str] | None = None
    ) -> Annotation:
        """Create annotation with validation and context extraction."""
        # 1. Validate offsets
        # 2. Verify resource exists
        # 3. Extract context (50 chars before/after)
        # 4. Create annotation record
        # 5. Enqueue embedding generation if note exists
        # 6. Emit annotation.created event
        pass
    
    def update_annotation(
        self,
        annotation_id: str,
        user_id: str,
        note: str | None = None,
        tags: List[str] | None = None,
        color: str | None = None,
        is_shared: bool | None = None
    ) -> Annotation:
        """Update annotation with ownership check."""
        pass
    
    def delete_annotation(self, annotation_id: str, user_id: str) -> bool:
        """Delete annotation with ownership check."""
        pass
    
    # Search Operations
    def search_fulltext(
        self,
        user_id: str,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Annotation]:
        """Full-text search across notes and highlighted text."""
        # Use LIKE query on note and highlighted_text
        # Filter by user_id for privacy
        # Target: <100ms for 10,000 annotations
        pass
    
    def search_semantic(
        self,
        user_id: str,
        query: str,
        limit: int = 50
    ) -> List[Tuple[Annotation, float]]:
        """Semantic search using embeddings."""
        # 1. Generate query embedding
        # 2. Retrieve user annotations with embeddings
        # 3. Compute cosine similarity
        # 4. Sort by similarity descending
        # 5. Return top N with scores
        pass
    
    def search_by_tags(
        self,
        user_id: str,
        tags: List[str],
        match_all: bool = False
    ) -> List[Annotation]:
        """Search annotations by tags."""
        # Support ANY (OR) or ALL (AND) matching
        pass
    
    # Export Operations
    def export_markdown(
        self,
        user_id: str,
        resource_id: str | None = None
    ) -> str:
        """Export annotations to Markdown format."""
        # Group by resource
        # Format with headers, blockquotes, metadata
        pass
    
    def export_json(
        self,
        user_id: str,
        resource_id: str | None = None
    ) -> List[Dict]:
        """Export annotations to JSON format."""
        pass
    
    # Helper Methods
    def _extract_context(
        self,
        content: str,
        start_offset: int,
        end_offset: int
    ) -> Tuple[str, str]:
        """Extract 50 chars before and after highlight."""
        pass
    
    def _generate_embedding_async(
        self,
        annotation_id: str,
        note: str
    ) -> None:
        """Generate embedding in background."""
        pass
```

**Database Model Updates**:
- Ensure all fields from Phase 7.5 spec exist
- Add indexes: (user_id, resource_id), (created_at)
- Add check constraints for offset validation

**API Endpoints to Add**:
- POST /resources/{id}/annotations
- GET /resources/{id}/annotations
- GET /annotations
- GET /annotations/{id}
- PUT /annotations/{id}
- DELETE /annotations/{id}
- GET /annotations/search/fulltext
- GET /annotations/search/semantic
- GET /annotations/search/tags
- GET /annotations/export/markdown
- GET /annotations/export/json



### 2. Collection Service (Add Missing Features)

**Location**: `backend/app/modules/collections/service.py`

**Current State**: Basic CRUD exists
**Target State**: Add embeddings and recommendations

**Methods to Add**:

```python
class CollectionService:
    # Existing methods remain...
    
    def compute_aggregate_embedding(
        self,
        collection_id: str
    ) -> List[float] | None:
        """Compute mean embedding from member resources."""
        # 1. Query all member resources with embeddings
        # 2. If no embeddings, return None
        # 3. Stack into numpy matrix
        # 4. Compute column-wise mean
        # 5. Normalize to unit length (L2 norm)
        # 6. Store in collection.embedding
        # 7. Return embedding vector
        pass
    
    def get_resource_recommendations(
        self,
        collection_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get similar resources based on collection embedding."""
        # 1. Retrieve collection embedding
        # 2. Query resources by cosine similarity
        # 3. Exclude resources already in collection
        # 4. Order by similarity DESC
        # 5. Return top N with scores
        pass
    
    def get_collection_recommendations(
        self,
        collection_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get similar collections based on embedding."""
        # 1. Retrieve collection embedding
        # 2. Query collections by cosine similarity
        # 3. Exclude source collection
        # 4. Filter by visibility (user access)
        # 5. Order by similarity DESC
        # 6. Return top N with scores
        pass
    
    def validate_hierarchy(
        self,
        collection_id: str,
        new_parent_id: str
    ) -> bool:
        """Prevent circular references in hierarchy."""
        # Traverse up parent chain
        # If collection_id encountered → cycle detected
        pass
    
    def add_resources_batch(
        self,
        collection_id: str,
        user_id: str,
        resource_ids: List[str]
    ) -> Collection:
        """Add multiple resources in batch."""
        # Validate ownership
        # Validate all resource_ids exist
        # Batch insert associations
        # Trigger embedding recomputation
        # Emit collection.resource_added event
        pass
```

**Event Handlers to Add**:
```python
@event_bus.subscribe("resource.deleted")
async def handle_resource_deleted(event: Event):
    """Remove deleted resource from all collections."""
    # Remove from collection_resources
    # Recompute affected collection embeddings
```

**API Endpoints to Add**:
- GET /collections/{id}/recommendations
- GET /collections/{id}/embedding



### 3. Search Module Integration (Migrate Legacy Services)

**Target Structure**:
```
backend/app/modules/search/
├── service.py              # Main SearchService (exists)
├── sparse_embeddings.py    # Migrated from services/
├── reranking.py           # Migrated from services/
├── rrf.py                 # Migrated from services/
├── hybrid_methods.py      # Migrated from services/
└── router.py              # Updated with new endpoints
```

**Migration Steps**:

1. **Copy and Adapt Services**:
   - Move `sparse_embedding_service.py` → `search/sparse_embeddings.py`
   - Move `reranking_service.py` → `search/reranking.py`
   - Move `reciprocal_rank_fusion_service.py` → `search/rrf.py`
   - Move `hybrid_search_methods.py` → `search/hybrid_methods.py`

2. **Update SearchService to Use Migrated Services**:

```python
class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.sparse_embeddings = SparseEmbeddingService(db)
        self.reranking = RerankingService()
        self.rrf = ReciprocalRankFusionService()
    
    def three_way_hybrid_search(
        self,
        query: str,
        limit: int = 20,
        use_reranking: bool = True
    ) -> List[Dict]:
        """Execute three-way hybrid search with RRF fusion."""
        # 1. Execute FTS5 search (up to 100 candidates)
        fts_results = self._fulltext_search(query, limit=100)
        
        # 2. Execute dense vector search (up to 100 candidates)
        dense_results = self._semantic_search(query, limit=100)
        
        # 3. Execute sparse vector search (up to 100 candidates)
        sparse_results = self.sparse_embeddings.search(query, limit=100)
        
        # 4. Apply query-adaptive weighting
        weights = self._compute_adaptive_weights(query)
        
        # 5. Merge with RRF
        merged = self.rrf.fuse(
            [fts_results, dense_results, sparse_results],
            weights=weights
        )
        
        # 6. Optionally rerank top candidates
        if use_reranking:
            merged = self.reranking.rerank(query, merged[:100])
        
        return merged[:limit]
    
    def _compute_adaptive_weights(self, query: str) -> List[float]:
        """Compute query-adaptive weights for RRF."""
        base_weights = [0.33, 0.33, 0.34]  # FTS5, dense, sparse
        
        word_count = len(query.split())
        
        # Short queries: boost FTS5
        if word_count <= 3:
            base_weights[0] *= 1.5
        
        # Long queries: boost dense
        if word_count > 10:
            base_weights[1] *= 1.5
        
        # Technical queries: boost sparse
        if any(c in query for c in ['(', ')', '{', '}', '=', '+', '-']):
            base_weights[2] *= 1.5
        
        # Question queries: boost dense
        if query.lower().startswith(('who', 'what', 'when', 'where', 'why', 'how')):
            base_weights[1] *= 1.3
        
        # Normalize to sum to 1.0
        total = sum(base_weights)
        return [w / total for w in base_weights]
```

3. **Update Imports Throughout Codebase**:
   - Find all `from app.services.X import Y`
   - Replace with `from app.modules.search.X import Y`

4. **Remove Legacy Files**:
   - Delete `app/services/sparse_embedding_service.py`
   - Delete `app/services/reranking_service.py`
   - Delete `app/services/reciprocal_rank_fusion_service.py`
   - Delete `app/services/hybrid_search_methods.py`

**API Endpoints to Add**:
- GET /search/three-way (three-way hybrid search)
- GET /search/compare (side-by-side comparison)



### 4. Summarization Evaluator Service

**Location**: `backend/app/modules/quality/summarization_evaluator.py` (new file)

**Implementation**:

```python
class SummarizationEvaluator:
    def __init__(self, openai_api_key: str | None = None):
        self.openai_api_key = openai_api_key
        self.bert_scorer = None  # Lazy load BERTScore model
    
    def evaluate_summary(
        self,
        summary: str,
        reference: str,
        use_geval: bool = True
    ) -> Dict[str, float]:
        """Evaluate summary quality using multiple metrics."""
        results = {}
        
        # G-Eval metrics (if API key available)
        if use_geval and self.openai_api_key:
            results.update(self._geval_metrics(summary, reference))
        else:
            # Fallback scores
            results.update({
                'coherence': 0.7,
                'consistency': 0.7,
                'fluency': 0.7,
                'relevance': 0.7
            })
        
        # FineSurE metrics
        results.update(self._finesure_metrics(summary, reference))
        
        # BERTScore
        results['bertscore_f1'] = self._bertscore(summary, reference)
        
        # Composite score
        results['overall'] = self._compute_composite(results)
        
        return results
    
    def _geval_metrics(
        self,
        summary: str,
        reference: str
    ) -> Dict[str, float]:
        """Compute G-Eval metrics using GPT-4."""
        import openai
        
        openai.api_key = self.openai_api_key
        
        metrics = {}
        
        # Coherence
        prompt = f"""Rate the coherence of this summary on a scale of 1-5.
Reference: {reference}
Summary: {summary}
Score (1-5):"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        score = float(response.choices[0].message.content.strip())
        metrics['coherence'] = (score - 1) / 4  # Normalize to 0-1
        
        # Similar for consistency, fluency, relevance...
        
        return metrics
    
    def _finesure_metrics(
        self,
        summary: str,
        reference: str
    ) -> Dict[str, float]:
        """Compute FineSurE completeness and conciseness."""
        # Completeness: coverage of key information
        # Extract key phrases from reference
        # Check presence in summary
        
        # Conciseness: information density
        # Optimal compression ratio: 5-15%
        compression_ratio = len(summary) / len(reference)
        
        if 0.05 <= compression_ratio <= 0.15:
            conciseness = 1.0
        else:
            # Penalize deviation from optimal range
            conciseness = max(0, 1 - abs(compression_ratio - 0.1) * 5)
        
        return {
            'completeness': 0.8,  # Placeholder - implement key phrase matching
            'conciseness': conciseness
        }
    
    def _bertscore(self, summary: str, reference: str) -> float:
        """Compute BERTScore F1."""
        from bert_score import score
        
        if self.bert_scorer is None:
            # Lazy load model
            pass
        
        P, R, F1 = score(
            [summary],
            [reference],
            model_type="microsoft/deberta-xlarge-mnli",
            verbose=False
        )
        
        return F1.item()
    
    def _compute_composite(self, metrics: Dict[str, float]) -> float:
        """Compute weighted composite score."""
        weights = {
            'coherence': 0.20,
            'consistency': 0.20,
            'fluency': 0.15,
            'relevance': 0.15,
            'completeness': 0.15,
            'conciseness': 0.05,
            'bertscore_f1': 0.10
        }
        
        return sum(metrics.get(k, 0) * v for k, v in weights.items())
```

**Integration with QualityService**:

```python
class QualityService:
    def __init__(self, db: Session):
        self.db = db
        self.summarization_evaluator = SummarizationEvaluator(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def evaluate_resource_summary(self, resource_id: str) -> Dict:
        """Evaluate summary quality for a resource."""
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        if not resource.summary:
            return {"error": "No summary available"}
        
        metrics = self.summarization_evaluator.evaluate_summary(
            summary=resource.summary,
            reference=resource.content,
            use_geval=True
        )
        
        # Store metrics in resource
        resource.summary_coherence = metrics['coherence']
        resource.summary_consistency = metrics['consistency']
        resource.summary_fluency = metrics['fluency']
        resource.summary_relevance = metrics['relevance']
        resource.summary_completeness = metrics['completeness']
        resource.summary_conciseness = metrics['conciseness']
        resource.summary_bertscore = metrics['bertscore_f1']
        resource.summary_quality_overall = metrics['overall']
        
        self.db.commit()
        
        return metrics
```

**Database Schema Updates**:
Add to Resource model:
- summary_coherence: Float
- summary_consistency: Float
- summary_fluency: Float
- summary_relevance: Float
- summary_completeness: Float
- summary_conciseness: Float
- summary_bertscore: Float
- summary_quality_overall: Float

**API Endpoints to Add**:
- POST /quality/evaluate-summary/{resource_id}
- GET /quality/summary-metrics/{resource_id}



### 5. Scholarly Metadata Service (Complete Implementation)

**Location**: `backend/app/modules/scholarly/service.py`

**Current State**: Minimal implementation
**Target State**: Full metadata extraction

**Methods to Implement**:

```python
class ScholarlyService:
    def __init__(self, db: Session):
        self.db = db
    
    def extract_metadata(self, resource_id: str) -> Dict:
        """Extract comprehensive scholarly metadata."""
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        metadata = {}
        
        # Extract equations
        metadata['equations'] = self._extract_equations(resource.content)
        
        # Extract tables
        metadata['tables'] = self._extract_tables(resource.content)
        
        # Extract figures
        metadata['figures'] = self._extract_figures(resource.content)
        
        # Extract affiliations
        metadata['affiliations'] = self._extract_affiliations(resource.content)
        
        # Extract funding
        metadata['funding'] = self._extract_funding(resource.content)
        
        # Extract keywords
        metadata['keywords'] = self._extract_keywords(resource.content)
        
        # Store in resource
        resource.scholarly_metadata = json.dumps(metadata)
        self.db.commit()
        
        # Emit event
        event_bus.emit(Event(
            type="metadata.extracted",
            data={"resource_id": resource_id, "metadata": metadata}
        ))
        
        return metadata
    
    def _extract_equations(self, content: str) -> List[Dict]:
        """Extract LaTeX equations and convert to MathML."""
        import re
        
        equations = []
        
        # Find inline equations: $...$
        inline_pattern = r'\$([^\$]+)\$'
        for match in re.finditer(inline_pattern, content):
            equations.append({
                'type': 'inline',
                'latex': match.group(1),
                'mathml': self._latex_to_mathml(match.group(1)),
                'position': match.start()
            })
        
        # Find display equations: $$...$$
        display_pattern = r'\$\$([^\$]+)\$\$'
        for match in re.finditer(display_pattern, content):
            equations.append({
                'type': 'display',
                'latex': match.group(1),
                'mathml': self._latex_to_mathml(match.group(1)),
                'position': match.start()
            })
        
        return equations
    
    def _latex_to_mathml(self, latex: str) -> str:
        """Convert LaTeX to MathML."""
        try:
            from latex2mathml.converter import convert
            return convert(latex)
        except:
            return latex  # Fallback to LaTeX string
    
    def _extract_tables(self, content: str) -> List[Dict]:
        """Extract tables from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        tables = []
        
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': [],
                'caption': None
            }
            
            # Extract caption
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text(strip=True)
            
            # Extract headers
            thead = table.find('thead')
            if thead:
                for th in thead.find_all('th'):
                    table_data['headers'].append(th.get_text(strip=True))
            
            # Extract rows
            tbody = table.find('tbody') or table
            for tr in tbody.find_all('tr'):
                row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if row:
                    table_data['rows'].append(row)
            
            tables.append(table_data)
        
        return tables
    
    def _extract_figures(self, content: str) -> List[Dict]:
        """Extract figure captions and references."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        figures = []
        
        for figure in soup.find_all('figure'):
            fig_data = {
                'caption': None,
                'alt_text': None,
                'src': None
            }
            
            # Extract caption
            figcaption = figure.find('figcaption')
            if figcaption:
                fig_data['caption'] = figcaption.get_text(strip=True)
            
            # Extract image
            img = figure.find('img')
            if img:
                fig_data['alt_text'] = img.get('alt', '')
                fig_data['src'] = img.get('src', '')
            
            figures.append(fig_data)
        
        return figures
    
    def _extract_affiliations(self, content: str) -> List[str]:
        """Extract author affiliations."""
        # Pattern matching for common affiliation formats
        # "Department of X, University of Y"
        # "X Lab, Y Institute"
        import re
        
        patterns = [
            r'Department of [^,]+, [^,]+',
            r'[^,]+ Lab, [^,]+',
            r'[^,]+ Institute[^,]*'
        ]
        
        affiliations = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            affiliations.extend(matches)
        
        return list(set(affiliations))
    
    def _extract_funding(self, content: str) -> List[str]:
        """Extract funding information."""
        import re
        
        # Look for funding/acknowledgment sections
        funding_pattern = r'(?:funded by|supported by|grant[s]?)\s+([^.]+)'
        matches = re.findall(funding_pattern, content, re.IGNORECASE)
        
        return matches
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords and subject classifications."""
        # Look for explicit keyword sections
        # Or extract from metadata tags
        import re
        
        keyword_pattern = r'(?:keywords?|subjects?):?\s*([^.\n]+)'
        matches = re.findall(keyword_pattern, content, re.IGNORECASE)
        
        keywords = []
        for match in matches:
            # Split on commas or semicolons
            keywords.extend([k.strip() for k in re.split(r'[,;]', match)])
        
        return keywords
```

**API Endpoints to Add**:
- POST /scholarly/extract-metadata/{resource_id}
- GET /scholarly/metadata/{resource_id}
- GET /scholarly/equations/{resource_id}
- GET /scholarly/tables/{resource_id}



### 6. Graph Embeddings Service

**Location**: `backend/app/modules/graph/embeddings.py`

**Current State**: Stub class
**Target State**: Node2Vec and DeepWalk implementations

**Implementation**:

```python
class GraphEmbeddingsService:
    def __init__(self, db: Session):
        self.db = db
        self.embeddings_cache = {}
    
    def generate_node2vec_embeddings(
        self,
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        p: float = 1.0,
        q: float = 1.0
    ) -> Dict[str, List[float]]:
        """Generate Node2Vec embeddings for citation graph."""
        from node2vec import Node2Vec
        import networkx as nx
        
        # Build NetworkX graph from citation data
        G = self._build_networkx_graph()
        
        # Initialize Node2Vec
        node2vec = Node2Vec(
            G,
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            p=p,
            q=q,
            workers=4
        )
        
        # Train model
        model = node2vec.fit(window=10, min_count=1, batch_words=4)
        
        # Extract embeddings
        embeddings = {}
        for node in G.nodes():
            embeddings[node] = model.wv[node].tolist()
        
        # Cache embeddings
        self.embeddings_cache.update(embeddings)
        
        # Store in database or cache
        self._store_embeddings(embeddings)
        
        return embeddings
    
    def generate_deepwalk_embeddings(
        self,
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10
    ) -> Dict[str, List[float]]:
        """Generate DeepWalk embeddings (Node2Vec with p=1, q=1)."""
        return self.generate_node2vec_embeddings(
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            p=1.0,
            q=1.0
        )
    
    def get_embedding(self, node_id: str) -> List[float] | None:
        """Retrieve embedding for a node."""
        # Check cache first
        if node_id in self.embeddings_cache:
            return self.embeddings_cache[node_id]
        
        # Query from database
        # ...
        
        return None
    
    def find_similar_nodes(
        self,
        node_id: str,
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find similar nodes using embedding similarity."""
        target_embedding = self.get_embedding(node_id)
        
        if not target_embedding:
            return []
        
        # Compute cosine similarity with all other nodes
        similarities = []
        for other_id, other_embedding in self.embeddings_cache.items():
            if other_id != node_id:
                similarity = self._cosine_similarity(
                    target_embedding,
                    other_embedding
                )
                similarities.append((other_id, similarity))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def _build_networkx_graph(self) -> 'nx.Graph':
        """Build NetworkX graph from citation data."""
        import networkx as nx
        
        G = nx.DiGraph()
        
        # Query all citations
        citations = self.db.query(Citation).all()
        
        for citation in citations:
            G.add_edge(
                str(citation.source_id),
                str(citation.target_id)
            )
        
        return G
    
    def _store_embeddings(self, embeddings: Dict[str, List[float]]):
        """Store embeddings in database or cache."""
        # Store in Redis cache or database table
        pass
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np
        
        a_arr = np.array(a)
        b_arr = np.array(b)
        
        return np.dot(a_arr, b_arr) / (
            np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
        )
```

**API Endpoints to Add**:
- POST /graph/embeddings/generate (trigger embedding generation)
- GET /graph/embeddings/{node_id}
- GET /graph/embeddings/{node_id}/similar



### 7. Literature-Based Discovery (LBD) Service

**Location**: `backend/app/modules/graph/discovery.py`

**Current State**: Stub class
**Target State**: ABC discovery and hypothesis generation

**Implementation**:

```python
class LBDService:
    def __init__(self, db: Session):
        self.db = db
    
    def discover_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        limit: int = 50,
        time_slice: Tuple[datetime, datetime] | None = None
    ) -> List[Dict]:
        """Discover bridging concepts between A and C (ABC pattern)."""
        # 1. Find resources mentioning concept A
        resources_a = self._find_resources_with_concept(concept_a, time_slice)
        
        # 2. Find resources mentioning concept C
        resources_c = self._find_resources_with_concept(concept_c, time_slice)
        
        # 3. Find bridging concepts B that appear with A and C separately
        bridging_concepts = self._find_bridging_concepts(
            resources_a,
            resources_c
        )
        
        # 4. Filter out known A-C connections
        bridging_concepts = self._filter_known_connections(
            concept_a,
            concept_c,
            bridging_concepts
        )
        
        # 5. Rank by support strength and novelty
        hypotheses = self._rank_hypotheses(
            concept_a,
            concept_c,
            bridging_concepts
        )
        
        return hypotheses[:limit]
    
    def _find_resources_with_concept(
        self,
        concept: str,
        time_slice: Tuple[datetime, datetime] | None
    ) -> List[Resource]:
        """Find resources mentioning a concept."""
        query = self.db.query(Resource).filter(
            or_(
                Resource.title.contains(concept),
                Resource.content.contains(concept),
                Resource.abstract.contains(concept)
            )
        )
        
        if time_slice:
            start, end = time_slice
            query = query.filter(
                Resource.publication_date.between(start, end)
            )
        
        return query.all()
    
    def _find_bridging_concepts(
        self,
        resources_a: List[Resource],
        resources_c: List[Resource]
    ) -> List[str]:
        """Find concepts that appear with A and C separately."""
        from collections import Counter
        
        # Extract concepts from A resources
        concepts_with_a = set()
        for resource in resources_a:
            concepts_with_a.update(self._extract_concepts(resource))
        
        # Extract concepts from C resources
        concepts_with_c = set()
        for resource in resources_c:
            concepts_with_c.update(self._extract_concepts(resource))
        
        # Find intersection (concepts appearing with both A and C)
        bridging = concepts_with_a & concepts_with_c
        
        return list(bridging)
    
    def _extract_concepts(self, resource: Resource) -> Set[str]:
        """Extract key concepts from resource."""
        # Use NLP to extract noun phrases
        # Or use existing tags/keywords
        concepts = set()
        
        if resource.tags:
            concepts.update(json.loads(resource.tags))
        
        # Could also use spaCy for noun phrase extraction
        # import spacy
        # nlp = spacy.load("en_core_web_sm")
        # doc = nlp(resource.content[:1000])
        # concepts.update([chunk.text for chunk in doc.noun_chunks])
        
        return concepts
    
    def _filter_known_connections(
        self,
        concept_a: str,
        concept_c: str,
        bridging_concepts: List[str]
    ) -> List[str]:
        """Filter out already-known A-C connections."""
        # Check if any resources mention both A and C together
        known_connections = self.db.query(Resource).filter(
            and_(
                or_(
                    Resource.title.contains(concept_a),
                    Resource.content.contains(concept_a)
                ),
                or_(
                    Resource.title.contains(concept_c),
                    Resource.content.contains(concept_c)
                )
            )
        ).count()
        
        # If direct connections exist, this is not a novel hypothesis
        # Could implement more sophisticated filtering
        
        return bridging_concepts
    
    def _rank_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        bridging_concepts: List[str]
    ) -> List[Dict]:
        """Rank hypotheses by support strength and novelty."""
        hypotheses = []
        
        for concept_b in bridging_concepts:
            # Count A-B connections
            ab_count = self._count_connections(concept_a, concept_b)
            
            # Count B-C connections
            bc_count = self._count_connections(concept_b, concept_c)
            
            # Compute support strength
            support = min(ab_count, bc_count)
            
            # Compute novelty (inverse of A-C co-occurrence)
            ac_count = self._count_connections(concept_a, concept_c)
            novelty = 1.0 / (1.0 + ac_count)
            
            # Compute confidence score
            confidence = support * novelty
            
            hypotheses.append({
                'concept_a': concept_a,
                'concept_b': concept_b,
                'concept_c': concept_c,
                'ab_support': ab_count,
                'bc_support': bc_count,
                'novelty': novelty,
                'confidence': confidence,
                'evidence_chain': self._build_evidence_chain(
                    concept_a, concept_b, concept_c
                )
            })
        
        # Sort by confidence descending
        hypotheses.sort(key=lambda x: x['confidence'], reverse=True)
        
        return hypotheses
    
    def _count_connections(self, concept_1: str, concept_2: str) -> int:
        """Count resources mentioning both concepts."""
        return self.db.query(Resource).filter(
            and_(
                or_(
                    Resource.title.contains(concept_1),
                    Resource.content.contains(concept_1)
                ),
                or_(
                    Resource.title.contains(concept_2),
                    Resource.content.contains(concept_2)
                )
            )
        ).count()
    
    def _build_evidence_chain(
        self,
        concept_a: str,
        concept_b: str,
        concept_c: str
    ) -> List[Dict]:
        """Build evidence chain showing A→B and B→C connections."""
        chain = []
        
        # Find example A-B resources
        ab_resources = self.db.query(Resource).filter(
            and_(
                or_(
                    Resource.title.contains(concept_a),
                    Resource.content.contains(concept_a)
                ),
                or_(
                    Resource.title.contains(concept_b),
                    Resource.content.contains(concept_b)
                )
            )
        ).limit(3).all()
        
        for resource in ab_resources:
            chain.append({
                'type': 'A-B',
                'resource_id': str(resource.id),
                'title': resource.title
            })
        
        # Find example B-C resources
        bc_resources = self.db.query(Resource).filter(
            and_(
                or_(
                    Resource.title.contains(concept_b),
                    Resource.content.contains(concept_b)
                ),
                or_(
                    Resource.title.contains(concept_c),
                    Resource.content.contains(concept_c)
                )
            )
        ).limit(3).all()
        
        for resource in bc_resources:
            chain.append({
                'type': 'B-C',
                'resource_id': str(resource.id),
                'title': resource.title
            })
        
        return chain
```

**API Endpoints to Add**:
- POST /graph/discover (hypothesis discovery)
- GET /graph/hypotheses/{id}



### 8. User Profile Service (Complete Implementation)

**Location**: `backend/app/modules/recommendations/user_profile.py`

**Current State**: Minimal implementation
**Target State**: Full interaction tracking and preference learning

**Implementation**:

```python
class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
    
    def track_interaction(
        self,
        user_id: str,
        interaction_type: str,
        resource_id: str | None = None,
        metadata: Dict | None = None
    ):
        """Track user interaction event."""
        interaction = UserInteraction(
            user_id=user_id,
            interaction_type=interaction_type,
            resource_id=resource_id,
            metadata=json.dumps(metadata) if metadata else None,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(interaction)
        self.db.commit()
        
        # Emit event for profile update
        event_bus.emit(Event(
            type="user.interaction_tracked",
            data={
                "user_id": user_id,
                "interaction_type": interaction_type
            }
        ))
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get computed user profile."""
        # Query recent interactions (last 90 days)
        cutoff = datetime.utcnow() - timedelta(days=90)
        
        interactions = self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id,
            UserInteraction.timestamp >= cutoff
        ).all()
        
        profile = {
            'user_id': user_id,
            'interest_vector': self._compute_interest_vector(interactions),
            'frequent_topics': self._extract_frequent_topics(interactions),
            'frequent_tags': self._extract_frequent_tags(interactions),
            'interaction_counts': self._count_interactions(interactions),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _compute_interest_vector(
        self,
        interactions: List[UserInteraction]
    ) -> List[float]:
        """Compute user interest vector from interactions."""
        # Aggregate embeddings from viewed/annotated resources
        embeddings = []
        weights = []
        
        for interaction in interactions:
            if interaction.resource_id:
                resource = self.db.query(Resource).filter_by(
                    id=interaction.resource_id
                ).first()
                
                if resource and resource.embedding:
                    embeddings.append(json.loads(resource.embedding))
                    
                    # Weight recent interactions more heavily
                    age_days = (datetime.utcnow() - interaction.timestamp).days
                    weight = 1.0 / (1.0 + age_days / 30.0)  # Decay over 30 days
                    weights.append(weight)
        
        if not embeddings:
            return None
        
        # Compute weighted mean
        import numpy as np
        
        embeddings_array = np.array(embeddings)
        weights_array = np.array(weights).reshape(-1, 1)
        
        weighted_mean = np.sum(
            embeddings_array * weights_array,
            axis=0
        ) / np.sum(weights_array)
        
        # Normalize
        norm = np.linalg.norm(weighted_mean)
        if norm > 0:
            weighted_mean = weighted_mean / norm
        
        return weighted_mean.tolist()
    
    def _extract_frequent_topics(
        self,
        interactions: List[UserInteraction]
    ) -> List[str]:
        """Extract frequently accessed topics."""
        from collections import Counter
        
        topics = []
        
        for interaction in interactions:
            if interaction.resource_id:
                resource = self.db.query(Resource).filter_by(
                    id=interaction.resource_id
                ).first()
                
                if resource and resource.subject:
                    topics.append(resource.subject)
        
        # Count and return top 10
        topic_counts = Counter(topics)
        return [topic for topic, _ in topic_counts.most_common(10)]
    
    def _extract_frequent_tags(
        self,
        interactions: List[UserInteraction]
    ) -> List[str]:
        """Extract frequently used tags."""
        from collections import Counter
        
        tags = []
        
        # From annotations
        annotations = self.db.query(Annotation).filter(
            Annotation.user_id == interactions[0].user_id if interactions else None
        ).all()
        
        for annotation in annotations:
            if annotation.tags:
                tags.extend(json.loads(annotation.tags))
        
        # Count and return top 20
        tag_counts = Counter(tags)
        return [tag for tag, _ in tag_counts.most_common(20)]
    
    def _count_interactions(
        self,
        interactions: List[UserInteraction]
    ) -> Dict[str, int]:
        """Count interactions by type."""
        from collections import Counter
        
        counts = Counter(i.interaction_type for i in interactions)
        return dict(counts)
```

**Database Model**:

```python
class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

**Event Handlers**:

```python
@event_bus.subscribe("resource.viewed")
async def handle_resource_viewed(event: Event):
    user_profile_service.track_interaction(
        user_id=event.data['user_id'],
        interaction_type='view',
        resource_id=event.data['resource_id']
    )

@event_bus.subscribe("annotation.created")
async def handle_annotation_created(event: Event):
    user_profile_service.track_interaction(
        user_id=event.data['user_id'],
        interaction_type='annotate',
        resource_id=event.data['resource_id']
    )
```

**API Endpoints to Add**:
- GET /users/{user_id}/profile
- GET /users/{user_id}/interactions
- POST /users/{user_id}/interactions (manual tracking)



### 9. ML Classification Service (Complete Implementation)

**Location**: `backend/app/modules/taxonomy/ml_service.py`

**Current State**: Stub class
**Target State**: Full ML classification with active learning

**Implementation**:

```python
class MLClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.model = None
        self.model_metadata = {}
    
    def load_model(self, model_path: str):
        """Load pre-trained classification model."""
        import joblib
        
        self.model = joblib.load(model_path)
        
        # Load metadata
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.model_metadata = json.load(f)
    
    def predict(
        self,
        resource_id: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Predict taxonomy nodes for resource."""
        if not self.model:
            raise ValueError("Model not loaded")
        
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        # Extract features
        features = self._extract_features(resource)
        
        # Get predictions
        probabilities = self.model.predict_proba([features])[0]
        
        # Get top K predictions
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        predictions = []
        for idx in top_indices:
            node_id = self.model.classes_[idx]
            confidence = float(probabilities[idx])
            
            node = self.db.query(TaxonomyNode).filter_by(id=node_id).first()
            
            predictions.append({
                'node_id': str(node_id),
                'node_name': node.name if node else 'Unknown',
                'confidence': confidence,
                'is_uncertain': confidence < 0.5
            })
        
        return predictions
    
    def identify_uncertain_predictions(
        self,
        threshold: float = 0.5,
        limit: int = 100
    ) -> List[str]:
        """Identify resources with uncertain classifications for active learning."""
        # Query resources with low-confidence predictions
        # These are candidates for manual review
        
        uncertain_resources = []
        
        resources = self.db.query(Resource).filter(
            Resource.classification_confidence < threshold
        ).limit(limit).all()
        
        return [str(r.id) for r in resources]
    
    def retrain_model(
        self,
        training_data: List[Tuple[str, str]],
        validation_split: float = 0.2
    ) -> Dict:
        """Retrain model with new labeled data."""
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, f1_score
        
        # Prepare training data
        X = []
        y = []
        
        for resource_id, node_id in training_data:
            resource = self.db.query(Resource).filter_by(id=resource_id).first()
            if resource:
                features = self._extract_features(resource)
                X.append(features)
                y.append(node_id)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=validation_split,
            random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred, average='weighted')
        
        # Save model
        model_path = f"models/taxonomy_classifier_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pkl"
        import joblib
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            'version': datetime.utcnow().isoformat(),
            'accuracy': accuracy,
            'f1_score': f1,
            'training_samples': len(X_train),
            'validation_samples': len(X_val)
        }
        
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update current model
        self.model = model
        self.model_metadata = metadata
        
        return metadata
    
    def _extract_features(self, resource: Resource) -> List[float]:
        """Extract features for classification."""
        features = []
        
        # Use embedding as primary features
        if resource.embedding:
            features.extend(json.loads(resource.embedding))
        else:
            # Fallback: use TF-IDF or other features
            features.extend([0.0] * 768)  # Placeholder
        
        # Could add additional features:
        # - Text length
        # - Keyword presence
        # - Citation count
        # - Quality score
        
        return features
```

**API Endpoints to Add**:
- POST /taxonomy/classify/{resource_id}
- GET /taxonomy/predictions/{resource_id}
- POST /taxonomy/retrain
- GET /taxonomy/uncertain (active learning candidates)



### 10. Classification Coordination Service

**Location**: `backend/app/modules/taxonomy/classification_service.py`

**Current State**: Stub class
**Target State**: Unified classification interface

**Implementation**:

```python
class ClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = MLClassificationService(db)
        self.taxonomy_service = TaxonomyService(db)
    
    def classify_resource(
        self,
        resource_id: str,
        use_ml: bool = True,
        use_rules: bool = True
    ) -> Dict:
        """Classify resource using multiple methods."""
        predictions = []
        
        # ML-based classification
        if use_ml:
            try:
                ml_predictions = self.ml_service.predict(resource_id, top_k=5)
                for pred in ml_predictions:
                    pred['method'] = 'ml'
                predictions.extend(ml_predictions)
            except Exception as e:
                logger.error(f"ML classification failed: {e}")
        
        # Rule-based classification
        if use_rules:
            try:
                rule_predictions = self._rule_based_classify(resource_id)
                for pred in rule_predictions:
                    pred['method'] = 'rule'
                predictions.extend(rule_predictions)
            except Exception as e:
                logger.error(f"Rule-based classification failed: {e}")
        
        # Merge and resolve conflicts
        final_classification = self._merge_predictions(predictions)
        
        # Apply to resource
        self._apply_classification(resource_id, final_classification)
        
        # Emit event
        event_bus.emit(Event(
            type="resource.classified",
            data={
                "resource_id": resource_id,
                "classification": final_classification
            }
        ))
        
        return final_classification
    
    def _rule_based_classify(self, resource_id: str) -> List[Dict]:
        """Apply rule-based classification."""
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        predictions = []
        
        # Example rules based on keywords
        rules = {
            'machine learning': 'cs.LG',
            'neural network': 'cs.LG',
            'quantum': 'quant-ph',
            'biology': 'q-bio',
            'physics': 'physics'
        }
        
        content_lower = (resource.title + ' ' + resource.abstract).lower()
        
        for keyword, node_id in rules.items():
            if keyword in content_lower:
                node = self.db.query(TaxonomyNode).filter_by(
                    external_id=node_id
                ).first()
                
                if node:
                    predictions.append({
                        'node_id': str(node.id),
                        'node_name': node.name,
                        'confidence': 0.8,  # Rule-based confidence
                        'is_uncertain': False
                    })
        
        return predictions
    
    def _merge_predictions(
        self,
        predictions: List[Dict]
    ) -> Dict:
        """Merge predictions from multiple methods."""
        from collections import defaultdict
        
        # Group by node_id
        node_scores = defaultdict(list)
        
        for pred in predictions:
            node_scores[pred['node_id']].append({
                'confidence': pred['confidence'],
                'method': pred['method']
            })
        
        # Compute final scores
        final_predictions = []
        
        for node_id, scores in node_scores.items():
            # Average confidence across methods
            avg_confidence = sum(s['confidence'] for s in scores) / len(scores)
            
            # Boost if multiple methods agree
            if len(scores) > 1:
                avg_confidence *= 1.2
                avg_confidence = min(avg_confidence, 1.0)
            
            node = self.db.query(TaxonomyNode).filter_by(id=node_id).first()
            
            final_predictions.append({
                'node_id': node_id,
                'node_name': node.name if node else 'Unknown',
                'confidence': avg_confidence,
                'methods': [s['method'] for s in scores]
            })
        
        # Sort by confidence
        final_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'primary': final_predictions[0] if final_predictions else None,
            'alternatives': final_predictions[1:5] if len(final_predictions) > 1 else [],
            'all_predictions': final_predictions
        }
    
    def _apply_classification(
        self,
        resource_id: str,
        classification: Dict
    ):
        """Apply classification to resource."""
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        if classification['primary']:
            resource.taxonomy_node_id = classification['primary']['node_id']
            resource.classification_confidence = classification['primary']['confidence']
            resource.classification_method = ','.join(
                classification['primary']['methods']
            )
        
        self.db.commit()
```

**API Endpoints to Add**:
- POST /taxonomy/classify-resource/{resource_id}
- GET /taxonomy/classification/{resource_id}



### 11. Curation Service (Add Batch Operations)

**Location**: `backend/app/modules/curation/service.py`

**Current State**: Minimal implementation
**Target State**: Full batch operations and workflow management

**Methods to Add**:

```python
class CurationService:
    # Existing methods remain...
    
    def batch_review(
        self,
        resource_ids: List[str],
        curator_id: str,
        action: str,  # 'approve', 'reject', 'flag'
        comment: str | None = None
    ) -> Dict:
        """Perform batch review action on multiple resources."""
        results = {
            'success': [],
            'failed': []
        }
        
        for resource_id in resource_ids:
            try:
                self._review_resource(
                    resource_id,
                    curator_id,
                    action,
                    comment
                )
                results['success'].append(resource_id)
            except Exception as e:
                results['failed'].append({
                    'resource_id': resource_id,
                    'error': str(e)
                })
        
        # Emit event
        event_bus.emit(Event(
            type="curation.batch_reviewed",
            data={
                'curator_id': curator_id,
                'action': action,
                'count': len(results['success'])
            }
        ))
        
        return results
    
    def batch_tag(
        self,
        resource_ids: List[str],
        tags: List[str],
        curator_id: str
    ) -> Dict:
        """Add tags to multiple resources."""
        results = {'success': [], 'failed': []}
        
        for resource_id in resource_ids:
            try:
                resource = self.db.query(Resource).filter_by(
                    id=resource_id
                ).first()
                
                if resource:
                    existing_tags = json.loads(resource.tags) if resource.tags else []
                    existing_tags.extend(tags)
                    resource.tags = json.dumps(list(set(existing_tags)))
                    
                    results['success'].append(resource_id)
            except Exception as e:
                results['failed'].append({
                    'resource_id': resource_id,
                    'error': str(e)
                })
        
        self.db.commit()
        
        return results
    
    def get_review_queue(
        self,
        curator_id: str | None = None,
        status: str | None = None,
        min_quality: float | None = None,
        max_quality: float | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Resource]:
        """Get resources in review queue with filtering."""
        query = self.db.query(Resource)
        
        # Filter by review status
        if status:
            query = query.filter(Resource.review_status == status)
        else:
            query = query.filter(Resource.review_status == 'pending')
        
        # Filter by assigned curator
        if curator_id:
            query = query.filter(Resource.assigned_curator_id == curator_id)
        
        # Filter by quality score
        if min_quality is not None:
            query = query.filter(Resource.quality_score >= min_quality)
        if max_quality is not None:
            query = query.filter(Resource.quality_score <= max_quality)
        
        # Order by priority (low quality first)
        query = query.order_by(Resource.quality_score.asc())
        
        return query.limit(limit).offset(offset).all()
    
    def assign_to_curator(
        self,
        resource_ids: List[str],
        curator_id: str
    ) -> Dict:
        """Assign resources to a curator for review."""
        results = {'success': [], 'failed': []}
        
        for resource_id in resource_ids:
            try:
                resource = self.db.query(Resource).filter_by(
                    id=resource_id
                ).first()
                
                if resource:
                    resource.assigned_curator_id = curator_id
                    resource.review_status = 'assigned'
                    results['success'].append(resource_id)
            except Exception as e:
                results['failed'].append({
                    'resource_id': resource_id,
                    'error': str(e)
                })
        
        self.db.commit()
        
        return results
    
    def _review_resource(
        self,
        resource_id: str,
        curator_id: str,
        action: str,
        comment: str | None
    ):
        """Review a single resource."""
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
        
        # Update review status
        if action == 'approve':
            resource.review_status = 'approved'
        elif action == 'reject':
            resource.review_status = 'rejected'
        elif action == 'flag':
            resource.review_status = 'flagged'
        
        # Store review record
        review = CurationReview(
            resource_id=resource_id,
            curator_id=curator_id,
            action=action,
            comment=comment,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(review)
        self.db.commit()
        
        # Emit event
        event_bus.emit(Event(
            type="curation.reviewed",
            data={
                'resource_id': resource_id,
                'curator_id': curator_id,
                'action': action
            }
        ))
```

**Database Models to Add**:

```python
class CurationReview(Base):
    __tablename__ = "curation_reviews"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id"))
    curator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

**API Endpoints to Add**:
- POST /curation/batch/review
- POST /curation/batch/tag
- POST /curation/batch/assign
- GET /curation/queue



## Testing Strategy

### Unit Tests

Each service must have comprehensive unit tests:

**Annotation Service Tests**:
- `test_create_annotation_valid_offsets()`
- `test_create_annotation_invalid_offsets()`
- `test_fulltext_search_performance()`
- `test_semantic_search_similarity()`
- `test_export_markdown_format()`
- `test_context_extraction_boundaries()`

**Collection Service Tests**:
- `test_compute_aggregate_embedding()`
- `test_resource_recommendations_exclude_members()`
- `test_collection_recommendations_visibility()`
- `test_validate_hierarchy_circular_reference()`

**Search Service Tests**:
- `test_three_way_hybrid_search()`
- `test_query_adaptive_weighting()`
- `test_reranking_improves_results()`
- `test_sparse_embedding_generation()`

**Quality Service Tests**:
- `test_geval_metrics_with_api()`
- `test_geval_fallback_without_api()`
- `test_finesure_completeness()`
- `test_bertscore_computation()`

**Scholarly Service Tests**:
- `test_extract_latex_equations()`
- `test_extract_tables_structure()`
- `test_extract_figures_captions()`
- `test_extract_affiliations()`

**Graph Service Tests**:
- `test_node2vec_embeddings()`
- `test_deepwalk_embeddings()`
- `test_lbd_hypothesis_discovery()`
- `test_abc_pattern_detection()`

**User Profile Service Tests**:
- `test_track_interaction()`
- `test_compute_interest_vector()`
- `test_extract_frequent_topics()`
- `test_temporal_weighting()`

**ML Classification Service Tests**:
- `test_predict_top_k()`
- `test_identify_uncertain_predictions()`
- `test_retrain_model()`
- `test_feature_extraction()`

**Curation Service Tests**:
- `test_batch_review()`
- `test_batch_tag()`
- `test_get_review_queue_filtering()`
- `test_assign_to_curator()`

### Integration Tests

**End-to-End Workflows**:

1. **Annotation Workflow**:
   - Create resource
   - Create annotation
   - Search annotations
   - Export to Markdown
   - Verify all steps complete

2. **Collection Workflow**:
   - Create collection
   - Add resources
   - Compute embeddings
   - Get recommendations
   - Verify recommendations quality

3. **Search Workflow**:
   - Ingest resource
   - Generate embeddings (dense + sparse)
   - Execute three-way search
   - Apply reranking
   - Verify result quality

4. **Classification Workflow**:
   - Ingest resource
   - Extract features
   - ML prediction
   - Rule-based prediction
   - Merge predictions
   - Apply classification

### Performance Tests

**Performance Targets**:

```python
def test_annotation_search_performance():
    """Annotation search <100ms for 10,000 annotations."""
    # Create 10,000 annotations
    # Execute search
    # Assert latency < 100ms

def test_collection_embedding_performance():
    """Collection embedding <1s for 1000 resources."""
    # Create collection with 1000 resources
    # Compute embedding
    # Assert latency < 1s

def test_three_way_search_performance():
    """Three-way search <200ms (P95)."""
    # Execute 100 searches
    # Measure P95 latency
    # Assert P95 < 200ms

def test_summarization_evaluation_performance():
    """Summary evaluation <10s with G-Eval."""
    # Evaluate summary
    # Assert latency < 10s

def test_lbd_discovery_performance():
    """LBD discovery <5s for typical query."""
    # Execute hypothesis discovery
    # Assert latency < 5s
```

### Test Coverage Requirements

- Unit test coverage: >85% for all new services
- Integration test coverage: All API endpoints
- Performance test coverage: All critical paths
- Event handler coverage: All event subscriptions



## Migration and Deployment Strategy

### Phase 1: Critical Services (Week 1-2)

**Priority 1: Annotation Service**
- Implement full CRUD operations
- Add search capabilities
- Add export functionality
- Write comprehensive tests
- Update API documentation

**Priority 2: ML Classification**
- Implement MLClassificationService
- Implement ClassificationService
- Integrate with taxonomy module
- Fix "not yet implemented" errors
- Add model training scripts

**Priority 3: Collection Embeddings**
- Add embedding computation
- Add recommendation methods
- Update event handlers
- Test with large collections

### Phase 2: Search Integration (Week 3)

**Migrate Legacy Services**:
1. Copy services to search module
2. Update imports throughout codebase
3. Run full test suite
4. Verify no regressions
5. Delete legacy files

**Add Three-Way Search**:
1. Integrate sparse embeddings
2. Integrate reranking
3. Implement query-adaptive weighting
4. Add comparison endpoint
5. Performance testing

### Phase 3: Quality and Scholarly (Week 4)

**Summarization Evaluator**:
1. Implement G-Eval metrics
2. Implement FineSurE metrics
3. Implement BERTScore
4. Add database fields
5. Integrate with QualityService

**Scholarly Metadata**:
1. Implement LaTeX parsing
2. Implement table extraction
3. Implement figure extraction
4. Add metadata storage
5. Emit extraction events

### Phase 4: Graph Intelligence (Week 5)

**Graph Embeddings**:
1. Implement Node2Vec
2. Implement DeepWalk
3. Add embedding storage
4. Add similarity search
5. Performance optimization

**LBD Service**:
1. Implement ABC discovery
2. Implement hypothesis ranking
3. Add evidence chains
4. Add time-slicing
5. API endpoints

### Phase 5: User Profiles and Curation (Week 6)

**User Profiles**:
1. Implement interaction tracking
2. Implement profile computation
3. Add event handlers
4. Integrate with recommendations
5. Add profile export

**Curation Workflows**:
1. Implement batch operations
2. Implement review queue
3. Add curator assignment
4. Add review tracking
5. Workflow management

### Deployment Checklist

**Pre-Deployment**:
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Performance tests meet targets
- [ ] API documentation updated
- [ ] Database migrations created
- [ ] Event catalog updated
- [ ] Module READMEs updated

**Deployment Steps**:
1. Run database migrations
2. Deploy new code
3. Verify health checks
4. Monitor error rates
5. Monitor performance metrics
6. Verify event emissions

**Post-Deployment**:
- [ ] Smoke tests passing
- [ ] No error spikes
- [ ] Performance within targets
- [ ] Events flowing correctly
- [ ] Documentation accessible

### Rollback Plan

If issues arise:
1. Revert code deployment
2. Rollback database migrations (if needed)
3. Restore legacy services temporarily
4. Investigate and fix issues
5. Re-deploy with fixes

### Monitoring and Alerts

**Key Metrics to Monitor**:
- API endpoint latency (P50, P95, P99)
- Error rates by endpoint
- Database query performance
- Event emission rates
- Service health checks
- Memory and CPU usage

**Alerts to Configure**:
- Annotation search >200ms
- Collection embedding >2s
- Three-way search >500ms
- Classification errors >5%
- Event delivery failures
- Service health check failures



## Documentation Updates

### API Documentation

Update `backend/docs/api/` with new endpoints:

**annotations.md**:
- POST /resources/{id}/annotations
- GET /resources/{id}/annotations
- GET /annotations
- GET /annotations/{id}
- PUT /annotations/{id}
- DELETE /annotations/{id}
- GET /annotations/search/fulltext
- GET /annotations/search/semantic
- GET /annotations/search/tags
- GET /annotations/export/markdown
- GET /annotations/export/json

**collections.md**:
- GET /collections/{id}/recommendations
- GET /collections/{id}/embedding

**search.md**:
- GET /search/three-way
- GET /search/compare

**quality.md**:
- POST /quality/evaluate-summary/{resource_id}
- GET /quality/summary-metrics/{resource_id}

**scholarly.md**:
- POST /scholarly/extract-metadata/{resource_id}
- GET /scholarly/metadata/{resource_id}
- GET /scholarly/equations/{resource_id}
- GET /scholarly/tables/{resource_id}

**graph.md**:
- POST /graph/embeddings/generate
- GET /graph/embeddings/{node_id}
- GET /graph/embeddings/{node_id}/similar
- POST /graph/discover
- GET /graph/hypotheses/{id}

**recommendations.md**:
- GET /users/{user_id}/profile
- GET /users/{user_id}/interactions
- POST /users/{user_id}/interactions

**taxonomy.md**:
- POST /taxonomy/classify/{resource_id}
- GET /taxonomy/predictions/{resource_id}
- POST /taxonomy/retrain
- GET /taxonomy/uncertain

**curation.md**:
- POST /curation/batch/review
- POST /curation/batch/tag
- POST /curation/batch/assign
- GET /curation/queue

### Module READMEs

Update each module README with:
- Complete feature list
- Service descriptions
- API endpoint summary
- Event emissions/subscriptions
- Configuration options
- Usage examples

### Architecture Documentation

Update `backend/docs/architecture/`:

**modules.md**:
- Add complete service descriptions
- Update module dependency graph
- Document event flows
- Add integration patterns

**events.md**:
- Add new event types
- Document event payloads
- Update event catalog
- Add event flow diagrams

**database.md**:
- Add new models (UserInteraction, CurationReview)
- Update Resource model fields
- Document indexes
- Add migration notes

### Developer Guides

Update `backend/docs/guides/`:

**workflows.md**:
- Add annotation workflow
- Add classification workflow
- Add curation workflow
- Add LBD workflow

**testing.md**:
- Add testing patterns for new services
- Document performance test setup
- Add integration test examples

## Success Criteria

Phase 16.7 is complete when:

1. **All Services Implemented**:
   - ✅ Annotation Service fully functional
   - ✅ Collection embeddings and recommendations working
   - ✅ Search services migrated and integrated
   - ✅ Summarization evaluator operational
   - ✅ Scholarly metadata extraction working
   - ✅ Graph embeddings and LBD functional
   - ✅ User profiles tracking interactions
   - ✅ ML classification operational
   - ✅ Curation workflows complete

2. **All Tests Passing**:
   - ✅ Unit tests >85% coverage
   - ✅ Integration tests for all endpoints
   - ✅ Performance tests meet targets
   - ✅ No regressions in existing features

3. **Documentation Complete**:
   - ✅ API docs updated
   - ✅ Module READMEs updated
   - ✅ Architecture docs updated
   - ✅ Developer guides updated

4. **Production Ready**:
   - ✅ All health checks passing
   - ✅ Monitoring configured
   - ✅ Alerts configured
   - ✅ Deployment tested
   - ✅ Rollback plan validated

5. **Feature Parity**:
   - ✅ Every feature from phases 6-12 specs exists
   - ✅ All API endpoints from specs implemented
   - ✅ All database models complete
   - ✅ All event handlers operational

