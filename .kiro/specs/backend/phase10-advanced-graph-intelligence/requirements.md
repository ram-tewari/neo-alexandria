# Requirements Document - Phase 10: Advanced Graph Intelligence & Literature-Based Discovery

## Introduction

Phase 10 transforms Neo Alexandria's basic knowledge graph into an advanced graph intelligence system. This phase implements multi-hop neighbor discovery with intelligent filtering, Graph2Vec for learning structural embeddings, fusion embeddings combining content and topology, HNSW indexing for fast graph neighbor queries, and Literature-Based Discovery (LBD) implementing the ABC paradigm for hypothesis generation. The system enables researchers to discover implicit connections, identify research gaps, and find serendipitous insights through graph-guided exploration.

This phase builds upon:
- Phase 5: Basic knowledge graph with hybrid scoring
- Phase 6: Citation network extraction and PageRank
- Phase 4: Content embeddings for semantic similarity
- Phase 8.5: Taxonomy classification
- Phase 9: Quality assessment

## Glossary

- **Graph Intelligence System**: The complete system encompassing multi-layer graphs, embeddings, and discovery algorithms
- **Multi-Layer Graph**: A graph structure supporting multiple edge types (citation, co-authorship, subject similarity, temporal, content similarity)
- **Graph2Vec**: An algorithm that learns structural embeddings by treating subgraphs as documents
- **Fusion Embedding**: A combined embedding vector merging content-based and structure-based representations
- **HNSW**: Hierarchical Navigable Small World index for fast approximate nearest neighbor search
- **LBD**: Literature-Based Discovery, a methodology for generating research hypotheses
- **ABC Paradigm**: A discovery pattern where A→B and B→C relationships suggest a potential A→C hypothesis
- **Open Discovery**: Starting from concept A, discovering related concepts C through intermediate B
- **Closed Discovery**: Connecting two known concepts A and C by finding intermediate B
- **Ego Graph**: A subgraph containing a node and its neighbors within a specified radius
- **Plausibility Score**: A metric (0.0-1.0) indicating the likelihood that a discovered hypothesis is valid
- **Path Strength**: The product of edge weights along a multi-hop path
- **Structural Embedding**: A vector representation capturing graph topology rather than content
- **Weisfeiler-Lehman**: A graph labeling algorithm used in Graph2Vec for capturing structural patterns

## Requirements

### Requirement 1: Multi-Layer Graph Model

**User Story:** As a researcher, I want the system to model multiple types of relationships between resources, so that I can explore connections through different lenses (citations, co-authorship, topics, time periods).

#### Acceptance Criteria

1. WHEN the system stores graph relationships, THE Graph Intelligence System SHALL support five distinct edge types: citation, co_authorship, subject_similarity, temporal, and content_similarity
2. WHEN an edge is created, THE Graph Intelligence System SHALL store edge weight as a float value between 0.0 and 1.0
3. WHEN an edge is created, THE Graph Intelligence System SHALL record edge metadata including edge type, weight, creation source, and confidence score
4. WHEN querying edges, THE Graph Intelligence System SHALL support filtering by edge type
5. THE Graph Intelligence System SHALL enforce uniqueness constraint on (source_id, target_id, edge_type) tuples to prevent duplicate edges

### Requirement 2: Graph Embeddings Storage

**User Story:** As a system administrator, I want graph-based embeddings stored separately from content embeddings, so that I can manage and update them independently based on graph structure changes.

#### Acceptance Criteria

1. WHEN storing graph embeddings, THE Graph Intelligence System SHALL maintain separate storage for structural embeddings and fusion embeddings
2. WHEN a graph embedding is created, THE Graph Intelligence System SHALL record the embedding method (graph2vec, node2vec, or fusion)
3. WHEN a graph embedding is created, THE Graph Intelligence System SHALL record the embedding version for tracking purposes
4. THE Graph Intelligence System SHALL associate each graph embedding with exactly one resource through a foreign key relationship
5. WHEN updating graph structure, THE Graph Intelligence System SHALL preserve existing embeddings until explicitly recomputed

### Requirement 3: Discovery Hypothesis Storage

**User Story:** As a researcher, I want the system to store discovered hypotheses with supporting evidence, so that I can review, validate, and track potential research connections over time.

#### Acceptance Criteria

1. WHEN a hypothesis is discovered, THE Graph Intelligence System SHALL store the A resource (starting concept), C resource (target concept), and B resources (intermediates) as foreign key references
2. WHEN a hypothesis is created, THE Graph Intelligence System SHALL compute and store a plausibility score between 0.0 and 1.0
3. WHEN a hypothesis is created, THE Graph Intelligence System SHALL record hypothesis type as either "open" or "closed"
4. WHEN a hypothesis is created, THE Graph Intelligence System SHALL store supporting evidence including path strength, path length, and common neighbor count
5. WHEN a user validates a hypothesis, THE Graph Intelligence System SHALL record validation status and optional validation notes

### Requirement 4: Multi-Layer Graph Construction

**User Story:** As a researcher, I want the system to automatically build a multi-layer graph from existing data, so that I can explore relationships without manual graph construction.

#### Acceptance Criteria

1. WHEN building the graph, THE Graph Intelligence System SHALL create citation edges from all Citation records with resolved target resources
2. WHEN building the graph, THE Graph Intelligence System SHALL create co-authorship edges between resources sharing at least one author
3. WHEN building the graph, THE Graph Intelligence System SHALL create subject similarity edges between resources sharing taxonomy classifications
4. WHEN building the graph, THE Graph Intelligence System SHALL create temporal edges between resources published in the same year
5. WHEN the graph contains more than 1000 nodes, THE Graph Intelligence System SHALL cache the constructed graph in memory with timestamp tracking

### Requirement 5: Two-Hop Neighbor Discovery

**User Story:** As a researcher, I want to discover resources connected through intermediate nodes, so that I can find relevant but non-obvious connections in the literature.

#### Acceptance Criteria

1. WHEN querying neighbors with hops parameter set to 2, THE Graph Intelligence System SHALL traverse two levels of graph connections from the source resource
2. WHEN discovering multi-hop neighbors, THE Graph Intelligence System SHALL compute path strength as the product of edge weights along the path
3. WHEN ranking multi-hop neighbors, THE Graph Intelligence System SHALL combine path strength (50% weight), resource quality (30% weight), and novelty (20% weight)
4. WHEN filtering neighbors, THE Graph Intelligence System SHALL support minimum weight thresholds to exclude weak connections
5. WHEN returning neighbor results, THE Graph Intelligence System SHALL include path information showing intermediate nodes for 2-hop connections

### Requirement 6: Graph2Vec Structural Embeddings

**User Story:** As a data scientist, I want the system to learn structural embeddings that capture graph topology, so that I can find resources with similar positions in the knowledge network.

#### Acceptance Criteria

1. WHEN computing Graph2Vec embeddings, THE Graph Intelligence System SHALL extract ego graphs with radius 2 for each resource node
2. WHEN running Graph2Vec, THE Graph Intelligence System SHALL apply Weisfeiler-Lehman graph labeling for 2 iterations
3. WHEN generating embeddings, THE Graph Intelligence System SHALL produce 128-dimensional vectors by default
4. WHEN Graph2Vec computation completes, THE Graph Intelligence System SHALL store structural embeddings in the graph_embeddings table
5. WHEN graph structure changes significantly, THE Graph Intelligence System SHALL support recomputation of structural embeddings

### Requirement 7: Fusion Embeddings

**User Story:** As a researcher, I want embeddings that combine content and structure, so that similarity searches consider both what resources say and how they connect.

#### Acceptance Criteria

1. WHEN computing fusion embeddings, THE Graph Intelligence System SHALL combine content embeddings and structural embeddings using a weighted formula
2. WHEN combining embeddings, THE Graph Intelligence System SHALL apply alpha weight of 0.5 by default for equal contribution
3. WHEN dimension mismatch occurs, THE Graph Intelligence System SHALL truncate both vectors to the minimum dimension
4. WHEN fusion embedding is computed, THE Graph Intelligence System SHALL normalize the result vector to unit length
5. THE Graph Intelligence System SHALL store fusion embeddings separately from content and structural embeddings

### Requirement 8: HNSW Indexing

**User Story:** As a system user, I want fast similarity searches on large graphs, so that neighbor queries complete in under 100 milliseconds even with 10,000+ nodes.

#### Acceptance Criteria

1. WHEN building HNSW index, THE Graph Intelligence System SHALL index fusion embeddings for all resources with graph embeddings
2. WHEN performing k-NN queries, THE Graph Intelligence System SHALL return results in under 100 milliseconds for graphs with 10,000 nodes
3. WHEN adding new embeddings, THE Graph Intelligence System SHALL support incremental index updates without full rebuild
4. WHEN querying the index, THE Graph Intelligence System SHALL support configurable k parameter for number of nearest neighbors
5. THE Graph Intelligence System SHALL store HNSW index identifiers in the graph_embeddings table for reference

### Requirement 9: Open Discovery

**User Story:** As a researcher, I want to start from a known concept and discover related concepts I haven't considered, so that I can identify new research directions.

#### Acceptance Criteria

1. WHEN performing open discovery from resource A, THE Graph Intelligence System SHALL identify intermediate resources B that connect A to potential targets C
2. WHEN generating open discovery hypotheses, THE Graph Intelligence System SHALL rank candidates by plausibility score combining path strength and semantic similarity
3. WHEN open discovery completes, THE Graph Intelligence System SHALL return at least 10 hypothesis candidates if sufficient graph connectivity exists
4. WHEN computing plausibility, THE Graph Intelligence System SHALL consider path strength (40% weight), common neighbors (30% weight), and semantic similarity (30% weight)
5. THE Graph Intelligence System SHALL store open discovery hypotheses with hypothesis_type set to "open"

### Requirement 10: Closed Discovery

**User Story:** As a researcher, I want to connect two known concepts through intermediate literature, so that I can understand how disparate ideas might relate.

#### Acceptance Criteria

1. WHEN performing closed discovery between resources A and C, THE Graph Intelligence System SHALL find all intermediate resources B where paths A→B→C exist
2. WHEN multiple paths exist, THE Graph Intelligence System SHALL rank paths by combined path strength
3. WHEN no 2-hop paths exist, THE Graph Intelligence System SHALL attempt 3-hop discovery with reduced confidence
4. WHEN closed discovery completes, THE Graph Intelligence System SHALL return paths ordered by plausibility score
5. THE Graph Intelligence System SHALL store closed discovery hypotheses with hypothesis_type set to "closed"

### Requirement 11: Hypothesis Plausibility Scoring

**User Story:** As a researcher, I want hypotheses ranked by plausibility, so that I can focus on the most promising connections first.

#### Acceptance Criteria

1. WHEN scoring a hypothesis, THE Graph Intelligence System SHALL compute path strength as the product of all edge weights in the path
2. WHEN scoring a hypothesis, THE Graph Intelligence System SHALL count common neighbors between A and C resources
3. WHEN computing plausibility, THE Graph Intelligence System SHALL normalize the score to range 0.0 to 1.0
4. WHEN path length exceeds 2 hops, THE Graph Intelligence System SHALL apply a penalty factor of 0.5 per additional hop
5. THE Graph Intelligence System SHALL store plausibility scores with each hypothesis record

### Requirement 12: Discovery API Endpoints

**User Story:** As a frontend developer, I want REST API endpoints for discovery operations, so that I can integrate graph intelligence features into the user interface.

#### Acceptance Criteria

1. THE Graph Intelligence System SHALL provide GET /discovery/open endpoint accepting resource_id and returning open discovery hypotheses
2. THE Graph Intelligence System SHALL provide POST /discovery/closed endpoint accepting source_id and target_id and returning connection paths
3. THE Graph Intelligence System SHALL provide GET /graph/resources/{id}/neighbors endpoint with hops parameter supporting values 1 or 2
4. THE Graph Intelligence System SHALL provide GET /discovery/hypotheses endpoint returning paginated hypothesis list with filtering by type
5. THE Graph Intelligence System SHALL provide POST /discovery/hypotheses/{id}/validate endpoint accepting validation status and notes

### Requirement 13: Hypothesis Validation

**User Story:** As a researcher, I want to mark hypotheses as validated or rejected, so that the system learns from human feedback and improves future suggestions.

#### Acceptance Criteria

1. WHEN a user validates a hypothesis, THE Graph Intelligence System SHALL update the is_validated field to true or false
2. WHEN validation occurs, THE Graph Intelligence System SHALL store optional validation notes provided by the user
3. WHEN retrieving hypotheses, THE Graph Intelligence System SHALL support filtering by validation status
4. WHEN a hypothesis is validated as true, THE Graph Intelligence System SHALL increase edge weights along the discovered path by 10%
5. THE Graph Intelligence System SHALL record the user_id of the person who performed validation

### Requirement 14: Performance Optimization

**User Story:** As a system administrator, I want graph operations to complete quickly, so that researchers experience responsive interactions even with large knowledge bases.

#### Acceptance Criteria

1. WHEN performing 2-hop neighbor discovery, THE Graph Intelligence System SHALL complete queries in under 500 milliseconds for graphs with 5,000 nodes
2. WHEN building multi-layer graph, THE Graph Intelligence System SHALL complete construction in under 30 seconds for 10,000 resources
3. WHEN computing Graph2Vec embeddings, THE Graph Intelligence System SHALL process at least 100 nodes per minute
4. WHEN performing HNSW k-NN queries, THE Graph Intelligence System SHALL return results in under 100 milliseconds
5. THE Graph Intelligence System SHALL cache frequently accessed graph structures in memory with automatic invalidation on updates

### Requirement 15: Integration with Recommendations

**User Story:** As a researcher, I want recommendation algorithms to leverage graph intelligence, so that I receive more diverse and serendipitous suggestions.

#### Acceptance Criteria

1. WHEN generating recommendations, THE Graph Intelligence System SHALL include 2-hop neighbors as candidate resources
2. WHEN ranking recommendations, THE Graph Intelligence System SHALL use fusion embeddings for similarity computation
3. WHEN recommendations include graph-based candidates, THE Graph Intelligence System SHALL indicate the connection path in the response
4. WHEN LBD hypotheses exist for a resource, THE Graph Intelligence System SHALL include hypothesis-based recommendations
5. THE Graph Intelligence System SHALL weight graph-based recommendations at 30% and content-based recommendations at 70% in the final ranking

### Requirement 16: Graph Visualization Enhancement

**User Story:** As a researcher, I want to visualize multi-layer graphs with different edge types, so that I can understand the nature of connections between resources.

#### Acceptance Criteria

1. WHEN rendering graph visualization, THE Graph Intelligence System SHALL use distinct colors for each edge type
2. WHEN displaying 2-hop neighbors, THE Graph Intelligence System SHALL highlight intermediate nodes with a different visual style
3. WHEN showing hypothesis paths, THE Graph Intelligence System SHALL render the A→B→C path with emphasized edges
4. WHEN graph contains more than 50 nodes, THE Graph Intelligence System SHALL provide filtering controls for edge types
5. THE Graph Intelligence System SHALL display edge weights as line thickness in the visualization

### Requirement 17: Database Migration

**User Story:** As a system administrator, I want database schema changes applied safely, so that existing data remains intact while new features are enabled.

#### Acceptance Criteria

1. THE Graph Intelligence System SHALL provide an Alembic migration script creating the graph_edges table with all required fields and indexes
2. THE Graph Intelligence System SHALL provide an Alembic migration script creating the graph_embeddings table with foreign key to resources
3. THE Graph Intelligence System SHALL provide an Alembic migration script creating the discovery_hypotheses table with ABC relationship fields
4. WHEN migration is applied, THE Graph Intelligence System SHALL create composite index on (source_id, target_id, edge_type) with unique constraint
5. WHEN migration is reversed, THE Graph Intelligence System SHALL cleanly drop all Phase 10 tables without affecting existing data

### Requirement 18: Comprehensive Testing

**User Story:** As a developer, I want comprehensive test coverage for graph intelligence features, so that I can confidently deploy and maintain the system.

#### Acceptance Criteria

1. THE Graph Intelligence System SHALL provide unit tests for multi-layer graph construction covering all five edge types
2. THE Graph Intelligence System SHALL provide unit tests for 2-hop neighbor discovery with various filtering scenarios
3. THE Graph Intelligence System SHALL provide unit tests for Graph2Vec embedding generation and fusion computation
4. THE Graph Intelligence System SHALL provide integration tests for LBD hypothesis generation in both open and closed modes
5. THE Graph Intelligence System SHALL provide API endpoint tests for all discovery endpoints with success and error cases
