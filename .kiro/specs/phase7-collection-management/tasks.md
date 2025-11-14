# Implementation Plan: Phase 7 Collection Management

This implementation plan breaks down the Phase 7 Collection Management feature into discrete, actionable coding tasks. Each task builds incrementally on previous work and references specific requirements from the requirements document.

## Task List

- [x] 1. Create Collection and CollectionResource database models





  - Define Collection model in `backend/app/database/models.py` with all fields (id, name, description, owner_id, visibility, parent_id, embedding, timestamps)
  - Define CollectionResource association table with composite primary key (collection_id, resource_id) and added_at timestamp
  - Add relationship mappings: Collection→Resource (many-to-many), Collection→Collection (self-referential parent/subcollections)
  - Add relationship to Resource model: resources→collections (back_populates)
  - Configure cascade delete behavior for parent→subcollections and collection/resource associations
  - Add database indexes on owner_id, visibility, and parent_id fields
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.4, 11.4_

- [x] 2. Create Alembic migration for collections tables





  - Generate new Alembic migration script for collections and collection_resources tables
  - Define upgrade() to create collections table with all columns, constraints, and indexes
  - Define upgrade() to create collection_resources association table with foreign keys and composite index
  - Configure CASCADE delete for parent_id foreign key and both association table foreign keys
  - Define downgrade() to drop both tables in correct order
  - Test migration up and down on clean database
  - _Requirements: 1.1, 9.4, 10.1, 11.4_

- [x] 3. Implement core CollectionService CRUD methods





- [x] 3.1 Create CollectionService class and initialization


  - Create `backend/app/services/collection_service.py` file
  - Define CollectionService class with __init__(db: Session) constructor
  - Add table creation safety check (Base.metadata.create_all pattern)
  - Import required models (Collection, CollectionResource, Resource)
  - _Requirements: 1.1, 2.1_

- [x] 3.2 Implement create_collection method


  - Accept parameters: owner_id, name, description, visibility, parent_id
  - Validate name length (1-255 characters)
  - Validate visibility value is one of: private, shared, public
  - If parent_id provided, verify parent exists and owner matches
  - Call validate_hierarchy to prevent circular references
  - Create Collection instance with uuid4() id and default visibility='private'
  - Commit to database and return Collection object
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 9.1, 9.2, 9.3_

- [x] 3.3 Implement get_collection method with access control


  - Accept collection_id and user_id parameters
  - Query Collection by id
  - Raise ValueError if not found
  - Check access: if visibility='private', verify user_id == owner_id
  - If visibility='public', allow access
  - Return Collection with eager-loaded resources (use joinedload)
  - _Requirements: 2.2, 5.1, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.4 Implement update_collection method


  - Accept collection_id, user_id, and updates dictionary
  - Retrieve collection using get_collection (enforces access)
  - Verify user_id == owner_id, raise authorization error if not
  - Validate updated fields (name length, visibility value)
  - If parent_id changed, call validate_hierarchy
  - Apply updates to collection object
  - Update updated_at timestamp
  - Commit and return updated Collection
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 9.1, 9.2, 9.3_

- [x] 3.5 Implement delete_collection method


  - Accept collection_id and user_id parameters
  - Retrieve collection and verify ownership
  - Delete collection (cascade will handle subcollections and associations)
  - Commit transaction
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.6 Implement list_collections method with filtering


  - Accept user_id, owner_filter, visibility_filter, page, limit parameters
  - Build base query for Collection
  - Apply owner filter if provided
  - Apply visibility filter if provided
  - Apply access control: include collections where user is owner OR visibility is public
  - Count total results before pagination
  - Apply sorting (created_at DESC) and pagination (offset/limit)
  - Return tuple of (collections list, total count)
  - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [x] 4. Implement resource membership management

- [x] 4.1 Implement add_resources method


  - Accept collection_id, user_id, and resource_ids list (max 100)
  - Retrieve collection and verify ownership
  - Validate all resource_ids exist in Resource table
  - Batch insert CollectionResource associations (use bulk_insert_mappings)
  - Handle duplicate associations gracefully (ignore or use ON CONFLICT)
  - Trigger recompute_embedding after successful insert
  - Commit and return updated Collection
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 11.5_

- [x] 4.2 Implement remove_resources method

  - Accept collection_id, user_id, and resource_ids list (max 100)
  - Retrieve collection and verify ownership
  - Batch delete CollectionResource associations where collection_id matches and resource_id in list
  - Trigger recompute_embedding after successful delete
  - Commit and return updated Collection
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 11.5_

- [x] 5. Implement aggregate embedding computation

- [x] 5.1 Implement recompute_embedding method

  - Accept collection_id parameter
  - Query all resources in collection that have non-null embeddings
  - If no embeddings found, set collection.embedding to None and return
  - Extract embedding vectors into list of lists
  - Call compute_aggregate_embedding helper function
  - Store result in collection.embedding field
  - Commit and return embedding vector
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [x] 5.2 Implement compute_aggregate_embedding helper function


  - Accept list of embedding vectors (List[List[float]])
  - Use numpy to stack vectors into matrix
  - Compute column-wise mean
  - Normalize result to unit length (L2 norm)
  - Return as list of floats
  - Handle edge cases: empty list, single vector, zero vector
  - _Requirements: 7.2, 7.4_

- [x] 6. Implement hierarchy validation

- [x] 6.1 Implement validate_hierarchy method


  - Accept collection_id and new_parent_id parameters
  - If new_parent_id is None, return True (top-level collection)
  - Start traversal at new_parent_id
  - Follow parent_id chain up the hierarchy
  - If collection_id encountered, raise ValueError (circular reference)
  - If None reached, return True (valid hierarchy)
  - Limit traversal depth to 10 levels to prevent infinite loops
  - _Requirements: 9.3_

- [x] 7. Implement recommendation methods

- [x] 7.1 Implement get_recommendations method


  - Accept collection_id, user_id, limit, include_resources, include_collections parameters
  - Retrieve collection and verify access
  - Get collection.embedding, raise error if None
  - Initialize results dictionary with "resources" and "collections" keys
  - If include_resources, call find_similar_resources
  - If include_collections, call find_similar_collections
  - Return results dictionary
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.2 Implement find_similar_resources helper


  - Accept target_embedding, exclude_resource_ids, limit parameters
  - Query all Resources with non-null embeddings
  - Exclude resources in exclude_resource_ids list
  - Compute cosine similarity for each resource embedding vs target
  - Sort by similarity descending
  - Return top N resources with similarity scores
  - _Requirements: 8.1, 8.3, 8.5_

- [x] 7.3 Implement find_similar_collections helper


  - Accept target_embedding, user_id, exclude_collection_id, limit parameters
  - Query all Collections with non-null embeddings
  - Apply access control filter (owner or public visibility)
  - Exclude collection with exclude_collection_id
  - Compute cosine similarity for each collection embedding vs target
  - Sort by similarity descending
  - Return top N collections with similarity scores
  - _Requirements: 8.2, 8.4, 8.5_

- [x] 7.4 Implement cosine_similarity utility function


  - Accept two embedding vectors (List[float])
  - Use numpy to compute dot product
  - Divide by product of L2 norms
  - Return similarity score (float between -1 and 1)
  - Handle edge cases: zero vectors, different dimensions
  - _Requirements: 8.1, 8.2_

- [x] 8. Create Pydantic schemas for collections
  - Create `backend/app/schemas/collection.py` file
  - Define CollectionCreate schema with name, description, visibility, parent_id fields
  - Define CollectionUpdate schema with optional fields
  - Define ResourceMembershipUpdate schema with resource_ids list (min 1, max 100)
  - Define ResourceSummary schema with id, title, creator, quality_score
  - Define CollectionResponse schema with all collection fields plus resource_count and resources list
  - Define CollectionListResponse schema with items, total, page, limit
  - Define RecommendationResponse schema with resources and collections lists
  - Add field validators for name length, visibility enum, resource_ids count
  - _Requirements: 1.2, 1.3, 2.3, 2.4, 3.5, 12.8_

- [x] 9. Implement collection API endpoints
- [x] 9.1 Create collections router and POST /collections endpoint
  - Create `backend/app/routers/collections.py` file
  - Define APIRouter with prefix="/collections" and tags=["collections"]
  - Implement POST / endpoint for creating collections
  - Extract owner_id from authentication token (dependency)
  - Call collection_service.create_collection with request data
  - Return CollectionResponse with 201 status
  - Handle validation errors (400), authorization errors (401)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 12.1, 12.7, 12.8_

- [x] 9.2 Implement GET /collections/{id} endpoint
  - Accept collection_id path parameter
  - Extract user_id from authentication token
  - Call collection_service.get_collection
  - Build CollectionResponse with resource summaries
  - Return 200 with response
  - Handle not found (404), forbidden (403) errors
  - _Requirements: 5.1, 6.1, 6.2, 6.3, 6.4, 6.5, 12.2, 12.7_

- [x] 9.3 Implement PUT /collections/{id} endpoint
  - Accept collection_id path parameter and CollectionUpdate body
  - Extract user_id from authentication token
  - Call collection_service.update_collection
  - Return CollectionResponse with 200 status
  - Handle validation (400), authorization (403), not found (404) errors
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 12.3, 12.7, 12.8_

- [x] 9.4 Implement DELETE /collections/{id} endpoint
  - Accept collection_id path parameter
  - Extract user_id from authentication token
  - Call collection_service.delete_collection
  - Return 204 No Content on success
  - Handle authorization (403), not found (404) errors
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 12.4, 12.7_

- [x] 9.5 Implement GET /collections endpoint with filtering
  - Accept query parameters: owner_id, visibility, page, limit
  - Extract user_id from authentication token
  - Call collection_service.list_collections with filters
  - Build CollectionListResponse with pagination metadata
  - Return 200 with response
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 12.5, 12.7_

- [x] 9.6 Implement POST /collections/{id}/resources endpoint
  - Accept collection_id path parameter and ResourceMembershipUpdate body
  - Extract user_id from authentication token
  - Call collection_service.add_resources
  - Return CollectionResponse with updated resource_count
  - Handle validation (400), authorization (403), not found (404) errors
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 12.5, 12.7, 12.8_

- [x] 9.7 Implement DELETE /collections/{id}/resources endpoint
  - Accept collection_id path parameter and ResourceMembershipUpdate body
  - Extract user_id from authentication token
  - Call collection_service.remove_resources
  - Return CollectionResponse with updated resource_count
  - Handle authorization (403), not found (404) errors
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 12.5, 12.7_

- [x] 9.8 Implement GET /collections/{id}/recommendations endpoint
  - Accept collection_id path parameter
  - Accept query parameters: limit (default 10, max 50), include_resources (default true), include_collections (default true)
  - Extract user_id from authentication token
  - Call collection_service.get_recommendations
  - Return RecommendationResponse with resources and collections lists
  - Handle forbidden (403), not found (404) errors
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 12.6, 12.7_

- [x] 9.9 Implement GET /collections/{id}/embedding endpoint
  - Accept collection_id path parameter
  - Extract user_id from authentication token
  - Retrieve collection and verify access
  - Return embedding vector and dimension
  - Handle forbidden (403), not found (404) errors
  - _Requirements: 7.5, 12.6, 12.7_

- [x] 10. Integrate collection cleanup with resource deletion
  - Modify `backend/app/services/resource_service.py` delete_resource method
  - Before deleting resource, query all CollectionResource associations for resource_id
  - Store affected collection_ids
  - Delete CollectionResource associations (CASCADE will handle this, but explicit is better)
  - For each affected collection_id, call collection_service.recompute_embedding
  - Complete resource deletion
  - Log resource deletion impact on collections
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 11. Register collections router in main application
  - Import collections router in `backend/app/main.py`
  - Add router to FastAPI app with app.include_router(collections.router)
  - Verify router is registered after database initialization
  - Test that /collections endpoints are accessible
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [x] 12. Write comprehensive tests for Phase 7
- [x] 12.1 Write collection model tests
  - Test Collection creation with all field combinations
  - Test parent/subcollection relationships
  - Test cascade delete for subcollections
  - Test many-to-many resource relationships
  - Test CollectionResource association table
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.4_

- [x] 12.2 Write CollectionService CRUD tests
  - Test create_collection with valid and invalid inputs
  - Test get_collection with access control scenarios
  - Test update_collection with ownership verification
  - Test delete_collection with cascade behavior
  - Test list_collections with filtering and pagination
  - _Requirements: 1.1, 2.1, 2.2, 4.1, 4.2, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3_

- [x] 12.3 Write resource membership tests
  - Test add_resources with batch operations
  - Test remove_resources with batch operations
  - Test duplicate resource handling
  - Test invalid resource_id handling
  - Test authorization for membership changes
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 12.4 Write embedding computation tests
  - Test recompute_embedding with various resource counts
  - Test compute_aggregate_embedding algorithm correctness
  - Test embedding normalization
  - Test null embedding handling
  - Test embedding updates on membership changes
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 12.5 Write hierarchy validation tests
  - Test validate_hierarchy with valid parent assignments
  - Test circular reference detection
  - Test multi-level hierarchy traversal
  - Test parent deletion cascade
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 12.6 Write recommendation tests
  - Test get_recommendations with resources and collections
  - Test cosine similarity calculations
  - Test exclusion of source collection and member resources
  - Test access control in collection recommendations
  - Test recommendation limits
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12.7 Write API endpoint integration tests
  - Test POST /collections endpoint with authentication
  - Test GET /collections/{id} with access control
  - Test PUT /collections/{id} with authorization
  - Test DELETE /collections/{id} with cascade
  - Test GET /collections with filtering
  - Test POST/DELETE /collections/{id}/resources
  - Test GET /collections/{id}/recommendations
  - Test error responses (400, 401, 403, 404)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

- [x] 12.8 Write performance tests
  - Test collection retrieval with 1000 resources (<500ms)
  - Test embedding computation with 1000 resources (<1s)
  - Test batch add_resources with 100 resources (<2s)
  - Test recommendation query performance (<1s)
  - Test list_collections pagination performance
  - _Requirements: 4.5, 7.4, 11.1, 11.2, 11.3_

- [x] 13. Update documentation for Phase 7



- [x] 13.1 Update README.md


  - Add Phase 7 section describing collection management features
  - Explain use cases: organizing research, sharing reading lists, discovering related materials
  - Describe hierarchical organization and recommendation capabilities
  - Add example workflows for creating and managing collections
  - _Requirements: All_


- [x] 13.2 Update API_DOCUMENTATION.md

  - Document all /collections endpoints with request/response examples
  - Include authentication requirements
  - Document query parameters and filtering options
  - Add error response examples
  - Document recommendation endpoint behavior
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_



- [x] 13.3 Update DEVELOPER_GUIDE.md
  - Add section on collection service architecture
  - Document many-to-many association pattern
  - Explain aggregate embedding computation
  - Document hierarchy validation approach
  - Add guidance on extending collection features
  - _Requirements: All_

- [x] 13.4 Update CHANGELOG.md


  - Add Phase 7 entry with release date
  - List all new features: CRUD, membership, embeddings, recommendations, hierarchy
  - Document new API endpoints
  - Note integration with resource deletion
  - _Requirements: All_


- [x] 13.5 Create EXAMPLES_PHASE7.md


  - Provide code examples for creating collections via API
  - Show resource membership management examples
  - Demonstrate recommendation queries
  - Include hierarchical collection examples
  - Add Python client examples for common workflows
  - _Requirements: All_
