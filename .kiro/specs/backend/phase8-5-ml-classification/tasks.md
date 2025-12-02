wp# Implementation Plan

- [x] 1. Database schema and migrations





  - Create Alembic migration for taxonomy_nodes and resource_taxonomy tables
  - Add all required indexes for performance
  - Add check constraints for data validation
  - Test migration forward and backward
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 11.11_

- [x] 2. Taxonomy data models

  - Create TaxonomyNode model in app/models.py with all fields and relationships
  - Create ResourceTaxonomy association model with classification metadata
  - Add proper SQLAlchemy relationships and constraints
  - Add __repr__ methods for debugging
  - _Requirements: 1.1, 6.1, 6.2, 6.3_

- [x] 3. Taxonomy service - core CRUD operations


  - [x] 3.1 Implement create_node() with parent validation and path computation

    - Validate parent exists
    - Compute level and materialized path
    - Update parent is_leaf flag
    - _Requirements: 1.2, 1.3_

  - [x] 3.2 Implement update_node() for metadata changes

    - Update name, description, keywords, allow_resources
    - Recalculate slug and path if name changes
    - _Requirements: 1.1_

  - [x] 3.3 Implement delete_node() with cascade and reparenting options

    - Validate no resources assigned
    - Support cascade deletion of descendants
    - Support reparenting children to parent
    - _Requirements: 1.5, 9.8_

  - [x] 3.4 Implement move_node() for reparenting

    - Prevent circular references
    - Update level and path for node and descendants
    - _Requirements: 1.6, 1.7_

  - [x] 3.5 Implement helper methods (_slugify, _compute_path, _is_descendant, _update_descendants)

    - Slug generation from names
    - Path computation from parent hierarchy
    - Circular reference detection
    - Recursive descendant updates
    - _Requirements: 1.2, 1.3, 1.6, 1.7_

- [x] 4. Taxonomy service - hierarchical queries





  - [x] 4.1 Implement get_tree() for nested tree retrieval

    - Support root_id parameter for subtrees
    - Support max_depth parameter for depth limiting
    - Build recursive nested structure
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 4.2 Implement get_ancestors() using materialized path

    - Parse path to extract ancestor slugs
    - Query ancestors efficiently
    - Return in hierarchical order
    - _Requirements: 8.1, 8.2, 8.5_

  - [x] 4.3 Implement get_descendants() using path pattern matching




    - Query nodes with path LIKE pattern
    - Return all descendants at any depth
    - _Requirements: 8.3, 8.4, 8.5_

- [x] 5. Taxonomy service - resource classification






  - [x] 5.1 Implement classify_resource() method

    - Remove existing predicted classifications
    - Add new classifications with confidence scores
    - Flag low confidence (<0.7) for review
    - Compute review priority scores
    - _Requirements: 6.4, 6.5, 6.6, 6.7_


  - [x] 5.2 Implement _update_resource_counts() method

    - Count direct resources per node
    - Count descendant resources using path queries
    - Update cached counts in taxonomy_nodes
    - _Requirements: 1.8, 6.8_
-

- [x] 6. ML classification service - model infrastructure




  - [x] 6.1 Implement MLClassificationService class initialization


    - Set up model_name, model_version, db session
    - Initialize model and tokenizer as None (lazy loading)
    - Initialize label mappings
    - _Requirements: 2.1, 14.1_

  - [x] 6.2 Implement _load_model() with lazy loading


    - Load tokenizer from Hugging Face
    - Load model from checkpoint or base model
    - Load label mapping from JSON
    - Move to GPU if CUDA available
    - Set model to eval mode
    - _Requirements: 2.1, 13.4, 13.5, 13.6, 14.4, 14.5, 15.7_
-

- [x] 7. ML classification service - training




  - [x] 7.1 Implement fine_tune() method


    - Build label mapping from unique taxonomy IDs
    - Convert multi-label to multi-hot encoding
    - Split train/validation (80/20)
    - Tokenize texts with max_length=512
    - Create PyTorch datasets
    - _Requirements: 2.2, 2.3, 2.7, 5.2, 5.3_


  - [x] 7.2 Configure Hugging Face Trainer

    - Set training arguments (epochs, batch_size, learning_rate)
    - Configure evaluation strategy
    - Set up model checkpointing
    - Define compute_metrics callback
    - _Requirements: 5.1, 5.4, 5.5, 5.6_



  - [x] 7.3 Execute training and save model

    - Train model with Trainer API
    - Evaluate on validation set
    - Save model, tokenizer, and label map
    - Return evaluation metrics
    - _Requirements: 5.6, 5.7, 14.2, 14.3_



  - [x] 7.4 Implement _compute_metrics() for evaluation

    - Compute F1 score (macro average)
    - Compute precision and recall
    - Handle multi-label classification metrics
    - _Requirements: 2.6_

- [x] 8. ML classification service - semi-supervised learning






  - [x] 8.1 Implement _semi_supervised_iteration() method




    - Predict labels for unlabeled data
    - Filter high-confidence predictions (>=0.9)
    - Generate pseudo-labeled examples
    - Combine with original labeled data
    - Re-train model for one epoch
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 9. ML classification service - inference






  - [x] 9.1 Implement predict() for single text classification

    - Tokenize input text
    - Forward pass through model
    - Apply sigmoid activation
    - Get top-K predictions
    - Convert indices to taxonomy node IDs
    - _Requirements: 2.4, 2.5, 2.8_



  - [x] 9.2 Implement predict_batch() for efficient batch processing

    - Process texts in batches (32 for GPU, 8 for CPU)
    - Tokenize batch
    - Forward pass with batch
    - Apply sigmoid and get top-K for each
    - _Requirements: 2.5, 13.1, 13.2, 13.3_

- [x] 10. ML classification service - active learning






  - [x] 10.1 Implement identify_uncertain_samples() method

    - Query resources (prioritize predicted classifications)
    - Predict classifications for resources
    - Compute entropy uncertainty metric
    - Compute margin uncertainty metric
    - Compute confidence uncertainty metric
    - Combine uncertainty scores
    - Sort by uncertainty descending
    - Return top-N most uncertain
    - _Requirements: 4.1, 4.2, 4.3, 4.7_


  - [x] 10.2 Implement update_from_human_feedback() method

    - Remove existing predicted classifications
    - Add human-labeled classifications (confidence=1.0)
    - Check if retraining threshold reached (100 labels)
    - Trigger retraining notification
    - _Requirements: 4.4, 4.5, 4.6_

- [x] 11. Classification service integration





  - Enhance existing ClassificationService to integrate ML classifier
  - Add use_ml flag for ML vs rule-based selection
  - Implement classify_resource() with ML integration
  - Filter predictions by confidence threshold (>=0.3)
  - Call TaxonomyService to store classifications
  - _Requirements: 6.5, 12.4, 12.5_

- [x] 12. Pydantic schemas for API





  - Create TaxonomyNodeCreate schema
  - Create TaxonomyNodeUpdate schema
  - Create ClassificationFeedback schema
  - Create ClassifierTrainingRequest schema
  - Add to app/schemas/taxonomy.py
  - _Requirements: 9.1, 9.2, 10.4, 10.7_

- [x] 13. API endpoints - taxonomy management




  - [x] 13.1 Implement POST /taxonomy/nodes endpoint


    - Accept TaxonomyNodeCreate request
    - Call TaxonomyService.create_node()
    - Return created node
    - _Requirements: 9.1_

  - [x] 13.2 Implement PUT /taxonomy/nodes/{node_id} endpoint

    - Accept TaxonomyNodeUpdate request
    - Call TaxonomyService.update_node()
    - Return updated node
    - _Requirements: 9.2_

  - [x] 13.3 Implement DELETE /taxonomy/nodes/{node_id} endpoint

    - Accept cascade query parameter
    - Call TaxonomyService.delete_node()
    - Handle resource assignment errors
    - Return deletion status
    - _Requirements: 9.3, 9.8_

  - [x] 13.4 Implement POST /taxonomy/nodes/{node_id}/move endpoint

    - Accept new_parent_id in request body
    - Call TaxonomyService.move_node()
    - Handle circular reference errors
    - Return move status
    - _Requirements: 9.4_

  - [x] 13.5 Implement GET /taxonomy/tree endpoint

    - Accept root_id and max_depth query parameters
    - Call TaxonomyService.get_tree()
    - Return nested tree structure
    - _Requirements: 9.5_

  - [x] 13.6 Implement GET /taxonomy/nodes/{node_id}/ancestors endpoint

    - Call TaxonomyService.get_ancestors()
    - Return ancestor list
    - _Requirements: 9.6_

  - [x] 13.7 Implement GET /taxonomy/nodes/{node_id}/descendants endpoint

    - Call TaxonomyService.get_descendants()
    - Return descendant list
    - _Requirements: 9.7_
-

- [x] 14. API endpoints - classification operations







  - [x] 14.1 Implement POST /taxonomy/classify/{resource_id} endpoint





    - Accept resource_id path parameter
    - Enqueue background classification task
    - Return 202 Accepted status
    - _Requirements: 10.1, 10.2_

  - [x] 14.2 Implement GET /taxonomy/active-learning/uncertain endpoint


    - Accept limit query parameter
    - Call MLClassificationService.identify_uncertain_samples()
    - Return list of uncertain resources with scores
    - _Requirements: 10.3_

  - [x] 14.3 Implement POST /taxonomy/active-learning/feedback endpoint


    - Accept ClassificationFeedback request
    - Call MLClassificationService.update_from_human_feedback()
    - Return update status
    - _Requirements: 10.4_

  - [x] 14.4 Implement POST /taxonomy/train endpoint


    - Accept ClassifierTrainingRequest
    - Enqueue background training task
    - Return 202 Accepted status
    - _Requirements: 10.5, 10.6, 10.7_



- [x] 15. Resource ingestion integration










  - Add classification trigger to resource ingestion pipeline
  - Execute after embedding generation, before quality scoring
  - Enqueue background classification task
  - Handle classification failures gracefully
  - _Requirements: 12.1, 12.2, 12.3_
-

- [x] 16. Install ML dependencies




  - Add transformers, torch, scikit-learn to requirements.txt
  - Install packages in virtual environment
  - Verify CUDA availability for GPU acceleration
  - _Requirements: 2.1, 13.6_

- [x] 17. Unit tests for taxonomy service











  - Test create_node() with and without parent
  - Test update_node() metadata changes
  - Test delete_node() cascade and reparenting
  - Test move_node() and circular reference prevention
  - Test get_tree() with depth limits
  - Test get_ancestors() and get_descendants()
  - Test classify_resource() and resource counts
  - Test helper methods (_slugify, _compute_path, _is_descendant)
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6, 1.7, 1.8, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2, 8.3, 8.4, 8.5_




- [x] 18. Unit tests for ML classification service



  - Test fine_tune() with labeled data
  - Test predict() single text classification
  - Test predict_batch() batch processing
  - Test _semi_supervised_iteration() pseudo-labeling
  - Test identify_uncertain_samples() active learning
  - Test update_from_human_feedback() feedback integration
  - Test _load_model() lazy loading
  - Test label mapping conversion
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 19. Integration tests for end-to-end workflows





  - Test complete classification workflow (create taxonomy → ingest resource → verify classification)
  - Test active learning workflow (classify → identify uncertain → submit feedback → verify manual labels)
  - Test semi-supervised learning workflow (prepare datasets → fine-tune → verify pseudo-labels)
  - Test API endpoints with database integration
  - _Requirements: 12.1, 12.2, 12.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_



- [x] 20. Performance tests
















  - Test single prediction inference time (<100ms)
  - Test batch prediction performance
  - Test ancestor query performance (<10ms)
  - Test descendant query performance (<10ms)
  - Test tree retrieval performance (<50ms for depth 5)

  - Compare GPU vs CPU inference speeds

  - _Requirements: 2.5, 13.3, 13.1, 13.2_


- [x] 21. Documentation updates












  - [x] 21.1 Update README.md with Phase 8.5 overview


    - Add ML classification feature description
    - Add hierarchical taxonomy description
    - Add semi-supervised and active learning descriptions

    - _Requirements: All_


  - [x] 21.2 Update API_DOCUMENTATION.md with new endpoints


    - Document all taxonomy management endpoints
    - Document all classification endpoints
    - Add request/response examples
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_


  - [x] 21.3 Create ML classification usage guide

    - Document model training workflow
    - Document semi-supervised learning setup
    - Document active learning workflow
    - Add code examples
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_


  - [x] 21.4 Update DEVELOPER_GUIDE.md with architecture details

    - Add taxonomy service architecture
    - Add ML classification service architecture
    - Add integration points
    - Add troubleshooting guide
    - _Requirements: All_


  - [x] 21.5 Update CHANGELOG.md with Phase 8.5 changes

    - List all new features
    - List API changes
    - List database schema changes
    - _Requirements: All_
