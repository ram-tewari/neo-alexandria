# Implementation Plan

- [x] 1. Implement NCF model architecture




  - Create `backend/app/models/ncf_model.py` with NCFModel class
  - Implement user and item embedding layers with configurable dimensions
  - Implement MLP layers with ReLU activation
  - Implement forward pass with concatenated embeddings
  - Add sigmoid output layer for score prediction
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Implement NCF service






- [x] 2.1 Create NCF service class structure

  - Create `backend/app/services/ncf_service.py` with NCFService class
  - Implement `__init__` method with database session and model path
  - Add model, user_id_map, and item_id_map attributes
  - Implement lazy loading pattern for model initialization
  - _Requirements: 1.1, 1.4_


- [x] 2.2 Implement model loading functionality

  - Implement `_load_model()` method to load checkpoint from disk
  - Load model state dict, user/item mappings, and hyperparameters
  - Handle missing checkpoint with clear error message
  - Move model to GPU if CUDA available, otherwise CPU
  - Set model to evaluation mode
  - _Requirements: 1.1, 1.4, 1.5, 8.4, 8.5_


- [x] 2.3 Implement prediction methods

  - Implement `predict()` for single user-item score prediction
  - Implement `predict_batch()` for efficient batch prediction
  - Convert user/item IDs to indices using mappings
  - Handle unknown users/items gracefully
  - Return scores as dictionary mapping item_id to score
  - _Requirements: 1.2, 1.3, 8.1, 8.3_


- [x] 2.4 Implement recommendation generation

  - Implement `recommend()` method for top-K recommendations
  - Query candidate items from database
  - Use batch prediction for efficiency
  - Sort by score and return top-K items
  - Support exclude_seen parameter to filter viewed items
  - _Requirements: 1.2, 8.1_


- [x] 2.5 Implement cold start handling

  - Implement `_handle_cold_start()` method for new users
  - Query popular items from database (most interactions)
  - Return popular items as fallback recommendations
  - Log cold start events for monitoring
  - Add confidence score indicating cold start status
  - _Requirements: 7.1, 7.2, 7.3, 7.4_


- [x] 3. Create data preparation utilities




- [x] 3.1 Implement classification data loader

  - Create `backend/scripts/prepare_training_data.py`
  - Implement `load_classification_test_data()` to read JSON dataset
  - Parse samples and extract text and taxonomy codes
  - Convert to list of (text, [taxonomy_ids]) tuples
  - Validate data format and log warnings for issues
  - _Requirements: 5.1, 5.4, 5.5_


- [x] 3.2 Implement recommendation data loader

  - Implement `load_recommendation_test_data()` to read JSON dataset
  - Parse interactions and extract user_id, item_id, timestamp
  - Create user and item ID mappings
  - Return interactions list and ID mappings
  - _Requirements: 5.2, 5.4, 5.5_



- [ ] 3.3 Implement data augmentation
  - Implement `augment_classification_data()` for small datasets
  - Create text variations using paraphrasing techniques
  - Ensure augmented data maintains label consistency
  - Target minimum dataset size of 500 examples

  - _Requirements: 5.3_


- [ ] 3.4 Implement synthetic data generation
  - Implement `create_synthetic_interactions()` for NCF training
  - Generate random user-item pairs with realistic patterns
  - Add temporal patterns and popularity bias
  - Ensure sufficient data for training (minimum 1000 interactions)
  - _Requirements: 5.3_

- [x] 4. Implement NCF training script




- [x] 4.1 Create training script structure


  - Create `backend/scripts/train_ncf.py`
  - Implement command-line argument parsing (epochs, batch_size, lr, data_path, output_dir)
  - Add logging configuration for training progress
  - Implement main() function as entry point
  - _Requirements: 3.1, 3.2, 9.1, 9.2, 9.3, 9.4, 9.5_


- [x] 4.2 Implement data loading and preparation

  - Implement `load_interaction_data()` to load from JSON or database
  - Create user and item ID mappings (string to integer)
  - Split data into train/validation sets (80/20)
  - Log dataset statistics (num users, items, interactions, density)
  - _Requirements: 3.1, 3.2_


- [x] 4.3 Implement negative sampling

  - Implement `create_negative_samples()` for implicit feedback
  - Generate 4 negative samples per positive interaction
  - Ensure negative samples are not in positive set
  - Create balanced dataset with 1:4 positive:negative ratio
  - _Requirements: 3.3_


- [x] 4.4 Implement training loop

  - Implement `train_ncf_model()` function
  - Initialize NCF model with hyperparameters
  - Use Adam optimizer with configurable learning rate
  - Use binary cross-entropy loss for implicit feedback
  - Train for specified number of epochs
  - Log training loss every 10 batches
  - _Requirements: 3.4_


- [x] 4.5 Implement evaluation

  - Implement `evaluate_model()` function
  - Compute NDCG@10 on validation set
  - Compute Hit Rate@10 on validation set
  - Log evaluation metrics after each epoch
  - _Requirements: 3.5_


- [x] 4.6 Implement checkpoint saving

  - Save model state dict to `backend/models/ncf_benchmark_v1.pt`
  - Save user and item ID mappings in checkpoint
  - Save hyperparameters and training metrics
  - Create models directory if it doesn't exist
  - Log checkpoint save location
  - _Requirements: 3.6, 6.2, 6.4, 6.5_


- [x] 5. Implement classification training script




- [x] 5.1 Create training script structure

  - Create `backend/scripts/train_classification.py`
  - Implement command-line argument parsing
  - Add logging configuration
  - Implement main() function as entry point
  - _Requirements: 4.1, 9.1, 9.2, 9.3, 9.4, 9.5_



- [x] 5.2 Implement data loading
  - Implement `load_classification_data()` to load test dataset
  - Use prepare_training_data utilities
  - Validate data format and completeness
  - Log dataset statistics
  - _Requirements: 4.1, 5.1_

- [x] 5.3 Implement data augmentation
  - Implement `augment_dataset()` if dataset is too small
  - Target minimum 500 examples for training
  - Use text variation techniques
  - Maintain label consistency
  - _Requirements: 5.3_

- [x] 5.4 Implement training pipeline
  - Initialize MLClassificationService with benchmark_v1 version
  - Call fine_tune() method with loaded data
  - Train for 3 epochs with batch size 16
  - Use learning rate 2e-5
  - _Requirements: 4.2, 4.3_

- [x] 5.5 Implement evaluation and saving

  - Evaluate model on validation set
  - Report F1 score, precision, and recall
  - Model is automatically saved by MLClassificationService
  - Verify checkpoint saved to correct location
  - Log training completion and metrics
  - _Requirements: 4.4, 4.5, 4.6, 6.1, 6.3, 6.5_

- [x] 6. Update benchmark test fixtures






- [x] 6.1 Update trained_ncf_model fixture

  - Modify `backend/tests/ml_benchmarks/conftest.py`
  - Update `trained_ncf_model` fixture to use NCFService
  - Load model from `backend/models/ncf_benchmark_v1.pt`
  - Handle missing model with clear skip message
  - _Requirements: 10.2, 10.5_


- [x] 6.2 Verify trained_classifier fixture

  - Verify `trained_classifier` fixture loads benchmark_v1 model
  - Ensure it works with updated checkpoint location
  - Test fixture with sample prediction
  - _Requirements: 10.1, 10.5_


- [x] 6.3 Add model availability checks


  - Add helper function to check if models are trained
  - Provide clear instructions if models are missing
  - Update skip messages with training commands
  - _Requirements: 10.5_
- [x] 7. Train models and verify benchmarks







- [ ] 7. Train models and verify benchmarks


- [x] 7.1 Train classification model




  - Run `python backend/scripts/train_classification.py`
  - Verify training completes successfully
  - Verify checkpoint is created at correct location
  - Verify model can be loaded by service
  - _Requirements: 4.7, 10.1_


- [x] 7.2 Train NCF model

  - Run `python backend/scripts/train_ncf.py`
  - Verify training completes successfully
  - Verify checkpoint is created at correct location
  - Verify model can be loaded by service
  - _Requirements: 10.2_


- [x] 7.3 Run classification benchmarks

  - Run classification quality metric tests
  - Run classification latency test
  - Verify all 6 tests pass
  - Verify metrics meet baseline thresholds
  - _Requirements: 10.3, 10.4_

- [ ] 7.4 Run NCF benchmarks
  - Run collaborative filtering quality metric tests
  - Run NCF latency test
  - Verify all 4 tests pass
  - Verify metrics meet baseline thresholds
  - _Requirements: 10.3, 10.4_

- [ ] 7.5 Run full benchmark suite
  - Run all 19 benchmark tests
  - Verify all tests pass (or skip with clear reason)
  - Generate benchmark report
  - Verify report shows improved coverage
  - _Requirements: 10.3, 10.4_
- [x] 8. Documentation and cleanup

- [x] 8. Documentation and cleanup




- [x] 8.1 Update developer documentation


  - Add training instructions to DEVELOPER_GUIDE.md
  - Document NCF service API
  - Add examples of using trained models
  - Document model checkpoint locations
  - _Requirements: 9.5_


- [x] 8.2 Add README for training scripts

  - Create README in backend/scripts/ directory
  - Document training script usage
  - Provide example commands
  - List hyperparameter options
  - _Requirements: 9.5_


- [x] 8.3 Update ML benchmarks documentation

  - Update ML_BENCHMARKS.md with new results
  - Document model training requirements
  - Add troubleshooting section
  - _Requirements: 10.5_
