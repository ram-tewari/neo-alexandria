# Neo Alexandria 2.0 - Complete Backend Features for Frontend Integration

## 📋 Overview
This document lists EVERY backend feature that needs to be integrated into the frontend, organized by functional area.

---

## 1. 📚 RESOURCE MANAGEMENT

### Core Resource Operations
- **Create Resource** - `POST /resources`
  - Ingest content from URLs
  - Async processing with status tracking
  - Support for HTML, PDF, plain text
  
- **List Resources** - `GET /resources`
  - Pagination (limit, offset)
  - Filtering by classification, language, quality, subjects
  - Sorting by various fields
  - Search query parameter
  
- **Get Resource Details** - `GET /resources/{id}`
  - Full resource metadata
  - Dublin Core fields
  - Quality scores
  - Classification
  - Embeddings info
  
- **Update Resource** - `PUT /resources/{id}`
  - Edit metadata
  - Update classification
  - Modify subjects/tags
  
- **Delete Resource** - `DELETE /resources/{id}`
  - Cascade deletion
  - Remove from collections
  
- **Check Ingestion Status** - `GET /resources/{id}/status`
  - Processing status
  - Error messages
  - Completion timestamps

### Resource Classification
- **Manual Classification Override** - `PUT /resources/{id}/classify`
  - Override auto-classification
  - Set custom classification code

### Resource Quality
- **Get Quality Details** - `GET /resources/{id}/quality-details`
  - Detailed quality breakdown
  - Dimension scores (accuracy, completeness, consistency, timeliness, relevance)
  - Quality history
  - Outlier status

---

## 2. 🔍 SEARCH & DISCOVERY

### Search Methods
- **Basic Search** - `POST /search`
  - Hybrid keyword + semantic search
  - Configurable weighting
  - Faceted filtering
  - Pagination
  
- **Three-Way Hybrid Search** - `GET /search/three-way-hybrid`
  - FTS5 + Dense vectors + Sparse vectors
  - Reciprocal Rank Fusion (RRF)
  - Optional ColBERT reranking
  - Adaptive weighting
  
- **Compare Search Methods** - `GET /search/compare-methods`
  - Side-by-side comparison
  - FTS5 vs Dense vs Sparse vs Hybrid
  - Performance metrics
  
- **Evaluate Search Quality** - `POST /search/evaluate`
  - nDCG, Recall, Precision, MRR
  - Relevance judgments
  - Method comparison

### Sparse Embeddings
- **Generate Sparse Embeddings** - `POST /admin/sparse-embeddings/generate`
  - Batch processing
  - Progress tracking
  - BGE-M3 model

---

## 3. 🎯 RECOMMENDATIONS

### Personalized Recommendations
- **Get Recommendations** - `GET /recommendations` or `GET /api/recommendations`
  - Content-based filtering
  - Fresh content discovery
  - Explainable reasoning
  - Configurable limit
  
- **Track User Interactions** - `POST /api/interactions`
  - View, click, save, share events
  - Implicit feedback
  - Engagement tracking
  
- **Submit Feedback** - `POST /api/recommendations/feedback`
  - Explicit ratings
  - Thumbs up/down
  - Improve recommendations
  
- **Get Performance Metrics** - `GET /api/recommendations/metrics`
  - Click-through rate
  - Conversion rate
  - Diversity metrics

### User Profile
- **Get User Profile** - `GET /api/profile`
  - Interests
  - Interaction history
  - Preferences
  
- **Update Profile** - `PUT /api/profile`
  - Modify interests
  - Set preferences
  - Update settings

---

## 4. 📊 COLLECTIONS

### Collection Management
- **Create Collection** - `POST /collections`
  - Name, description
  - Visibility (private/shared/public)
  - Parent collection (hierarchical)
  
- **List Collections** - `GET /collections`
  - Filter by owner
  - Filter by visibility
  - Pagination
  - Include resource counts
  
- **Get Collection Details** - `GET /collections/{id}`
  - Metadata
  - Member resources
  - Subcollections
  - Aggregate embedding
  
- **Update Collection** - `PUT /collections/{id}`
  - Edit metadata
  - Change visibility
  - Move to different parent
  
- **Delete Collection** - `DELETE /collections/{id}`
  - Cascade delete subcollections
  - Remove resource associations

### Collection Resources
- **Add/Remove Resources** - `PUT /collections/{id}/resources`
  - Batch operations (up to 100)
  - Add or remove mode
  - Automatic embedding update
  
- **Get Collection Recommendations** - `GET /collections/{id}/recommendations`
  - Similar resources
  - Similar collections
  - Semantic similarity

---

## 5. ✍️ ANNOTATIONS & ACTIVE READING

### Annotation Management
- **Create Annotation** - `POST /resources/{resource_id}/annotations`
  - Character-offset highlighting
  - Rich notes
  - Tags and colors
  - Context preservation
  
- **List Resource Annotations** - `GET /resources/{resource_id}/annotations`
  - All annotations for a resource
  - Sorted by position
  
- **List User Annotations** - `GET /annotations`
  - All user annotations
  - Pagination
  - Filter by resource, collection, tags
  
- **Get Annotation** - `GET /annotations/{id}`
  - Full annotation details
  
- **Update Annotation** - `PUT /annotations/{id}`
  - Edit note
  - Modify tags
  - Change color
  
- **Delete Annotation** - `DELETE /annotations/{id}`
  - Remove annotation

### Annotation Search
- **Full-Text Search** - `GET /annotations/search/fulltext`
  - Search notes and highlighted text
  - <100ms for 10K annotations
  
- **Semantic Search** - `GET /annotations/search/semantic`
  - Conceptual similarity
  - Cosine similarity scores
  
- **Tag Search** - `GET /annotations/search/tags`
  - Filter by tags
  - Tag-based organization

### Annotation Export
- **Export to Markdown** - `GET /annotations/export/markdown`
  - Formatted markdown
  - Resource grouping
  - Include metadata
  
- **Export to JSON** - `GET /annotations/export/json`
  - Structured data
  - Full annotation details
  - Integration-ready

---

## 6. 🔗 CITATION NETWORK

### Citation Management
- **Get Resource Citations** - `GET /citations/resources/{id}/citations`
  - Inbound citations (who cites this)
  - Outbound citations (what this cites)
  - Citation types (reference, dataset, code, general)
  
- **Get Citation Graph** - `GET /citations/graph/citations`
  - Network visualization data
  - Configurable depth
  - Node and edge data
  
- **Extract Citations** - `POST /citations/resources/{id}/citations/extract`
  - Trigger extraction
  - HTML, PDF, Markdown support
  - Async processing
  
- **Resolve Internal Citations** - `POST /citations/resolve`
  - Link citations to existing resources
  - Match by URL, DOI, title
  
- **Compute Importance** - `POST /citations/importance/compute`
  - PageRank scoring
  - Citation network analysis
  - Importance metrics

---

## 7. 🕸️ KNOWLEDGE GRAPH

### Graph Exploration
- **Get Resource Neighbors** - `GET /graph/resource/{id}/neighbors`
  - Mind-map visualization
  - Related resources
  - Hybrid scoring (vector + tags + classification)
  - Configurable limit
  
- **Get Graph Overview** - `GET /graph/overview`
  - System-wide relationships
  - Top connections
  - Network statistics
  - Configurable thresholds

---

## 8. 🔬 DISCOVERY & HYPOTHESES

### Open Discovery
- **Open Discovery** - `GET /discovery/open`
  - Find hidden connections
  - A-B-C pattern discovery
  - Plausibility scoring
  
### Closed Discovery
- **Closed Discovery** - `POST /discovery/closed`
  - Verify A-C connections
  - Find intermediate resources (B)
  - Path analysis

### Graph Discovery
- **Get Discovery Neighbors** - `GET /discovery/graph/resources/{id}/neighbors`
  - Discovery-focused neighbors
  - Hypothesis generation
  
### Hypothesis Management
- **List Hypotheses** - `GET /discovery/hypotheses`
  - All discovered hypotheses
  - Filter by type, plausibility
  - Pagination
  
- **Validate Hypothesis** - `POST /discovery/hypotheses/{id}/validate`
  - User validation
  - Add notes
  - Track validation status

---

## 9. 🏷️ TAXONOMY & CLASSIFICATION

### Taxonomy Management
- **Get Taxonomy Tree** - `GET /taxonomy/tree`
  - Hierarchical structure
  - Root nodes
  - Configurable depth
  - Subtree support
  
- **Create Taxonomy Node** - `POST /taxonomy/nodes`
  - Name, description
  - Parent node
  - Keywords
  - Allow resources flag
  
- **Get Node Details** - `GET /taxonomy/nodes/{id}`
  - Node metadata
  - Resource count
  - Descendant count
  
- **Update Node** - `PUT /taxonomy/nodes/{id}`
  - Edit metadata
  - Update keywords
  
- **Delete Node** - `DELETE /taxonomy/nodes/{id}`
  - Cascade option
  - Reassign resources
  
- **Move Node** - `POST /taxonomy/nodes/{id}/move`
  - Change parent
  - Reorganize hierarchy
  
- **Get Ancestors** - `GET /taxonomy/nodes/{id}/ancestors`
  - Breadcrumb trail
  - Path to root
  
- **Get Descendants** - `GET /taxonomy/nodes/{id}/descendants`
  - All child nodes
  - Recursive

### ML Classification
- **Classify Resource** - `POST /taxonomy/classify/{resource_id}`
  - Auto-classify using ML
  - Multi-label support
  - Confidence scores
  
- **Get Uncertain Predictions** - `GET /taxonomy/active-learning/uncertain`
  - Active learning queue
  - Low-confidence predictions
  - Human review needed
  
- **Submit Feedback** - `POST /taxonomy/active-learning/feedback`
  - Correct classifications
  - Improve model
  - Continuous learning
  
- **Train Model** - `POST /taxonomy/train`
  - Fine-tune classifier
  - Labeled + unlabeled data
  - Semi-supervised learning
  - Model versioning

### Classification Tree
- **Get Classification Tree** - `GET /classification/tree` or `GET /authority/classification/tree`
  - UDC-inspired codes
  - Hierarchical structure
  - Top-level categories

---

## 10. 🎨 AUTHORITY CONTROL

### Subject Management
- **Subject Suggestions** - `GET /authority/subjects/suggest`
  - Autocomplete
  - Canonical forms
  - Usage frequency
  - Variant matching

---

## 11. ✅ QUALITY MANAGEMENT

### Quality Analysis
- **Get Quality Details** - `GET /resources/{id}/quality-details`
  - Dimension breakdown
  - Historical trends
  - Outlier detection
  
- **Recalculate Quality** - `POST /quality/recalculate`
  - Batch recalculation
  - Specific resources or all
  - Async processing
  
- **Get Outliers** - `GET /quality/outliers`
  - Low-quality resources
  - Anomaly detection
  - Pagination
  
- **Get Degradation Report** - `GET /quality/degradation`
  - Quality trends over time
  - Degrading resources
  - Time window analysis
  
- **Evaluate Summary** - `POST /summaries/{resource_id}/evaluate`
  - Summary quality metrics
  - Coherence, consistency, fluency, relevance
  
- **Get Quality Distribution** - `GET /quality/distribution`
  - Histogram data
  - Score distribution
  - Statistical analysis
  
- **Get Quality Trends** - `GET /quality/trends`
  - Time-series data
  - Granularity (daily/weekly/monthly)
  - Trend analysis
  
- **Get Dimension Averages** - `GET /quality/dimensions`
  - Average scores per dimension
  - System-wide metrics
  
- **Get Review Queue** - `GET /quality/review-queue`
  - Resources needing review
  - Priority sorting
  - Pagination

---

## 12. 🛠️ CURATION

### Curation Tools
- **Get Review Queue** - `GET /curation/review-queue`
  - Low-quality items
  - Threshold filtering
  - Pagination
  
- **Batch Update** - `POST /curation/batch-update`
  - Update multiple resources
  - Bulk operations
  - Field updates
  
- **Get Low Quality Resources** - `GET /curation/low-quality`
  - Filter by threshold
  - Curation candidates
  
- **Bulk Quality Check** - `POST /curation/bulk-quality-check`
  - Recalculate quality for multiple resources
  - Batch processing
  
- **Get Quality Analysis** - `GET /curation/quality-analysis/{resource_id}`
  - Detailed quality report
  - Improvement suggestions

---

## 13. 📈 MONITORING & METRICS

### Performance Monitoring
- **Get Performance Metrics** - `GET /api/monitoring/performance`
  - Response times
  - Throughput
  - Error rates
  
- **Get Recommendation Quality** - `GET /api/monitoring/recommendation-quality`
  - CTR, conversion rate
  - Diversity metrics
  - Time window analysis
  
- **Get User Engagement** - `GET /api/monitoring/user-engagement`
  - Active users
  - Interaction counts
  - Engagement trends
  
- **Get Model Health** - `GET /api/monitoring/model-health`
  - ML model status
  - Prediction counts
  - Error rates
  
- **ML Health Check** - `GET /api/monitoring/health/ml`
  - Model availability
  - Performance metrics
  - Resource usage

### Database Monitoring
- **Get Database Metrics** - `GET /api/monitoring/database`
  - Connection pool status
  - Query performance
  - Table sizes
  
- **Get Pool Status** - `GET /api/monitoring/db/pool`
  - Active connections
  - Pool utilization
  - Wait times

### Event Monitoring
- **Get Event History** - `GET /api/monitoring/events/history`
  - Recent events
  - Event types
  - Timestamps

### Cache Monitoring
- **Get Cache Stats** - `GET /api/monitoring/cache/stats`
  - Hit/miss rates
  - Memory usage
  - Key counts

### Worker Monitoring
- **Get Worker Status** - `GET /api/monitoring/workers/status`
  - Celery workers
  - Task queues
  - Processing status

### Health Checks
- **Health Check** - `GET /api/monitoring/health`
  - Overall system health
  - Component status
  - Uptime

### System Metrics
- **Get Metrics** - `GET /metrics`
  - Prometheus-compatible
  - System-wide metrics
  - Time-series data

---

## 14. 📖 SCHOLARLY FEATURES

### Scholarly Metadata
- All scholarly fields are part of resource model:
  - Authors, affiliations
  - DOI, PMID, arXiv ID, ISBN
  - Journal, conference
  - Volume, issue, pages
  - Publication year
  - Funding sources
  - Acknowledgments
  - Equation/table/figure counts
  - Extracted equations, tables, figures
  - Metadata completeness score
  - Extraction confidence
  - Manual review flag

---

## 🎯 PRIORITY LEVELS FOR FRONTEND INTEGRATION

### 🔴 CRITICAL (Must Have - Phase 1)
1. Resource Management (CRUD)
2. Basic Search
3. Collections (CRUD)
4. Resource List/Grid View
5. Resource Detail View

### 🟡 HIGH PRIORITY (Phase 2)
1. Annotations & Active Reading
2. Knowledge Graph Visualization
3. Three-Way Hybrid Search
4. Taxonomy Browser
5. Quality Dashboard

### 🟢 MEDIUM PRIORITY (Phase 3)
1. Citation Network Visualization
2. Recommendations Feed
3. Discovery & Hypotheses
4. Curation Tools
5. User Profile Management

### 🔵 LOW PRIORITY (Phase 4)
1. Advanced Monitoring Dashboards
2. ML Model Training UI
3. Active Learning Interface
4. Bulk Operations UI
5. Export/Import Tools

---

## 📝 NOTES

### Authentication
- Currently no authentication required
- Future: API key authentication
- Future: Rate limiting

### Async Operations
- Many operations are async (Celery)
- Status endpoints for tracking
- Webhook support planned

### Real-Time Updates
- WebSocket support planned
- Server-sent events for status
- Live search results

### Batch Operations
- Most endpoints support batch operations
- Pagination for large datasets
- Configurable limits

### Export Formats
- JSON (all endpoints)
- Markdown (annotations)
- CSV (planned)
- PDF (planned)

---

## 🔗 API Documentation
- Interactive Docs: http://127.0.0.1:8000/docs
- OpenAPI Spec: http://127.0.0.1:8000/openapi.json
- ReDoc: http://127.0.0.1:8000/redoc (if enabled)

---

**Total Endpoints**: 75+
**Total Features**: 100+
**Backend Status**: ✅ Fully Operational with PostgreSQL
