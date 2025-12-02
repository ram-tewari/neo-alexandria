# Requirements Document

## Introduction

This specification defines the requirements for implementing a Neural Collaborative Filtering (NCF) service and training scripts for both the classification and recommendation models in Neo Alexandria. The goal is to enable all ML benchmark tests by providing trained models and the necessary infrastructure for model training and inference.

## Glossary

- **NCF**: Neural Collaborative Filtering - A deep learning approach to collaborative filtering for recommendation systems
- **Classification Model**: A transformer-based multi-label text classification model for taxonomy assignment
- **Training Script**: A standalone Python script that trains a model using prepared datasets
- **Model Checkpoint**: A saved model state that can be loaded for inference
- **User-Item Interaction**: A record of a user engaging with a resource (view, bookmark, rating, etc.)
- **Embedding**: A dense vector representation of users or items in a latent space
- **Cold Start**: The problem of making recommendations for new users or items with limited interaction history
- **NDCG**: Normalized Discounted Cumulative Gain - A ranking quality metric
- **Hit Rate**: The proportion of test cases where the relevant item appears in the top-K recommendations

## Requirements

### Requirement 1: NCF Service Implementation

**User Story:** As a developer, I want an NCF service that provides collaborative filtering recommendations, so that users can receive personalized resource suggestions based on interaction patterns.

#### Acceptance Criteria

1. WHEN THE System initializes the NCF service, THE NCFService SHALL load the trained model from a checkpoint file
2. WHEN a user requests recommendations, THE NCFService SHALL predict scores for candidate items using the neural network
3. WHEN predicting for a batch of items, THE NCFService SHALL process items efficiently with batch inference
4. WHERE the model checkpoint exists, THE NCFService SHALL load the pre-trained weights and embeddings
5. WHEN the model is not available, THE NCFService SHALL raise an appropriate exception with guidance

### Requirement 2: NCF Model Architecture

**User Story:** As a data scientist, I want a properly implemented NCF model architecture, so that the system can learn complex user-item interaction patterns.

#### Acceptance Criteria

1. THE NCF model SHALL implement separate embedding layers for users and items
2. THE NCF model SHALL implement a multi-layer perceptron (MLP) for learning interaction functions
3. THE NCF model SHALL support configurable embedding dimensions (default: 64)
4. THE NCF model SHALL support configurable hidden layer sizes (default: [128, 64, 32])
5. THE NCF model SHALL output prediction scores between 0 and 1 using sigmoid activation

### Requirement 3: NCF Training Script

**User Story:** As a developer, I want a training script for the NCF model, so that I can train recommendation models on user interaction data.

#### Acceptance Criteria

1. THE training script SHALL load user-item interaction data from the database or CSV files
2. THE training script SHALL split data into training and validation sets (80/20 split)
3. THE training script SHALL implement negative sampling for implicit feedback data
4. THE training script SHALL train the model using binary cross-entropy loss
5. THE training script SHALL evaluate the model using NDCG@10 and Hit Rate@10 metrics
6. THE training script SHALL save the trained model checkpoint to the models directory
7. THE training script SHALL log training progress and metrics to the console

### Requirement 4: Classification Model Training Script

**User Story:** As a developer, I want a training script for the classification model, so that I can train taxonomy classification models on labeled resource data.

#### Acceptance Criteria

1. THE training script SHALL load labeled classification data from the test dataset
2. THE training script SHALL use the existing MLClassificationService for training
3. THE training script SHALL train the model for at least 3 epochs
4. THE training script SHALL evaluate the model on a validation set
5. THE training script SHALL save the trained model checkpoint with version "benchmark_v1"
6. THE training script SHALL report F1 score, precision, and recall metrics
7. THE training script SHALL complete training in under 30 minutes on CPU

### Requirement 5: Training Data Preparation

**User Story:** As a developer, I want training data preparation utilities, so that I can convert test datasets into training-ready formats.

#### Acceptance Criteria

1. THE System SHALL provide a function to load classification test data from JSON
2. THE System SHALL provide a function to load recommendation test data from JSON
3. THE System SHALL augment small datasets with synthetic examples if needed
4. THE System SHALL validate data format and completeness before training
5. THE System SHALL handle missing or malformed data gracefully with warnings

### Requirement 6: Model Checkpoint Management

**User Story:** As a developer, I want consistent model checkpoint management, so that trained models can be reliably saved and loaded.

#### Acceptance Criteria

1. THE System SHALL save classification models to `backend/models/classification/benchmark_v1/`
2. THE System SHALL save NCF models to `backend/models/ncf_benchmark_v1.pt`
3. THE System SHALL save label mappings alongside classification models
4. THE System SHALL save user and item ID mappings alongside NCF models
5. THE System SHALL create model directories automatically if they don't exist

### Requirement 7: Cold Start Handling

**User Story:** As a system, I want to handle cold start scenarios gracefully, so that recommendations can be provided even for new users or items.

#### Acceptance Criteria

1. WHEN a user has no interaction history, THE NCFService SHALL return popular items as fallback recommendations
2. WHEN an item is new, THE NCFService SHALL use content-based features if available
3. THE NCFService SHALL log cold start scenarios for monitoring
4. THE NCFService SHALL provide a confidence score indicating cold start status

### Requirement 8: Performance Requirements

**User Story:** As a user, I want fast model inference, so that recommendations and classifications are provided in real-time.

#### Acceptance Criteria

1. THE NCFService SHALL predict recommendations for a single user in under 50ms (p95)
2. THE MLClassificationService SHALL classify a single text in under 100ms (p95)
3. THE NCFService SHALL support batch prediction for efficiency
4. THE System SHALL use GPU acceleration when available
5. THE System SHALL fall back to CPU if GPU is not available

### Requirement 9: Training Script CLI

**User Story:** As a developer, I want command-line interfaces for training scripts, so that I can easily train models with different configurations.

#### Acceptance Criteria

1. THE training scripts SHALL accept command-line arguments for hyperparameters
2. THE training scripts SHALL support `--epochs`, `--batch-size`, and `--learning-rate` arguments
3. THE training scripts SHALL support `--data-path` for custom dataset locations
4. THE training scripts SHALL support `--output-dir` for custom checkpoint locations
5. THE training scripts SHALL display help text with `--help` argument

### Requirement 10: Integration with Benchmark Tests

**User Story:** As a developer, I want trained models to work seamlessly with benchmark tests, so that all tests can pass without modification.

#### Acceptance Criteria

1. THE trained classification model SHALL be loadable by the `trained_classifier` fixture
2. THE trained NCF model SHALL be loadable by the `trained_ncf_model` fixture
3. THE models SHALL meet or exceed baseline performance thresholds in benchmarks
4. THE models SHALL support all operations required by benchmark tests
5. THE System SHALL provide clear error messages if models are not found
