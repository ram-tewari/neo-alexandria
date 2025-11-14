# Implementation Plan - Phase 10: Advanced Graph Intelligence & Literature-Based Discovery

## Overview

This implementation plan breaks down Phase 10 into discrete, incremental tasks. Each task builds on previous work and integrates seamlessly with existing Phase 5 graph service, Phase 6 citation network, and other components.

## Task List

- [x] 1. Database models and migration for multi-layer graph









  - Create GraphEdge, GraphEmbedding, and DiscoveryHypothesis models in backend/app/database/models.py
  - Add proper indexes, foreign keys, and check constraints
  - Create Alembic migration script
  - Test migration up/down
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 2. Multi-layer graph construction in GraphService






  - [x] 2.1 Implement build_multilayer_graph() method

    - Create NetworkX MultiDiGraph
    - Add all resources as nodes with metadata
    - Create citation edges from Citation table
    - Create co-authorship edges from Resource.authors
    - Create subject similarity edges from ResourceTaxonomy
    - Create temporal edges from Resource.publication_year
    - Implement graph caching with timestamp tracking
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  


  - [x] 2.2 Implement edge weight calculations

    - Citation edges: weight = 1.0
    - Co-authorship edges: weight = 1.0 / num_shared_authors
    - Subject similarity edges: weight = 0.5
    - Temporal edges: weight = 0.3
    - Store edges in graph_edges table for persistence
    - _Requirements: 1.2, 1.3_

- [x] 3. Two-hop neighbor discovery





  - [x] 3.1 Implement get_neighbors_multihop() method

    - BFS traversal for 1-hop and 2-hop neighbors
    - Compute path_strength as product of edge weights
    - Filter by edge_types parameter
    - Filter by min_weight threshold
    - Track intermediate nodes for 2-hop paths
    - _Requirements: 5.1, 5.2, 5.4, 5.5_
  

  - [x] 3.2 Implement neighbor ranking algorithm


    - Compute novelty score: 1.0 / (1 + log(degree + 1))
    - Combine path_strength (50%), quality_overall (30%), novelty (20%)
    - Sort by combined score descending
    - Return top-K neighbors with path metadata
    - _Requirements: 5.3, 14.1_
-

- [x] 4. Graph embeddings service - Graph2Vec




  - [x] 4.1 Create GraphEmbeddingsService class


    - Initialize with database session
    - Lazy load GraphService dependency
    - _Requirements: 6.1_
  
  - [x] 4.2 Implement compute_graph2vec_embeddings()

    - Extract 2-hop ego graphs for each resource
    - Initialize karateclub Graph2Vec model (dimensions=128, wl_iterations=2)
    - Train model on ego graphs
    - Store structural embeddings in graph_embeddings table
    - Batch commit every 100 nodes with progress logging
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 14.3_
-

- [x] 5. Fusion embeddings and HNSW indexing


  - [x] 5.1 Implement compute_fusion_embeddings()


    - Query resources with both content and structural embeddings
    - Handle dimension mismatch by truncating to minimum
    - Compute fusion: alpha * content + (1-alpha) * structural
    - Normalize fusion vector to unit length
    - Store in GraphEmbedding.fusion_embedding
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 5.2 Implement build_hnsw_index()

    - Initialize hnswlib index (space='cosine', ef_construction=200, M=16)
    - Add fusion embeddings to index
    - Save index to disk: backend/data/hnsw_index_phase10.bin
    - Update GraphEmbedding.hnsw_index_id
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 14.4_
  
  - [x] 5.3 Implement query_hnsw_index()







    - Load index from disk if not in memory
    - Query k nearest neighbors
    - Return resource IDs with similarity scores
    - _Requirements: 8.2_

- [x] 6. Literature-Based Discovery service




  - [x] 6.1 Create LBDService class


    - Initialize with database session
    - Lazy load GraphService and GraphEmbeddingsService
    - _Requirements: 9.1, 10.1_
  
  - [x] 6.2 Implement open_discovery()


    - Find all B resources connected to A (1-hop)
    - For each B, find C resources (2-hop from A)
    - Exclude C resources with direct A→C edge
    - Compute path_strength for each A→B→C path
    - Count common neighbors between A and C
    - Compute semantic similarity using embeddings
    - Calculate plausibility score (40% path + 30% neighbors + 30% semantic)
    - Filter by min_plausibility threshold
    - Store hypotheses in discovery_hypotheses table
    - Return top-K hypotheses ranked by plausibility
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 11.1, 11.2, 11.3_
  
  - [x] 6.3 Implement closed_discovery()


    - Check for direct A→C edge (return if exists)
    - Find all 2-hop paths A→B→C
    - If no 2-hop paths, try 3-hop with penalty
    - Compute path_strength and plausibility
    - Apply hop penalty: plausibility * (0.5 ^ (hops - 2))
    - Store best hypothesis in database
    - Return all paths ranked by plausibility
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.4_

- [x] 7. Discovery API endpoints





  - [x] 7.1 Create discovery router (backend/app/routers/discovery.py)


    - Import dependencies and create APIRouter
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 7.2 Implement GET /discovery/open endpoint

    - Accept resource_id, limit, min_plausibility parameters
    - Call LBDService.open_discovery()
    - Return hypotheses with C resources and evidence
    - Handle 404 for non-existent resource
    - _Requirements: 12.1_
  
  - [x] 7.3 Implement POST /discovery/closed endpoint

    - Accept ClosedDiscoveryRequest with a_resource_id, c_resource_id, max_hops
    - Call LBDService.closed_discovery()
    - Return paths with B resources and plausibility
    - _Requirements: 12.2_
  
  - [x] 7.4 Implement GET /graph/resources/{id}/neighbors endpoint

    - Accept hops, edge_types, min_weight, limit parameters
    - Call GraphService.get_neighbors_multihop()
    - Return neighbors with path metadata
    - _Requirements: 12.3_
  
  - [x] 7.5 Implement GET /discovery/hypotheses endpoint

    - Accept hypothesis_type, is_validated, min_plausibility, pagination parameters
    - Query discovery_hypotheses table with filters
    - Return paginated results
    - _Requirements: 12.4_
  
  - [x] 7.6 Implement POST /discovery/hypotheses/{id}/validate endpoint

    - Accept HypothesisValidation with is_valid and notes
    - Update hypothesis.is_validated and validation_notes
    - If valid, increase edge weights along path by 10%
    - Record user_id
    - _Requirements: 12.5, 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 8. Pydantic schemas for discovery





  - Create ClosedDiscoveryRequest schema
  - Create HypothesisValidation schema
  - Create NeighborResponse schema
  - Create HypothesisResponse schema
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 9. Integration with recommendation service







  - [x] 9.1 Add graph-based recommendations to RecommendationService

    - Call get_neighbors_multihop() for 2-hop neighbors
    - Call open_discovery() for hypothesis-based recommendations
    - Rank graph candidates by score
    - _Requirements: 15.1, 15.2, 15.4_
  
  - [x] 9.2 Implement recommendation fusion


    - Combine content-based (70%) and graph-based (30%) recommendations
    - Re-rank combined results
    - Include connection path in response for graph-based recs
    - _Requirements: 15.3, 15.5_

- [ ] 10. Graph visualization enhancements




  - Update graph visualization to support multi-layer rendering
  - Use distinct colors for each edge type
  - Highlight intermediate nodes for 2-hop paths
  - Emphasize hypothesis paths (A→B→C)
  - Add edge type filtering controls
  - Display edge weights as line thickness
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_


- [x] 11. Comprehensive testing








  - [x] 11.1 Unit tests for multi-layer graph construction


    - Test citation edge creation
    - Test co-authorship edge creation
    - Test subject similarity edge creation
    - Test temporal edge creation
    - Test graph caching
    - Test edge weight calculations
    - _Requirements: 18.1_
  
  - [x] 11.2 Unit tests for 2-hop neighbor discovery


    - Test 1-hop retrieval
    - Test 2-hop retrieval with path tracking
    - Test edge type filtering
    - Test min_weight filtering
    - Test ranking algorithm
    - Test limit enforcement
    - _Requirements: 18.2_
  
  - [x] 11.3 Unit tests for Graph2Vec embeddings



    - Test ego graph extraction
    - Test embedding generation
    - Test embedding storage
    - Test dimension consistency
    - Test disconnected components handling
    - _Requirements: 18.3_
  

  - [x] 11.4 Unit tests for fusion embeddings

    - Test fusion computation
    - Test dimension mismatch handling
    - Test normalization
    - Test missing embeddings handling
    - _Requirements: 18.3_
  

  - [x] 11.5 Unit tests for HNSW indexing


    - Test index building
    - Test k-NN query performance
    - Test index persistence
    - Test incremental updates
    - Test query accuracy
    - _Requirements: 18.3_
  
  - [x] 11.6 Unit tests for LBD open discovery




    - Test A→B→C path discovery
    - Test direct connection exclusion
    - Test plausibility scoring
    - Test min_plausibility filtering
    - Test hypothesis storage
    - Test ranking
    - _Requirements: 18.4_
  


  - [x] 11.7 Unit tests for LBD closed discovery

    - Test 2-hop path finding
    - Test 3-hop path finding with penalty
    - Test path strength calculation
    - Test common neighbor counting
    - Test hypothesis storage
    - Test no paths handling
    - _Requirements: 18.4_

  
  - [x] 11.8 API endpoint tests

    - Test all discovery endpoints (success and error cases)
    - Test neighbor query endpoint
    - Test hypothesis listing and validation
    - Test pagination and filtering
    - _Requirements: 18.5_
  

  - [x] 11.9 Integration tests


    - Test end-to-end discovery workflow
    - Test recommendation integration
    - _Requirements: 18.5_
  
  - [x] 11.10 Performance tests


    - Test 2-hop query latency (<500ms for 5,000 nodes)
    - Test HNSW query latency (<100ms for 10,000 nodes)
    - Test graph construction time (<30s for 10,000 resources)
    - Test Graph2Vec computation rate (>100 nodes/minute)
    - Test memory usage

- [x] 12. Documentation updates





  - Update README.md with Phase 10 features
  - Update API_DOCUMENTATION.md with discovery endpoints
  - Update DEVELOPER_GUIDE.md with graph intelligence architecture
  - Update CHANGELOG.md with Phase 10 changes
  - Create Phase 10 user guide with examples
  - _Requirements: All requirements covered in documentation_
