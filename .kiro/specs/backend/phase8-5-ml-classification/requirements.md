# Requirements Document

## Introduction

Phase 8.5 introduces a sophisticated machine learning-based classification system to replace the existing rule-based approach. This feature implements transformer-based classification using fine-tuned BERT/DistilBERT models, a hierarchical taxonomy tree with parent-child relationships, semi-supervised learning to leverage unlabeled data, and active learning workflows for continuous improvement with minimal human labeling effort.

The system will enable users to manage a hierarchical taxonomy tree, automatically classify resources with high accuracy and confidence scores, and continuously improve classification through active learning feedback loops.

## Glossary

- **System**: The Neo Alexandria knowledge management platform
- **ML_Classifier**: The machine learning classification service using transformer models
- **Taxonomy_Tree**: The hierarchical category structure with parent-child relationships
- **Resource**: A document, article, or content item to be classified
- **Confidence_Score**: A numerical value between 0.0 and 1.0 indicating classification certainty
- **Active_Learning**: A machine learning approach that identifies uncertain predictions for human review
- **Semi_Supervised_Learning**: Training approach using both labeled and unlabeled data
- **Taxonomy_Node**: A single category in the hierarchical taxonomy tree
- **Materialized_Path**: A string representation of a node's position in the tree hierarchy
- **Pseudo_Labeling**: Technique where high-confidence predictions on unlabeled data are used as training examples
- **Fine_Tuning**: Process of adapting a pre-trained model to a specific task
- **Multi_Label_Classification**: Classification where resources can belong to multiple categories

## Requirements

### Requirement 1: Hierarchical Taxonomy Management

**User Story:** As a knowledge manager, I want to create and manage a hierarchical taxonomy tree with nested categories, so that I can organize resources in a structured, multi-level classification system.

#### Acceptance Criteria

1. THE System SHALL store taxonomy nodes with unique identifiers, names, slugs, parent references, tree level, and materialized path
2. WHEN a user creates a taxonomy node with a parent, THE System SHALL compute the node level as parent level plus one
3. WHEN a user creates a taxonomy node with a parent, THE System SHALL compute the materialized path by concatenating parent path with node slug
4. THE System SHALL support taxonomy trees with depth of five levels or greater
5. WHEN a user deletes a taxonomy node without cascade, THE System SHALL reparent child nodes to the deleted node's parent
6. WHEN a user moves a taxonomy node to a new parent, THE System SHALL update the level and materialized path for the node and all descendants
7. THE System SHALL prevent circular references when moving nodes
8. THE System SHALL maintain resource counts for each taxonomy node including direct and descendant resources

### Requirement 2: Transformer-Based Classification

**User Story:** As a system administrator, I want to use fine-tuned BERT models for resource classification, so that classification accuracy exceeds rule-based approaches by at least 40%.

#### Acceptance Criteria

1. THE ML_Classifier SHALL use DistilBERT or BERT base models as the foundation
2. WHEN fine-tuning the model, THE ML_Classifier SHALL accept labeled data as text and taxonomy node identifier pairs
3. THE ML_Classifier SHALL support multi-label classification where resources can belong to multiple categories
4. WHEN predicting classifications, THE ML_Classifier SHALL return confidence scores between 0.0 and 1.0 for each predicted category
5. THE ML_Classifier SHALL complete inference for a single resource in less than 100 milliseconds
6. WHEN the model achieves F1 score greater than 0.85, THE System SHALL consider the model production-ready
7. THE ML_Classifier SHALL tokenize input text with maximum length of 512 tokens
8. THE ML_Classifier SHALL apply sigmoid activation for multi-label probability computation

### Requirement 3: Semi-Supervised Learning

**User Story:** As a data scientist, I want to leverage unlabeled data through semi-supervised learning, so that I can train effective models with fewer than 500 labeled examples.

#### Acceptance Criteria

1. WHEN fewer than 500 labeled examples are available, THE ML_Classifier SHALL support semi-supervised learning with unlabeled data
2. THE ML_Classifier SHALL perform initial training on labeled data before pseudo-labeling
3. WHEN generating pseudo-labels, THE ML_Classifier SHALL only use predictions with confidence greater than or equal to 0.9
4. THE ML_Classifier SHALL combine pseudo-labeled examples with original labeled data for retraining
5. WHEN unlabeled data is provided, THE ML_Classifier SHALL execute at least one semi-supervised iteration
6. THE System SHALL log the number of pseudo-labeled examples generated during semi-supervised learning

### Requirement 4: Active Learning Workflow

**User Story:** As a content curator, I want the system to identify uncertain classifications for my review, so that I can improve model accuracy with minimal labeling effort.

#### Acceptance Criteria

1. THE ML_Classifier SHALL compute uncertainty scores using entropy, margin, and confidence metrics
2. WHEN identifying uncertain samples, THE ML_Classifier SHALL return resources sorted by uncertainty in descending order
3. THE System SHALL flag classifications with confidence less than 0.7 for human review
4. WHEN a user provides correct classifications, THE System SHALL store them with confidence 1.0 and predicted_by value of "manual"
5. WHEN 100 or more new human-labeled examples accumulate, THE System SHALL trigger a notification for model retraining
6. THE System SHALL remove existing predicted classifications when human feedback is provided for a resource
7. THE ML_Classifier SHALL compute review priority scores for flagged classifications

### Requirement 5: Model Training and Fine-Tuning

**User Story:** As a machine learning engineer, I want to fine-tune classification models on domain-specific data, so that the system adapts to the specific content and taxonomy of the knowledge base.

#### Acceptance Criteria

1. THE ML_Classifier SHALL accept training parameters including epochs, batch size, and learning rate
2. WHEN fine-tuning, THE ML_Classifier SHALL split labeled data into 80% training and 20% validation sets
3. THE ML_Classifier SHALL use learning rate of 2e-5 as the default value
4. THE ML_Classifier SHALL train for 3 epochs as the default value
5. THE ML_Classifier SHALL save model checkpoints after each epoch
6. THE ML_Classifier SHALL compute F1 score, precision, and recall on the validation set
7. WHEN training completes, THE ML_Classifier SHALL save the model, tokenizer, and label mapping to disk
8. THE ML_Classifier SHALL use GPU acceleration when CUDA is available

### Requirement 6: Resource Classification Assignment

**User Story:** As a system user, I want resources to be automatically classified with confidence scores, so that I can understand classification certainty and identify items needing review.

#### Acceptance Criteria

1. WHEN a resource is classified, THE System SHALL store taxonomy node identifiers with confidence scores
2. THE System SHALL store the model version identifier that generated each classification
3. THE System SHALL distinguish between predicted classifications and manual classifications using the is_predicted flag
4. WHEN confidence is less than 0.7, THE System SHALL set needs_review to true
5. THE System SHALL filter predictions to only include categories with confidence greater than or equal to 0.3
6. WHEN new predicted classifications are added, THE System SHALL remove existing predicted classifications for that resource
7. THE System SHALL preserve manual classifications when updating predicted classifications
8. THE System SHALL update taxonomy node resource counts after classification changes

### Requirement 7: Taxonomy Tree Retrieval

**User Story:** As a frontend developer, I want to retrieve the taxonomy tree as nested JSON, so that I can render an interactive tree view for users.

#### Acceptance Criteria

1. THE System SHALL return taxonomy trees as nested dictionary structures with children arrays
2. WHEN a root node identifier is provided, THE System SHALL return the tree starting from that node
3. WHEN a maximum depth is specified, THE System SHALL limit tree traversal to that depth
4. THE System SHALL include node metadata in tree responses including identifier, name, slug, level, path, and resource counts
5. THE System SHALL retrieve all root nodes when no root identifier is specified
6. THE System SHALL use recursive queries to build nested tree structures

### Requirement 8: Taxonomy Ancestry and Descendants

**User Story:** As a user browsing the taxonomy, I want to see breadcrumb trails and explore subcategories, so that I can understand the hierarchical context and navigate efficiently.

#### Acceptance Criteria

1. WHEN retrieving ancestors, THE System SHALL return all parent nodes up to the root in hierarchical order
2. THE System SHALL use materialized path for efficient ancestor queries
3. WHEN retrieving descendants, THE System SHALL return all child nodes at any depth below the specified node
4. THE System SHALL use materialized path pattern matching for efficient descendant queries
5. THE System SHALL return empty arrays when a node has no ancestors or descendants

### Requirement 9: API Endpoints for Taxonomy Operations

**User Story:** As an API consumer, I want RESTful endpoints for taxonomy management, so that I can integrate taxonomy operations into applications and workflows.

#### Acceptance Criteria

1. THE System SHALL provide POST endpoint at /taxonomy/nodes for creating taxonomy nodes
2. THE System SHALL provide PUT endpoint at /taxonomy/nodes/{node_id} for updating taxonomy nodes
3. THE System SHALL provide DELETE endpoint at /taxonomy/nodes/{node_id} for deleting taxonomy nodes
4. THE System SHALL provide POST endpoint at /taxonomy/nodes/{node_id}/move for reparenting nodes
5. THE System SHALL provide GET endpoint at /taxonomy/tree for retrieving tree structures
6. THE System SHALL provide GET endpoint at /taxonomy/nodes/{node_id}/ancestors for breadcrumb trails
7. THE System SHALL provide GET endpoint at /taxonomy/nodes/{node_id}/descendants for subcategory exploration
8. WHEN a taxonomy node has assigned resources, THE System SHALL return an error preventing deletion

### Requirement 10: API Endpoints for Classification Operations

**User Story:** As an API consumer, I want endpoints for classification and active learning, so that I can trigger classifications and provide feedback programmatically.

#### Acceptance Criteria

1. THE System SHALL provide POST endpoint at /taxonomy/classify/{resource_id} for classifying resources
2. THE System SHALL execute classification as a background task and return 202 Accepted status
3. THE System SHALL provide GET endpoint at /taxonomy/active-learning/uncertain for retrieving uncertain samples
4. THE System SHALL provide POST endpoint at /taxonomy/active-learning/feedback for submitting human corrections
5. THE System SHALL provide POST endpoint at /taxonomy/train for initiating model fine-tuning
6. THE System SHALL execute training as a background task and return 202 Accepted status
7. THE System SHALL accept training parameters including labeled data, unlabeled data, epochs, and batch size

### Requirement 11: Database Schema and Migrations

**User Story:** As a database administrator, I want proper schema definitions and migrations for taxonomy tables, so that data integrity is maintained and queries are performant.

#### Acceptance Criteria

1. THE System SHALL create taxonomy_nodes table with columns for identifier, name, slug, parent_id, level, path, description, keywords, resource counts, metadata flags, and timestamps
2. THE System SHALL create resource_taxonomy association table with columns for identifier, resource_id, taxonomy_node_id, confidence, is_predicted, predicted_by, needs_review, review_priority, and timestamps
3. THE System SHALL create index on taxonomy_nodes parent_id column
4. THE System SHALL create index on taxonomy_nodes path column
5. THE System SHALL create unique index on taxonomy_nodes slug column
6. THE System SHALL create index on resource_taxonomy resource_id column
7. THE System SHALL create index on resource_taxonomy taxonomy_node_id column
8. THE System SHALL create index on resource_taxonomy needs_review column
9. THE System SHALL add check constraint ensuring level is greater than or equal to zero
10. THE System SHALL add check constraint ensuring confidence is between 0.0 and 1.0
11. THE System SHALL support forward and backward migration with alembic upgrade and downgrade commands

### Requirement 12: Integration with Resource Ingestion

**User Story:** As a system operator, I want resources to be automatically classified during ingestion, so that new content is immediately organized without manual intervention.

#### Acceptance Criteria

1. WHEN a resource completes content extraction, THE System SHALL enqueue a classification background task
2. THE System SHALL execute classification after embedding generation and before quality scoring
3. WHEN classification fails, THE System SHALL log the error without blocking resource ingestion
4. THE System SHALL use the ML classifier when use_ml flag is true
5. THE System SHALL fall back to rule-based classification when use_ml flag is false

### Requirement 13: Performance and Scalability

**User Story:** As a system architect, I want classification to be performant and scalable, so that the system handles large volumes of resources efficiently.

#### Acceptance Criteria

1. THE ML_Classifier SHALL process batch predictions with batch size of 32 when GPU is available
2. THE ML_Classifier SHALL process batch predictions with batch size of 8 when GPU is not available
3. THE System SHALL complete single resource classification in less than 100 milliseconds on average
4. THE ML_Classifier SHALL load models lazily on first prediction request
5. THE ML_Classifier SHALL cache loaded models in memory for subsequent predictions
6. WHEN CUDA is available, THE ML_Classifier SHALL move models to GPU for acceleration

### Requirement 14: Model Versioning and Checkpoints

**User Story:** As a machine learning engineer, I want model versions to be tracked and stored, so that I can manage model evolution and rollback if needed.

#### Acceptance Criteria

1. THE ML_Classifier SHALL store model version identifiers with each classification
2. THE System SHALL save model checkpoints to the models/classification/{version} directory
3. THE ML_Classifier SHALL save label mappings as JSON files alongside model checkpoints
4. WHEN loading a model, THE ML_Classifier SHALL attempt to load from the specified version checkpoint
5. WHEN a checkpoint is not found, THE ML_Classifier SHALL fall back to the base pre-trained model
6. THE System SHALL include model version in the predicted_by field of resource_taxonomy records

### Requirement 15: Error Handling and Validation

**User Story:** As a developer, I want comprehensive error handling and validation, so that the system provides clear feedback and maintains data integrity.

#### Acceptance Criteria

1. WHEN a parent node does not exist, THE System SHALL return an error preventing node creation
2. WHEN attempting to delete a node with resources, THE System SHALL return an error with resource count
3. WHEN attempting circular reparenting, THE System SHALL return an error preventing the operation
4. WHEN a node identifier is not found, THE System SHALL return an error with the invalid identifier
5. THE System SHALL validate that confidence scores are between 0.0 and 1.0
6. THE System SHALL validate that taxonomy node slugs are unique
7. WHEN model loading fails, THE ML_Classifier SHALL log the error and fall back to base model
