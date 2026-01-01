# Requirements Document: Phase 16.7 - Missing Features Implementation

## Introduction

Phase 16.7 completes the Neo Alexandria backend by implementing all missing features from phases 6-12 that were left incomplete during the vertical slice refactoring. This phase ensures every service, feature, and capability specified in the original design documents is fully implemented and integrated into the modular architecture. The work focuses on completing annotation systems, collection recommendations, advanced search capabilities, quality assessment, scholarly metadata extraction, graph intelligence, and ML classification.

## Glossary

- **Annotation System**: Complete subsystem for text highlighting, notes, semantic search, and export
- **Collection Service**: Full-featured collection management with embeddings and recommendations
- **Sparse Embedding Service**: BGE-M3 based sparse vector generation for keyword-focused search
- **Reranking Service**: ColBERT cross-encoder for search result refinement
- **Summarization Evaluator**: Multi-metric summary quality assessment (G-Eval, FineSurE, BERTScore)
- **Scholarly Service**: Academic metadata extraction including LaTeX, tables, and equations
- **Graph Embeddings Service**: Node2Vec and DeepWalk for graph-based representations
- **LBD Service**: Literature-Based Discovery for hypothesis generation
- **User Profile Service**: Interaction tracking and preference learning for recommendations
- **ML Classification Service**: Active learning and model training for taxonomy classification
- **Legacy Services**: Services currently in `app/services/` that need module integration

## Requirements

### Requirement 1: Complete Annotation Service Implementation

**User Story:** As a researcher, I want a fully functional annotation system so that I can highlight text, add notes, search semantically, and export my annotations.

#### Acceptance Criteria

1. THE Annotation Service SHALL implement complete CRUD operations for annotations with character offset validation
2. THE Annotation Service SHALL implement full-text search across notes and highlighted text with <100ms response time for 10,000 annotations
3. THE Annotation Service SHALL implement semantic search using annotation embeddings with similarity scoring
4. THE Annotation Service SHALL implement tag-based filtering supporting ANY and ALL tag matching modes
5. THE Annotation Service SHALL implement Markdown export with resource grouping and formatting
6. THE Annotation Service SHALL implement JSON export with complete metadata
7. THE Annotation Service SHALL extract and store 50-character context windows before and after highlights
8. THE Annotation Service SHALL generate embeddings asynchronously for annotation notes
9. THE Annotation Service SHALL support collection association via JSON array storage
10. THE Annotation Service SHALL integrate with search service to include annotation matches in global search

### Requirement 2: Complete Collection Service Features

**User Story:** As a researcher, I want collections to support aggregate embeddings and recommendations so that I can discover related resources and collections.

#### Acceptance Criteria

1. THE Collection Service SHALL compute aggregate embeddings as mean vectors of member resource embeddings
2. THE Collection Service SHALL recompute embeddings automatically when resources are added or removed
3. THE Collection Service SHALL normalize aggregate embeddings to unit length
4. THE Collection Service SHALL provide resource recommendations based on collection embedding similarity
5. THE Collection Service SHALL provide collection recommendations based on embedding similarity
6. THE Collection Service SHALL exclude already-included resources from recommendations
7. THE Collection Service SHALL validate hierarchical relationships to prevent circular references
8. THE Collection Service SHALL support batch resource operations for up to 100 resources
9. THE Collection Service SHALL complete embedding computation within 1 second for 1000 resources
10. THE Collection Service SHALL expose GET /collections/{id}/recommendations endpoint

### Requirement 3: Integrate Search Services into Search Module

**User Story:** As a developer, I want all search-related services consolidated in the search module so that the architecture follows the vertical slice pattern.

#### Acceptance Criteria

1. THE Search Module SHALL integrate SparseEmbeddingService from legacy services directory
2. THE Search Module SHALL integrate RerankingService from legacy services directory
3. THE Search Module SHALL integrate ReciprocalRankFusionService from legacy services directory
4. THE Search Module SHALL integrate HybridSearchMethods from legacy services directory
5. THE Search Module SHALL maintain all existing functionality during migration
6. THE Search Module SHALL update all imports to reference new module locations
7. THE Search Module SHALL remove legacy service files after successful migration
8. THE Search Module SHALL expose three-way hybrid search via unified SearchService
9. THE Search Module SHALL support query-adaptive weighting based on query characteristics
10. THE Search Module SHALL complete three-way hybrid search within 200ms (P95)

### Requirement 4: Implement Summarization Evaluator Service

**User Story:** As a content curator, I want advanced summary quality metrics so that I can identify high-quality and low-quality summaries systematically.

#### Acceptance Criteria

1. THE Summarization Evaluator SHALL implement G-Eval coherence metric using GPT-4 API
2. THE Summarization Evaluator SHALL implement G-Eval consistency metric using GPT-4 API
3. THE Summarization Evaluator SHALL implement G-Eval fluency metric using GPT-4 API
4. THE Summarization Evaluator SHALL implement G-Eval relevance metric using GPT-4 API
5. THE Summarization Evaluator SHALL implement FineSurE completeness metric
6. THE Summarization Evaluator SHALL implement FineSurE conciseness metric
7. THE Summarization Evaluator SHALL implement BERTScore F1 using microsoft/deberta-xlarge-mnli
8. THE Summarization Evaluator SHALL compute composite summary quality score with configurable weights
9. THE Summarization Evaluator SHALL store all metric scores in Resource model
10. THE Summarization Evaluator SHALL provide fallback scores when OpenAI API is unavailable

### Requirement 5: Complete Scholarly Metadata Service

**User Story:** As a researcher, I want comprehensive academic metadata extraction so that equations, tables, and citations are properly parsed and stored.

#### Acceptance Criteria

1. THE Scholarly Service SHALL parse LaTeX equations and convert to MathML or plain text
2. THE Scholarly Service SHALL extract tables from HTML and PDF content
3. THE Scholarly Service SHALL parse table structures including headers and data cells
4. THE Scholarly Service SHALL extract figure captions and references
5. THE Scholarly Service SHALL identify and extract author affiliations
6. THE Scholarly Service SHALL parse funding information and acknowledgments
7. THE Scholarly Service SHALL extract keywords and subject classifications
8. THE Scholarly Service SHALL store extracted metadata in structured JSON format
9. THE Scholarly Service SHALL emit metadata.extracted events for downstream processing
10. THE Scholarly Service SHALL complete extraction within 2 seconds per resource

### Requirement 6: Implement Graph Embeddings Service

**User Story:** As a researcher, I want graph-based embeddings so that I can discover resources through network relationships and structural patterns.

#### Acceptance Criteria

1. THE Graph Embeddings Service SHALL implement Node2Vec algorithm for graph embeddings
2. THE Graph Embeddings Service SHALL implement DeepWalk algorithm for graph embeddings
3. THE Graph Embeddings Service SHALL support configurable walk length and number of walks
4. THE Graph Embeddings Service SHALL support configurable embedding dimensions (default 128)
5. THE Graph Embeddings Service SHALL train embeddings on citation graph structure
6. THE Graph Embeddings Service SHALL store node embeddings in graph database or cache
7. THE Graph Embeddings Service SHALL provide similarity search using graph embeddings
8. THE Graph Embeddings Service SHALL support incremental updates when graph changes
9. THE Graph Embeddings Service SHALL complete embedding generation within 10 seconds for 1000 nodes
10. THE Graph Embeddings Service SHALL expose embeddings via GET /graph/embeddings/{node_id}

### Requirement 7: Implement Literature-Based Discovery Service

**User Story:** As a researcher, I want automated hypothesis discovery so that I can identify novel connections between concepts in the literature.

#### Acceptance Criteria

1. THE LBD Service SHALL implement ABC discovery pattern (A→B, B→C, infer A→C)
2. THE LBD Service SHALL identify bridging concepts between two target concepts
3. THE LBD Service SHALL rank hypotheses by support strength and novelty
4. THE LBD Service SHALL filter out already-known connections from results
5. THE LBD Service SHALL support time-slicing to discover historical vs recent connections
6. THE LBD Service SHALL provide evidence chains showing intermediate connections
7. THE LBD Service SHALL compute confidence scores for generated hypotheses
8. THE LBD Service SHALL limit hypothesis generation to top 50 candidates
9. THE LBD Service SHALL complete discovery within 5 seconds for typical queries
10. THE LBD Service SHALL expose POST /graph/discover endpoint for hypothesis generation

### Requirement 8: Complete User Profile Service

**User Story:** As a user, I want the system to learn my preferences so that recommendations improve over time based on my interactions.

#### Acceptance Criteria

1. THE User Profile Service SHALL track resource view events with timestamps
2. THE User Profile Service SHALL track annotation creation events
3. THE User Profile Service SHALL track collection membership events
4. THE User Profile Service SHALL track search query history
5. THE User Profile Service SHALL compute user interest vectors from interaction history
6. THE User Profile Service SHALL identify frequently accessed topics and tags
7. THE User Profile Service SHALL weight recent interactions more heavily than old ones
8. THE User Profile Service SHALL provide user profile data to recommendation service
9. THE User Profile Service SHALL support profile export for transparency
10. THE User Profile Service SHALL emit user.profile_updated events when profiles change

### Requirement 9: Implement ML Classification Service

**User Story:** As a system administrator, I want ML-based classification with active learning so that the taxonomy system improves accuracy over time.

#### Acceptance Criteria

1. THE ML Classification Service SHALL load pre-trained classification models from disk
2. THE ML Classification Service SHALL predict top-K taxonomy nodes for resources
3. THE ML Classification Service SHALL provide confidence scores for predictions
4. THE ML Classification Service SHALL support active learning by identifying uncertain predictions
5. THE ML Classification Service SHALL retrain models when sufficient new labeled data exists
6. THE ML Classification Service SHALL validate model performance on held-out test set
7. THE ML Classification Service SHALL store model metadata including version and accuracy
8. THE ML Classification Service SHALL support multiple classification models per taxonomy
9. THE ML Classification Service SHALL complete prediction within 500ms per resource
10. THE ML Classification Service SHALL expose POST /taxonomy/classify endpoint

### Requirement 10: Implement Classification Coordination Service

**User Story:** As a developer, I want a unified classification interface so that rule-based and ML-based classification work together seamlessly.

#### Acceptance Criteria

1. THE Classification Service SHALL coordinate between rule-based and ML-based classification
2. THE Classification Service SHALL merge predictions from multiple classifiers
3. THE Classification Service SHALL resolve conflicts using confidence scores
4. THE Classification Service SHALL apply business rules to override low-confidence predictions
5. THE Classification Service SHALL emit resource.classified events after classification
6. THE Classification Service SHALL support manual classification overrides
7. THE Classification Service SHALL track classification accuracy metrics
8. THE Classification Service SHALL provide classification explanations showing reasoning
9. THE Classification Service SHALL complete classification within 1 second per resource
10. THE Classification Service SHALL integrate with resource ingestion pipeline

### Requirement 11: Complete Curation Service Features

**User Story:** As a content curator, I want batch operations and workflow management so that I can efficiently review and approve content at scale.

#### Acceptance Criteria

1. THE Curation Service SHALL support batch quality review operations for multiple resources
2. THE Curation Service SHALL support batch approval and rejection workflows
3. THE Curation Service SHALL support batch tagging and metadata updates
4. THE Curation Service SHALL track review status (pending, approved, rejected)
5. THE Curation Service SHALL assign resources to curators for review
6. THE Curation Service SHALL provide review queue filtering by quality score
7. THE Curation Service SHALL emit curation.reviewed events after review actions
8. THE Curation Service SHALL support review comments and feedback
9. THE Curation Service SHALL complete batch operations within 5 seconds for 100 resources
10. THE Curation Service SHALL expose POST /curation/batch endpoints

### Requirement 12: Performance and Integration Requirements

**User Story:** As a system architect, I want all services to meet performance targets and integrate properly with the event-driven architecture.

#### Acceptance Criteria

1. ALL services SHALL emit appropriate events for state changes
2. ALL services SHALL subscribe to relevant events from other modules
3. ALL services SHALL complete operations within specified performance targets
4. ALL services SHALL handle errors gracefully with descriptive messages
5. ALL services SHALL log operations for debugging and monitoring
6. ALL services SHALL use database transactions for data consistency
7. ALL services SHALL support async operations where appropriate
8. ALL services SHALL follow the vertical slice module pattern
9. ALL services SHALL have comprehensive unit and integration tests
10. ALL services SHALL update API documentation with new endpoints

### Requirement 13: Database Schema Completeness

**User Story:** As a developer, I want all database models to support the full feature set so that no data is lost or unavailable.

#### Acceptance Criteria

1. THE Annotation model SHALL include all fields from Phase 7.5 spec
2. THE Collection model SHALL include embedding field for aggregate embeddings
3. THE Resource model SHALL include sparse_embedding field for Phase 8
4. THE Resource model SHALL include summary quality metric fields for Phase 9
5. THE Resource model SHALL include scholarly metadata fields for extracted content
6. THE Graph models SHALL support node embeddings storage
7. THE User interaction models SHALL support profile tracking
8. THE Taxonomy models SHALL support ML model metadata
9. ALL models SHALL have appropriate indexes for query performance
10. ALL models SHALL have proper foreign key constraints and cascades

### Requirement 14: API Endpoint Completeness

**User Story:** As a frontend developer, I want all planned API endpoints to exist so that I can build complete user interfaces.

#### Acceptance Criteria

1. THE Annotations module SHALL expose all CRUD and search endpoints from Phase 7.5
2. THE Collections module SHALL expose recommendation endpoints from Phase 7
3. THE Search module SHALL expose three-way hybrid search endpoint from Phase 8
4. THE Quality module SHALL expose summary evaluation endpoints from Phase 9
5. THE Scholarly module SHALL expose metadata extraction endpoints
6. THE Graph module SHALL expose discovery and embedding endpoints from Phase 10
7. THE Recommendations module SHALL expose profile-based endpoints from Phase 11
8. THE Taxonomy module SHALL expose classification endpoints from Phase 8.5
9. THE Curation module SHALL expose batch operation endpoints
10. ALL endpoints SHALL return consistent error responses and status codes

### Requirement 15: Testing and Documentation Requirements

**User Story:** As a developer, I want comprehensive tests and documentation so that I can maintain and extend the system confidently.

#### Acceptance Criteria

1. EACH service SHALL have unit tests covering all public methods
2. EACH service SHALL have integration tests covering API endpoints
3. EACH service SHALL have performance tests validating response times
4. EACH module SHALL have updated README.md documenting features
5. THE API documentation SHALL include all new endpoints with examples
6. THE architecture documentation SHALL reflect completed features
7. THE test suite SHALL achieve >85% code coverage for new services
8. THE documentation SHALL include migration notes for legacy service removal
9. THE documentation SHALL include event catalog updates
10. THE documentation SHALL include troubleshooting guides for new features

